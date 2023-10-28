from transformers import GPT2Tokenizer, GPT2LMHeadModel
import re


class GPT2:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

    def generate(self, input_text):
        input_text = input_text.replace("\n", "")
        text = "[user]: " + input_text + " \n[AI]: "
        encoded_input = self.tokenizer(text, return_tensors="pt")
        outputs = self.model.generate(
            **encoded_input,                     
            max_length=1024,
            no_repeat_ngram_size=2,
            labels=encoded_input["input_ids"],
            num_beams=5
        )
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        result = result.replace(text, "")
        result = result.replace("\n", "")
        result = re.sub(r'[~@#$^&*]', '', result)
        result = re.sub(r'\s+', ' ', result)
        return result