import logging
import random

from config import Hint

log = logging.getLogger(__name__)


def compare_two_words(word: str, ref: str) -> list[str, int]:
    hint = ""
    score = 0
    for i in range(len(word)):
        if word[i] == ref[i]:
            hint += Hint.HIT.value
            score += 10
        elif word[i] in ref:
            hint += Hint.PRESENT.value
            score += 1
        else:
            hint += Hint.MISS.value
    return hint, score


def get_highest_words(word: str, candidates: list[str]) -> list[list[str], list[str]]:
    highest = []
    highest_score = 0
    highest_hint = []
    for candidate in candidates:
        hint, score = compare_two_words(word, candidate)
        log.debug(f"{word=} {candidate=}, {hint=}, {score=}")
        print(f"{word=} {candidate=}, {hint=}, {score=}")
        if score > highest_score:
            highest = [candidate]
            highest_score = score
            highest_hint = [hint]
        elif score == highest_score:
            highest.append(candidate)
            highest_hint.append(hint)
    return highest, highest_hint


def filter_candidates(word: str, hint: str, candidates: list[str]) -> list[str]:
    update = list(candidates)
    if word in update:
        update.remove(word)

    drop = set()
    for candidate in update:
        for idx, h in enumerate(hint):
            if h == Hint.HIT.value and word[idx] in candidate:
                drop.add(candidate)
                break

    for d in drop:
        update.remove(d)
    log.debug(f"{drop=} {update=}")
    return update


def filter_by_history(word: str, hint: str, candidates: list[str]) -> list[str]:
    update = list(candidates)
    if word in update:
        update.remove(word)

    drop = set()
    for candidate in update:
        for idx, h in enumerate(hint):
            if h == Hint.MISS.value and word[idx] in candidate:
                drop.add(candidate)
            elif h == Hint.PRESENT.value and word[idx] in candidate[idx]:
                drop.add(candidate)

    for d in drop:
        update.remove(d)
    log.debug(f"filter_by_history: {drop=} {update=}")
    return update


def get_lowest_words(guess, words_list) -> list[list[str], list[str]]:
    lowest = []
    lowest_score = 1000
    lowest_hint = []
    for word in words_list:
        hint, score = compare_two_words(guess, word)
        if score < lowest_score:
            lowest = [word]
            lowest_score = score
            lowest_hint = [hint]
        elif score == lowest_score:
            lowest.append(word)
            lowest_hint.append(hint)
    return lowest, lowest_hint


if __name__ == "__main__":
    words_list = ["hello", "world", "quite", "fancy", "fresh", "panic", "crazy", "buggy", "scare"]
    extra_words = ["mouse", "guess", "apply", "apple", "orange", "grape", "melon", "lemon", "peach"]
    histories = []

    answer = ""
    for i in range(10):
        print(f"\n{words_list=}")
        print(f"{histories=}")
        guess = input(f"Attempt {i + 1}: ").lower()
        if len(words_list) == 1:
            hint, score = compare_two_words(guess, answer)
            print(f"show hint: {hint=}")
            if hint == Hint.HIT.value * len(answer):
                print(f"Congratulations! You guessed it in {i + 1} attempt(s).")
                break
            continue

        highest, hint = get_highest_words(guess, words_list)

        update = set(words_list)
        for i in range(len(highest)):
            remain = filter_candidates(highest[i], hint[i], words_list)
            update = update.intersection(remain)
        update = list(update)
        print(f"{update=}")

        remainging = set(update)
        for history in histories:
            remain = filter_by_history(history[0], history[1], update)
            remainging = remainging.intersection(remain)
        update = list(remainging)
        print(f"{remainging=}")

        if len(update) > 0:
            words_list = update
        lowest, hints = get_lowest_words(guess, words_list)

        if len(update) == 1:
            answer = update[0]

        if len(update) == 0:
            print(f"All candidates are dropped, {lowest=} {hints=} {words_list=}")
            answer = random.choice(lowest)
            hint = hints[lowest.index(answer)]
            words_list = [answer]
        hint = hints[0]

        histories.append((guess, hint))
        print(f"show hint: {hint=} {answer=}")
