from transformers import AutoTokenizer, BertForTokenClassification
from transformers import pipeline


class NER:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.model = BertForTokenClassification.from_pretrained("dslim/bert-base-NER")

    def generate(self, input_text):
        nlp = pipeline("ner", model=self.model, tokenizer=self.tokenizer)
        ners = nlp(input_text)
        res = []
        for ner in ners:
            if ner["entity"][0] == 'B':
                res.append(ner["word"])
            else:
                res[-1] = res[-1] + ner["word"].replace("#", "")
        return res