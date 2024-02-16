
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel
from collections import Counter

import os
import spacy
from spacy import displacy

# import language model
spacy.cli.download("en_core_web_md")
nlp = spacy.load("en_core_web_md")

#spacy.cli.download("en_core_web_sm")
#nlp = spacy.load("en_core_web_sm")

app = FastAPI()

# load entity dictionaries from config file
def load_config_from_env():
    """
    load dicts from json config file
    :param config_file: path to config file
    :return: dictionary 
    
    """
    config_file_path = os.getenv("CONFIG_FILE_PATH")
    if not config_file_path:
        raise ValueError("CONFIG_FILE_PATH environment variable is not set")
    
    with open(config_file_path, "r") as f:
        config = json.load(f)
    return config["entity_dicts"], config["allowed_labels"]

#load dictionaries from config file
entity_dicts, allowed_labels = load_config_from_env()

# add entity ruler patterns to spaCy pipeline
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(entity_dicts)

def extract_entities(text, allowed_labels):
    """
    extracts entities and associated labels
    :param text: article text
    returns dictionary of entity and label
    """
    doc = nlp(text)
    results = {}
    items = [(x.text, x.label_) for x in doc.ents if x.label_ in allowed_labels]
    labels = Counter([x[1] for x in items])
    ent_counts = Counter([x[0] for x in items])

    results['ents_labels'] = items
    results['entities'] = [x[0] for x in items]
    results['labels'] = labels
    results['ent_counts'] = ent_counts

    return results

class Article(BaseModel):
    text: str

# define route
@app.get("/")
def read_main():
    return {"message": "Welcome to your basic NER app!"}

@app.post("/entities")
async def analyze_text(query: Article):
    try:
        entities = extract_entities(query.text, allowed_labels)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/form", response_class = HTMLResponse)
async def form_get():
    return'''
    <html>
    <head>
    <title>NER Extractor</title>
    </head>
    <br><br>
    <h1>Extract Entities From Your Text</h1>
    <body>
    <form method="post">
    <label for="msg">Enter your text:</label><br>
    <textarea id="msg" name="msg" rows="10" cols="100" placeholder="Enter your text here" required></textarea>
    <br><br>
    <input type="submit"/> 
    </form>
    </body>
    </html>
    '''
    

@app.post("/form", response_class = HTMLResponse)
async def analyze_form_text(msg: str = Form()):
    try:
        doc = nlp(msg)
        html = displacy.render(doc, style = "ent", page = True)
        return HTMLResponse(content = html)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

