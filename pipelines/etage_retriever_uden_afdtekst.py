"""

Ud fra en DF med en "Adresse" kolonne bruges denne AI til at udlede
1) Etage, 2) Forklaring til etage

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


def extract_etage(text: str):
    if text is None:
        return None

    # Normaliser for unicode og whitespaces.
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text)

    # 1) Først: tjek fast tekst (case-insensitive)
    if "der er ingen etage" in text.casefold():
        return "DER ER INGEN ETAGE"

    # 2) Ellers: find første tal
    m = re.search(r"\d+", text)
    return m.group() if m else None

def pipeline(row, model, config):
    try:

        # Prompt building
        prompt_params = {
            "adresse": row["Adresse"],
            "lejemålstype": row["Lejemålstype"]
        }

        prompt = build_prompt(config['prompt'], prompt_params)

        raw = model.response(prompt=prompt)
        response = str(raw)


        etage = extract_etage(response)
        print("\n"*5)
        print("\n" + "=" * 60)

        print(f"""
        Lejemål
        -> Selskab:      {row['sel']}
        -> Afdeling:     {row['afd']}
        -> Lejemål nr.:  {row['lejemaal']}
        -> Type:         {row['Lejemålstype']}
        -> Adresse:      {row['Adresse']}
        """)

        if etage == "DER ER INGEN ETAGE":
            print("Klassifikation")
            print("  -> Ingen etage registreret")
        else:
            print("Klassifikation")
            print(f"  -> {etage} etage")

        print("\nForklaring fra model")
        print("-" * 60)
        print(response)
        print("-" * 60 + "\n")

        return etage, response

    except Exception as e:
        print(e)
        return None, None




if __name__ == '__main__':

    print('Script started')

    # Load config
    config_path = '../config/etage_retriever_uden_afdtekst.yaml'
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

        etage, forklaring = pipeline(df.loc[idx], model_api, config)

        if etage is not None:
            if str(etage).strip().casefold() == 'der er ingen etage':
                # Hvis ingen etage, f.eks. ST TH
                df.at[idx, "Etage"] = None
                df.at[idx, "Forklaring"] = forklaring
            else:
                # Hvis etage
                df.at[idx, "Etage"] = etage
                df.at[idx, "Forklaring"] = forklaring
        else:
                # Hvis fejl
                df.at[idx, "Etage"] = 9999
                df.at[idx, "Forklaring"] = None

        print("Antal lejemål gennemgået: ", counter)


        check_and_create_backup(df, idx, config)

    write_df(df, config['output'])
    print('Output written')
        
