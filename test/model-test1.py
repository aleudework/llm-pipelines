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
from model import response_structured, response
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
    
    Fakturalinje: VOSS Komfur VB9385L med installation

    """
    return prompt


# === Main Setup ===


if __name__ == '__main__':


    model_name = 'phi-4'
    
    setup_logger()

    system_prompt = sys_prompt()
    logging.info('Data loaded')

    model = lms.llm(model_name)


    result = response(system_prompt, 0, model, config=None, log_every=100)

    print(result)

