from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import umap.umap_ as umap
import matplotlib.pyplot as plt
import numpy as np



documents = [
    # Technology
    "Python is a popular programming language for backend and AI development.",
    "Django is a Python framework used to build web applications quickly.",
    "FastAPI is useful for building modern APIs with Python.",
    "Machine learning models can be trained on large datasets.",
    "Embeddings convert text into numerical vectors for similarity search.",

    # Sports
    "Cricket is one of the most popular sports in India.",
    "A batsman scored a century in the final match.",
    "Football players need stamina, speed, and teamwork.",
    "The team won the championship after a close game.",
    "Bowling and fielding are important parts of cricket.",

    # Food
    "Pizza is made with cheese, sauce, and bread dough.",
    "Pasta can be served with creamy or tomato-based sauce.",
    "Indian food often includes spices, curry, and rice.",
    "Fresh fruits and vegetables are essential for a healthy diet.",
    "Biryani is a flavorful rice dish cooked with spices.",

    # Travel
    "Paris is famous for the Eiffel Tower and art museums.",
    "Traveling by train can be relaxing and scenic.",
    "Hotels and flights should be booked in advance during holidays.",
    "Mountains, beaches, and forests attract many tourists.",
    "A passport is required for international travel."
]

labels = (
    ["Tech"] * 5 +
    ["Sports"] * 5 +
    ["Food"] * 5 +
    ["Travel"] * 5
)

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(documents)

print("Embedding shape:", embeddings.shape)

umap_model = umap.UMAP(
    n_neighbors=5,
    min_dist=0.3,
    n_components=2,
    random_state=42
)
umap_embeddings = umap_model.fit_transform(embeddings)

print("UMAP output shape:", umap_embeddings.shape)
# Expected: (20, 2)

# --------------------------------------------------
# 4) Reduce dimensions using t-SNE
# --------------------------------------------------
tsne_model = TSNE(
    n_components=2,
    perplexity=5,
    random_state=42,
    init="random"
)
tsne_embeddings = tsne_model.fit_transform(embeddings)

print("t-SNE output shape:", tsne_embeddings.shape)
# Expected: (20, 2)

# --------------------------------------------------
# 5) Plotting function
# --------------------------------------------------
def plot_embeddings(points, title):
    plt.figure(figsize=(9, 6))

    unique_labels = list(set(labels))
    for label in unique_labels:
        idxs = [i for i, l in enumerate(labels) if l == label]
        x = points[idxs, 0]
        y = points[idxs, 1]

        plt.scatter(x, y, label=label, s=80)

        for i in idxs:
            plt.annotate(str(i), (points[i, 0], points[i, 1]), fontsize=8)

    plt.title(title)
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.legend()
    plt.grid(True)
    plt.show()

# --------------------------------------------------
# 6) Visualize
# --------------------------------------------------
plot_embeddings(umap_embeddings, "UMAP Visualization of Document Embeddings")
plot_embeddings(tsne_embeddings, "t-SNE Visualization of Document Embeddings")