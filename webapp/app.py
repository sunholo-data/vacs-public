import chainlit as cl
from chainlit.types import ThreadDict

from typing import Optional, Dict

from cl_events import (
    main_logic, 
    chat_profile_logic, 
    auth_callback_logic, 
    on_chat_start_logic, 
    setup_agent_logic, 
    on_chat_resume_logic,
    oauth_callback_logic
    )

@cl.on_message
async def main(message: cl.Message):
    await main_logic(message)

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    return await chat_profile_logic(current_user)


# google oauth authentication
@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return oauth_callback_logic(provider_id, token, raw_user_data, default_user)

# password auth
#@cl.password_auth_callback
#def auth_callback(username: str, password: str) -> Optional[cl.User]:
#    return auth_callback_logic(username, password)

@cl.on_chat_start
async def on_chat_start():
    await on_chat_start_logic()

@cl.on_settings_update
async def setup_agent(settings):
    await setup_agent_logic(settings)

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    await on_chat_resume_logic(thread)