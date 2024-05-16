import datetime

from langchain_core.output_parsers import StrOutputParser
import langchain.text_splitter as text_splitter
from langchain.docstore.document import Document

from .prompts import (
    summary_question_prompt
)
from .utils import log, model, quick_model, FAST_TOKEN_LIMIT, TOKEN_INPUT_LIMIT

def format_docs(x: dict):
    docs = x["metadata"]
    chat_history = x["chat_history"]

    formatted_docstring_list = []
    char_count = 0
    for doc in docs:
        metadata_fields = ['source', 'eventTime', 'objectId', 'images_gsurls']
        if doc is None:
            log.warning(f"doc is none in format_docs {docs}")
            continue
        doc_content = doc.page_content
        doc_source = doc.metadata.get('source')
        doc_objectId = doc.metadata.get('objectId')
        doc_eventTime = doc.metadata.get('eventTime')

        doc_metadatas = []
        for field in metadata_fields:
            doc_metadata = f"{field}:{doc.metadata.get(field)}"
            doc_metadatas.append(doc_metadata)
        doc_metadatas_parsed = "\n".join(doc_metadatas)
        char_count += len(doc_content)
        
        formatted_doc = f"# {doc_source}\n## {doc_objectId}\n{doc_eventTime}\n\n{doc_content}\n\n#### metadata\n{doc_metadatas_parsed}"
        formatted_docstring_list.append(formatted_doc)

    log.info(f"Found [{len(docs)}] documents to use in context with total character count: [{char_count}]")
    if char_count > TOKEN_INPUT_LIMIT:
        log.warning(f"char_count [{char_count}] of returned docs to context greater than TOKEN_INPUT_LIMIT [{TOKEN_INPUT_LIMIT}] - loss of context")
        summarised_docs = summarise_knowing_question(
            docs=formatted_docstring_list, 
            question=x["question"],
            n_chunks=10,
            chat_history=chat_history)
        if len(summarised_docs) > 0:
            formatted_docstring_list = [summarised_docs]
    elif char_count < TOKEN_INPUT_LIMIT + 2000:
        summary_context = summarise_knowing_question(
            docs=formatted_docstring_list, 
            question=x["question"], 
            n_chunks=1,
            chat_history=chat_history)
        if len(summary_context) > 0:
            formatted_docstring_list.extend(summary_context)
        
    return "\n\n".join(formatted_docstring_list)[:TOKEN_INPUT_LIMIT]

def add_summaries_to_docstring(docs, char_count, question, chat_history):

    BUFFER = 2000

    if char_count > TOKEN_INPUT_LIMIT:
        log.warning(f"char_count [{char_count}] of returned docs to context greater than TOKEN_INPUT_LIMIT [{TOKEN_INPUT_LIMIT}] - loss of context")
        summarised_docs = summarise_knowing_question(
            docs=docs, 
            question=question,
            n_chunks=10,
            chat_history=chat_history)
        if len(summarised_docs) > 0:
            return summarised_docs
        else:
            return docs
    elif char_count < TOKEN_INPUT_LIMIT + BUFFER:
        log.info("Summariseing knowing question now")
        summary_context = summarise_knowing_question(
            docs=docs, 
            question=question, 
            n_chunks=1,
            chat_history=chat_history)
        if len(summary_context) > 0:
            return docs.extend(summary_context)

def summarise_knowing_question(docs: list[str], question: str, n_chunks: int =10, chat_history:str = ""):

    log.debug(f"summarise_knowing_question: docs: {type(docs)} chat_history: {type(chat_history)}")
    long_text = "\n\n".join(docs)

    summary_chain = summary_question_prompt | quick_model | StrOutputParser()

    splitter = text_splitter.RecursiveCharacterTextSplitter(chunk_size=TOKEN_INPUT_LIMIT/n_chunks, chunk_overlap=0)
    summaries = []
    for chunk in splitter.split_text(long_text):
        summary = summary_chain.invoke({"context": chunk, "question": question, "chat_history": chat_history})
        summaries.append(summary)
    
    return summaries

def load_chat_history(input_dict:dict) -> str:
    log.debug(f"Got chat history for summary: {type(input_dict)}")
    chat_history_list = input_dict.get('chat_history')
    formatted_str = ""
    if chat_history_list:
        log.debug(f"Got chat history_dict: {type(chat_history_list)}")
        if isinstance(chat_history_list, str):
            # it gets itself ('chat_history') converted from a string from a list of ChatEntries
            log.debug("Got chat history string, returning")

            return chat_history_list
        
        if isinstance(chat_history_list, list):
            for history in chat_history_list:
                #print(f"Reading chat_entry: {history} {type(history)}")
                if history.name.lower() == "human":
                    formatted_str += f"\n> Human: {history.content}\n"
                elif history.name.lower() == "ai":
                    formatted_str += f"\n> AI: {history.content}\n"
                else:
                    log.warning(f"Got unknown history.name: {history.name} {history.content}")
                    formatted_str += f"{history.name} {history.content}\n"
        else:
            log.warning(f"Got unknown chat_history_dict: {chat_history_list}")

            return ""

    #print(f"Got chat history:\n {str}")
    token_limit = formatted_str[:FAST_TOKEN_LIMIT]
    last_10000 = token_limit[-10000:]

    return last_10000


def format_private_docs(docs):
    if not docs:
        log.warning("Found no private doc content")
        return None

    formatted_docs = []
    now = datetime.datetime.now()
    for doc in docs:
        # stuff here?
        formatted_docs.append(doc)
    
    all_docs = "\n\n".join(formatted_docs)[:TOKEN_INPUT_LIMIT]

    if len(all_docs) < 5:
        log.warning("Not enough private doc content found: {all_docs}")
        return None
    
    output_doc_string = f"""\n
# Private user upload
The below is text that has been uploaded directly by the user.  
It should be prioritised and used for any answer you give.
## Private content
{all_docs}
# End of private content
"""
    log.info(f"Total private content length: {len(output_doc_string)}")

    output_doc = Document(page_content=output_doc_string, 
                          metadata = {"source": "private_upload", "eventTime":now})
    
    return output_doc

def format_chat_history(input_dict: dict) -> dict:

    chat_history = load_chat_history(input_dict)
    input_dict["chat_history"] = chat_history

    return input_dict

def format_chat_summary(input_dict: dict) -> dict:
    log.info(f"Formatting chat summary: {input_dict}")
    str = load_chat_history(input_dict)

    # no summary if under 1000
    if len(str) < 1000:
        str = "No summary"
    
    input_dict["chat_summary"] = str
    
    return input_dict

