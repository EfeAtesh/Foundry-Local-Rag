import sqlite3

#table named documents
#if those tables already exists than delete their cursor.execute calls from below

connection = sqlite3.connect('database-rag.db')
cursor = connection.cursor()
"""
cursor.execute('''
    CREATE TABLE documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        embedding BLOB,
        distance REAL,
        source TEXT,
        approxcolorr REAL,
        approxcolorg REAL,
        approxcolorb REAL,
        approxcolora REAL
    )
''')


cursor.execute('''
    CREATE TABLE queries(
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_question TEXT,
    query_answer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )


''')
"""
print("Table created successfully.")




connection.commit()
connection.close()

