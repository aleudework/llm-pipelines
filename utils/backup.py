import pandas as pd
import os
import logging


def load_backup(df: pd.DataFrame, backup_file_path: str):
    """
    Loads parquet backup file. Returns df with or without backup and index to start from
    """

    # Check if backup exists
    if backup_file_path and os.path.exists(backup_file_path):
        backup = pd.read_parquet(backup_file_path)

        if not backup.empty:
            # Overwrite the first rows in df as long as backup with the backup 
            backup_len = len(backup)
            df.iloc[:backup_len] = backup
            logging.info(f"Found and read backup with {backup_len} rows")
            return df, backup_len
        
        # Returns df and index to start from
        return df, 0
    
    # If no backup path, just return df
    return df, 0
    
def delete_backup(backup_file_path: str):
    """
    Delete a backup if exists
    """
    if backup_file_path and os.path.exists(backup_file_path):
        os.remove(backup_file_path)
        logging.info('Backup was removed')


def create_backup(df, idx, backup_file_path):
    """
    Create parquet DF backup after a given iterations.
    Gemmer altid som .parquet-fil (fjerner tidligere extension hvis den findes).
    """
    if backup_file_path:
        # Fjern eksisterende extension, hvis der er én
        base = os.path.splitext(backup_file_path)[0]
        parquet_path = base + '.parquet'

        df.iloc[:idx+1].to_parquet(parquet_path, index=False)
        logging.info(f'Backup created with {idx + 1} rows at {parquet_path}')
