from langchain_community.document_loaders import DirectoryLoader,PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace,
)
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

dir_loader = DirectoryLoader(
    "../policy_pdfs",
    glob="**/*.pdf",
    loader_cls=PyMuPDFLoader,
    show_progress=False
)

pdf_documents = dir_loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

chunks = splitter.split_documents(pdf_documents)
print(len(chunks))


# Load embedding model locally
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",   # folder where DB will be stored
    collection_name="policy_docs"
)

print("Chroma vector store created successfully!")

retriever = vector_store.as_retriever(search_kwargs={"k": 10})


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=300
)

prompt = ChatPromptTemplate.from_template("""
Answer only from the given context.

you have the context so try to give answer from context like if user asked for pregency leave show them same as maternity leave same for if user asked for accident leave show them emergency leave and all like by your own intelligence
Context:
{context}

Question:
{question}

Answer:
""")

parser = StrOutputParser()


while True:
    question = input("\nAsk Question (exit to stop): ")

    if question.lower() == "exit":
        break

    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])

    chain = prompt | llm | parser

    result = chain.invoke({
        "context": context,
        "question": question
    })

    print("\nAnswer:\n", result)
