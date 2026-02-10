import re

import re

def decode_regex(pattern: str, text: str):
    match = re.search(pattern, text)
    return match.group() if match else None