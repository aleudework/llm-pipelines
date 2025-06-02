import os
import sys
import lmstudio as lms
from lmstudio import Chat
import pandas as pd
import logging
import json
from pydantic import BaseModel


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from prompts import build_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, create_backup
from logs import setup_logger
from model import response_structured
from wrapper import wrapper

# === Schemas ===

class Indkøb(BaseModel):
    label: str # Only materialeindkøb or tjenesteydelse
    reason: str # A reason for the choice
    secure: int # 1 to 10 on how sure it is on its answer


# === Functions ===
def sys_prompt():
    prompt = """Du arbejder for en dansk boligadministration, som står for drift og vedligeholdelse af boliger.  
    Du får nu en fakturalinje, som du skal klassificere som enten en **tjenesteydelse** eller et **materialeindkøb**, alt efter hvad der passer bedst.

    Definitioner:  
    - "tjenesteydelse": Arbejde, service eller drift (fx rengøring, reparationer, håndværk).  
    - "materialeindkøb": Fysiske ting, der bliver købt (fx maling, værktøj, reservedele).

    Opgave:  
    1. Sæt `label` til enten `"tjenesteydelse"` eller `"materialeindkøb"`.  
    2. Giv en kort begrundelse i `reason` (1–2 linjer), som forklarer hvorfor du valgte den klassificering.
    3. Giv et tal i 'secure' mellem 1 og 10 på, hvor sikker du er på dit svar. 10 er mest sikker, 1 er mindst sikker.
    """
    return prompt

def create_prompt(row, input_col):

    text = row[input_col]
    prompt = f"Fakturalinje: {text}"
    return prompt



# === Main Setup ===


if __name__ == '__main__':

    data_path = ''
    output_path = ''
    model_name = ''
    input_col = 'Fakturabeskrivelse'

    df = load_df(data_path)
    setup_logger()

    batch_size = 25
    total_rows = len(df)

    system_prompt = sys_prompt()

    logging('CHAT MODE')
    logging('Data loaded')

    model = lms.llm(model_name)

    logging('Model loaded')


    for super_idx in range(0, total_rows, batch_size):
        end_idx = min(super_idx + batch_size, total_rows)

        chat = Chat(system_prompt)
        
        for idx in range(super_idx, end_idx):
            row = df.loc[idx]
            prompt = create_prompt(row, input_col)

            chat.add_user_message(prompt)

            prediction = model.respond(chat, response_format=Indkøb)

            if isinstance(prediction, str):
                prediction = json.loads(prediction)

            df.at[idx, 'Klassificering'] = prediction['label']
            df.at[idx, 'Score'] = prediction['secure']
            df.at[idx, 'Begrundelse'] = prediction['reason']

            logging(f"Iteration {idx}")   

    write_df(df, output_path)