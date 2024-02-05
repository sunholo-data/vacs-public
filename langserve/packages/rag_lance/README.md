# rag_lance

This template imports a corpus via LanceDB to power simple documentation chats.

If you are inside this directory, then you can spin up a LangServe instance directly by:


```shell
cd application/qna/langserve/packages/rag_lance
ln -s ../../../../../config config
langchain serve
```

This will start the FastAPI app with a server is running locally at 
[http://localhost:8000](http://localhost:8000)

We can see all templates at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
We can access the playground at [http://127.0.0.1:8000/pirate-speak/playground](http://127.0.0.1:8000/pirate-speak/playground)  

We can access the template from code with:

```python
from langserve.client import RemoteRunnable

runnable = RemoteRunnable("http://localhost:8000/pirate-speak")
```

## Loading

Add documents to the GCS bucket with folder `/vector_name` e.g. `/rag_lance` to have the data chunked and embedded available to the LanceDB backend using GCS.

