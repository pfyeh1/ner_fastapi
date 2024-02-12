
from fastapi import FastAPI, HTTPException
import spacy
import json
from pydantic import BaseModel
from collections import Counter

# import language model
spacy.cli.download("en_core_web_md")
nlp = spacy.load("en_core_web_md")

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
    ents_labels = [(x.text, x.label_) for x in doc.ents]
    labels = Counter([x[1] for x in ents_labels])
    ent_counts = Counter([x[0] for x in ents_labels])

    results['ents_labels'] = ents_labels
    results['entities'] = [x[0] for x in ents_labels]
    results['labels'] = labels
    results['ent_counts'] = ent_counts

    return results

class Article(BaseModel):
    text: str


# define route

@app.get("/")
def read_main():
    return {"message": "Hello!"}

@app.post("/entities")
async def analyze_text(query: Article):
    try:
        entities = extract_entities(query.text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
