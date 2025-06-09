import logging
import lmstudio as lms
import pandas as pd

from config import load_config
from dataframe import load_df
from backup import load_backup
from logs import setup_logger

def wrapper(config_path, log_name='log'):
    # Load config file
    config = load_config(config_path)

    # Setup logger
    setup_logger(config, log_name=log_name)

    # Load data
    df = load_df(config['data'])

    # Check for backup and then load backup
    df, idx = load_backup(df, config)
    logging.info('Data loaded')
    print('Data loaded')

    # Load model
    model = lms.llm(config['model'])
    logging.info(f'Model {config['model']} succesfully loaded')
    print('Model loaded')

    # Check for backup iteration config
    backup_itr = config.get('backup_itr') or 100

    return df, idx, model, config, backup_itr
