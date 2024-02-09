from sunholo.utils import load_config

def lookup_config(chat_profile):

    configs, filename = load_config("config/llm_config.yaml")
    for name, value in configs.items():
        value["name"] = name
        if value.get('display_name') == chat_profile:
            return value
        elif name == chat_profile:
            return value