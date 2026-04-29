from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

loader = TextLoader('company_details.txt',encoding='utf-8')
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 30,
    chunk_overlap=0
)

chunks = splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

vector = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print(vector.similarity_search("who is CEO of zignuts?"))

"""retriver = vector.as_retriever(search_kwargs={'k':2})

result = retriver.invoke('who is CEO of zignuts?')
print(result)"""