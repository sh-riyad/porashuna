RAG_PROMPT = """
Your task is to carefully think step by step and answer the user's question in Bangla using only the most relevant information from the provided context.

Follow these steps:

Step 1: Read and understand the user question.  
Step 2: Search through the given context to find only the parts directly relevant to the question.  
Step 3: Based on those relevant parts, logically determine the answer.  
Step 4: Write a clear, short, and accurate answer in Bangla. Do not add anything extra or outside the context.

Here is an example:

---
Question: Who is referred to as "Sushrushak" in the language of metaphor?  
Context: ... অনুপ্রমের ভাষায় শুশ্রুষক বলা হয়েছে শুশ্রুষককে ...  
Answer: শুশ্রুষককে

---

Now answer the following:

Question: {question}

Context:
{context}


Previous Conversation:
{chat_history}

Answer (in Bangla):
"""
