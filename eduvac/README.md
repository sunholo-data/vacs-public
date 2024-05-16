# EduVAC

Open source code for the EduVAC private VAC on https://multivac.sunholo.com

See https://dev.sunholo.com/docs/VACs/eduvac for more details.


## Local Testing
 
This is a Langserve VAC, so the original README below will help:

## Installation

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Launch LangServe

```bash
langchain serve --port 8080
```

## Private Cloud Runs behind VPC

To see the private websites behind a Cloud Run VPC you need to see it locally via the gcloud proxy:

```sh
gcloud run services proxy eduvac --region=europe-west1
```

Can then view at `http://localhost:8080/docs`

### Multivac URL

```bash
curl http://localhost:8080/eduvac/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"question":"Teach me this content"}
  }'

```
