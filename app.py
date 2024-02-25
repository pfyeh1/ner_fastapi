
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel
from collections import Counter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import spacy
from spacy import displacy


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
    return config["entity_dicts"], config["allowed_labels"], config["testing"]

def extract_entities(text, allowed_labels):
    """
    extracts entities and associated labels
    :param text: article text
    returns dictionary of entity and label
    """
    doc = nlp(text)
    results = {}
    items = list(set([(x.text, x.label_) for x in doc.ents if x.label_ in allowed_labels]))
    labels = Counter([x[1] for x in items])
    ent_counts = Counter([x[0] for x in items])

    results['ents_labels'] = items
    results['entities'] = list(set([x[0] for x in items]))
    results['labels'] = labels
    results['ent_counts'] = ent_counts

    return results

class Article(BaseModel):
    text: str

# define route
@app.get("/")
async def read_main(request: Request):
    return templates.TemplateResponse(request = request, name = "index.html")

@app.post("/entities")
async def analyze_text(query: Article):
    try:
        entities = extract_entities(query.text, allowed_labels)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/form", response_class = HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})

@app.post("/form", response_class = HTMLResponse)
async def analyze_form_text(msg: str = Form(), style: str = Form(...),
       options: str = Form(...)):
    try:
        doc = nlp(msg)
        html = ""
        if style == "ent":
            if options == "dct":
                html = displacy.render(doc, style = "ent", options = dct, page = True)
            else:
                html = displacy.render(doc, style = "ent", page = True)
            
        back_button = '<br><a href="/form"><button>Go back to form</button></a>'
        return HTMLResponse(content=html + back_button)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

#load dictionaries from config file
entity_dicts, allowed_labels, testing = load_config_from_env()

# import language model
if testing == "true":
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
else:
    spacy.cli.download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")

# create dict for use in displacy
dct = {'ents':allowed_labels}

# add entity ruler patterns to spaCy pipeline
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns(entity_dicts)