import os
import logging
from datetime import datetime
import requests

def get_log_path(config):
    """
    Returns the robust log folder path based on project name from config.
    Always uses ../log/{project_name}
    """
    project_name = config['project']
    return os.path.join('../logs', project_name)

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

def webhook_logger(idx, config, message, webhook_url=None, webhook_itr=None):
    """
    Sender beskeder ud til server
    """
    if webhook_url is None:
        webhook_url = config['others']['webhook_url']
    
    if webhook_itr is None:
        webhook_itr = config['others']['webhook_itr']
        if webhook_itr is None:
            webhook_itr = 500
    
    if webhook_url is None:
        return
    
    if webhook_url and (idx + 1) % webhook_itr == 0:
        data = {"content": message}
        requests.post(webhook_url, json=data)
        logging.info('Webhook message sent to server')




