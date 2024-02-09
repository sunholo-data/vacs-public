import chainlit as cl
from typing import Optional, Dict

from sunholo.logging import setup_logging

logging = setup_logging()

def oauth_callback_logic(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  logging.info(f"raw_user_data: {raw_user_data}")
  logging.info(f"provider_id: {provider_id}")
  if provider_id == "google":
    if "hd" in raw_user_data:
      if raw_user_data["hd"] == "sunholo.com":
          return cl.User(
              identifier="admin", 
              metadata = {"role":"ADMIN", 
                          "provider":"google", 
                          "tags":["admin_user"],
                          "hd": raw_user_data["hd"],
                          "locale": raw_user_data["locale"],
                          "email": raw_user_data["email"]
                          }
          )
    else:
        return cl.User(
           identifier=raw_user_data["name"],
           metadata = {"role": "USER", 
                       "provider":"google", 
                       "tags":["user"],
                       "hd": raw_user_data.get("hd"),
                       "locale": raw_user_data["locale"],
                       "email": raw_user_data["email"]
                      }
        )
  return cl.User(
           identifier=raw_user_data["name"],
           metadata = {"role": "USER-FREE", 
                       "provider": provider_id, 
                       "tags":["user", "free"],
                       "hd": raw_user_data.get("hd"),
                       "locale": raw_user_data["locale"],
                       "email": raw_user_data["email"]
                      }
        )
