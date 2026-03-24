#!/usr/bin/env python
# coding: utf-8

# In[12]:


from pypdf import PdfReader
import os

def load_pdf_text(path):
    pdf_reader = PdfReader(path)
    text = []
    file = os.path.basename(path)
    
    for page_num , page in enumerate(pdf_reader.pages):
        content = {}
        content["page"] = page_num
        content["text"] = page.extract_text() or ""
        content["source"] = file
        text.append(content)
    return text


# In[ ]:




