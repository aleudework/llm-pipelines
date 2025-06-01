

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