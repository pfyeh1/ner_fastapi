
from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
import json
from pydantic import BaseModel
from collections import Counter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import json
import re

import spacy
from spacy import displacy
from spacy.util import filter_spans

from pyvis.network import Network
from collections import defaultdict

import uuid

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
    return (
        config["entity_dicts"],
        config["allowed_labels"],
        config["testing"],
        config['network_options'],
        config['product_patterns']
    )

def extract_entities(text, allowed_labels, product_patterns):
    """
    extracts entities and associated labels
    :param text: article text
    returns dictionary of entity and label
    """
    doc = make_spacy_doc(text, product_patterns)

    results = {}
    items = list(set([(x.text, x.label_) for x in doc.ents if x.label_ in allowed_labels]))
    labels = Counter([x[1] for x in items])
    ent_counts = Counter([x[0] for x in items])

    #results['ents_labels'] = items
    results['ents_labels'] = list(set(items))
    results['entities'] = list(set([x[0] for x in items]))
    results['labels'] = labels
    results['ent_counts'] = ent_counts

    return results

def make_spacy_doc(text, product_patterns):
    """
    extracts entities utilizing patterns
    :param text: article text
    returns dictionary of entity and label
    """ 
    doc = nlp(text)

    # let's get regex extracted entities
    new_ents = []
 
    for ptrn in product_patterns:
        for match in re.finditer(ptrn, doc.text):
            ent = doc.char_span(match.start(), match.end(), label='PRODUCT')
            if ent is not None:  # Ensure the span is valid
                new_ents.append(ent)

    # combine existing entities with new entities
    all_entities = new_ents + list(doc.ents) 

    # Use filter_spans to remove overlaps
    filtered_entities = filter_spans(all_entities)

    doc.ents = filtered_entities

    return doc

def create_network(text, allowed_labels, net_option, product_patterns):
    """
    extracts entities and associated labels
    :param text: article text
    returns network graph
    """   
    doc = make_spacy_doc(text, product_patterns)

    # initalize network
    net = Network(bgcolor="#222222", font_color="white", cdn_resources = 'remote')

    # Create a defaultdict to store node IDs
    node_ids = defaultdict(lambda: len(node_ids))

    # Add nodes and edges
    for ent in doc.ents:
        if ent.label_ in allowed_labels:
            source_id = node_ids[ent.text]
            net.add_node(source_id, label=ent.text, title=ent.label_)
            for token in ent.sent:
                if token.ent_type_:
                    target_id = node_ids[token.text]
                    net.add_node(target_id, label=token.text, title=token.ent_type_)
                    if source_id != target_id:  # Avoid self-loops
                        net.add_edge(source_id, target_id)  
    # customize network
    net.set_options(net_options)
    
    return net

class Article(BaseModel):
    text: str

# define route
@app.get("/")
async def read_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/entities")
async def analyze_text(query: Article):
    try:
        entities = extract_entities(query.text, allowed_labels, product_patterns)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

@app.get("/form", response_class = HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})

@app.post("/form", response_class = HTMLResponse)
async def analyze_form_text(request:Request, msg: str = Form(), action: str = Form()):
    try:
        if action == 'extract':
            doc = make_spacy_doc(msg, product_patterns)
            content_html = displacy.render(doc, style = "ent",options = dct, page = True)
        elif action == 'visualize':
            net = create_network(msg, allowed_labels, net_options, product_patterns)
            # generate html
            content_html = net.generate_html()
        else:
            content_html = "<p>Oops! Something went wrong!</p>"
        
        #back_button = '<br><a href="/form"><button>Go back to form</button></a>'
        #return HTMLResponse(content=content_html + back_button)
        return templates.TemplateResponse("base.html", {
            "request":request,
            "content_html":content_html
            })
    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))

#load dictionaries from config file
entity_dicts, allowed_labels, testing, net_options, product_patterns = load_config_from_env()

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
ruler = nlp.add_pipe("entity_ruler", before = 'ner')
ruler.add_patterns(entity_dicts)