import os
import sys
import lmstudio as lms
import pandas as pd
import logging
import json
from typing import List
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))


from prompts import build_prompt, load_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, create_backup
from logs import setup_logger
from model import response_structured, response_image_input
from wrapper import wrapper
from pdf_to_image import find_pdf, pdf_to_images, remove_images
from temp import create_temp_folder, remove_temp_folder

# === Schemas ===

class Fakturalinje(BaseModel):
    fakturalinje_beskrivelse: str
    antal: int
    linje_beløb: float

class Faktura(BaseModel):
    kreditor: str
    fakturalinjer: List[Fakturalinje]
    secure: int

# === Functions ===

def pdf_path(row, config):

    pdf_folder = config['pdf_folder']
    col_id = config['data_params']['fakt_id']
    pdf_name = row[col_id] # ID matching pdf-file to find
    find_pdf_ = find_pdf(pdf_name, pdf_folder)
    return find_pdf_

def create_backup(fakturalinjer, idx, backup_path):
    if backup_path and str(backup_path).lower() != "null":
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        df_backup = pd.DataFrame(fakturalinjer)
        # Save backup
        df_backup.to_parquet(backup_path)
        # Save idx (how far we are)
        with open(backup_path + ".idx", "w") as f:
            f.write(str(idx))
        
        logging.info('Backup created')

def load_backup(backup_path):
    if backup_path and str(backup_path).lower() != "null" and os.path.exists(backup_path):
        df_backup = pd.read_parquet(backup_path)
        logging.info('Loaded from backup')
        if os.path.exists(backup_path + ".idx"):
            with open(backup_path + ".idx", "r") as f:
                idx = int(f.read())
        else:
            idx = len(df_backup)  # fallback: antag alt lavet
        return df_backup.to_dict(orient="records"), idx
    else:
        return [], 0

def delete_backup(backup_path):
    try:
        if backup_path and str(backup_path).lower() != "null":
            # Remove backup
            if os.path.exists(backup_path):
                os.remove(backup_path)
            # Remove idx
            if os.path.exists(backup_path + ".idx"):
                os.remove(backup_path + ".idx")
            logging.info('Removed backup')
    except Exception:
        pass

def explode_invoice_row(row, faktura_result):
    base_data = row.to_dict()
    new_rows = []
    for idx, linje in enumerate(faktura_result['fakturalinjer'], 1):  # starter fra 1
        d = base_data.copy()
        d['kreditor'] = faktura_result.get('kreditor', '')
        d['secure'] = faktura_result.get('secure', '')
        d.update(linje)  # tilføj alle felter fra fakturalinjen
        d['linjenummer'] = idx
        new_rows.append(d)
    return new_rows


# === Pipeline ===

def pipeline(row, idx, model, config, prompt, temp):
    try:
        pdf = pdf_path(row, config)
        images = pdf_to_images(pdf, temp)
        result_raw = response_image_input(prompt=prompt, idx=idx, model=model, images=images, config=config, log_every=1)
        prompt_2 = build_prompt('../prompts/faktura_reader_2.txt', {'faktura_text': result_raw})
        result = response_structured(prompt_2, idx, model, Faktura, config, log_every=1)
        remove_images(images)

        return result

    except Exception as e:
        logging.error(f"Error at {idx}: {repr(e)}")
        return row


# === Main Setup ===

if __name__ == '__main__':
    print('Script started')

    config_path = '../config/faktura_reader.yaml'
    # Load config file
    config = load_config(config_path)
    # Setup logger
    setup_logger(config['log'])

    # Load data
    df = load_df(config['data'])

    model = lms.llm(config['model'])
    logging.info(f'Model {config['model']} succesfully loaded')

    backup_itr = config.get('backup_itr') or 250

    # Create temp folder
    temp_path = create_temp_folder(config['pdf_folder'])

    # Load prompt
    prompt = load_prompt('../prompts/faktura_reader_1.txt')

    # Load backup if possible
    all_new_fakturalinjer, idx = load_backup(config['backup'])

    # LOOP
    for idx in range(idx, len(df)):
        result = pipeline(df.loc[idx], idx, model, config, prompt, temp_path)
        new_fakturalinjer = explode_invoice_row(df.loc[idx], result)
        all_new_fakturalinjer.extend(new_fakturalinjer)

    # Build and write DF
    df_final = pd.DataFrame(all_new_fakturalinjer)
    write_df(df_final, config['output'])

    # Delete backup
    delete_backup(config['backup'])

    # Remove temp folder
    remove_temp_folder(temp_path)




