# Haystack RAG Application

RAG Application built with Haystack, FastAPI and Amazon Bedrock.

It currently can answer questions based on the Wikipedia pages of [Seven Wonders of the Ancient World](https://en.wikipedia.org/wiki/Wonders_of_the_World).

Example questions:
```
"Where is Gardens of Babylon?"
"Why did people build Great Pyramid of Giza?"
"What does Rhodes Statue look like?"
"Why did people visit the Temple of Artemis?"
"What is the importance of Colossus of Rhodes?"
"What happened to the Tomb of Mausolus?"
"How did Colossus of Rhodes collapse?"
```

## Install prerequisites

- Install Python 3.11 or higher: https://www.python.org/downloads/
- Install uv: https://docs.astral.sh/uv/

## Configuring the Project

You must first create an [AWS account](https://portal.aws.amazon.com/).

Create a `.env` file in the `backend` directory of the project and populate it with the values:
```
MODEL_ID="deepseek.v3.2"
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

I have tested it with:

```
MODEL_ID="deepseek.v3.2"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

## Run the project

cd into `backend` directory: `cd backend`

To run the project run the following command: `uv run fastapi dev main.py`.

### Test the application

Ingest data:
```
curl -X 'POST' \
  'http://127.0.0.1:8000/ingest-data' \
  -H 'accept: application/json' \
  -d ''
```

The ingestion process takes somewhere between 30-60s.

Start asking questions:
```
curl --get "http://127.0.0.1:8000/chat" \
     --data-urlencode "question=Why did people build Great Pyramid of Giza?"
```

You should start seeing responses based on the ingested data:
```
{
    "response": "The Great Pyramid of Giza was built primarily as a tomb for the Fourth Dynasty pharaoh Khufu (Cheops). This purpose is clearly stated in the provided context, which describes it as \"the largest Egyptian pyramid and the tomb of Fourth Dynasty pharaoh Khufu.\"\n\nThe broader reasons for its monumental scale and effort relate to religious and cultural beliefs of ancient Egypt. Pyramids were designed as grand, eternal resting places to protect the pharaoh's body and possessions, which was essential for his soul's journey and continued rule in the afterlife. The immense resources and sophisticated construction techniques described—such as the precise fitting of casing stones, the use of ramps, and the organized workforce—were dedicated to creating a structure that would ensure the pharaoh's immortality and demonstrate his divine power and authority.\n\n**Answer:** The Great Pyramid of Giza was built as a monumental tomb for Pharaoh Khufu, serving as his eternal resting place to ensure his successful transition to the afterlife and to demonstrate his supreme authority and divine connection."
}
```
