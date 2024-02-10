
from fastapi import FastAPI, HTTPException
import spacy
import json
from pydantic import BaseModel
from collections import Counter

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
    """
    extracts entities and associated labels
    :param text: article text
    returns dictionary of entity and label
    """
    doc = nlp(text)
    results = {}
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    labels =Counter([x[1] for x in entities])
    results['entities'] = entities
    results['labels'] = labels

    return results

class Article(BaseModel):
    text: str


# define route

@app.get("/")
def read_main():
    return {"message": "Hello!"}

@app.post("/ner")
async def analyze_text(query: Article):
    try:
        entities = extract_entities(query.text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
