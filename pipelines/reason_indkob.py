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
from model import response_structured, response
from wrapper import wrapper
from extractor import extract_label_from_response



# === Functions ===

def create_prompt(row, config):
    # Get prompt path
    path = '../prompts/reason_indkob.txt' # Prompt path

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

    answer = response(prompt, idx, model, model_config, 1)
    print(answer)

    return answer

# === Pipeline ===

def pipeline(row, idx, model, config):
    try:

        prompt = create_prompt(row, config)
        answer = model_response(prompt, idx, model, config)
        label, reason, data = extract_label_from_response(answer, labels=config['labels'])

        return label, reason, data

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return row, None, None


# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/reason_indkob.yaml'

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)

    for col in ['Label', 'Reason', 'Thinking Words', 'Total Words']:
        if col not in df.columns:
            df[col] = None

    # Loop over each row in df
    for idx in range(idx, len(df)):

        # Handle row with pipeline
        label, reason, data = pipeline(df.loc[idx], idx, model, config)

        print('label')
        print(label)
        print(data)

        df.at[idx, 'Label'] = label
        df.at[idx, 'Reason'] = reason
        df.at[idx, 'Thinking Words'] = data['thinking words']
        df.at[idx, 'Total Words'] = data['total words']

        # Create backup
        if backup_itr and ((idx + 1) % backup_itr == 0):
            create_backup(df, idx, config['backup'])

    # Write final output
    write_df(df, config['output'])
    print('Output written')

    # Delete backup as it is not needed anymore
    delete_backup(config['backup'])