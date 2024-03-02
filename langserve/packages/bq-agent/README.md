
# csv-agent

This template uses a [pandas agent](https://python.langchain.com/docs/integrations/toolkits/pandas) with tools [BigQuery DataFrames](https://cloud.google.com/python/docs/reference/bigframes/latest) to read a BigQuery table for interaction (question-answering) with tabular data.

## Environment Setup

Set the `OPENAI_API_KEY` environment variable to access the OpenAI models.


## Usage

To use this package, you should first have the LangChain CLI installed:

```shell
pip install -U langchain-cli
```

To create a new LangChain project and install this as the only package, you can do:

```shell
langchain app new my-app --package bq-agent
```

If you want to add this to an existing project, you can just run:

```shell
langchain app add bq-agent
```

And add the following code to your `server.py` file:
```python

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


add_routes(app, csv_agent_chain, path="/bq-agent")
```

(Optional) Let's now configure LangSmith. 
LangSmith will help us trace, monitor and debug LangChain applications. 
LangSmith is currently in private beta, you can sign up [here](https://smith.langchain.com/). 
If you don't have access, you can skip this section


```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # if not specified, defaults to "default"
```

If you are inside this directory, then you can spin up a LangServe instance directly by:

```shell
langchain serve
```

This will start the FastAPI app with a server is running locally at 
[http://localhost:8000](http://localhost:8000)

We can see all templates at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

We can access the playground at [http://127.0.0.1:8000/bq-agent/playground](http://127.0.0.1:8000/bq-agent/playground)  

We can access the template from code with:

```python
from langserve.client import RemoteRunnable

runnable = RemoteRunnable("http://localhost:8000/csv-agent")
```