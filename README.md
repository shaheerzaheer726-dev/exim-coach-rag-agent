# Exim Coach RAG Agent

A command-line chatbot ("Exim Assistant") that answers questions about **Exim Coach**, a global trade consultancy, using Retrieval-Augmented Generation (RAG). It retrieves relevant passages from a knowledge base and passes them to an LLM, so answers stay grounded in the company's real course, pricing, and service details.

The assistant has a custom personality defined in `system_prompt.txt`, streams its replies word by word, and shows a loading spinner while it waits for the model.

> **Note:** The knowledge base contains demo data, and the default persona is deliberately snobbish and insulting. It is intended for demonstration purposes, so tone it down before putting it in front of real customers.

## Features

- RAG pipeline built with LangChain
- Free chat models via [OpenRouter](https://openrouter.ai)
- Local embeddings via HuggingFace (`all-MiniLM-L6-v2`), with no embedding API costs
- Persistent vector store with Chroma
- Heading-aware chunking, so each course, service, and FAQ stays together
- Streaming responses and a CLI loading spinner
- Short-term conversation memory (the last 4 exchanges)
- Personality and rules kept in a plain text file, easy to edit without touching code

## Tech Stack

| Component | Tool |
|---|---|
| Framework | LangChain |
| Chat model | OpenRouter (OpenAI-compatible API) |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Vector store | Chroma |
| Language | Python 3.10+ |

## Project Structure

```
.
├── data/
│   └── coach_chatbot_knowledge_base.txt   # Knowledge base the agent answers from
├── config.py            # LLM and embedding settings
├── ingest.py            # Splits the knowledge base and builds the vector store
├── agent.py             # Interactive chat loop with retrieval and streaming
├── spinner.py           # CLI loading spinner
├── system_prompt.txt    # Agent personality and behavior rules
├── requirements.txt
├── .env.example         # Template for your API key
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

Install the CPU-only build of PyTorch first (it is much smaller than the default), then the rest:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 4. Add your OpenRouter API key

Get a key at https://openrouter.ai/keys, then copy the example file and fill it in:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Edit `.env`:

```
OPENROUTER_API_KEY=your-key-here
```

### 5. Choose a model

Open `config.py` and set `CHAT_MODEL` to a model ID from https://openrouter.ai/models. Free models end in `:free`. Availability changes often, so if you get a "model not found" error, pick another one.

## Usage

### Build the vector store

Run this once, and again whenever you edit the knowledge base:

```bash
python ingest.py
```

### Start the chatbot

```bash
python agent.py
```

Type your question at the `You:` prompt, and type `exit` to quit.

Example questions to try:

- `How much is the basic course?`
- `What's in module 3 of the advanced course?`
- `Which products can you help me export?`

## Configuration

| Setting | Location | Default |
|---|---|---|
| Chat model | `config.py` (`CHAT_MODEL`) | A free OpenRouter model |
| Temperature | `config.py` | `0.5` |
| Max reply tokens | `config.py` (`max_tokens`) | `8000` |
| Embedding model | `config.py` | `all-MiniLM-L6-v2` |
| Chunk size / overlap | `ingest.py` | `800` / `100` |
| Chunks retrieved per question | `agent.py` (`k`) | `4` |
| Conversation memory | `agent.py` | Last 4 exchanges |
| Personality and rules | `system_prompt.txt` | Edit freely |

## How It Works

1. **Ingest:** `ingest.py` splits the knowledge base by its headings, breaks long sections into smaller chunks, and tags each chunk with its section path. The chunks are embedded locally and saved to a Chroma database in `chroma_db/`.
2. **Retrieve:** when you ask a question, `agent.py` finds the 4 most similar chunks.
3. **Generate:** the system prompt, the retrieved chunks, the recent chat history, and your question go to the OpenRouter model, and the reply streams back to the terminal.

The agent is instructed to answer only from the retrieved context and to say so when the information isn't in the knowledge base.

## Customizing

- **Use a different business:** replace the file in `data/`, update the path in `ingest.py`, rewrite `system_prompt.txt`, and re-run `python ingest.py`.
- **Change the personality:** edit `system_prompt.txt`. No code changes needed.
- **Better quality:** try a larger free model on OpenRouter, since small models can follow persona and length rules less reliably.

## Known Limitations

- Retrieval uses only the latest message, so vague follow-ups like "how much is it?" can retrieve the wrong chunks. A query-rewriting step would fix this.
- Free OpenRouter models are rate-limited and can be slow or unavailable at busy times.
- Some free models log prompts or use them for training. Check a model's data policy before sending sensitive information.
- The first run downloads the embedding model, so it needs an internet connection once.
