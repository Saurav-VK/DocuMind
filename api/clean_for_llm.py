import re

def clean_for_llm(retrieved_data):
    lines = retrieved_data["text"].split('\n')

    cleaned_lines = []
    
    for line in lines:
        if re.search(r'(figure|fig|table\.)\s*\d+' , line , re.IGNORECASE):
            continue
        cleaned_lines.append(line)


    return '\n'.join(cleaned_lines).strip()

