import chainlit as cl
import logging
from sunholo.agents import send_to_qa_async
from sunholo.logging import setup_logging
from sunholo.streaming import generate_proxy_stream_async
from .config import lookup_config
import json
log = setup_logging(logger_name="chainlit")

logger_httpx = logging.getLogger('httpx')

# Set the logging level to WARNING, so INFO messages will be suppressed
logger_httpx.setLevel(logging.WARNING)

def generate_chainlit_output(bot_output):
    # just pass through as processes after stream the JSON object
    return bot_output

def generate_chainlit_sources(bot_output):

    try:
        the_json = json.loads(bot_output)
    except Exception as e:
        log.warning("Could not parse chainlit output {bot_output}")
        return None
    
    source_documents = the_json.get("source_documents", None)  # type: List[Document]

    text_elements = ""  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_metadata = source_doc.get("metadata")
            log.info(f"source_metadata: {source_metadata}")
            source_name = source_metadata.get("source")
            # Create the text element referenced in the message
            text_elements += f"\n * {source_name}"
    
    return text_elements

async def main_logic(message: cl.Message):
    app_user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    memory = cl.user_session.get("memory")

    log.info(f"app_user: {app_user}")
    log.info(f"Got message: {message.to_dict()}")
          
    memory.append({"name": "Human", "content": message.content})

    user_input = message.content
    chat_history = memory
    message_author = app_user.identifier
    config = lookup_config(chat_profile)

    log.info(f"chat_profile: {chat_profile} {type(chat_profile)}")  
    async def stream_response():
        generate = await generate_proxy_stream_async(
            send_to_qa_async,
            user_input,
            vector_name=config["name"],
            chat_history=chat_history,
            generate_f_output=generate_chainlit_output,
            # kwargs
            stream_wait_time=0.5,
            stream_timeout=120,
            message_author=message_author,
        )
        # Stream the response from the generator
        async for part in generate():
            yield part

    avatar_url = config.get("avatar_url")
    if not avatar_url:
        avatar_url = "https://avatars.githubusercontent.com/u/128686189?s=400&u=a1d1553023f8ea0921fba0debbe92a8c5f840dd9&v=4"
    await cl.Avatar(
        name=chat_profile,
        url=avatar_url,
    ).send()

    # Create a reply message for streaming
    msg = cl.Message(author=chat_profile, content="")

    # Stream the content token by token
    async for token in stream_response():
        if token:
            # Check if token is a byte string
            if isinstance(token, bytes):
                token_str = token.decode('utf-8')  # Decoding byte string to a regular string
            else:
                token_str = token  # It's already a string

            if token_str.startswith("###JSON"):
                json_part = token_str.split("###JSON_START###")[1].split("###JSON_END###")[0]
                log.info(f"Got JSON part {json_part}")
                txt_elements = generate_chainlit_sources(json_part)
                if txt_elements:
                    await msg.stream_token(f"\n\n*Sources:*\n{txt_elements}")
            else:
                await msg.stream_token(token_str)
    log.info("chanlit streaming finished")


    # Send the final message
    memory.append({"name": "AI", "content": msg.content})  
    await msg.update()
