# Vertex GenAI

This is a demo of using VertexAI grounding with Google Search as well as LlamaIndex RAG within a Vertex AI chat bot.

See more documentation at https://dev.sunholo.com/docs/VACs/vertex-llamaindex/

## Architecture

You can't use Llamaindex RAG tools alongside the Google Search and Vertex AI Search tools in the same model for some reason.

Instead two models are made to async batch call requests for the context, then a third model gathers them together for streaming to the end user.

## Config

An example configuration file is needed to configure what features are available:

```yaml
kind: vacConfig
apiVersion: v1
gcp_config: # reached via vac='global'
  project_id: your-gcp-project
  location: europe-west1
vac:  
  personal_llama:
    llm: vertex
    model: gemini-1.5-pro-preview-0514
    agent: vertex-genai
    display_name: Gemini with grounding via Google Search and LlamaIndex
    grounding:
      google_search: true # if true will use Google Search in grounding results
    memory:
      - llamaindex-native:
          vectorstore: llamaindex
          rag_id: 123123132 # you create this during setup
    gcp_config:
      project_id: your-gcp-project
      location: us-central1   # llamaindex is only available in us-central1 atm
    chunker:
      chunk_size: 1000
      overlap: 200
```

Also install `sunholo` with GCP and HTTP features: `sunholo[gcp,http]`

To test using the CLI also install `sunholo[cli]`

e.g

```sh
pip install sunholo[gcp,http,cli]
```


## Test calls

### Locally

Start up the Flask server:

```sh
python vertex-genai/app.py
```

curl query against the URLs:

```shell
curl http://127.0.0.1:8080/vac/personal_llama \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What do you know about MLOps?"
}'

curl http://127.0.0.1:8080/vac/streaming/personal_llama \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What do you know about MLOps?"
}'
```

### Deployed

If deployed on Multivac, you can use the `sunholo` CLI to chat with an instance via a proxy for the authenticated calls:

Assuming the same config as above, which has a [practioners guide to MLOPs](https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf) within its Llamaindex:

```shell
sunholo vac chat personal_llama  

VAC Proxies - `sunholo proxy list`                           
┏━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ VAC          ┃ Port ┃ PID   ┃ URL                   ┃ Local ┃ Logs                  ┃
┡━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ vertex-genai │ 8080 │ 48434 │ http://127.0.0.1:8080 │ No    │ No log file specified │
└──────────────┴──────┴───────┴───────────────────────┴───────┴───────────────────────┘
╭───────────────────────────────── Gemini with grounding via Google Search and LlamaIndex ─────────────────────────────────╮
│ Starting VAC chat session                                                                                                │
╰────── stream: http://127.0.0.1:8080/vac/streaming/personal_llama invoke: http://127.0.0.1:8080/vac/personal_llama ───────╯
You: what is MLOps?
✺ Thinking...
```

The reply below takes the grounding from LlamaIndex:

```bash
personal_llama: MLOps, short for Machine Learning Operations, is a methodology bridging the gap between machine learning application 
development and their real-world deployment and operation. It aims to streamline and automate the entire lifecycle of an ML 
model, from its initial development to deployment and ongoing maintenance. 

Here's a breakdown of what MLOps encompasses:

* **Standardized Processes:** MLOps establishes standardized workflows and best practices for building, deploying, and 
managing ML systems, ensuring consistency and efficiency.
* **Automation:** It emphasizes automating repetitive tasks within the ML lifecycle, like model training, testing, and 
deployment, to accelerate development and reduce errors.
* **Reliability and Scalability:**  MLOps promotes practices that guarantee the reliability, scalability, and performance of
ML models in production environments. 
* **Continuous Improvement:** By incorporating monitoring, logging, and feedback mechanisms, MLOps enables continuous model 
improvement and adaptation over time.

**In essence, MLOps combines the best of software engineering and machine learning to deliver ML solutions in a robust, 
scalable, and automated manner.** 

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Testing the Google Search grounding:

```bash
You: what happened this week in the run up to the UK election?
✺ Thinking...

personal_llama: Combining the information provided:

While I cannot access real-time information to confirm specific news from last week, it's likely that news regarding the UK 
general election included:

* **Reform UK launching their campaign in Clacton.** This suggests the party is actively campaigning in specific areas.
* **The Liberal Democrats announcing an NHS funding pledge.**  This indicates parties are revealing key policy points in 
their election manifestos. 
```