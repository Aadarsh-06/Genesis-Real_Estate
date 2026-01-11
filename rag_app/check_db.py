import chromadb

client = chromadb.PersistentClient(path="chroma_db")
col = client.get_collection("real_estate")
results = col.get(limit=200, include=["metadatas"])

cities = set(m["city"] for m in results["metadatas"])
bedrooms = set(m["bedrooms"] for m in results["metadatas"])

print("Cities in DB:", cities)
print("Bedrooms in DB:", bedrooms)
print("Total docs:", col.count())
