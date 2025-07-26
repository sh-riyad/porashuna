

### Introduction

**Porashuna** is a multilingual Retrieval-Augmented Generation (RAG) system designed to process PDF documents, retrieve relevant information, and generate meaningful responses. Currently, the system supports queries in **Bangla** only.

Porashuna leverages a **multimodal Gemini model** to extract Bangla content from PDFs with high precision. It maintains chat history, stores documents in a **vector database**, and ensures efficient retrieval of contextual responses.The system is built with **FastAPI**, which provides essential API endpoints for seamless integration with other applications or frontends.

---


### Technology Stack

* **Orchestration & AI Logic**: LangChain, LangSmith
* **Multimodal Extraction**: `google.generativeai` (Gemini API)
* **Text Generation**: ChatGoogleGenerativeAI
* **Embeddings**: GoogleGenerativeAIEmbeddings
* **Vector Database**: Chroma
* **Database**: SQLite
* **ORM**: SQLAlchemy
* **PDF Processing**: PyPDF2
* **Data Validation**: Pydantic
* **Web Framework (API)**: FastAPI
* **Core Language**: Python

---

### Project Structure

```
porashuna/
├── main.py                      # FastAPI application entry point
├── index.html                   # Frontend web interface
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker container configuration
├── docker-compose.yml           # Docker Compose setup
├── README.md                    # Project documentation
├── .dockerignore                # Docker ignore file

├── app/                         # Main application package
│   ├── api/                     # API layer
│   │   └── v1/                  # Version 1 endpoints
│   │       ├── __init__.py
│   │       ├── chat.py          # Chat/Q&A endpoints
│   │       └── document.py      # Document upload & processing endpoints
│
│   ├── core/                    # Core system configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Application settings
│   │   ├── database.py          # Database connection setup
│   │   └── vector_store.py      # Chroma vector store setup
│
│   ├── crud/                    # Database CRUD operations
│   │   └── chat_history.py      # Chat history operations
│
│   ├── middleware/              # Custom middleware logic
│   │   ├── __init__.py
│   │   └── middleware.py
│
│   ├── models/                  # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── chat_history.py
│
│   ├── prompts/                 # Prompt templates for LLM
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat-related prompts
│   │   └── extract_text.py      # PDF extraction prompts
│
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat request/response models
│   │   ├── chat_history.py
│   │   └── document.py
│
│   ├── services/                # Core business logic
│   │   ├── __init__.py
│   │   ├── embedding_models.py  # Embedding model logic
│   │   ├── llm.py               # Text-based LLM service
│   │   └── multimodal_llm.py    # Multimodal Gemini model logic
│
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       └── pdf_utils.py         # PDF processing helpers

├── notebooks/                   # Jupyter notebooks for experimentation
│   ├── Text Extraction (different tools).ipynb
│   ├── Text extraction with llm.ipynb
│   └── resources/               # Sample PDF files
```

### Workflow

![PDF Chunking and Embedding](./docs/chuck%20process.png)


The original PDF is divided into smaller chunks, each consisting of 5 pages. This chunking helps manage the context window limitations of the language model. Each chunk is then passed through the Gemini Multimodal model to extract Bangla text in Markdown format. The extracted texts from all chunks are combined into a single coherent document. This combined content is then converted into embeddings using `GoogleGenerativeAIEmbeddings` and stored in a Chroma vector database for efficient semantic search.

![Query Processing and Response](./docs/generate%20response.png)

When a user submits a Bangla query, it is first embedded and then compared against the vector database using similarity search. Relevant document chunks are retrieved and passed to the language model (ChatGoogleGenerativeAI) to generate a refined, context-aware response. Additionally, the system maintains chat history in a database to preserve conversational context and continuity across multiple user interactions.

---

### API Documentation

---

#### 1. `POST /document/upload`
Uploads a PDF file, splits it into chunks, extracts Bangla text using Gemini multimodal, generates embeddings, and stores the content in a vector database.

**Request:**  
- File upload (`multipart/form-data`)  
- Accepts one Bangla PDF file

**Example Response:**
```json
{
  "message": "PDF processed, text extracted and saved to vector store successfully",
  "original_file": "HSC26-Bangla1st-Paper-15-20.pdf",
  "total_pages": 6,
  "chunks_processed": 2,
  "chunks_extraction_details": [
    {
      "chunk_file": "HSC26-Bangla1st-Paper-15-20_chunk_001.pdf",
      "text_length": 9563,
      "status": "success"
    },
    {
      "chunk_file": "HSC26-Bangla1st-Paper-15-20_chunk_002.pdf",
      "text_length": 1332,
      "status": "success"
    }
  ],
  "file_size": "236.72 KB",
  "text_length": 10897,
  "vector_chunks_created": 8,
  "extraction_time_seconds": 114.31
}
````

---

#### 2. `GET /document/health`

Checks the health of the vector database and confirms whether documents are available.

**Request:**

* No input

**Example Response:**

```json
{
  "status": "healthy",
  "vector_store_connected": true,
  "documents_available": true,
  "estimated_document_count": 1
}
```

---

#### 3. `POST /chat/ask`

Accepts a Bangla question, searches for relevant chunks in the vector store, and returns an LLM-generated answer with supporting sources.

**Example Request:**

```json
{
  "question": "“এ গাড়ির এই দুই বেঞ্চ আগে হইতেই দুই সাহেব রিজার্ভ করিয়াছেন, আপনাদিগকে অন্য গাড়িতে যাইতে হইবে।” কে জিজ্ঞাসা করল?",
  "max_results": 5
}
```

**Example Response:**

```json
{
  "question": "“এ গাড়ির এই দুই বেঞ্চ আগে হইতেই দুই সাহেব রিজার্ভ করিয়াছেন, আপনাদিগকে অন্য গাড়িতে যাইতে হইবে।” কে জিজ্ঞাসা করল?",
  "answer": "এই উক্তিটি রবীন্দ্রনাথ ঠাকুরের 'কাবুলিওয়ালা' গল্পের অংশ। এখানে একজন রেলওয়ের কর্মচারী (যেমন গার্ড বা টিকেট কালেক্টর) এই কথাটি জিজ্ঞাসা করেছিলেন।",
  "sources": [
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 8,
      "similarity_score": 0.4128,
      "content_preview": "=== Page 20 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\n..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 7,
      "similarity_score": 0.4138,
      "content_preview": "=== Page 20 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\n..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 3,
      "similarity_score": 0.4361,
      "content_preview": "=== Page 17 ===\nHSC 26\nঅনলাইন ব্যাচ\nমামার নিষেধ অমান্য করিয..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 2,
      "similarity_score": 0.4382,
      "content_preview": "=== Page 16 ===\nআমি তাড়াতাড়ি কাঠের বেঞ্চে পা দিয়ে উঠলাম..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 4,
      "similarity_score": 0.4388,
      "content_preview": "=== Page 18 ===\nলেখক পরিচিতি\nনাম\nপ্রকৃত নাম: রবীন্দ্রনাথ ঠাক..."
    }
  ],
  "context_used": "=== Page 20 === ... চাচার সঙ্গে 'অপরিচি"
}
```

---

### Run the System

Follow these steps to set up and run the Porashuna system locally:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sh-riyad/porashuna.git
   cd porashuna
    ````

2. **Create Environment File**
   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

3. **Fill in the Environment Variables**
   Open the `.env` file and provide the necessary credentials (e.g., Google API key, embedding model, database config).

4. **Build and Start the Containers**

   ```bash
   docker-compose up --build
   ```

5. **Access API Documentation**
   Visit the FastAPI interactive docs:
   [http://localhost:8080/docs](http://localhost:8080/docs)


---

### Questions and Answers

1. **What method or library did you use to extract the text, and why? Did you face any formatting challenges with the PDF content?**  
**Answer:**  
I used the **Gemini Multimodal API** to extract Bangla text from PDF files. Traditional tools like PyPDFLoader, pdfplumber, pymupdf4llm and Easyocr often fail to capture Bangla text accurately, especially when the document includes images embedded within paragraphs. The Gemini Multimodal model effectively handles such complex layouts, preserves structures like tables, charts, and MCQs, and can even provide brief descriptions of images—capabilities that most traditional tools lack.

Reference : [Text Extraction (different tools).ipynb](./notebooks/Text%20Extraction%20(different%20tools).ipynb)


2. **What chunking strategy did you choose (e.g., paragraph-based, sentence-based, character limit)? Why do you think it works well for semantic retrieval?**  
**Answer:**  
I chose a **character-based chunking** strategy. Since Bangla text extraction is already challenging, paragraph- or sentence-based chunking often results in data loss or fragmented chunks. Character-based chunking helps preserve as much content as possible, which is crucial for improving the quality of semantic similarity during retrieval.



3. **What embedding model did you use? Why did you choose it? How does it capture the meaning of the text?**  
**Answer:**  
I used Google's **`embedding-001`** model. It is free to use, supports multilingual inputs—including Bangla—and performs well in capturing semantic meaning. The model is trained on diverse data and handles Bangla characters effectively, making it suitable for embedding content in this context.



4. **How are you comparing the query with your stored chunks? Why did you choose this similarity method and storage setup?**  
**Answer:**  
I use **similarity search with scoring** (top `k = 5`) to retrieve the most relevant chunks from the vector database. This method helps match the query with semantically similar document segments. The vector database (Chroma) allows for fast, scalable retrieval, making it ideal for this use case.



5. **How do you ensure that the question and the document chunks are compared meaningfully? What would happen if the query is vague or missing context?**  
**Answer:**  
Currently, the system relies solely on **vector similarity** without additional reasoning or clarification. This can lead to poor results for vague or ambiguous queries. To address this, I plan to implement **Agentic RAG**, which would allow the system to reason over context, disambiguate intent, and reformulate questions when needed.


6. **Do the results seem relevant? If not, what might improve them (e.g., better chunking, better embedding model, larger document)?**  
**Answer:**  
The results are not always accurate, especially in complex queries. However, relevance can be improved through **prompt tuning**, **better error handling during extraction**, and by implementing an **Agentic RAG pipeline** to decompose tasks and refine the model's responsibilities. Improved chunking strategies and training feedback loops will also enhance accuracy over time.

---


### Sample Input

```json
{
  "question": "রবীন্দ্রনাথ ঠাকুরের ছদ্মনাম কী?",
  "max_results": 5
}
````

---

### Sample Output

```json
{
  "question": "রবীন্দ্রনাথ ঠাকুরের ছদ্মনাম কী?",
  "answer": "রবীন্দ্রনাথ ঠাকুরের ছদ্মনাম হলো **ভানুসিংহ ঠাকুর**।\n\nতিনি এই ছদ্মনামে 'ভানুসিংহের পদাবলী' রচনা করেছিলেন।",
  "sources": [
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 5,
      "similarity_score": 0.5295,
      "content_preview": "গ্রন্থের জন্য প্রথম এশীয় হিসেবে, নোবেল পুরস্কার (১৯১৩), কলকাতা বিশ্ববিদ্যালয়\nকর্তৃক ডি-লিট (১৯১৩),..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 8,
      "similarity_score": 0.5353,
      "content_preview": "=== Page 20 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\nপাঠ্যপুস্তকের প্রশ্ন\n10\nMINUTE\nSCHOOL\nবহুনির..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 7,
      "similarity_score": 0.5466,
      "content_preview": "19\n\n\n=== Page 20 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\nপাঠ্যপুস্তকের প্রশ্ন\n10\nMINUTE\nSCHOOL\nব..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 4,
      "similarity_score": 0.5669,
      "content_preview": "=== Page 18 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\nলেখক পরিচিতি\nনাম\nপ্রকৃত নাম: রবীন্দ্রনাথ ঠাক..."
    },
    {
      "source": "HSC26-Bangla1st-Paper-15-20.pdf",
      "chunk_index": 2,
      "similarity_score": 0.5686,
      "content_preview": "15\n\n=== Page 16 ===\nআমি তাড়াতাড়ি কাঠের বেঞ্চে পা দিয়ে উঠলাম। যমুনাটি বিস্মিতভাবে বলল, “না, আমরা গ..."
    }
  ],
  "context_used": "গ্রন্থের জন্য প্রথম এশীয় হিসেবে, নোবেল পুরস্কার (১৯১৩), কলকাতা বিশ্ববিদ্যালয়\nকর্তৃক ডি-লিট (১৯১৩), ঢাকা বিশ্ববিদ্যালয় কর্তৃক ডি-লিট (১৯৩৬), অক্সফোর্ড\nবিশ্ববিদ্যালয় কর্তৃক ডি-লিট (১৯৪০)।\nজীবনাবসান\n৭ আগস্ট, ১৯৪১ খ্রিস্টাব্দ (২২ শ্রাবণ, ১৩৪৮ বঙ্গাব্দ), জোড়াসাঁকোর ঠাকুরবাড়িতে।\n\n=== Page 20 ===\nHSC 26\nঅনলাইন ব্যাচ\nবাংলা ইংরেজি আইসিটি\nপাঠ্যপুস্তকের প্রশ্ন\n...\n=== Page 18 ===\nHSC 26\nলেখক পরিচিতি\nপ্রকৃত নাম: রবীন্দ্রনাথ ঠাকুর।\nছদ্মনাম: ভানুসিংহ ঠাকুর।\n..."
}
```

---
