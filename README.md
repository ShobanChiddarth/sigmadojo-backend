# SigmaDojo backend

FastAPI backend of SigmaDojo.

## [API DOCS](./docs/API.md)

## Requirements

1. python 3.12
2. `pip install -r requirements.txt`

Database requirement is sqlite, natively handled.

## Steps to run

1. `set -a`
2. `cp sample.env .env`
2. Edit .env
3. `source .env`
4. `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Available as container

### Pull:
```bash
docker pull shobanchiddarth/sigmadojo-backend:latest
```

### Run:
```bash
docker run -d -p 127.0.0.1:8000:8000 shobanchiddarth/sigmadojo-backend:latest
```

