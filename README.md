Code for app hosted at https://covid.marcoinacio.com

# Serve on localhost

To serve a copy on localhost:62081 run:

`poetry install`

`poetry run python app/preprocessing.py`

`poetry run ./start_server.sh`

# Deploy on Kubernetes

To deploy on Kubernetes, build the image (change the image name accordingly)

`docker build . -t marcoinacio/covid-app:1.0`

`docker push marcoinacio/covid-app:1.0`

(Edit the file image name on file `deploy_on_kubernetes.yaml`)

`kubectl apply -f deploy_on_kubernetes.yaml`
