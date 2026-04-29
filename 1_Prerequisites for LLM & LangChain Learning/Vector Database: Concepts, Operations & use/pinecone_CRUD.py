from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="pcsk_4f9vDX_SMRwJT5aDsWXipuYSq7j9zUX1GYPq3uo6nSbtiMKVVJ5GP6BjAkaFze3iK6HzFX")
# CREATING INDEX
"""

if 'my-index' not in pc.list_indexes().names():
    pc.create_index(
        name='my-index',
        dimension=1536,
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

print("Hello") """

#print(pc.describe_index(name='my-index'))

index = pc.Index("my-index")



# INSERT
"""index.upsert(vectors=[
    {
        "id": "vec1",
        "values": [0.1] * 1536,
        "metadata": {"text": "hello"}
    },
    {
        "id": "vec2",
        "values": [0.2] * 1536,
        "metadata": {"text": "world"}
    },
    {
        "id": "vec3",
        "values": [0.3] * 1536,
        "metadata": {"text": "pinecone test"}
    }
],namespace="data1")

"""

# FETCH 

# print(index.fetch(['vec1','vec2'],namespace='data1'))


# update 

"""index.update(
    id="vec1",
    values=[0.9] * 1536,
    set_metadata={
        "text": "updated vector",
        "category": "new"
    },
    namespace="data1"
)
"""

# DELETE 

index.delete(ids=['vec1','vec2'],namespace="data1")