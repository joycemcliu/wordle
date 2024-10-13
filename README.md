# Wordle
The Wordle game is a puzzle where a player have six attempts to guess a 5-letter word, receiving feedback on correct letters and their positions after each guess.

Flow:

loop until either player guess correctly or on a allowed rounds:
1. player submits a 5-letter word as a guess
2. host checks the guess is a valid English word in case-insensitive
3. host shows hint to player


## Repository structure
```
.
├── wordle/
│   ├── client/
│   │    ├── static/
│   │    │     ├── css/
│   │    │     └── js/
│   │    ├── template/     // html template
│   │    └── client.py     // client's program entrypoint
│   ├── data/              // postgres's data
│   └── server/
│   │    ├── alembic/      // db migration handle
│   │    ├── logs/         // server log
│   │    ├── middleware/   // server's api middleware
│   │    ├── models/       // db schema
│   │    ├── src/          // reusable logic
│   │    ├── views/        // server's api endpoint
│   │    └── server.py     // server's program entrypoint
├── .env
├── docker-compose.yml
└── requirements.txt       // python's requirements
```



## Running the service
### For dmeo
This mode is for demonstration, the 5-letter word list is using list: [hello,world,quite,fancy,fresh,panic,crazy,buggy,scare]
1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Start Service by:
    ```sh
    docker compose up
    ```
Server api doc: http://0.0.0.0:8710/docs.

Then open http://localhost:8711.

###

### For development
This mode is for development, with features:
- will restart and reload updated changes on save.
- can override possible word list by changing `WORD_LIST` in `.env`.

### Start by Docker
1. Change to `ENV=dev` in `.env`.
2. Start service by `docker compose up`.
Server api doc: http://0.0.0.0:8710/docs.

Then open http://localhost:8711.

### Start by Python
1. Start postgres by the following or other postgres service.
   ```sh
   docker compose up -d postgres
   ```
2. Set up a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
3. Start server in terminal by:
   ```sh
   cd server
   ENV=demo CLIENT_PORT=8011 POSTGRES_URL=postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/wordle
   ```
4. Start client in another terminal by:
   ```sh
   cd client
   ENV=demo SERVER_PORT=8010 python client.py
   ```
Server api doc: http://0.0.0.0:8010/docs.
Then open http://localhost:8701/.

### Run test case
To run tests with verbose output:
```sh
pytest -v
```

## Service features
### Game mode
- Normal wordle by selecting "normal" in page
- Host cheating wordle by selecting "hard" in page.
   - Enhance "host cheating" difficutly by not updating a list of word candidates if the guess already in the previous history
- Adjustable number of attemps. (client restriction: min=1, max=20).

### UI/UX
- Start a new game by a button.
- Support inputting keystore by keyboard.
- Show hints in different color: green="HIT", orange="PRESENT", grey="MISS".
- Show hints on vitural keyboard in different color.
- Show guess message when submitting
- Reload page still keep the game history.

### Server implementation
- Postgres
   - Vocabulary: store possible words and corresponding length
      - pre-defined 14,855 5-letter words.
      - for checking if a guess is a valid English word
      - for selecting answer candidates
   - User: store username
      - (not implemented) show user statistics
   - Game:
      - for getting game settings(eg.maximum allowed attampts, selected answer candidates, game status...)
      - for getting game history by id
   - GameHistory: store game history
      - for getting game history and resume game progress

- API server
   - framework: fastapi
   - api input validation: pydantic
   - logging: fastapi's middleware, store in `server/logs`
   - ORM: sqlachemly
   - DB migration: alembic
      - add db version by `alembic revision -m "some_msg"`
      - automatically run migration when server start

### Client implementation
- Web server framework: fastapi
- UI: primitive control by javascript and css
