from collections import abc
import numbers
import math
from foundry_local_sdk import Configuration, FoundryLocalManager
import sqlite3
from datetime import datetime

documents = [
    "Foundry Local runs AI models directly on your device without cloud connectivity.",
    "The Foundry Local SDK supports Python, C#, JavaScript, and Rust.",
    "Embedding models convert text into numerical vectors for similarity search.",
    "Foundry Local uses ONNX Runtime for efficient model inference on CPUs and GPUs.",
    "The model catalog provides pre-optimized models that you can download and run locally.",
    "Retrieval-augmented generation grounds model responses in your own data.",
    "Vector similarity search finds documents that are semantically close to a query.",
    "Chat completions generate natural language responses from a prompt and context.",
]


def main():
    config = Configuration(app_name = "foundry_local_rag")
    FoundryLocalManager.initialize(config)

    embedding_model = FoundryLocalManager.instance.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(lambda p : print(f"Downloading embedding model:{p:.1f}%", end="", flush=True))
    print()
    embedding_model.load()
        
    embedding_client = embedding_model.get_embedding_client()
    doc_embeddings = [item.embedding for item in embedding_client.generate_embeddings(documents).data]

    for i, (doc, emb) in enumerate(zip(documents, doc_embeddings)):
        min_val = min(emb)
        max_val = max(emb)
        norm = lambda v: (v - min_val) / (max_val - min_val) * 255 if max_val != min_val else 0
        cursor.execute('''
            INSERT OR IGNORE INTO documents (id, text, embedding, distance, source, approxcolorr, approxcolorg, approxcolorb, approxcolora)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (i + 1, doc, str(emb), 0.0, "knowledge_base", norm(emb[0]), norm(emb[1]), norm(emb[2]), norm(emb[3])))
    connection.commit()

    print(f"İndexed {len(doc_embeddings)} documents.")
   
    chat_model = FoundryLocalManager.instance.catalog.get_model("qwen2.5-0.5b")
    chat_model.download(lambda p : print(f"Downloading chat model:{p:.1f}%", end="", flush=True))
    print()
    chat_model.load()
    
    while True:
        query = (input("Question: "))
        if not query or query.lower() == "quit":
            print("Models unloaded. Done!")
            connection.close()
            break

        print(repr(query)) 
        query_response = embedding_model.get_embedding_client().generate_embeddings([query])
        query_emb = query_response.data[0].embedding

        results = find_relevant(query_emb, doc_embeddings, top_k=3)

        context = "\n".join(f"-{documents[i]}" for i, _ in results)

        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only the provided context. "
                    "If the context doesn't contain enough information, say so.\n\n"
                    f"Context:\n{context}"
                ),
            },
            {"role": "user", "content": query},
        ]        

        print("Answer: ", end="", flush=True)

        #todo if query from user is same then print out same answer

        for chunk in chat_model.get_chat_client().complete_streaming_chat(messages):
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=False)
                    
                    
        print()
        print("\n")

        cursor.execute('''
                        INSERT INTO queries (query_question, query_answer, timestamp)
                        VALUES (?, ?, ?)
                    ''', (query, content, datetime.now()))
        connection.commit()
        print("\n" + "answer saved!" + "\n ")


    embedding_model.unload()
    chat_model.unload()
    print("Models unloaded. Done!")


# actually pol function in calculator 
# zip function it pairs elements from two lists
def cosine_similarity(a,b):
    return sum(x*y for x,y in zip(a,b)) / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b)))
    



def find_relevant(query_embedding, doc_embeddings, top_k=3):
    scores = []
    for i, doc_emb in enumerate(doc_embeddings):
        score = cosine_similarity(query_embedding, doc_emb)
        scores.append((i, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


    


if __name__ == "__main__":
    connection = sqlite3.connect('database-rag.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM documents
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(row)



    connection.commit()

    main()
    

