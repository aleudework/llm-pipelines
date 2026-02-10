import sys
import os
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from model_api import Model_API


prompt = "giv mig tre ord"
model = 'meta-llama-3.1-8b-instruct'


model_api = Model_API(model = model)

res = model_api.response(prompt=prompt)

print(res)

print ("----")

prompt = "Er teksten positiv eller negativ? Tekst: Jeg elsker is. Output KUN i JSON"

class Classification(BaseModel):
    label: str
    confidence: float

res = model_api.response(prompt=prompt, text_format = Classification)

print(res)