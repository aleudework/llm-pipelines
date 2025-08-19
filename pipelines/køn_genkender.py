import os
import sys
import re
import lmstudio as lms
import pandas as pd
import logging
import json
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from prompts import build_prompt, load_multiple_prompts, format_multiple_prompts, format_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, check_and_create_backup
from logs import setup_logger, webhook_logger
from model import response_structured, create_chat, add_message, gpt_oss_message_decoder
from wrapper import wrapper


# === Helpers ===

def find_gender(text: str) -> str | None:
    # søg efter første forekomst af "mand" eller "kvinde" uanset case
    match = re.search(r"\b(mand|kvinde)\b", text, flags=re.IGNORECASE)
    if match:
        word = match.group(1).lower()
        if word == "mand":
            return "Mand"
        elif word == "kvinde":
            return "Kvinde"
    return None

def find_first_number(text: str) -> int | None:
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())
    return None

# === Pipeline ===

def pipeline(df, row, idx, model, config):
    try:
        # An object to be filled and returned
        output = {
            'gender': None,
            'secure': None,
        }

        # An object to fill prompts
        prompt_variables = {
            'name': row['Navn'],
            'gender': None,
        }

        # Load all prompts
        prompts = load_multiple_prompts(config)

        # Creates chat from system prompt
        chat = create_chat(prompts[0])

        # First chat
        prompt_1 = format_prompt(prompts[1], prompt_variables)
        res_1, chat = add_message(chat, prompt_1, idx, model, {'max_tokens': 2000}, 1)
        # Decoding
        res_1_decoded = gpt_oss_message_decoder(res_1)
        gender = find_gender(res_1_decoded)
        print(res_1)

        # Adding
        output['gender'] = gender
        prompt_variables['gender'] = gender

        # Second chat
        prompt_2 = format_prompt(prompts[2], prompt_variables)
        res_2, chat = add_message(chat, prompt_2, idx, model, {'max_tokens': 2000}, 1)
        secure = find_first_number(res_2)
        # Adding
        output['secure'] = secure
        print(res_2)

        return output

    except Exception as e:
        print(e)
        return e
    
# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/køn_genkender.yaml'

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)

    for idx in range(idx, len(df)):
        
        result = pipeline(df, df.loc[idx], idx, model, config)

        print(result)

        if result is not None:
            df.at[idx, 'Køn'] = result.get('gender', None)
            df.at[idx, 'Sikker på køn'] = result.get('secure', None)
        
        else:

            df.at[idx, 'Køn'] = None
            df.at[idx, 'Sikker på køn'] = None

        check_and_create_backup(df, idx, config)

    write_df(df, config['output'])
    print('Output written')
            


