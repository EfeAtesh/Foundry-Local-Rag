# Foundry Local RAG

**Microsoft AI Summer School 2026**  
*Fully offline Retrieval-Augmented Generation (RAG) assistant running local Qwen embedding and chat completion models via the Foundry Local SDK.*

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=for-the-badge&logo=vite&logoColor=white)

---

## Key Features

> [!IMPORTANT]  
> **100% Offline Inference**  
> Runs `qwen3-embedding-0.6b` and `qwen2.5-0.5b` models locally. No data leaves the device.

*   **Dynamic Topic Toggles:** Sidebar options load specialized manuals (Vehicle Fixing, Water & Fire, Wilderness Survival) directly into RAM, keeping the vector database unpolluted.
*   **Automatic Memory Cleanup:** Context guides are automatically flushed from RAM after response generation.
*   **Academic Citations:** Automatically appends bibliographic metadata to topic responses.
*   **macOS Tahoe Theme UI:** Dual-pane desktop-style chat with dark/light mode detection.

---

## System Architecture

```mermaid
graph TD
    A[React Client UI] -- "1. Submit Query (POST /query)" --> B[FastAPI Backend Server]
    B -- "2. Check Suffix" --> C{Topic Active?}
    C -- "Yes (é*:1, 2, 3)" --> D[Read specific Markdown File into RAM]
    C -- "No" --> E[getTopChunks: Cosine Similarity search in SQLite DB]
    D -- "3. Build Prompt Context" --> F[Inference: Qwen 2.5 Chat LLM]
    E -- "3. Build Prompt Context" --> F
    F -- "4. Stream Tokens & Save Query" --> G[Write log to SQLite DB]
    F -- "5. Return JSON Response" --> A
```

---

## 📂 Project Directory Structure

```text
Foundry-Local-Rag/
├── main.py                      # FastAPI server & RAG logic (Qwen embedding/chat, SQLite vector search)
├── database-rag.db              # SQLite database for pre-computed vector embeddings & query logs
├── vehicle_fixing_guide.md      # Vehicle Maintenance Manual (Topic 1: é*:1)
├── water_and_fire_guide.md      # Water Procurement & Firecraft Manual (Topic 2: é*:2)
├── wilderness_survival_guide.md # Wilderness Survival Manual (Topic 3: é*:3)
├── presentation.html            # 6-Slide Interactive Presentation (Light Theme)
├── presentation.pdf             # Exported 16:9 PDF Presentation
├── generate_pdf.js              # Puppeteer script for PDF generation
├── sqlite_basics.py             # SQLite helper & database seeding script
└── frontend/                    # React frontend application (Vite)
    ├── src/
    │   ├── App.jsx              # macOS Tahoe chat UI & topic toggle logic
    │   ├── App.css              # Glassmorphism, traffic light controls & custom styling
    │   └── main.jsx             # React entry point
    ├── index.html               # HTML container
    └── package.json             # Frontend dependencies & scripts
```

---

## Setup & Installation

### Prerequisites

| Tool | Version | Purpose |
| :--- | :--- | :--- |
| **Node.js** | `v18+` | Frontend dev server |
| **Python** | `v3.9+` | FastAPI server and local inference |

### Quick Start

1. **Backend Setup** (Root Directory)
   ```bash
   pip install fastapi uvicorn foundry-local-sdk pypdf pydantic
   python3 main.py
   ```
   *Backend starts at `http://127.0.0.1:8000`. Swagger docs at `/docs`.*

2. **Frontend Setup** (`/frontend` Directory)
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Frontend starts at `http://localhost:5173`.*

---

## References

*   **Survival Content:** Adapted from *U.S. Army Survival Manual FM 3-05.70 / FM 21-76*.
*   **Vehicle Maintenance:** Adapted from *Utah State University Extension, Dept. of Automotive Technology*.
*   **Water and Fire Content:** Adapted from *U.S. Army Survival Manual FM 3-05.70 / FM 21-76*.
*   [FastAPI Documentation](https://fastapi.tiangolo.com) | [React Reference](https://react.dev)
