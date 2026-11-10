import shutil
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from config import embeddings

KB_PATH = Path("data/coach_chatbot_knowledge_base.txt")
DB_DIR = "chroma_db"

text = KB_PATH.read_text(encoding="utf-8")

# 1. Split by headings so related content stays together
header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
    strip_headers=False,
)
sections = header_splitter.split_text(text)

# 2. Split any oversized section into smaller chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = splitter.split_documents(sections)

# 3. Prefix each chunk with its heading path for context
for c in chunks:
    path = " > ".join(v for _, v in sorted(c.metadata.items()))
    c.page_content = f"[{path}]\n{c.page_content}"

# 4. Rebuild the database from scratch (avoids duplicates on re-runs)
shutil.rmtree(DB_DIR, ignore_errors=True)
Chroma.from_documents(chunks, embeddings, persist_directory=DB_DIR)

print(f"Done. Stored {len(chunks)} chunks in '{DB_DIR}'.")