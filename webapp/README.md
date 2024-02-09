# Webapp

Using chainlit as its great

## local testing

Use local auth:

Init gcloud

```sh
#gcloud config configurations create sunholo
gcloud config configurations activate sunholo
gcloud auth application-default login
```

Copying over the config file form root directory to look like as its deployed on Cloud Run

From this folder:

```bash
ln -s ../../config config
```

Run in write mode:

```bash
chainlit run --port=8080 app.py -w
```