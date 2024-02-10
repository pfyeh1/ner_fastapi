
from fastapi import FastAPI, HTTPException
import spacy

# import language model
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

app = FastAPI()

def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({'text': ent.text,
                         'label': ent.label_})
    return entities

# define route
@app.post("/ner")
async def analyze_ner(text: str):
    try:
        entities = extract_entities(text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))
