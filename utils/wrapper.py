import logging
import lmstudio as lms
import pandas as pd

from prompts import build_prompt
from config import load_config
from dataframe import load_df, write_df
from backup import load_backup, delete_backup, create_backup
from logs import setup_logger
from model import response_structured

def wrapper(config_path):
    # Load config file
    config = load_config(config_path)

    # Setup logger
    setup_logger(config['log'])

    # Load data
    df = load_df(config['data'])

    # Check for backup and then load backup
    df, idx = load_backup(df, config['backup'])
    logging.info('Data loaded')
    print('Data loaded')

    # Load model
    model = lms.llm(config['model'])
    logging.info(f'Model {config['model']} succesfully loaded')
    print('Model loaded')

    # Check for backup iteration config
    backup_itr = config.get('backup_itr') or 250

    return df, idx, model, config, backup_itr
