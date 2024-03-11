# NER using spaCy and FastAPI
```
Basic Named Entity Extractor using spaCy and FastAPI
```

## Description
Project to understand how to deploy a basic ML model into production using Docker and AWS ECR, and EC2 services as well as learning how to use the FastAPI library. Named Entity Extractor uses pre-trained spaCy english language model supplemented with regex patterns and an entity dictionary.

## Getting Started
Config file is used to manage custom entity lists and regex patterns. One can also define the the labeled entities the model will extract by defining a list of allowed labels.

```JSON
{
  "entity_dicts": [
      {"label": "ORG", "pattern": [{"LOWER": "hamas"}]},
      {"label": "ORG", "pattern": [{"LOWER": "hizballah"}]}
      {"label": "ORG", "pattern": [{"LOWER": "isis"}]}
    ],
   
    "allowed_labels": ["GPE",
                        "FAC",
                        "PERSON",
                        "ORG",
                        "PRODUCT",
                        "LOC",
                        "EVENT",
                        "LAW"]
  }
```

## Routes

| Method     | URL           |
|------------|---------------|
| `POST`     | `/entities`   | 
| `GET`      | `/form`       | 
| `POST`     | `/form`       | 


## Further Reading

Helpful links on integrating spaCy and FastAPI, dockerizing your app, pushing docker images into AWS's ECR and pulling the image to deploy on EC2.
- https://medium.com/@meetakoti.kirankumar/deploying-fastapi-web-application-in-aws-a1995675087d
- https://towardsdatascience.com/deploying-your-first-machine-learning-api-1649236c695e
- https://yudanta.github.io/posts/deploy-spacy-ner-with-fast-api/
- https://www.freecodecamp.org/news/build-and-push-docker-images-to-aws-ecr/
- https://levelup.gitconnected.com/deploy-a-dockerized-fastapi-application-to-aws-cc757830ba1b
- https://plainenglish.io/community/how-to-deploy-a-docker-image-to-amazon-ecr-and-run-it-on-amazon-ec2-3a8445




