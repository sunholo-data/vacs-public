from .utils import VECTOR_NAME, log_count_chars_in_docs, log
from .parsers import format_private_docs

from sunholo.database.alloydb import get_sources_from_docstore_async

async def get_retriever(x: dict) -> dict:

    source_filters = x.get("source_filters", [])
    private_docs = x.get("private_docs")
    source_filters_and_or = x.get("source_filters_and_or", False)

    log.info(f"get_retriever with commands: {x}")
    
    private_document=None
    if private_docs:
        private_document = format_private_docs(private_docs)
    
    search_type = "AND" if source_filters_and_or else "OR"

    if not source_filters:
        x["metadata"] = [private_document]
        return x

    # Collect unique sources
    log.info(f"Retrieved doc sources derived from objectId: {source_filters} search_type: {search_type}")

    documents = []
    try:
        documents = await get_sources_from_docstore_async(source_filters, vector_name=VECTOR_NAME, search_type=search_type)
    except Exception as err:
        log.warning(f"Only private_docs=True available. No documents could be import from a Docstore: {str(err)}")
        
    log_count_chars_in_docs(documents, f"whole_document with source_filters: {source_filters} search_type: {search_type}")
    
    if private_document:
        documents.extend([private_document])
        log_count_chars_in_docs(documents, f"whole_document with source_filters: {source_filters} search_type: {search_type} and private_doc")

    x["metadata"] = documents

    return x