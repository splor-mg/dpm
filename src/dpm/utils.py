import re
from unidecode import unidecode

def as_identifier(x): 
    x = unidecode(x) 
    ret = re.sub('\W|^(?=\d)','_', x).lower()
    return ret
