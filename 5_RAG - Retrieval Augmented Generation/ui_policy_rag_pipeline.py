import os
import shutil
import streamlit as st

from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq



st.set_page_config(page_title="Policy PDF Q&A", page_icon="📄", layout="wide")
st.title("📄 Policy PDF Question Answering")
st.write("Ask questions from your policy PDFs using LangChain + Chroma + Groq.")



st.sidebar.header("Settings")

groq_api_key = st.sidebar.text_input("Enter GROQ API Key", type="password")
pdf_folder = st.sidebar.text_input("PDF Folder Path", value="../policy_pdfs")
persist_directory = st.sidebar.text_input("Chroma DB Folder", value="./chroma_db")
collection_name = st.sidebar.text_input("Collection Name", value="policy_docs")

chunk_size = st.sidebar.number_input("Chunk Size", min_value=100, max_value=2000, value=300, step=50)
chunk_overlap = st.sidebar.number_input("Chunk Overlap", min_value=0, max_value=500, value=50, step=10)
top_k = st.sidebar.number_input("Top K Chunks", min_value=1, max_value=20, value=10, step=1)

create_db = st.sidebar.button("Create / Load Vector DB")
reset_db = st.sidebar.button("Delete Existing DB")



@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def load_documents(folder_path: str):
    loader = DirectoryLoader(
        folder_path,
        glob="**/*.pdf",
        loader_cls=PyMuPDFLoader,
        show_progress=False
    )
    return loader.load()


def split_documents(documents, chunk_size_value, chunk_overlap_value):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size_value,
        chunk_overlap=chunk_overlap_value
    )
    return splitter.split_documents(documents)


def create_or_load_vectorstore(folder_path, persist_dir, collection, chunk_size_value, chunk_overlap_value):
    embeddings = get_embeddings()

    # If DB already exists, load it
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        vector_store = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            collection_name=collection
        )
        return vector_store, "Loaded existing Chroma vector DB."


    documents = load_documents(folder_path)
    chunks = split_documents(documents, chunk_size_value, chunk_overlap_value)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
        collection_name=collection
    )

    return vector_store, f"Created new Chroma vector DB with {len(chunks)} chunks."


def get_llm(api_key: str):
    return ChatGroq(
        groq_api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=300
    )


def answer_question(vector_store, api_key, question, k):
    retriever = vector_store.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_template("""
Answer only from the given context.
If the answer is not present in the context, say:
"I could not find the answer in the provided documents."

Context:
{context}

Question:
{question}

Answer:
""")

    parser = StrOutputParser()
    llm = get_llm(api_key)
    chain = prompt | llm | parser

    result = chain.invoke({
        "context": context,
        "question": question
    })

    return result, docs



if "vector_store_ready" not in st.session_state:
    st.session_state.vector_store_ready = False

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []



if reset_db:
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        st.sidebar.success("Existing Chroma DB deleted successfully.")
        st.session_state.vector_store_ready = False
        st.session_state.vector_store = None
    else:
        st.sidebar.info("No existing DB folder found.")


if create_db:
    if not pdf_folder.strip():
        st.error("Please provide the PDF folder path.")
    else:
        try:
            with st.spinner("Preparing vector database..."):
                vector_store, message = create_or_load_vectorstore(
                    folder_path=pdf_folder,
                    persist_dir=persist_directory,
                    collection=collection_name,
                    chunk_size_value=chunk_size,
                    chunk_overlap_value=chunk_overlap
                )

                st.session_state.vector_store = vector_store
                st.session_state.vector_store_ready = True

            st.success(message)

        except Exception as e:
            st.error(f"Error while creating/loading vector DB: {e}")



st.subheader("Ask Questions")

question = st.text_input("Enter your question")

ask_button = st.button("Get Answer")

if ask_button:
    if not groq_api_key:
        st.error("Please enter your GROQ API Key in the sidebar.")
    elif not st.session_state.vector_store_ready:
        st.error("Please create/load the vector DB first.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        try:
            with st.spinner("Searching documents and generating answer..."):
                result, docs = answer_question(
                    vector_store=st.session_state.vector_store,
                    api_key=groq_api_key,
                    question=question,
                    k=top_k
                )

            st.session_state.chat_history.append({
                "question": question,
                "answer": result,
                "docs": docs
            })

        except Exception as e:
            st.error(f"Error while answering question: {e}")



if st.session_state.chat_history:
    st.subheader("Conversation")

    for idx, item in enumerate(reversed(st.session_state.chat_history), start=1):
        st.markdown(f"### Q{idx}: {item['question']}")
        st.write(item["answer"])

        with st.expander("Show Retrieved Chunks"):
            for i, doc in enumerate(item["docs"], start=1):
                source = doc.metadata.get("source", "Unknown Source")
                page = doc.metadata.get("page", "Unknown Page")

                st.markdown(f"**Chunk {i}**")
                st.write(f"**Source:** {source}")
                st.write(f"**Page:** {page}")
                st.write(doc.page_content)
                st.markdown("---")