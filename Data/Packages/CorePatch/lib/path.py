from typing import List
from os.path import isdir
import re
import string

def get_windows_drivers() -> List[str]:
    return list(filter(lambda e: isdir(f'{e}:'), string.ascii_uppercase))

def fmtpath(path: str) -> str:
    path = re.sub(r'/+', '/', path.replace('\\', '/'))
    if path.find(':') == 1:
        path = f'/{path[0]}{path[2:]}'
    return path
