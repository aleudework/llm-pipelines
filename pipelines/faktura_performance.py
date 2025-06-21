import os
import sys
import re
import lmstudio as lms
import pandas as pd
import logging
import json
from pydantic import BaseModel
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from prompts import build_prompt, load_multiple_prompts, format_multiple_prompts, format_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, check_and_create_backup
from logs import setup_logger, webhook_logger
from model import response_structured, create_chat, add_message
from wrapper import wrapper


# === Schemas ===

# === Functions ===

def find_faktura(df, kreditor, fakturanummer, col_linjenummer, col_fakturabeskrivelse, col_antal, col_stykpris):
    """
    Helper

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

def create_dictionary(df, row, config, more_keys=None):
    kreditor = config['data_params']['kreditor']
    fakturanummer = config['data_params']['fakturanummer']
    linjenummer = config['data_params']['linjenummer']
    input_col = config['data_params']['input_col']
    antal = config['data_params']['antal']
    stykpris = config['data_params']['stykpris']

    if pd.isna(row[input_col]):
        return

    faktura = find_faktura(df, row[kreditor], row[fakturanummer], linjenummer, input_col, antal, stykpris)

    # Get input label
    input_row = row[input_col]
    kreditor_row = row[kreditor]

    # Directory for variables
    input_dict = {
        'fakturalinje': input_row,
        'kreditor': kreditor_row,
        'faktura': faktura
    }

    if more_keys:
        final_dict = {**input_dict, **more_keys}
    else:
        final_dict = input_dict

    return final_dict

def classify(answer, labels):
    answer_lower = answer.lower()

    for label in labels:
        label_lowered = label.lower()
        if label_lowered in answer_lower:
            return label
    return "Ukendt"

def classify_indkob(answer):
    for word in answer.split():
        word_lowered = word.lower()
        if 'mat' in word_lowered:
            return 'Materialeindkøb'
        elif 'tjen' in word_lowered:
            return 'Tjenesteydelse'
        else:
            return 'Ukendt'
        
def first_number(answer):
    """
    Returns the first number from a string
    """
    match = re.search(r'\d+', answer)
    if match:
        return int(match.group())
    return -1

# === Pipeline ===


def pipeline(df, row, idx, model, config):
    try:
        output = {
            'label': None,
            'secure': None,
            'reason': None,
            'category': None,
            'secure_category': None,
            'reason_category': None,
            'faktura': None
        }

        prompts = load_multiple_prompts(config) # Load all prompts
        chat = create_chat(prompts[0])

        dict1 = create_dictionary(df, row, config)
        output['faktura'] = dict1['faktura']

        prompt1 = format_prompt(prompts[1], dict1)
        res1, chat = add_message(chat, prompt1, idx, model, {'max_tokens': 35}, -1)
        output['label'] = classify(res1, ['Tjenesteydelse', 'Materialeindkøb'])

        dict2 = create_dictionary(df, row, config, {'klassificering': output['label']})
        prompt2 = format_prompt(prompts[2], dict2)
        res2, chat, stats = add_message(chat, prompt2, idx, model, {'max_tokens': 150}, 1, stats=True)
        output['reason'] = res2

        prompt3 = format_prompt(prompts[3], dict2)
        res3, chat = add_message(chat, prompt3, idx, model, {'max_tokens': 25}, -1)
        output['secure'] = first_number(res3)
    
        return output, stats

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return output, None

# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/faktura_performance.yaml'

    start_time = datetime.datetime.now()

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)

    webhook_logger(0, config, 'STARTED')

    # Loop over each row in df
    for idx in range(idx, len(df)):

        # Handle row with pipeline
        result, stats = pipeline(df, df.loc[idx], idx, model, config)
        
        if result is not None:
            df.at[idx, 'Klassificering'] = result.get('label', None)
            df.at[idx, 'Score'] = result.get('secure', None)
            df.at[idx, 'Begrundelse'] = result.get('reason', None)

            # Håndter faktura som JSON-streng
            faktura = result.get('faktura', None)
            try:
                faktura_json = json.dumps(faktura, ensure_ascii=False)
            except Exception as e:
                faktura_json = None
                logging.warning(f"Kunne ikke konvertere faktura til JSON ved row {idx}: {repr(e)}")
            
            df.at[idx, 'Hele Fakturaen'] = faktura_json
            df.at[idx, 'Stats'] = stats if stats else None

        else:
            df.at[idx, 'Klassificering'] = None
            df.at[idx, 'Score'] = None
            df.at[idx, 'Begrundelse'] = None
            df.at[idx, 'Hele Fakturaen'] = None
            df.at[idx, 'Stats'] = None

        # Check and create backup
        check_and_create_backup(df, idx, config)
        
        logger_msg = f"-------- Row: {idx+1}, Data: {result} ---- Stats: {stats}"
        webhook_logger(idx, config, logger_msg)

    webhook_logger(0, config, 'DONE')

    end_time = datetime.datetime.now()
    duration = end_time - start_time

    output_path = config['output']
    base_path = os.path.splitext(output_path)[0]  # remove extension
    txt_path = base_path + '_runtime.txt'

    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {duration}\n")

    print(f"Runtime written to {txt_path}")

    # Write final output
    write_df(df, config['output'])
    print('Output written')

    # Delete backup as it is not needed anymore
    #delete_backup(config)