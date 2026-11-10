from pathlib import Path
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from config import llm, embeddings
from spinner import Spinner

# Load the vector store and the system prompt
vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
system_prompt = Path("system_prompt.txt").read_text(encoding="utf-8")

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "{system_prompt}\n\n"
     "## KNOWLEDGE BASE CONTEXT\n"
     "Answer using only the context below. Never invent prices, services, or "
     "course details. If the answer isn't in the context, say you don't have "
     "that information and steer the user back to export topics.\n\n"
     "{context}"),
    MessagesPlaceholder("history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

history = []
print("Exim Assistant ready. Type 'exit' to quit.\n")

while True:
    question = input("You: ").strip()
    if question.lower() in {"exit", "quit"}:
        break
    if not question:
        continue

    docs = retriever.invoke(question)

    print()  # blank line before the reply area
    spinner = Spinner()
    spinner.start()

    answer = ""
    first_chunk = True
    try:
        for chunk in chain.stream({
            "system_prompt": system_prompt,
            "context": format_docs(docs),
            "history": history,
            "question": question,
        }):
            if first_chunk:
                spinner.stop()  # first words arrived, so remove the spinner
                print("Exim Assistant: ", end="", flush=True)
                first_chunk = False
            print(chunk, end="", flush=True)
            answer += chunk
    finally:
        if first_chunk:
            spinner.stop()  # also stops it if an error happens before any reply
    print("\n")

    history += [HumanMessage(content=question), AIMessage(content=answer)]
    history = history[-8:] # keeps the last 4 exchanges