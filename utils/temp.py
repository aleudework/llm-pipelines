import os
import shutil
import logging

def create_temp_folder(path):
    """
    Create temp folder. Expect:
    """
    # Build path to temp folder
    temp_folder = os.path.join(path, "temp")
    # Create temp folder
    os.makedirs(temp_folder, exist_ok=True)
    # Return temp folder path
    logging.info('Temp folder created')
    return temp_folder

def remove_temp_folder(path):
    """
    Removes only temp folder
    """
    # Check for temp folder included in path
    if os.path.basename(os.path.normpath(path)) == "temp":
        temp_path = path
    else:
    # If temp folder not included, add temp
        temp_path = os.path.join(path, "temp")
    # Remove temp folder
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
        logging.info('Temp folder removed')
    # Return now removed temp folder path
    return temp_path

