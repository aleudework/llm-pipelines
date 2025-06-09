import pandas as pd
import os
import logging

def get_backup_path(config):
    """
    Helper function
    Returns the robust backup path based on project name from config.
    Always uses ../backup/{project_name}/backup.parquet
    """
    project_name = config['project']
    return os.path.join('../backup', project_name, 'backup.parquet')

def load_backup(df: pd.DataFrame, config):
    """
    Loads a parquet backup file if it exists.
    Returns the DataFrame (possibly updated with backup data) and
    the index to start from.
    """
    backup_path = get_backup_path(config)

    # Check if backup file exists
    if os.path.exists(backup_path):
        backup = pd.read_parquet(backup_path)
        if not backup.empty:
            backup_len = len(backup)
            # Overwrite the first rows in df with the backup data
            df.iloc[:backup_len] = backup
            logging.info(f"Found and read backup with {backup_len} rows")
            return df, backup_len

    # If no backup or empty backup, return original df and start at index 0
    return df, 0

def delete_backup(config):
    """
    Deletes the backup file if it exists.
    """
    backup_path = get_backup_path(config)
    if os.path.exists(backup_path):
        os.remove(backup_path)
        logging.info('Backup was removed')

def create_backup(df, idx, config):
    """
    Creates a parquet backup of the DataFrame after a given number of iterations.
    Always saves as .parquet (removes previous extension if it exists).
    Ensures the folder exists before saving.
    """
    backup_path = get_backup_path(config)
    # Remove any existing file extension and enforce .parquet
    base = os.path.splitext(backup_path)[0]
    parquet_path = base + '.parquet'
    # Ensure the directory exists
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    # Save the backup (up to and including idx)
    df.iloc[:idx+1].to_parquet(parquet_path, index=False)
    logging.info(f'Backup created with {idx + 1} rows at {parquet_path}')