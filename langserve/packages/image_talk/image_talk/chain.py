from langchain_core.messages import HumanMessage, BaseMessage

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

from operator import itemgetter

from sunholo.components import get_llm_chat
from sunholo.logging import setup_logging

from pydantic import BaseModel
from typing import Optional, List, Dict

log = setup_logging()

VECTOR_NAME = "image_talk"

class Question(BaseModel):
    question: str
    chat_history: Optional[List[Dict]] = None
    image_url: Optional[str] = None

_inputs = RunnableParallel({
        "image_url": itemgetter("image_url"),
        "question": itemgetter("question")
    })

def _prompt(a_dict) -> list[BaseMessage]:
    question = a_dict["question"] 
    image_url = a_dict.get("image_url", None)
    if image_url is None:
        return [
            HumanMessage(content=[
                {
                    "type": "text",
                    "text": "I have not upload an image, please reply asking for me to upload an image for you to function"
                }
            ])
        ]
    return [
        HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"{image_url}"},
                },
                {
                    "type": "text",
                    "text": f"{question}",
                }
            ]
        )
    ]


_model = get_llm_chat(VECTOR_NAME)
# if you update this, you MUST also update ../pyproject.toml
# with the new `tool.langserve.export_attr`
chain = _inputs | _prompt | _model |  StrOutputParser()

chain = chain.with_types(input_type=Question)


