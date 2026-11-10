from config import llm, embeddings

# Test the chat model
print("LLM:", llm.invoke("Say hello in one sentence.").content)

# Test the embeddings
vector = embeddings.embed_query("teeth whitening")
print("Embedding length:", len(vector))