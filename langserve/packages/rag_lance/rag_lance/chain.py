from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever

from sunholo.components import get_llm_chat, pick_vectorstore, get_embeddings
from sunholo.logging import setup_logging

from operator import itemgetter

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

template = """Answer the question based only on the following context.:
{context}

If the context does not help if not relevant to the question, answer "I can't help with your question, it doesn't seem related to my memory."

Question: {question}
Your Answer (only if relevant to the question, say "I can't help with your question" otherwise):
"""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

_inputs = RunnableParallel({
        "context": itemgetter("question") | retriever | format_docs,
        "question": itemgetter("question")
    })

chain = _inputs | prompt | model | StrOutputParser()

class Question(BaseModel):
    question: str

chain = chain.with_types(input_type=Question)