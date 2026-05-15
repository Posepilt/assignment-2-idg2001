# IDG2001 Cloud Technologies - Assignment 2

## Group members
* Emil Voldengen Larsen (10065)
* Adrian David Fonseca Malvik (10102)
* Arbresha Mehmeti (10075)

## About
A REST API for looking up Olympic Games data, split into multiple services running in Docker with Docker Compose.

## How to run
From the project root, build and start all services:
```bash
# from the project root
docker compose up --build
```

The main API will be available at: http://localhost:8000  
Interactive documentation at: http://localhost:8000/docs

## How to test
Install dev dependencies and run pytest and mypy from inside the `/main-api` folder. Flake8 is run from the project root.
```bash
# from /main-api
pip install -r requirements-dev.txt
pytest
mypy .

# from the project root
flake8 .
```
