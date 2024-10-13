import { getCookie, setCookie, eraseCookie } from './cookie.js';

let serverPort = window.config.serverPort;
let clientPort = window.config.clientPort;

document.addEventListener("DOMContentLoaded", function () {
    serverPort = window.config.serverPort;
    clientPort = window.config.clientPort;
});

// let "newGame" be a function that is exported from the script.js file
window.newGame = newGame;

const api_base = `http://localhost:${serverPort}`;

let Hint_ENUM = {
    HIT: "0",
    PRESENT: "?",
    MISS: "_"
};

const maxCols = 5;
let maxRows = 6;
let currentRow = 0;
let currentCol = 0;
let currentCellId = 0;
let guess = '';

let id = getCookie("wordle_game");
let user = getCookie("wordle_user");
let gameActive = true;

class NumAttempts {
    constructor() {
        this.numAttempts = document.getElementById("num-attempts");
        this.numAttempts.addEventListener("input", function () {
            maxRows = numAttempts.value;
        });
    }
    getNumAttempts() {
        return this.numAttempts.value;
    }
    setNumAttemptsValue(value) {
        this.numAttempts.value = value;
    }
}
const numAttempts = new NumAttempts();


class Cell {
    static getCell(row, col, offset = 0) {
        let num = row * maxCols + col + offset;
        return document.getElementById("guess-container").rows[Math.floor(num / maxCols)].cells[num % maxCols];
    }
    static getCellNum(row, col) {
        return row * maxCols + col;
    }
}

class GameMode {
    constructor() {
        this.mode = document.getElementById("game-mode").value;

        this.gameMode = document.getElementById("game-mode");
        this.gameMode.addEventListener("change", () => {
            this.mode = this.gameMode.value;
        });
    }
    getGameMode() {
        return this.gameMode.value;
    }
}
const gameMode = new GameMode();
getGameHistory();

// Game control logic
function getGameHistory() {
    if (!id) {
        getNewGame();
        return;
    }

    fetch(api_base + "/v1/game/" + id, {
        method: "GET"
    }).then(response => {
        if (!response.ok) {
            throw new Error(response.status);
        }
        return response.json();
    }).then(game => {
        id = game.id;
        maxRows = game.max_rounds;
        numAttempts.setNumAttemptsValue(maxRows);

        gameActive = game.is_end === false;

        if (game.history === undefined) {
            return;
        }
        createGuessContainer(maxRows, maxCols);
        createKeyboard();

        for (let i = 0; i < game.history.length; i++) {
            const word = game.history[i].word;
            const hint = game.history[i].hint;
            for (let j = 0; j < word.length; j++) {
                const cell = Cell.getCell(i, 0, j);
                cell.textContent = word[j].toUpperCase();
            }
            currentCol = 0;
            currentRow = i;
            currentCellId = currentRow * maxCols;
            updateGuess(hint, word);
        }
        currentCol = 0;
        currentRow = game.num_attempts;
        currentCellId = currentRow * maxCols;

        if (game.is_end) {
            let last_hint = game.history[game.history.length - 1].hint;
            if (last_hint === Hint_ENUM.HIT.repeat(maxCols)) {
                updateGuessMsg("You win!", "green");
            } else {
                updateGuessMsg("Answer: " + game.answer, "grey");
            }
            gameActive = false;
        }
    }).catch(error => {
        if (error.message == 404) {
            eraseCookie("wordle_game");
            eraseCookie("wordle_user");
            id = "";
            user = "";
            getNewGame();
            return;
        }
        console.error("error", error);
        updateGuessMsg(error.message, "red");
        // retry after 1 second
        setTimeout(getGameHistory, 1000);
    });
}

function getNewGame() {
    eraseCookie("wordle_game");
    if (numAttempts.getNumAttempts() < 1) {
        numAttempts.setNumAttemptsValue(maxRows);
    }
    maxRows = numAttempts.getNumAttempts();

    let url = api_base + "/v1/game/new?mode=" + gameMode.getGameMode() + "&num_attempts=" + maxRows;
    if (user) {
        url += "&user_id=" + user;
    }
    fetch(url, {
        method: "GET"
    }).then(response => response.json()).then(game => {
        if (game.id) {
            setCookie("wordle_game", game.id, 1);
            setCookie("wordle_user", game.user_id, 7);
            id = game.id;
            user = game.user_id;
        }
    });
    createGuessContainer(maxRows, maxCols);
    createKeyboard();
}

function newGame() {
    currentRow = 0;
    currentCol = 0;
    currentCellId = 0;
    guess = '';
    gameActive = true;

    getNewGame();
    const guessMsg = document.getElementById('guess-msg');
    guessMsg.textContent = ' ';

    createGuessContainer(maxRows, maxCols);
    createKeyboard();
}


// Draw the guess container
function createGuessContainer(rows, cols) {
    document.getElementById("guess-container").innerHTML = '';
    const table = document.getElementById("guess-container");

    for (let i = 0; i < rows; i++) {
        const row = document.createElement("tr");

        for (let j = 0; j < cols; j++) {
            const cell = document.createElement("td");
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
}

// Draw the keyboard
function createKeyboard() {
    document.getElementById("keyboard").innerHTML = '';
    const keyboardRows = [
        ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['ENTER', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '⌫']
    ];
    const keyboard = document.getElementById('keyboard');
    keyboardRows.forEach(rowKeys => {
        const row = document.createElement('div');
        row.classList.add('row');

        rowKeys.forEach(key => {
            const keyElement = document.createElement('div');
            keyElement.classList.add('key');
            keyElement.id = 'key-' + key;
            keyElement.textContent = key;
            if (key === 'ENTER') {
                keyElement.classList.add('enter');
            } else if (key === '⌫') {
                keyElement.classList.add('backspace');
            } else {
                keyElement.classList.add(key);
            }

            keyElement.addEventListener('click', () => {
                if (!gameActive) {
                    return;
                }
                clearGuessMsg();
                if (key === 'ENTER') {
                    checkGuess();
                } else if (key === '⌫') {
                    deleteLetter();
                } else {
                    insertLetter(key);
                }
            });
            row.appendChild(keyElement);
        });
        keyboard.appendChild(row);
    });
}

// Game's keyboard control logic
function insertLetter(letter) {
    if (currentCol >= maxCols) {
        return
    }
    if (Cell.getCellNum(currentRow, currentCol) < maxCols * maxRows) {
        const currentCell = Cell.getCell(currentRow, currentCol);
        currentCell.textContent = letter;
        currentCellId++;
        currentCol++;
        guess += letter;
    }
}

function deleteLetter() {
    if (currentCol <= 0) {
        return;
    }
    if (currentCellId > 0) {
        currentCellId--;
        currentCol--;
        const currentCell = Cell.getCell(currentRow, currentCol);
        currentCell.textContent = " ";
        guess = guess.slice(0, -1);
    }
}

function updateGuess(hint, word) {
    if (currentRow >= maxRows) {
        return;
    }

    for (let i = 0; i < maxCols; i++) {
        let h = hint[i];
        const cell = Cell.getCell(currentRow, 0, i);
        let w = word[i].toUpperCase();
        const key = document.getElementById("key-" + w);

        cell.style.color = "white";
        if (h === Hint_ENUM.HIT) {
            cell.style.backgroundColor = "green";
            key.style.backgroundColor = "green";
        } else if (h === Hint_ENUM.PRESENT) {
            cell.style.backgroundColor = "orange";
            if (key.style.backgroundColor !== "green") {
                key.style.backgroundColor = "orange";
            }
        } else {
            cell.style.backgroundColor = "grey";
            if (key.style.backgroundColor === "white") {
                key.style.backgroundColor = "grey";
            }
        }
    }
}

function submitGuess() {
    if (guess.length === 0 || guess.length !== maxCols) {
        return;
    }

    fetch(api_base + "/v1/game/submit?id=" + id + "&guess=" + guess, {
        method: "GET",
    }).then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {

                throw new Error(errorData.detail || "Unknown error");
            });
        }
        return response.json();
    }).then(data => {
        if (data.hint == Hint_ENUM.HIT.repeat(maxCols)) {
            updateGuessMsg("You win!", "green");
            gameActive = false;
        } else if (currentRow >= maxRows - 1) {
            updateGuessMsg("Answer: " + data.answer, "grey");
            gameActive = false;
        }

        updateGuess(data.hint, guess);
        currentRow++;
        currentCol = 0;
        guess = "";
    }).catch(error => {
        console.error("error", error);
        updateGuessMsg(error.message, "red");
    });
}

// Modify the guess message
function updateGuessMsg(msg, color) {
    const guessMsg = document.getElementById("guess-msg");
    guessMsg.textContent = msg;
    guessMsg.style.color = color;
}
function clearGuessMsg() {
    const guessMsg = document.getElementById('guess-msg');
    guessMsg.textContent = ' ';
}



// Capture keyboard input
document.addEventListener("keydown", function (event) {
    if (!gameActive) {
        return;
    }
    if (document.activeElement.tagName === "INPUT") {
        return;
    }
    clearGuessMsg();

    const key = event.key.toUpperCase();

    if (key === "BACKSPACE" || key === "DELETE") {
        event.preventDefault();
        deleteLetter();
    } else if (key.length === 1 && key >= "A" && key <= "Z") {
        insertLetter(key);
    } else if (key === "ENTER") {
        event.preventDefault();
        if (guess.length !== maxCols) {
            updateGuessMsg("Not enough letters", "black");
            return;
        }
        submitGuess();
    } else {
        console.log("Invalid key pressed");
    }
});
