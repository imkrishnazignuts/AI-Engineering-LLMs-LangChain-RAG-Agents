from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
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
print(f"Loaded pages/chunks from PDFs: {len(pdf_documents)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=0
)

chunks = splitter.split_documents(pdf_documents)
print(f"Total split chunks: {len(chunks)}")


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


persist_dir = "./chroma_db"


vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_dir,
    collection_name="policy_docs"
)

print("Chroma vector store created successfully!")


retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 6, "fetch_k": 20, "lambda_mult": 0.7}
)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=400
)


prompt = ChatPromptTemplate.from_template("""
You are a policy assistant.

Answer ONLY from the provided context.
If the user's wording is different, match related HR policy terms intelligently.
Examples:
- pregnancy leave -> maternity leave
- accident leave -> emergency leave
- medical leave -> sick leave

Rules:
1. Give the exact answer from context when available.
2. If exact wording is different but meaning is same, explain that clearly.
3. If answer is found, quote the relevant part briefly.
4. If answer is not found in context, say: "I could not find this in the provided documents."

Context:
{context}

Question:
{question}

Answer:
""")

parser = StrOutputParser()
chain = prompt | llm | parser


def expand_query(query: str) -> str:
    q = query.lower()

    replacements = {
        "pregnancy leave": "pregnancy leave maternity leave",
        "pregnecy leave": "pregnancy leave maternity leave",
        "maternity": "maternity pregnancy",
        "accident leave": "accident leave emergency leave medical leave",
        "sick leave": "sick leave medical leave",
        "casual leave": "casual leave personal leave",
    }

    expanded = query
    for key, value in replacements.items():
        if key in q:
            expanded += " " + value

    return expanded


def rerank_docs(question: str, docs):
    keywords = question.lower().split()

    def score(doc):
        text = doc.page_content.lower()
        return sum(1 for kw in keywords if kw in text)

    return sorted(docs, key=score, reverse=True)


while True:
    question = input("\nAsk Question (exit to stop): ").strip()

    if question.lower() == "exit":
        break

    expanded_question = expand_query(question)

    docs = retriever.invoke(expanded_question)
    docs = rerank_docs(expanded_question, docs)

    print("\n--- Retrieved Chunks ---")
    for i, doc in enumerate(docs[:4], 1):
        print(f"\nChunk {i}:")
        print(doc.page_content[:500])

    context = "\n\n".join(
        [f"[Chunk {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs[:4])]
    )

    result = chain.invoke({
        "context": context,
        "question": question
    })

    print("\nAnswer:\n", result)