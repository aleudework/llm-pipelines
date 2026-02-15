"""

Ud fra en overskrift og en afdelingstekst gives værdien "Ja/Nej" om det er gældende.

"""

import os
import logging
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))

from prompts import build_prompt, load_multiple_prompts, format_multiple_prompts, format_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, check_and_create_backup
from logs import setup_logger, webhook_logger
from model import response_structured, create_chat, add_message, gpt_oss_message_decoder
from wrapper import wrapper
from model_api import Model_API
import re
import unicodedata


def extract_ja_nej(text: str):
    if text is None:
        return None

    # Normaliser unicode og whitespace
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text)

    # Find første hele ord "ja" eller "nej" (case-insensitive)
    m = re.search(r"\b(ja|nej)\b", text, flags=re.IGNORECASE)

    return m.group().lower() if m else None

def pipeline(row, model, config):
    try:

        # Prompt building
        prompt_params = {
            "overskrift": row["Afdelingstekst i EG Bolig"],
            "tekst": row["Klausul indhold"]
        }

        prompt = build_prompt(config['prompt'], prompt_params)

        raw = model.response(prompt=prompt)
        response = str(raw)

        ja_nej = extract_ja_nej(response)

        print("Overskrift: ", row["Afdelingstekst i EG Bolig"])
        print("Tekst: ", row["Klausul indhold"])
        print("- - - ")

        print("Ja/Nej: ", ja_nej)
        print ("- - -")
        print(response)
        print ("__________________")
        
        logging.info(f"Overskrift: {row["Afdelingstekst i EG Bolig"]} | Tekst: {row["Klausul indhold"]}")
        logging.info(f"Ja_Nej: {ja_nej}")

        return ja_nej, response

    except Exception as e:
        print(e)
        return None, None




if __name__ == '__main__':

    print('Script started')

    # Load config
    config_path = '../config/afdelingstekster_ja_nej.yaml'
    config = load_config(config_path)

    # Setup logger
    setup_logger(config, log_name="log")

    # Load DF
    df = load_df(config['data'])

    # Check for backup and then load backup
    df, idx = load_backup(df, config)
    logging.info('Data loaded')
    print('Data loaded')
    backup_itr = config.get('backup_itr') or 100 # Backup itr

    # Start model
    model_api = Model_API(config)
    print("Model loaded")

    counter = 0

    for idx in range(idx, len(df)):
        counter += 1

        ja_nej, forklaring = pipeline(df.loc[idx], model_api, config)

        if ja_nej is not None:
                # Hvis etage
            df.at[idx, "Ja_Nej"] = ja_nej
            df.at[idx, "Forklaring"] = forklaring
        else:
            # Hvis fejl
            df.at[idx, "Etage"] = None
            df.at[idx, "Forklaring"] = None

        print("Counter ", counter)
        print("-----")

        check_and_create_backup(df, idx, config)

    write_df(df, config['output'])
    print('Output written')
        
