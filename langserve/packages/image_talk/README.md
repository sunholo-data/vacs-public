# Image talk via Langserve

Gemini Pro Vision 1.0

If you are inside this directory, then you can spin up a LangServe instance directly by:


```shell
cd application/qna/langserve/packages/image_talk
ln -s ../config config
langchain serve
```

This will start the FastAPI app with a server is running locally at 
[http://localhost:8000](http://localhost:8000)

We can see all templates at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
We can access the playground at [http://127.0.0.1:8000/image_talk/playground](http://127.0.0.1:8000/image_talkplayground)  

We can access the template from code with:

```python
from langserve.client import RemoteRunnable

runnable = RemoteRunnable("http://localhost:8000/image_talk")
```

## Loading

Images are uploaded the the DOC bucket in a timestamped folder.

