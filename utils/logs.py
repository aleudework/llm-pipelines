import os
import logging
from datetime import datetime

def get_log_path(config):
    """
    Returns the robust log folder path based on project name from config.
    Always uses ../log/{project_name}
    """
    project_name = config['project']
    return os.path.join('../log', project_name)

def setup_logger(config, log_name="log"):
    """
    Sets up a logging handler that logs to a file in the project-specific log folder.
    If the log folder does not exist, it will be created.

    1) Checks if the log folder exists; creates it if necessary.
    2) Sets up a logging handler that writes to a dated log file.
    3) Removes any old logging handlers to avoid duplicate logs.
    """

    # Get the path for the log folder
    log_folder = get_log_path(config)
    os.makedirs(log_folder, exist_ok=True)  # Ensure the log directory exists

    # Create log file path with today's date
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_path = os.path.join(log_folder, f"{log_name}_{date_str}.log")

    # Remove old handlers to prevent duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up logging to file
    logging.basicConfig(
        filename=log_path,
        filemode='w',  # Overwrite the log file every run
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )
    print(f"Logger set up: {log_path}")