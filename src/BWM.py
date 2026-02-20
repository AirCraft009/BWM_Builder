import pandas as pd
import re
from PIL import Image
import torch
from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor
import ruleset 

class Bwm_builder:
    def __init__(self) :
        # decide platform apple(mps), nvidia(cuda) or cpu and set dtype accordingly
        device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float32 if device == "mps" else torch.bfloat16

        self.model = LightOnOcrForConditionalGeneration.from_pretrained("lightonai/LightOnOCR-2-1B", torch_dtype=dtype).to(device)
        self.processor = LightOnOcrProcessor.from_pretrained("lightonai/LightOnOCR-2-1B")
        print(f"Model loaded on {device} with dtype {dtype}")
        
    def image_question(self, imagepath : str, question : str, maxTokens : int = 1024) -> str:
        image = Image.open(imagepath)
        conversation = [{"role": "user", "content": 
            [{"type": "image", "image": image}, 
                {"type": "text", "text": ruleset.ruleset + "\n\n" + question}]
            }]

        inputs = self.processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            temperature=0.0
        )
        inputs = {k: v.to(device=self.model.device, dtype=self.model.dtype) if v.is_floating_point() else v.to(self.model.device) for k, v in inputs.items()}

        output_ids = self.model.generate(**inputs, max_new_tokens=maxTokens)

        generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]

        output_text = self.processor.decode(generated_ids, skip_special_tokens=True)
        
        return output_text
                    
    def extract_data(self, image_path):
        
        image = Image.open(image_path)
        conversation = [{"role": "user", "content": [{"type": "image", "image": image}]}]

        inputs = self.processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            temperature=0.0,
        )
        inputs = {k: v.to(device=self.model.device, dtype=self.model.dtype) if v.is_floating_point() else v.to(self.model.device) for k, v in inputs.items()}

        output_ids = self.model.generate(**inputs, max_new_tokens=1024)

        generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]

        output_text = self.processor.decode(generated_ids, skip_special_tokens=True)
        return output_text
    
        
builder = Bwm_builder()
print(builder.image_question("tests/Beispiel-Aufgabe.png", "Question : Extract the all information specified above and return it in the specified JSON format."))