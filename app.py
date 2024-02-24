
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel
from collections import Counter
from fastapi.templating import Jinja2Templates

import os
import spacy
from spacy import displacy


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
        <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            width: 50%;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
        }
        label, textarea {
            display: block;
            margin-bottom: 10px;
        }
        textarea {
            width: auto;
            min-width: 100%; /* minimum width */
            max-width: 100%; /* maximum width */
            height: auto;
            min_height: 150px;
            padding: 10px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        input[type="submit"] {
            padding: 10px 20px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
    </head>
    <br><br>
    <h1>Preview Extracted Entities</h1>
    <body>
    <form method="post">

    <textarea id="msg" name="msg" rows="10" cols="100" placeholder="Enter your text here" required></textarea>
    <br><br>
    <input type="submit"/> 
    <input type="button" value="Clear Text" onclick="document.getElementById('msg').value='';"/>
    </form>
    </body>
    </html>
    '''
    

@app.post("/form", response_class = HTMLResponse)
async def analyze_form_text(msg: str = Form()):
    try:
        doc = nlp(msg)
        html = displacy.render(doc, style = "ent", page = True)
        return HTMLResponse(content=html + '<br><a href="/form"><button>Go back to form</button></a>')
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