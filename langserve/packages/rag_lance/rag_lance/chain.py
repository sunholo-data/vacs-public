from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableBranch
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever

from sunholo.components import get_llm_chat, pick_vectorstore, get_embeddings
from sunholo.logging import setup_logging

from operator import itemgetter

from typing import Optional, List

VECTOR_NAME = "rag_lance"

log = setup_logging()
embeddings = get_embeddings(VECTOR_NAME)
vectorstore = pick_vectorstore("lancedb", 
                               vector_name=VECTOR_NAME, 
                               embeddings=embeddings)

model = get_llm_chat(VECTOR_NAME)

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(), llm=model
)

template = """Answer the question based only on the following context:
# Context
{context}
# End Context

# Chat Summary
{chat_summary}
# Chat History
{chat_history}

If the context or chat history does not help if not relevant to the question, answer "I can't help with your question, it doesn't seem related to my memory."

Question: {question}
Your Answer (only if relevant to the question, say "I can't help with your question" otherwise):
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)[:110000]

# chat history
chat_summary = """Summarise the conversation below:
{chat_history}
"""
summary_prompt = ChatPromptTemplate.from_template(chat_summary)

class ChatEntry(BaseModel):
    name: str
    content: str

def load_chat_history(input_dict):
    log.debug(f"Got chat history for summary: {type(input_dict)}")
    chat_history_dict = input_dict.get('chat_history')
    str = ""
    if chat_history_dict:
        for history in chat_history_dict:
            log.debug(f"Reading chat_entry: {history} {type(history)}")
            if history.name.lower() == "human":
                str += f"Human: {history.content}\n"
            elif history.name.lower() == "ai":
                str += f"AI: {history.content}\n"
            else:
                log.warning(f"Got unknown history.name: {history.name} {history.content}")
                str += f"{history.name} {history.content}\n"

    log.debug(f"Got chat history:\n {str}")
    return str 
   
def format_chat_history(chat_history):
    str = load_chat_history(chat_history)

    # last 1000 characters
    return str[-1000:]

def format_chat_summary(input_dict):
    str = load_chat_history(input_dict)

    # no summary if under 1000
    if len(str) < 1000:
        return "No summary"
    return str

summary_branch = RunnableBranch(
    (lambda x: "No summary" in x, RunnablePassthrough()),
    (RunnableLambda(
        lambda x:{"chat_history": x}) | summary_prompt | model | StrOutputParser()
        )
).with_config(run_name="BranchSummary")

_inputs = RunnableParallel({
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question"),
        "chat_history": RunnableLambda(format_chat_history).with_config(run_name="FormatChatHistory"),
        "chat_summary": RunnableLambda(format_chat_summary).with_config(run_name="FormatChatSummary") | summary_branch
    }).with_config(run_name="Inputs")

chain = _inputs | prompt | model | StrOutputParser()



class Question(BaseModel):
    question: str
    #{"human": "How's the weather?", "ai": "It's sunny."},
    chat_history: Optional[List[ChatEntry]] = None

chain = chain.with_types(input_type=Question)
