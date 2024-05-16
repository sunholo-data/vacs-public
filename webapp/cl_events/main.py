import chainlit as cl
from sunholo.agents import send_to_qa_async, handle_special_commands

from sunholo.streaming import generate_proxy_stream_async

from .config import lookup_config, k_settings, convert_field
from .uploads import process_uploads, get_bucket_and_type
from .sources import generate_chainlit_sources, stream_sources
from .avatar import set_avatar
from .images import add_images
from .log import log

def generate_chainlit_output(bot_output):
    # just pass through as processes after stream the JSON object
    return bot_output

async def main_logic(message: cl.Message):
    app_user        = cl.user_session.get("user")
    chat_profile    = cl.user_session.get("chat_profile")
    memory          = cl.user_session.get("memory")

    log.info(f"app_user: {app_user}")
    log.info(f"Got message: {message.to_dict()}")

    memory.append({"name": "Human", "content": message.content})

    user_input      = message.content
    chat_history    = memory
    message_author  = app_user.identifier
    config          = lookup_config(chat_profile)
    settings        = cl.user_session.get("settings")
    source_filters  = convert_field(settings.get("source_filters")) if settings else None
    search_kwargs   = k_settings(settings) if settings else None
    whole_document  = settings.get("whole_document") if settings else False
    source_filters_and_or = settings.get("source_filters_and_or") if settings else False
    private_upload  = settings.get("private_upload") if settings else None
    
    log.info(f"user settings: {settings}")

    log.info(f"chat_profile: {chat_profile}")  
    log.info(f"chat_history: {chat_history}")
    log.info(f"user_session: {cl.user_session}")

    # sets img and private urls to the settings "latest_private_uploads"
    file_urls = await process_uploads(message)
    log.info(f"file_urls: {file_urls}")

    if file_urls:
        if private_upload:
            msg_string = "Finished uploading files, they are available for the rest of this chat session until you replace with another upload."
        else:
            msg_string = "Finished uploading files. They will be available in the database after processing"
        msg = cl.Message(author=chat_profile, content=msg_string)
        await msg.send()

        return        

    img_url = cl.user_session.get("latest_image_url")
    if img_url:
        log.info("Got latest image_url from history: {img_url}")

    private_docs = cl.user_session.get("latest_private_uploads")
    if private_docs:
        log.info("Found private docs from latest_private_uploads, private_docs active for this message")

    # sets the avatars for the chat
    await set_avatar()

    # Create a reply message for streaming and make a spinner
    msg = cl.Message(author=chat_profile, content="")
    await msg.send()

    sources_elements = []
    async def stream_response():
        generate = await generate_proxy_stream_async(
            send_to_qa_async,
            user_input,
            vector_name=config["name"],
            chat_history=chat_history,
            generate_f_output=lambda x: x, # this is for parsing the response if required
            # kwargs
            stream_wait_time=0.5,
            stream_timeout=120,
            message_author=message_author,
            image_url=img_url,
            # kwargs passed to models
            source_filters = source_filters,
            search_kwargs = search_kwargs,
            private_docs=private_docs,
            whole_document=whole_document,
            source_filters_and_or=source_filters_and_or,
            # langchain configurable dictionary
            configurable={
                # if user role matches vector_name
                "role": app_user.metadata["role"],
                "vector_name": config["name"],
            },
            # kwargs for session tracking
            user_id=app_user.identifier,
            session_id=message.thread_id,
            message_source="chainlit"
        )
        # Stream the response from the generator
        async for part in generate():
            if isinstance(part, dict):
                new_sources_elements = await generate_chainlit_sources(part)
                yield None, new_sources_elements  # Yielding the updated list
            else:
                yield part, None

    bucket_name, _ = get_bucket_and_type("txt")
    special_reply = handle_special_commands(
        user_input, 
        vector_name=config["name"],
        chat_history=chat_history,
        bucket=bucket_name)
    
    if special_reply:
        await msg.stream_token(special_reply)
    else:
        # Stream the content token by token
        async for token, new_sources_elements in stream_response():
            if token:
                # Check if token is a byte string
                if isinstance(token, bytes):
                    log.warning(f"Got token as bytes - {token}")
                    token = token.decode('utf-8')  # Decoding byte string to a regular string

                await msg.stream_token(token)
                await add_images(msg)
            if new_sources_elements is not None:
                sources_elements.extend(new_sources_elements)

    log.info("chainlit streaming finished")

    if cl.user_session.get("latest_sources_elements"):
        log.info("Adding sources elements to message")
        await stream_sources(msg, cl.user_session.get("latest_sources_elements"))
    
    

    # Send the final message
    memory.append({"name": "AI", "content": msg.content})  
    log.info(f"msg elements: {msg.elements}")
    await msg.update()
