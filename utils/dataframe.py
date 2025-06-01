import pandas as pd
import logging


def excel_to_df(excel_path, exclude_sheets=None):
    """
    Reads all sheets in an Excel file, excluding specified ones, and returns them as one combined DataFrame.

    Parameters:
        excel_path (str): Path to the Excel file.
        exclude_sheets (list): List of sheet names to exclude (optional).
    """
    exclude_sheets = exclude_sheets or []

    # Read all sheets into a dict of DataFrames
    all_sheets = pd.read_excel(excel_path, sheet_name=None)

    # Filter out excluded sheets
    included_sheets = {name: df for name, df in all_sheets.items() if name not in exclude_sheets}

    # Combine and return as one DataFrame
    return pd.concat(included_sheets.values(), ignore_index=True)


def load_df(path: str, exclude_sheets=None) -> pd.DataFrame:
    """
    Loads df correctly, especially for Excel with multiple sheets

    path (str): DF path

    """
    # Get extension
    ext = path.rsplit('.', 1)[-1].lower()
    
    if ext == 'xlsx' or ext == 'xls':
        return excel_to_df(path, exclude_sheets)
    elif ext == 'csv':
        return pd.read_csv(path)
    elif ext == 'json':
        return pd.read_json(path)
    elif ext == 'parquet':
        return pd.read_parquet(path)
    else:
        logging.error('[ERROR]: No matching extension')
        return None
    

def write_df(df: pd.DataFrame, path: str, index=False):
    """
    Writes or output a df in the same format as the path extensioin
    """ 
    # Get extension
    ext = path.rsplit('.', 1)[-1].lower()
    
    if ext == 'xlsx' or ext == 'xls':
        df.to_excel(path, index=index)
    elif ext == 'csv':
        df.to_csv(path, index=index)
    elif ext == 'json':
        df.to_json(path, index=index)
    elif ext == 'parquet':
        df.to_parquet(path, index=index)
    else:
        print('[Error] No matching extension for writing')
        return
    
    logging.info(f'[Success] DF written to {path}')

