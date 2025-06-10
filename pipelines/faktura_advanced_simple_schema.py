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
    secure: int # 1 to 10 on how sure it is on its answer

# === Functions ===

def find_faktura(df, kreditor, fakturanummer, col_linjenummer, col_fakturabeskrivelse, col_antal, col_stykpris):
    """
    Find all rows for a given 'kreditor' and 'fakturanummer', 
    sort by line number, and return as JSON (only beskrivelse, antal, stykpris).
    """
    # Filtrer rækker der matcher kreditor OG fakturanummer
    filtered = df[(df['Kreditor'] == kreditor) & (df['Fakturanummer'] == fakturanummer)]

    # Sorter efter linjenummer (stigende)
    filtered = filtered.sort_values(by=col_linjenummer)
    
    
    # Vælg kun de relevante kolonner
    result = filtered[[col_linjenummer, col_fakturabeskrivelse, col_antal, col_stykpris]]
    
    # Byg en liste af dicts, kun med beskrivelse, antal og stykpris
    result_json = [
        {
            "fakturalinje": row[col_fakturabeskrivelse],
            "antal": row[col_antal],
            "stykpris": row[col_stykpris]
        }
        for _, row in result.iterrows()
    ]
    return result_json

def create_prompt(df, row, config):

    # Loading columns
    kreditor = config['data_params']['kreditor']
    fakturanummer = config['data_params']['fakturanummer']
    linjenummer = config['data_params']['linjenummer']
    input_col = config['data_params']['input_col']
    antal = config['data_params']['antal']
    stykpris = config['data_params']['stykpris']

    faktura = find_faktura(df, row[kreditor], row[fakturanummer], linjenummer, input_col, antal, stykpris)

    # Get prompt path
    path = '../prompts/faktura_advanced.txt' # Prompt path

    # Load and check input col

    # Get input label
    input_row = row[input_col]
    kreditor_row = row[kreditor]

    # Directory for variables
    input_dict = {
        'fakturalinje': input_row,
        'kreditor': kreditor_row,
        'faktura': faktura
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

def pipeline(df, row, idx, model, config):
    try:

        prompt = create_prompt(df, row, config)
        answer = model_response(prompt, idx, model, config)
        print(answer)
        answer_adjusted = label_adjuster(answer)

        return answer_adjusted

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return row


# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/faktura_advanced_simple_schema.yaml'

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)

    # Loop over each row in df
    for idx in range(idx, len(df)):

        # Handle row with pipeline
        result = pipeline(df, df.loc[idx], idx, model, config)

        df.at[idx, 'Klassificering'] = result['label']
        df.at[idx, 'Score'] = result['secure']

        # Create backup
        if backup_itr and ((idx + 1) % backup_itr == 0):
            create_backup(df, idx, config)

    # Write final output
    write_df(df, config['output'])
    print('Output written')

    # Delete backup as it is not needed anymore
    delete_backup(config)