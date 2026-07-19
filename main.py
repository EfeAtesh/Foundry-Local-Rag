from collections import abc
import numbers
from foundry_local_sdk import Configuration, FoundryLocalManager
import sqlite3
from datetime import datetime
import sys, os, pypdf, json, math
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

embedding_model = None
chat_model = None
connection = None
cursor = None
context = ""

documents = [""
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_model, chat_model, connection, cursor
    
    
    connection = sqlite3.connect('database-rag.db', check_same_thread=False)
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            text TEXT,
            embedding TEXT,
            distance REAL,
            source TEXT,
            approxcolorr REAL,
            approxcolorg REAL,
            approxcolorb REAL,
            approxcolora REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_question TEXT,
            query_answer TEXT,
            timestamp TEXT
        )
    ''')
    connection.commit()
    
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)

    embedding_model = FoundryLocalManager.instance.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(lambda p: print(f"Downloading embedding model: {p:.1f}%", end="\r", flush=True))
    print("\nEmbedding model downloaded.")
    embedding_model.load()
    
    chat_model = FoundryLocalManager.instance.catalog.get_model("qwen2.5-0.5b")
    chat_model.download(lambda p: print(f"Downloading chat model: {p:.1f}%", end="\r", flush=True))
    print("\nChat model downloaded.")
    chat_model.load()

    cursor.execute("SELECT COUNT(*) FROM documents")
    db_count = cursor.fetchone()[0]
    if db_count == 0:
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
        print(f"Indexed {len(doc_embeddings)} documents on startup.")
    
    yield  
    
    print("Shutting down.")
    if embedding_model:
        embedding_model.unload()
    if chat_model:
        chat_model.unload()
    if connection:
        connection.close()

    

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str
    message_history: list[dict[str, str]] = []



#same POL function from any standart scientific calculator

def cosine_similarity(a, b):
    return sum(x*y for x,y in zip(a,b)) / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b)))

def chunking(text):
    if isinstance(text, str):
        return [p.strip() for p in text.split("\n\n") if p.strip()]
    result = []
    for item in text:
        result.extend(chunking(item))
    return result



def getTopChunks(query, cursor, top_k=3):
    queryResponse = embedding_model.get_embedding_client().generate_embeddings([query])
    queryEmb = queryResponse.data[0].embedding

    cursor.execute("SELECT text, embedding FROM documents")
    rows = cursor.fetchall()

    scores = []
    for text, embStr in rows:
        dbEmb = json.loads(embStr)
        score = cosine_similarity(queryEmb, dbEmb)
        scores.append((text, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]

# API Endpoint
@app.post("/query")
def query_endpoint(request: ChatRequest):
    global chat_model, connection, cursor, context
    
    user_query = request.query
    context = ""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if user_query.endswith("é*:1"):
        query = user_query[:-(len("é*:1"))] + " (Source: Utah State University Extension, Dept. of Automotive Technology, Bulletin No. 402)"
        docs = readMD(os.path.join(base_dir, "vehicle_fixing_guide.md"))
        context = "\n".join(docs)
    elif user_query.endswith("é*:2"):
        query = user_query[:-(len("é*:2"))] + " (Source: U.S. Dept. of the Army, FM 3-05.70 Survival Manual, Chapter 6: Water Procurement & Chapter 7: Firecraft, 2002)"
        docs = readMD(os.path.join(base_dir, "water_and_fire_guide.md"))
        context = "\n".join(docs)
    elif user_query.endswith("é*:3"):
        query = user_query[:-(len("é*:3"))] + " (Source: U.S. Army Infantry School, FM 21-76 Survival Field Manual, Department of the Army, 1992)"
        docs = readMD(os.path.join(base_dir, "wilderness_survival_guide.md"))
        context = "\n".join(docs)
    else:
        query = user_query
        results = getTopChunks(query, cursor, top_k=3)
        context = "\n".join(f"- {text}" for text, _ in results)

    

    
    
    messages = [
        {
            "role": "system",
            "content": (
                "Answer the user's question using only the provided context. Explain everything shortly but very precise and accurate "
                "If the context doesn't contain enough information, say so.\n\n"
                f"Context:\n{context}"
            ),
        },
        {"role": "user", "content": query},
    ]

    full_content = ""
    try:
        for chunk in chat_model.get_chat_client().complete_streaming_chat(messages):
            if chunk.choices:
                content = chunk.choices[0].delta.content
                if content:
                    full_content += content
    except Exception as e:
        print(f"Hata: {e}")
        full_content = "Error."


    cursor.execute('''
        INSERT INTO queries (query_question, query_answer, timestamp)
        VALUES (?, ?, ?)
    ''', (user_query, full_content, datetime.now().isoformat()))
    connection.commit()
    context = ""

    return {"response": full_content}

@app.get("/")


def home():
    return {"status": "Foundry Local RAG API is running"}


def readMD(path):
    docs = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                continue
            if line.startswith("*"):
                continue
            if line.startswith("-"):
                continue
            if line.startswith("//"):
                continue
            elif line.startswith("\n"):
                continue
            else:
                docs.append(line)
            
    return docs


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



