
let serverPort = window.config.serverPort;
let clientPort = window.config.clientPort;

document.addEventListener("DOMContentLoaded", function () {
    serverPort = window.config.serverPort;
    clientPort = window.config.clientPort;
});

const api_base = `http://localhost:${serverPort}`;

let Hint_ENUM = {
    HIT: "0",
    PRESENT: "?",
    MISS: "_"
};

const maxCols = 5;
const maxRows = 6;
let currentRow = 0;
let currentCol = 0;
let currentCellId = 0;
let guess = '';

let id = getCookie("wordle_game");
let gameActive = true;

getGame();
createGuessContainer(maxRows, maxCols);
createKeyboard();

function getGame() {
    if (!id) {
        return;
    }
    fetch(api_base + "/v1/game/" + id, {
        method: "GET"
    }).then(response => response.json()).then(game => {
        id = game.id;

        gameActive = game.is_end === false;

        if (game.history === undefined) {
            return;
        }
        for (let i = 0; i < game.history.length; i++) {
            const word = game.history[i].word;
            const hint = game.history[i].hint;
            for (let j = 0; j < word.length; j++) {
                const cell = getCellByNum(i * maxCols + j);
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
        if (currentRow >= maxRows) {
            updateGuessMsg("Answer: " + game.answer, "grey");
            gameActive = false;
        }
    }).catch(error => {
        console.error("error", error);
        updateGuessMsg(error.message, "red");
    });
}


function getNewGame() {
    eraseCookie("wordle_game");

    fetch(api_base + "/v1/game/new", {
        method: "GET"
    }).then(response => response.json()).then(game => {
        if (game.id) {
            setCookie("wordle_game", game.id, 1);
            id = game.id;
        }
    });
}


function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));  // Convert days to milliseconds
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

function eraseCookie(name) {
    document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
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
    document.getElementById("guess-container").innerHTML = '';
    document.getElementById("keyboard").innerHTML = '';
    createGuessContainer(maxRows, maxCols);
    createKeyboard();
}


function createGuessContainer(rows, cols) {
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

function createKeyboard() {
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



function getCellByNum(num) {
    return document.getElementById("guess-container").rows[Math.floor(num / maxCols)].cells[num % maxCols];
}

function insertLetter(letter) {
    if (currentCol >= maxCols) {
        return
    }
    if (currentCellId < maxCols * maxRows) {
        const currentCell = getCellByNum(currentCellId);
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
        const currentCell = getCellByNum(currentCellId);
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
        const cell = getCellByNum(currentRow * maxCols + i);
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
function clearGuessMsg() {
    const guessMsg = document.getElementById('guess-msg');
    guessMsg.textContent = ' ';
}

// Capture keyboard input
document.addEventListener("keydown", function (event) {
    if (!gameActive) {
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
        submitGuess();
    } else {
        console.log("Invalid key pressed");
    }
});

function updateGuessMsg(msg, color) {
    const guessMsg = document.getElementById("guess-msg");
    guessMsg.textContent = msg;
    guessMsg.style.color = color;
}

