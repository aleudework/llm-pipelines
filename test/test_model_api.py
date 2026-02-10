import sys
import os
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from model_api import Model_API
from decoder import decode_regex


prompt = "giv mig tre ord"
model = 'openai/gpt-oss-20b'


model_api = Model_API(model = model)

prompt = "Hvilket sal er boligen på ud fra dens addresse: Hjortevænget 30 ST MF. Retunerer altid etagen først. Giv også en forklaring hertil. Hvis der ikke er en etage, skal du skrive DER ER INGEN ETAGE"

res = model_api.response(prompt=prompt)

print(res)

print("-----")

regex = r"(?i)der er ingen etage|(?!.*der er ingen etage)\d+"
out = decode_regex(regex, str(res))

print(out)

