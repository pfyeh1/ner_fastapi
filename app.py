
from fastapi import FastAPI, HTTPException
import spacy
import json

# import language model
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

app = FastAPI()

# load entity dictionaries from config file
def load_entity_dicts(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config["entity_dicts"]

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({'text': ent.text,
                         'label': ent.label_})
    return entities

# define route

@app.get("/")
def read_main():
    return {"message": "Hello!"}

@app.post("/ner")
async def analyze_ner(text: str):
    try:
        entities = extract_entities(text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
