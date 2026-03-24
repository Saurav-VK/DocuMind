import re

def is_valid_page(page):
    text = page["text"]
    
    if len(text.split()) < 30:
        return False

    if bool(re.search(r'(\.\s*){5,}', text)):
        return False

    if "contents" in text.lower():
        return False

    if "preface" in text.lower():
        return False

    if bool(re.search(r'\b(ix|iv|v|v?i{1,3}|x)\b' , text.lower().strip())):
        return False

    return True
            


# In[ ]:




