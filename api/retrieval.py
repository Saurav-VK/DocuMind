from sentence_transformers import SentenceTransformer

def retrieve_chunks(query , chunks , index , k = 3):

    encoder = SentenceTransformer("all-MiniLM-L6-v2")

    query_embedding = encoder.encode([query])

    distances , indices = index.search(query_embedding , k = k)
    
    results , seen = [] , set()

    for i , dist in zip(indices[0] , distances[0]):
        chunk = chunks[i]

        if chunk ["text"] in seen:
            continue
        seen.add(chunk["text"])

        results.append(
            {
                "text" : chunk["text"] ,
                "page" : chunk["page"] ,
                "source" : chunk["source"] ,
                "score" : float(dist)
            })

    return results
        


# In[ ]:




