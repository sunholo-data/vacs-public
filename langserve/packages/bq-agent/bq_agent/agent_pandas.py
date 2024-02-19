from pathlib import Path

import pandas as pd
# from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
# from langchain.chat_models import ChatOpenAI
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.pydantic_v1 import BaseModel, Field
# from langchain.tools.retriever import create_retriever_tool
# from langchain.vectorstores import FAISS
# from langchain_experimental.tools import PythonAstREPLTool
import bigframes.pandas as bpd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI



# Load data
df = bpd.read_gbq("SELECT name, job, created, transactions, revenue, permission, crm_id, FROM `annular-form-389809.merged_data.crm_ga4`LIMIT 45").to_pandas()

# Defining agent
agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)

# Default prompt
agent.run("Create 2 segments of high revenue customers described using meaningful features from the data.")

