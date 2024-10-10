import enum
import random

WORDS = ["HELLO", "WORLD", "QUITE", "FANCY", "FRESH", "PANIC", "CRAZY", "BUGGY"]
MAX_ATTEMPTS = 6
LEN_WORD = 5


class Hint(enum.Enum):
    HIT = "0"
    PRESENT = "?"
    MISS = "_"


def main():
    secret_word = random.choice(WORDS)
    print("Welcome to Wordle!")
    print("Try to guess a five-letter word in 6 attempts.")

    attempt = 0
    while attempt < MAX_ATTEMPTS:
        guess = input(f"Attempt {attempt + 1}: ").upper()

        if len(guess) != LEN_WORD:
            print("Please enter a five-letter word.")
            continue

        hint = ""
        for i in range(LEN_WORD):
            if guess[i] == secret_word[i]:
                hint += Hint.HIT.value
            elif guess[i] in secret_word:
                hint += Hint.PRESENT.value
            else:
                hint += Hint.MISS.value
        print(hint)

        if hint == Hint.HIT.value * LEN_WORD:
            print(f"Congratulations! You guessed it in {attempt + 1} attempt(s).")
            return

        attempt += 1
    print(f"Sorry, you didn't guess it. The word was {secret_word}.")


if __name__ == "__main__":
    main()
