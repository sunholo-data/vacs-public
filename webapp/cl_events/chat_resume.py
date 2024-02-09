import chainlit as cl
from chainlit.types import ThreadDict

async def on_chat_resume_logic(thread: ThreadDict):

    memory = list()

    root_messages = [m for m in thread["steps"] if m["parentId"] == None]
    for message in root_messages:
        if message["type"] == "USER_MESSAGE":       
            memory.append({"name": "Human", "content": message["output"]})
        else:
            memory.append({"name": "AI", "content": message["output"]})


    cl.user_session.set("memory", memory)
