from sentence_transformers import SentenceTransformer
import os 
from dotenv import load_dotenv
load_dotenv()
text = "hello i am krishna"

model = SentenceTransformer("all-MiniLM-L6-v2")

vectors = model.encode(text)

print(vectors)