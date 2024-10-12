# Wordle

## Running the App

### Use Docker
```sh
docker compose up -d
```
then open http://localhost:8711

### Use Python
Start postgres by the following or other postgres service.
```sh
docker compose up -d postgres
```

### Setup and Installation
1. Set up a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Copy .env.example to .env and fill in the necessary environment variables:
    ```
    cp .env.sample .env
    ```
    and update the values

Then start server side by:
```sh
cd server
ENV=demo CLIENT_PORT=8011 POSTGRES_URL=postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/wordle
```

Then start client side by:
```sh
cd client
ENV=demo SERVER_PORT=8010 python client.py
```
then open http://localhost:8701/
