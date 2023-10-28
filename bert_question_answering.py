import numpy as np
from openvino.model_zoo.model_api.models import BertEmbedding, BertQuestionAnswering
from openvino.model_zoo.model_api.models.tokens_bert import text_to_tokens, load_vocab_file, ContextWindow
from openvino.model_zoo.model_api.pipelines import get_user_config, AsyncPipeline
from openvino.model_zoo.model_api.adapters import create_core, OpenvinoAdapter


class ContextSource:
    def __init__(self, paragraphs, vocab, c_window_len):
        self.paragraphs = paragraphs
        self.c_tokens = [text_to_tokens(par.lower(), vocab) for par in paragraphs]
        self.c_window_len = c_window_len
        self.par_id = -1
        self.get_next_paragraph()

    def get_data(self):
        c_data = self.window.get_context_data(self.paragraphs[self.par_id])
        self.window.move()
        if self.window.is_over():
            self.get_next_paragraph()
        return c_data

    def get_next_paragraph(self):
        self.par_id += 1
        if not self.is_over():
            if self.c_tokens[self.par_id][0]:
                self.window = ContextWindow(self.c_window_len, *self.c_tokens[self.par_id])
            else:
                self.get_next_paragraph()

    def is_over(self):
        return self.par_id == len(self.paragraphs)

vocab = "question_answering/vocab.txt"
device = "CPU"
num_streams = ""
num_threads = None
model_emb = "question_answering/bert-large-uncased-whole-word-masking-squad-emb-0001.xml"
num_infer_requests = 0
layout_emb = None
input_names_emb = 'input_ids,attention_mask,token_type_ids,position_ids'
layout_qa = None
input_names_qa = 'input_ids,attention_mask,token_type_ids,position_ids'
output_names_qa = 'output_s,output_e'
max_answer_token_num = 15
model_qa_squad_ver = "1.2"
best_n = 10
model_qa = "question_answering/bert-small-uncased-whole-word-masking-squad-0002.xml"

class QA:
    def __init__(self, paragraphs):
        self.vocab = load_vocab_file(vocab)

        core = create_core()
        plugin_config = get_user_config(device, num_streams, num_threads)
        self.model_emb_adapter = OpenvinoAdapter(core, model_emb, device=device, plugin_config=plugin_config,
                                            max_num_requests=num_infer_requests, model_parameters = {'input_layouts': layout_emb})
        self.model_emb = BertEmbedding(self.model_emb_adapter, {'vocab': self.vocab, 'input_names': input_names_emb})

        max_len_context = 256
        self.max_len_question = 32

        for new_length in [self.max_len_question, max_len_context]:
            self.model_emb.reshape(new_length)
            if new_length == self.max_len_question:
                self.emb_request = core.compile_model(self.model_emb_adapter.model, device).create_infer_request()
            else:
                emb_pipeline = AsyncPipeline(self.model_emb)

        model_qa_adapter = OpenvinoAdapter(core, model_qa, device=device, plugin_config=plugin_config,
                                        max_num_requests=num_infer_requests, model_parameters = {'input_layouts': layout_qa})
        config = {
            'vocab': self.vocab,
            'input_names': input_names_qa,
            'output_names': output_names_qa,
            'max_answer_token_num': max_answer_token_num,
            'squad_ver': model_qa_squad_ver
        }
        model_bqa = BertQuestionAnswering(model_qa_adapter, config)
        self.qa_pipeline = AsyncPipeline(model_bqa)

        self.contexts_all = []

        c_window_len = model_bqa.max_length - (self.max_len_question + 3)
        
        source = ContextSource(paragraphs, self.vocab, c_window_len)
        next_window_id = 0
        next_window_id_to_show = 0
        self.contexts_all = []

        while True:
            if emb_pipeline.callback_exceptions:
                raise emb_pipeline.callback_exceptions[0]
            results = emb_pipeline.get_result(next_window_id_to_show)
            if results:
                embedding, meta = results
                meta['c_data'].emb = embedding
                self.contexts_all.append(meta['c_data'])
                next_window_id_to_show += 1
                continue

            if emb_pipeline.is_ready():
                if source.is_over():
                    break
                c_data = source.get_data()
                num = min(max_len_context - 2, len(c_data.c_tokens_id))
                emb_pipeline.submit_data((c_data.c_tokens_id[:num], max_len_context), next_window_id, {'c_data': c_data})
                next_window_id += 1
            else:
                emb_pipeline.await_any()

        emb_pipeline.await_all()
        if emb_pipeline.callback_exceptions:
            raise emb_pipeline.callback_exceptions[0]
        for window_id in range(next_window_id_to_show, next_window_id):
            results = emb_pipeline.get_result(window_id)
            embedding, meta = results
            meta['c_data'].emb = embedding
            self.contexts_all.append(meta['c_data'])
            next_window_id_to_show += 1

    def calc_question_embedding(self, tokens_id):
        num = min(self.max_len_question - 2, len(tokens_id))
        inputs, _ = self.model_emb.preprocess((tokens_id[:num], self.max_len_question))
        self.emb_request.infer(inputs)
        raw_result = self.model_emb_adapter.get_raw_result(self.emb_request)
        return self.model_emb.postprocess(raw_result, None)


    def update_answers_list(self, answers, output, c_data):
        same = [i for i, ans in enumerate(answers) if ans[1:3] == output[1:3] and ans[3] in c_data.context]
        if not same:
            answers.append((*output, c_data.context))
        else:
            assert len(same) == 1
            prev_score = answers[same[0]][0]
            answers[same[0]] = (max(output[0], prev_score), *output[1:], c_data.context)

    def generate(self, question):
        q_tokens_id, _ = text_to_tokens(question.lower(), self.vocab)
        q_emb = self.calc_question_embedding(q_tokens_id)
        distances = [(np.linalg.norm(context.emb - q_emb, 2), context) for context in self.contexts_all]
        distances.sort(key=lambda x: x[0])
        keep_num = min(best_n, len(distances))
        distances_filtered = distances[:keep_num]

        answers = []
        next_context_id = 0
        next_context_id_to_show = 0

        while True:
            if self.qa_pipeline.callback_exceptions:
                raise self.qa_pipeline.callback_exceptions[0]
            results = self.qa_pipeline.get_result(next_context_id_to_show)
            if results:
                next_context_id_to_show += 1
                output, meta = results
                self.update_answers_list(answers, output, meta['c_data'])
                continue

            if self.qa_pipeline.is_ready():
                if next_context_id == len(distances_filtered):
                    break
                _, c_data = distances_filtered[next_context_id]
                self.qa_pipeline.submit_data((c_data, q_tokens_id), next_context_id, {'c_data': c_data})
                next_context_id += 1
            else:
                self.qa_pipeline.await_any()

        self.qa_pipeline.await_all()
        if self.qa_pipeline.callback_exceptions:
            raise self.qa_pipeline.callback_exceptions[0]
        for context_id in range(next_context_id_to_show, next_context_id):
            results = self.qa_pipeline.get_result(context_id)
            output, meta = results
            self.update_answers_list(answers, output, meta['c_data'])

        answers = sorted(answers, key=lambda x: -x[0])[:3]
        result = []
        for score, s, e, context in answers:
            result.append(context[s:e])
        return result