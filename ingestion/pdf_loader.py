#!/usr/bin/env python
# coding: utf-8

# In[12]:



from pypdf import PdfReader
import os

def load_multiple_pdfs(path):

    text = []

    for file in os.listdir(path):

        if not file.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(path, file)

        pdf_reader = PdfReader(file_path)

        for page_num, page in enumerate(pdf_reader.pages):

            content = {}

            content["page"] = page_num
            content["text"] = page.extract_text() or ""
            content["source"] = file

            text.append(content)

    return text




# In[ ]:




