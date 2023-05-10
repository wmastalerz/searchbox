# searchbox-app
A simple search engine to search medium stories built with streamlit and elasticsearch. 
The demo of this app is available on [<!-- docs -->](https://search-box-app.docsapp.com/).

## Prepare Environments
The codes were tested and ran on Ubuntu 18.04 using python 3.7. 
Create and set up a python environment by running the following command in the terminal
```
# create python venv and install libraries in the requirements.txt
source ./create_env
```

## Docker
Since this app depends on the elasticsearch container, it is preferable to use docker compose. 
Before getting started, let's build the docker container of this app
```
docker build -t searchbox .
```
Then use local docker-compose (contain its own elasticsearch manifest):
```
source env/bin/activate
docker-compose up
# the webapp should be available in localhost:8501
```

Or deploy on Kubernetes (used exitsitng elasticsearch):
```
# push image to local current registry
docker tag searchbox localhost:8282/searchbox && docker push localhost:8282/searchbox

# deploy searchbox-app (values.elasticsearch -> name of current elasticsearch service)
helm install docs charts/searchbox
```

