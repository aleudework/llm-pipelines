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
from model import response_structured, create_chat, add_message
from wrapper import wrapper


# === Schemas ===

# === Functions ===

def get_largest_faktura(df, config, kreditor, fakturabeskrivelse):
    """
    For a given supplier (kreditor) and invoice description (fakturabeskrivelse), 
    find the invoice number (Fakturanummer) that occurs most frequently.
    Return all invoice lines (sorted by line number) for this invoice as a JSON-like list.
    """
    try: 
        # Get relevant column names from config
        col_kreditor = config['data_params_fakturaer']['kreditor']
        col_fakturabeskrivelse = config['data_params_fakturaer']['fakturabeskrivelse']
        col_antal = config['data_params_fakturaer']['antal']
        col_stykpris = config['data_params_fakturaer']['stykpris']
        col_linjenummer = config['data_params_fakturaer']['linjenummer']
        col_fakturanummer = config['data_params_fakturaer']['fakturanummer']

        # Filter rows matching both supplier and description
        filtered = df[(df[col_kreditor] == kreditor) & (df[col_fakturabeskrivelse] == fakturabeskrivelse)]

        # Return empty if nothing matches
        if filtered.empty:
            return []
        
        # Find the most common invoice number (the one appearing most times)
        faktura_mode = filtered[col_fakturanummer].mode()
        if faktura_mode.empty:
            return []
        
        fakturanummer = faktura_mode.iloc[0]

        # Filter to this invoice number and sort by line number
        filtered_faktura = filtered[filtered[col_fakturanummer] == fakturanummer].sort_values(by=col_linjenummer)

        # Build result as a list of dictionaries (line, quantity, unit price)
        result_json = [
            {
                "fakturalinje": row[col_fakturabeskrivelse],
                "antal": row[col_antal],
                "stykpris": row[col_stykpris]
            }
            for _, row in filtered_faktura.iterrows()
        ]
        return result_json

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return []
    
def add_keys_to_dict(input_dict, keys=None):
    if keys:
        return {**input_dict, **keys}
    else:
        return input_dict



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


def pipeline(df, df_fakt, row, idx, model, config):
    try:
        # Initialize output dict
        output = {
            'label': None,
            'secure': None,
            'reason': None,
            'faktura': None
        }
        

        # Initialize column names
        col_kreditor = config['data_params']['kreditor']
        col_fakturabeskrivelse = config['data_params']['input_col']

        # Load prompts and create chat with system prompt
        prompts = load_multiple_prompts(config) # Load all prompts
        chat = create_chat(prompts[0])

        # Load largest faktura matching varelinje
        faktura_json = get_largest_faktura(df_fakt, config, row[col_kreditor], row[col_fakturabeskrivelse])

        # Create an dict with values for prompts
        input_dict = {
            'fakturalinje': row[col_fakturabeskrivelse],
            'kreditor': row[col_kreditor],
            'faktura': faktura_json
        }

        # Query classification
        first_prompt = format_prompt(prompts[1], input_dict)
        first_res, chat = add_message(chat, first_prompt, idx, model, {'max_tokens': 35}, -1)
        output['label'] = classify(first_res, ['Tjenesteydelse', 'Materialeindkøb'])

        #Update dict
        input_dict = add_keys_to_dict(input_dict, {'klassificering': output['label']})

        # Query reason
        second_prompt = format_prompt(prompts[2], input_dict)
        second_res, chat, stats = add_message(chat, second_prompt, idx, model, {'max_tokens': 200}, 1, stats=True)
        output['reason'] = second_res

        # Query score
        third_prompt = format_prompt(prompts[3], input_dict)
        third_res, chat = add_message(chat, third_prompt, idx, model, {'max_tokens': 25}, -1)
        output['secure'] = first_number(third_res)

        # Add faktura_json to output
        output['faktura'] = faktura_json

        return output, stats

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return output, None

# === Main Setup ===

if __name__ == '__main__':

    print('Script started')

    config_path = '../config/faktura_effective.yaml'

    # Wrapper does
    # Setup logger
    # Load data or/and backup
    # Load model
    # Backup itr
    df, idx, model, config, backup_itr = wrapper(config_path)
    df_fakt = load_df(config['data_fakturaer'])

    # Loop over each row in df
    for idx in range(idx, len(df)):

        # Handle row with pipeline
        result, stats = pipeline(df, df_fakt, df.loc[idx], idx, model, config)
        
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

        else:
            df.at[idx, 'Klassificering'] = None
            df.at[idx, 'Score'] = None
            df.at[idx, 'Begrundelse'] = None
            df.at[idx, 'Hele Fakturaen'] = None

        # Check and create backup
        check_and_create_backup(df, idx, config)
        
        logger_msg = f"-------- Row: {idx+1}, Data: {result} ---- Stats: {stats}"
        webhook_logger(idx, config, logger_msg)


    # Write final output
    write_df(df, config['output'])
    print('Output written')

    # Delete backup as it is not needed anymore
    #delete_backup(config)