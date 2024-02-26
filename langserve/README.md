# test_langchain_template

## Installation

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Adding packages

Install the packages within `packages` directory

```bash
for d in packages/*; do 
    if [ -d "$d" ]; then 
        echo "Processing directory: $d"  # Add this line
        pip install -e "$d" 
    fi; 
done
```

Symlink the config folder:

From the `langserve` folder:

```bash
ln -s ../config config
```



## Setup LangSmith (Optional)
LangSmith will help us trace, monitor and debug LangChain applications. 
LangSmith is currently in private beta, you can sign up [here](https://smith.langchain.com/). 
If you don't have access, you can skip this section


```shell
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # if not specified, defaults to "default"
```

## Launch LangServe

```bash
langchain serve --port 8080
```

## Private Cloud Runs

To see the private websites such as qna/docs you need to see it locally via the gcloud proxy>

```sh
gcloud run services proxy langserve --region=europe-west1
```

Can then view at `http://localhost:8080/docs`

### Multivac URL

```bash
curl http://localhost:8080/pirate_speak/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"question":"Who is Mark Edmondson?"}
  }'

```
