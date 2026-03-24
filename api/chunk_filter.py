import re

def is_valid_chunk(chunk):

    text = chunk["text"]
    
    if len(text.strip()) < 20:
        return False

    if bool(re.search(r'(\.\s*){5,}' , text)):
        return False

    if text.isupper():
        return False

    return True


# In[ ]:




