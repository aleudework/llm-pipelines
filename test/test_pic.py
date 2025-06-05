import lmstudio as lms
from pdf2image import convert_from_path
import os
from pydantic import BaseModel
from typing import List

# === Pydantic schema ===
class Fakturalinje(BaseModel):
    fakturalinje_beskrivelse: str
    antal: int
    linje_beløb: float

class Faktura(BaseModel):
    kreditor: str
    fakturalinjer: List[Fakturalinje]
    secure: int

# === Load prompt ===
with open("../prompts/faktura_reader.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# === Konverter PDF til billede ===
pdf_path = "/Users/alhu/Data/Faktura_Samples/10.pdf"
temp_image_path = "temp_9_page1.png"
images = convert_from_path(pdf_path)
images[0].save(temp_image_path)

try:
    # === Forbered billede og kør model ===
    image_handle = lms.prepare_image(temp_image_path)
    model = lms.llm("llama-4-scout-17b-16e-instruct")

    chat = lms.Chat()
    chat.add_user_message(prompt, images=[image_handle])

    print("Kører testkald...")
    response = model.respond(chat)

    print("Svar fra model:")
    print(response.content)

finally:
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)