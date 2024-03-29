# DevOps Apprenticeship: Project Exercise

## System Requirements

The project uses poetry for Python to create an isolated environment and manage package dependencies. To prepare your system, ensure you have an official distribution of Python version 3.7+ and install poetry using one of the following commands (as instructed by the [poetry documentation](https://python-poetry.org/docs/#system-requirements)):

### Poetry installation (Bash)

```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

### Poetry installation (PowerShell)

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python
```

## Dependencies

The project uses a virtual environment to isolate package dependencies. To create the virtual environment and install required packages, run the following from your preferred shell:

```bash
$ poetry install
```

## Setup and Evironment variables

You'll also need to clone a new `.env` file from the `.env.tempalate` to store local configuration options. This is a one-time operation on first setup:

```bash
$ cp .env.template .env  # (first time only)
```

The `.env` file is used by flask to set environment variables when running `flask run`. This enables things like development mode (which also enables features like hot reloading when you make a file change). There's also a [SECRET_KEY](https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY) variable which is used to encrypt the flask session cookie.\'

Other values that we need for .env:
* `MONGO_COLLECTION`= MongoDB collection

As this app is registered on Github for authentication, additition values are needed for .env. These values can be will be known after creating an [OAuth App](https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app) on GitHub:
* `client_id`
* `client_secret`
* `redirect_uri`

The following variable is changed only during testing. This is to prevent the 'login_required' decorator from redirecting in tests.
* `disable_login=False`

In order to connect the app to the CosmosDB, the following variable needs to be passed in as an environment variable. This can be found through CLI or through the Azure Portal.
* `MONGODB_CONNECTION_STRING`

By default, when running locally, Flask logs everything at DEBUG level and above. This is because it's running in the development profile. When running in production, it will only log ERROR and above. We'd like to make this configurable. So a variable is added to the app config called LOG_LEVEL and this can be altered in .env.
* `LOG_LEVEL=INFO`

[Loggly](https://www.loggly.com/) is the log management service that will be used. For Loggly to access the logs, a loggly token is required.
* `LOGGLY_TOKEN`

## Secrets

Since we have sensitive information, the following variable need to be stored as Secrets:
* `LOGGLY_TOKEN`
* `SECRET_KEY`
* `MONGODB_CONNECTION_STRING`
* `GITHUB_CLIENT_ID`
* `GITHUB_CLIENT_SECRET`

Run the following Command with the values as arguments:

```bash
$ kubectl create secret generic test-secret --from-literal='GITHUB_CLIENT_ID=<GITHUB_CLIENT_ID>' --from-literal='GITHUB_CLIENT_SECRET=GITHUB_CLIENT_SECRET' --from-literal='MONGODB_CONNECTION_STRING=<MONGODB_CONNECTION_STRING>' --from-literal='SECRET_KEY=<SECRET_KEY>' --from-literal='LOGGLY_TOKEN=<LOGGLY_TOKEN>'
```

These values can then be referenced in deployment.yaml under `env` in `spec` using the following format:

```
name: GITHUB_CLIENT_ID
    valueFrom:
        secretKeyRef:
            name: test-secret
            key: GITHUB_CLIENT_ID
```

## Running the App

### With Poetry and Flask

Once the all dependencies have been installed, start the Flask app in development mode within the poetry environment by running:
```bash
$ poetry run flask run
```
If there is an error saying "address already in use", first runn the the following command then poetry:
```bash
$ kill -9 $(lsof -t -i:"5000")  
```

You should see output similar to the following:
```bash
 * Serving Flask app "app" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with fsevents reloader
 * Debugger is active!
 * Debugger PIN: 226-556-590
```
Now visit [`http://localhost:5000/`](http://localhost:5000/) in your web browser to view the app.

### Minikube

Minikube is a version of Kubernetes that you can run locally on a development machine. It can be a great way to learn about Kubernetes and test changes locally without having to set up and pay for hosting.

Download:
* [Docker](https://docs.docker.com/get-docker/)
* [Kubectl](https://kubernetes.io/docs/tasks/tools/)
* [minikube](https://minikube.sigs.k8s.io/docs/start/)

### Starting the app on Minikube

* `minikube start` - run this in an admin terminal to spin up the minikube cluster.
* `docker build --target production --tag todo-app:prod .` - create a Docker image for the Pod.
* `minikube image load todo-app:prod` - load in the docker image.
* `kubectl apply -f deployment.yaml` -  deploy a Pod running the docker image.
* `kubectl apply -f service.yaml ` - deploy the Service.
* `kubectl port-forward service/module-14 5000:5000` - link up our minikube Service with a port on localhost.

You can then visit http://localhost:5000/ in your web browser to view the app.

### Virtual Machine(VM) using Vagrant

The app can be ran in a virtual machine using Vagrant. 
Vagrant encapsulates development environment in a single configuration file, making it easy to share
between developers and launch without having to worry about Python environments and dependencies.

Download: 
* Hypervisor - Vagrant requires a hypervisor installed. recommended [VirtualBox](https://www.virtualbox.org/).
* Vagrant - Download and install vagrant from the [official website](https://www.vagrantup.com/). You can check it's installed correctly by running the `vagrant` command in your terminal.

### Starting the app on the VM

* `vagrant up` - Starts your VM, creating and provisioning it automatically if it is required. This command will automatically run the app on the browser.
* `vagrant ssh` - explore this VM using the bash shell. 

You can then visit http://localhost:5000/ in your web browser to view the app.

#### Other useful commands

* `vagrant provision` - Runs any VM provisioning steps specified in the Vagrantfile. Provisioning steps are one-off operations that adjust the system provided by the box.
* `vagrant suspend` - Suspends any running VM. The VM will be restarted on the next vagrant up command.
* `vagrant destroy` - Destroys the VM. It will be fully recreated the next time you run vagrant up.

### Using Docker containers

Download: 
* Docker - you'll need to install [Docker Desktop](https://www.docker.com/products/docker-desktop). Installation instructions for Windows can be found [here](https://docs.docker.com/docker-for-windows/install/). If prompted to choose between using Linux or Windows containers during setup, make sure you choose Linux containers.

#### Running the Dev, Prod & Test Container

The dev container has two key behaviours:
* Enables Flask's debugging/developer mode to provide detailed logging and feedback.
* Allows rapid changes to code files without having to rebuild the image each time.

The difference between the dev and prod container is that the prov container uses Gunicorn to run the app, whereas the dev container uses Flask.

You can create either a development, production or test image from the same Dockerfile
by running the following for dev:
```bash
$ docker build --target development --tag todo-app:dev .
```
or the the following for prod:
```bash
$ docker build --target production --tag todo-app:prod .
```
or the the following for test:
```bash
$ docker build --target test --tag my-test-image .
```
___

You can then start the dev container by running:
```bash
$ docker run --env-file .env -p 5000:5000 -v $(pwd)/todo_app:/todo_app/todo_app  todo-app:dev
```
or you can start the prod container by running:
```bash
$ docker run --env-file .env -p 5000:5000 todo-app:prod
```
or you can start the test container by running:
```bash
$ docker run --env-file .env my-test-image tests/e2e
```
## Run Tests

For Selenium tests, Download Firefox beforehand and you will need to download the matching version of the Gecko Driver executable and place it in the root of your project - the selenium driver just uses this under the hood.

If in poetry env:
* For unit and integration tests: run `pytest tests/int_unit`
* For Selenium tests: run `pytest tests/e2e`

If not in poetry env: 
* For unit and integration tests: run `poetry run pytest tests/int_unit`
* For Selenium tests: run `poetry run pytest tests/e2e`

## Continuous Deployment

This app is deployed on Azure.
You can then visit this link [here](https://devops-todo-app.azurewebsites.net) in your web browser to view the app on Azure.

The Travis CI:
* automatically builds and deploys the branch to Azure
* publishes the Docker images to Docker Hub
* update the Terraform resources before deploy