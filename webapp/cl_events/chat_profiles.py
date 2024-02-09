import chainlit as cl
from sunholo.utils import load_config

configs, filename = load_config("config/llm_config.yaml")

def to_proper_case(s):
    return ' '.join(word.capitalize() for word in s.replace('_', ' ').replace('-', ' ').split())

print(configs)

def craft_description(config):
    description = config.get('description')

    if description is None:
        description = f"VAC: {config.get('agent')} LLM: {config.get('llm')}"

    return description

def create_chat_profile(name, config):
    config = configs[name]
    return cl.ChatProfile(
        name=config.get('display_name', name),
        markdown_description=craft_description(config),
        icon=config.get("avatar_url", "public/logo_light.png")
    )

def tailor_chat_profiles(tags=None):
    # Check if tags is None or a list of strings
    if tags is not None and not all(isinstance(tag, str) for tag in tags):
        raise ValueError("Tags must be a list of strings or None")

    chat_profiles = []
    if tags is not None:
        for name, value in configs.items():
            if name in tags:
                chat_profile = create_chat_profile(name, configs[name])
                chat_profiles.append(chat_profile)
    else:
        for name, value in configs.items():
            chat_profile = create_chat_profile(name, configs[name])
            chat_profiles.append(chat_profile)
    
    return chat_profiles




async def chat_profile_logic(current_user: cl.User):
    if current_user.metadata["role"] == "ADMIN":
        admin_profiles = tailor_chat_profiles()
        return admin_profiles
    elif current_user.metadata["role"] == "USER":
        user_profiles = tailor_chat_profiles(["multivac_docs", "pirate_speak","csv_agent"])
        return user_profiles
    else:
        free_profiles = tailor_chat_profiles(["multivac_docs", "pirate_speak", "csv_agent"])
        return free_profiles
    #TODO: different chat_profiles based on current_user.tags
    return tailor_chat_profiles()
