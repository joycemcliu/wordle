# Wordle
This repo implemented task 1-3. [details](#Task-fulfilment)

The Wordle game is a puzzle where a player have six attempts to guess a 5-letter word, receiving feedback on correct letters and their positions after each guess.

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

## Service config
Mainly control by the values in `.env`:
```sh
# Control the environment of the application
# demo: words is selected from default word list
# dev: Extend demo env with reload server and client on file save
# <other>: words is selected from db and without reload on save feature
ENV=demo

# postgres setting
POSTGRES_DB=wordle
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres-pw
POSTGRES_PORT=35432

# service expose port
SERVER_PORT=8710
CLIENT_PORT=8711

# override server's default word list
# if empty then will use the default word list
WORD_LIST=hello
```

## Running the service
### For demo
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
PYTHONPATH=server pytest -v
```






# Task fulfilment
## Task1 - Normal wordle
- Play Normal wordle by selecting `normal` on "Mode" dropdown in page and then start by clicking "New Game" button
- Default maximum attampts is 6
- Default word length is 5
- Case-insensitive guess

Flow:
```
loop until either player guess correctly or on a allowed rounds:
   1. player submits a 5-letter word as a guess
   2. host checks the guess is a valid English word in case-insensitive
   3. host shows hint to player
```

## Task2 - Server/client wordle
### Server side
Server side is as a host of the game to responsible on:
- select the answer(or word candidates) at the begining of the game
- check player guess
   - whether is a valid english word
   - whether is invalid word length
- provide hint to client
- won't provide answer unless the game is over
- store game records(eg. player guesses history, hint of each guess, etc.)

Which is implemented on `./server` as an API server with componments:
   - Postgres: db named as `wordle` and has table with corresponding usage:
      - `Vocabulary`: store possible words and corresponding length
         - pre-defined 14,855 5-letter words.
         - for checking if a guess is a valid English word
         - for selecting answer candidates
      - `User`: store username
         - (not implemented) show user statistics
      - `Game`:
         - for getting game settings(eg.maximum allowed attampts, selected answer candidates, game status...)
         - for getting game history by id
      - `GameHistory`: store game history
         - for getting game history and resume game progress
   - API server
      - framework: fastapi
      - api input validation: pydantic
      - logging: fastapi's middleware, store in `server/logs`
      - ORM: sqlachemly
      - DB migration: alembic
         - add db version by `alembic revision -m "some_msg"` and modify the created file contents
         - automatically run migration when server start
      - python linter and formatter: ruff
### Client side
Which is implemented on `./client`, provides service to player by:
   - Web server: provide static websites
      - framework: fastapi
   - UI:
      - using primitive control by javascript and css
      - san start a new game by a button.
      - support inputting keystore by keyboard.
      - show hints in different color: green="HIT", orange="PRESENT", grey="MISS".
      - show hints on vitural keyboard in different color.
      - show guess message when submitting
      - reload page still keep the game history.
      - support selecting `normal` or `hard` mode in a dropdown.
      - adjustable number of attemps. (client restriction: min=1, max=20).

## Task 3 - Host cheaing wordle
Host cheating wordle can be played by selecting `hard` on "Mode" dropdown in page and then start by clicking "New Game" button.

Server handle logic: (refer to `./server/views/game.py`'s `submit_guess()` )
1. select a list of words(named `candidates`) by:
   - (`ENV=dev/demo`) default list: [hello,world,quite,fancy,fresh,panic,crazy,buggy,scare]) or
   - (`ENV!=dev/demo`) random pick `max(5, num_of_attempts_player_selected - 2)` words from db(ie. `Vocabulary` table)
2. received player guess and update `candidates` by:
   1. if guess appear previous -> return previous hint
   1. get the highest score words and corresponding hints in `candidates`
   2. filter out highest score words from `candidates`
   3. filter out words from `candidates` that violate highest score words and hints
   4. filter out words from `candidates` that violate previous hints
   5. update `candidates` by:
      - if the remaining `candidates` is empty, then pick a new valid word from db
      - if the remaining `candidates` is =1, then pick that word as answer
      - if the remaining `candidates` is >1, then find the lowest score words and hints
         - if Num_of(lowest score words) > 1, then random pick one
   6. return hint
