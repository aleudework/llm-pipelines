import os 

def get_prompt_path(config):
    """
    Helper function to get prompt path
    """

    project_name = config['project']
    prompt_file = project_name + '.txt'
    return os.path.join('../prompts', prompt_file)



def build_prompt(path: str, variables: dict ) -> str:
    """
    Build and finalizes a prompt based on an object with variables.

    Args:
        path (str): Path to prompt in .txt file
        variables (dict): A dictionary or object with variables for the prompt.
    
    Returns:
        str: The finalized prompt
    """

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Unpack dict and use it for prompt, like this: content.format(name="Alice", thing="chess")
    return content.format(**variables)

def load_prompt(path: str) -> str:
    """
    Simple load a prompt from txt
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content


def load_multiple_prompts(config, path=None):
    """
    Load multiple prompts in a single file.
    Splits whenever a line starts with '###'.
    Returns a list of prompts (each as a string).
    """

    prompt_path = path if path else get_prompt_path(config)

    with open(prompt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    prompts = []
    current_prompt = []

    for line in lines:
        if line.strip().startswith('###'):
            if current_prompt:
                prompts.append(''.join(current_prompt).strip())
                current_prompt = []
        else:
            current_prompt.append(line)

    # Add last prompt if any
    if current_prompt:
        prompts.append(''.join(current_prompt).strip())

    return prompts

def format_multiple_prompts(prompts, variables: dict):
    """
    Take a list of prompts and formats if possible.
    If it is not possible to format e.g. missing keys, it just returns the prompt as it is.
    Return list of prompts
    """

    filled_prompts = []
    for prompt in prompts:
        try:
            filled = prompt.format(**variables)
        except Exception:
            filled = prompt

        filled_prompts.append(filled)
    return filled_prompts



def format_prompt(prompt, variables):

    try:
        filled = prompt.format(**variables)
    except Exception:
        filled = prompt
    return filled if filled else prompt

