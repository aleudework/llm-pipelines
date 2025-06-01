import os
import logging
from datetime import datetime

def setup_logger(log_folder=None, log_name='log'):
    """
    The function does:
    1) Check if log_folder exists and otherwise creates it
    2) Sets up a logging handler 
    3) If log_folder is none, then it just set ups a logging handler
    """
    # Set up logging in logfile
    if log_folder is not None:
        os.makedirs(log_folder, exist_ok=True)  # Opret alle nødvendige mapper
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_path = os.path.join(log_folder, f"{log_name}_{date_str}.log")

        # Remove old handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            filename=log_path,
            filemode='w',  # Overskriv hver gang
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%H:%M:%S',
            level=logging.INFO
        )
        print(f"Logger sat op: {log_path}")

    # Only set up logging in terminal
    else:
        # Remove old handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%H:%M:%S',
            level=logging.INFO
        )
        print("Logger sat op: terminal")