import os
import sys
import lmstudio as lms
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

def create_prompt(row, config):
    # Get prompt path
    path = '../prompts/simple_indkob.txt' # Prompt path

    # Load and check input col
    input_col = config['data_params']['input_col']
    input_col = 'Fakturabeskrivelse' if input_col is None or str(input_col).lower() == "null" else input_col

    # Get input label
    input = row[input_col]

    # Directory for variables
    input_dict = {
        'fakturalinje': input
    }

    # Return the builded prompt
    return build_prompt(path, input_dict)


def model_response(prompt, idx, model, config):

    # Setup model config
    model_config = {
        'max_tokens': config['model_params']['max_tokens'],
        'temperature': config['model_params']['temperature']
    }

    answer = response_structured(prompt, idx, model, Indkøb, model_config, 1)
    return answer

def label_adjuster(answer):
    label = answer['label'].lower()
    if "mat" in label:
        answer['label'] = "Materialeindkøb"
    elif "tjen" in label:
        answer['label'] = "Tjenesteydelse"
    else:
        answer['label'] = "Ukendt"
    return answer

# === Pipeline ===

def pipeline(row, idx, model, config):
    try:

        prompt = create_prompt(row, config)
        answer = model_response(prompt, idx, model, config)
        answer_adjusted = label_adjuster(answer)

        return answer_adjusted

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return row


# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/simple_indkob.yaml'

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)

    # Loop over each row in df
    for idx in range(idx, len(df)):

        # Handle row with pipeline
        result = pipeline(df.loc[idx], idx, model, config)

        df.at[idx, 'Klassificering'] = result['label']
        df.at[idx, 'Score'] = result['secure']
        df.at[idx, 'Begrundelse'] = result['reason']

        # Create backup
        if backup_itr and ((idx + 1) % backup_itr == 0):
            create_backup(df, idx, config['backup'])

    # Write final output
    write_df(df, config['output'])
    print('Output written')

    # Delete backup as it is not needed anymore
    delete_backup(config['backup'])