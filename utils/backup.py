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
    Ensures df has all columns from backup and updates first rows with backup content.
    Returns updated df and index to start from.
    """
    backup_path = get_backup_path(config)

    if os.path.exists(backup_path):
        backup = pd.read_parquet(backup_path)
        if not backup.empty:
            backup_len = len(backup)

            # Add any missing columns from backup to df
            for col in backup.columns:
                if col not in df.columns:
                    df[col] = pd.NA

            # Add any missing columns from df to backup (so later code doesn't fail)
            for col in df.columns:
                if col not in backup.columns:
                    backup[col] = pd.NA

            # Update first rows in df with everything from backup (all columns)
            df.loc[:backup_len-1, :] = backup[df.columns].values

            logging.info(f"Found and read backup with {backup_len} rows")
            return df, backup_len

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