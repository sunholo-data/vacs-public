import chainlit as cl
from sunholo.logging import setup_logging
from .config import lookup_config

logging = setup_logging()

async def on_chat_start_logic():
    app_user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    config = lookup_config(chat_profile)
    memory = list()
    
    await cl.Avatar(
        name="sunholo",
        url="../public/logo_dark.png",
    ).send()

    cl.user_session.set("memory", memory)

    logging.info(f"Chat profile starting with {app_user.identifier}, ChatProfile: {chat_profile} with config: {config}")
    default_msg = f"Start chatting with {chat_profile} below"
    await cl.Message(
        author="sunholo",
        content=config.get('description', default_msg),
    ).send()


