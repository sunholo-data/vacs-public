import chainlit as cl

async def setup_agent_logic(settings):
    app_user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")

 
