import asyncio
import datetime
from sunholo.logging import setup_logging
from sunholo.utils.config import load_config_key
from sunholo.vertex import init_vertex, get_vertex_memories, print_grounding_response, vertex_safety

from vertexai.preview.generative_models import GenerativeModel, Tool, grounding

log = setup_logging("vertex-genai")

async def query_models_async(question, vector_name):
    rag_model, search_model = create_models(vector_name)
    safety = vertex_safety()

    rag_response_future = None
    search_response_future = None

    if rag_model:
        rag_response_future = rag_model.generate_content_async(question, safety_settings=safety)
    
    if search_model:
        search_response_future = search_model.generate_content_async(question, safety_settings=safety)

    rag_response, search_response = await asyncio.gather(rag_response_future, search_response_future)

    return rag_response, search_response

def vac_stream(question: str, vector_name, chat_history=[], callback=None, **kwargs):

    safety = vertex_safety()
    log.info(safety)

    gathered_answers, metadata = gather_answers(question, vector_name)

    model = load_config_key("model", vector_name=vector_name, kind="vacConfig")
    no_tools = GenerativeModel(
        model_name=model or "gemini-1.0-pro-002"
    )
    response = no_tools.generate_content(gathered_answers, 
                                         safety_settings=safety,
                                         stream=True)
    text = ""
    for chunk in response:
        try:
            callback.on_llm_new_token(token=chunk.text)
            text += chunk.text
        except ValueError as err:
            callback.on_llm_new_token(token=str(err))
    
    full_response = next(response, None) 

    callback.on_llm_end(response=full_response)
    log.info(f"rag_model.response: {full_response}")

    rag_response = metadata.get("rag_response").text if metadata.get("rag_response") else None
    search_response = metadata.get("search_response").text if metadata.get("search_response") else None
    grounding = print_grounding_response(metadata.get('search_response')) if metadata.get('search_response') else None

    metadata = {
        "chat_history": chat_history,
        "rag_response": rag_response,
        "search_response": search_response,
        "grounding": grounding
    }

    return {"answer": text, "metadata": metadata}


def vac(question: str, vector_name, chat_history=[], **kwargs):

    safety = vertex_safety()
    log.info(safety)
    
    gathered_answers, metadata = gather_answers(question, vector_name)
    model = load_config_key("model", vector_name=vector_name, kind="vacConfig")
    no_tools = GenerativeModel(
        model_name=model or "gemini-1.0-pro-002"
    )
    response = no_tools.generate_content(gathered_answers, 
                                         safety_settings=safety)

    log.info(f"Got response: {response}")
    rag_response = metadata.get("rag_response").text if metadata.get("rag_response") else None
    search_response = metadata.get("search_response").text if metadata.get("search_response") else None
    grounding = print_grounding_response(metadata.get('search_response')) if metadata.get('search_response') else None

    metadata = {
        "chat_history": chat_history,
        "rag_response": rag_response,
        "search_response": search_response,
        "grounding": grounding
    }

    return {"answer": response.text, "metadata": metadata}

def create_models(vector_name):
    gcp_config = load_config_key("gcp_config", vector_name=vector_name, kind="vacConfig")
    if not gcp_config:
        raise ValueError(f"Need config.{vector_name}.gcp_config to configure llamaindex on VertexAI")

    corpus_tools = []
    init_vertex(gcp_config)
    corpus_tools = get_vertex_memories(vector_name)

    # google search grounding tool
    # can't have this and llamaindex memories?
    ground = load_config_key("grounding", vector_name=vector_name, kind="vacConfig")
    if ground and ground.get("google_search"):
        gs_tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())
        log.info(f"Got Search Tool: {gs_tool}")

    # model
    model = load_config_key("model", vector_name=vector_name, kind="vacConfig")

    log.info(f"Vertex tools: {corpus_tools}")
    # Create a gemini-pro model instance
    # https://ai.google.dev/api/python/google/generativeai/GenerativeModel#streaming
    rag_model = None
    search_model = None

    generation_config = {
                "temperature":0.1,
                #top_p=0.95,
                #top_k=20,
                #candidate_count=1,
                "max_output_tokens":7000,
                #stop_sequences=["STOP!"],
    }

    if corpus_tools:
        rag_model = GenerativeModel(
            model_name=model or "gemini-1.0-pro-002", 
            tools=corpus_tools,
            generation_config=generation_config,
        )

    if gs_tool:
        search_model = GenerativeModel(
            model_name=model or "gemini-1.0-pro-002", 
            tools=[gs_tool],
            generation_config=generation_config
        )

    # can't query both of these in the same model
    return rag_model, search_model 

def gather_answers(question, vector_name):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    rag_response, search_response = loop.run_until_complete(query_models_async(question, vector_name))

    gathered_answers = f"""
Two attempts to answer are shown below, drawing from different sources. 
Todays date is: {datetime.datetime.now()}
Use them to inform your own answer:
<answer using internal memory>
{rag_response.text}
</answer using internal memory>
<answer using Google Search>
{search_response.text}
</answer using Google Search>

Original Question: {question}.
Your answer:
"""
    log.info(gathered_answers)

    metadata = {'rag_response':rag_response, 'search_response':search_response}
    
    return gathered_answers, metadata
