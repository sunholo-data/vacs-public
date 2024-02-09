import chainlit as cl
from typing import Optional

def auth_callback_logic(username: str, password: str) -> Optional[cl.User]:
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", 
            metadata = {"role":"ADMIN", "provider":"credentials", "tags":["admin_user"]}
        )
    elif (username, password) == ("test", "test"):
        return cl.User(
            identifier="test",
            metadata = {"role":"USER", "provider":"credentials", "tags":["regular_user"]}
        )
    else:
        return None