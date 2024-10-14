from game_guess import (
    Hint,
    compare_two_words,
    filter_by_history,
    filter_candidates,
    get_highest_words,
    get_lowest_words,
    update_candidate_by_host_cheating_rule,
)


# Test compare_two_words function
def test_compare_two_words():
    word = "hello"
    ref = "hills"
    expected_hint = (
        Hint.HIT.value + Hint.MISS.value + Hint.HIT.value + Hint.HIT.value + Hint.MISS.value
    )
    expected_score = 30

    hint, score = compare_two_words(word=word, ref=ref)

    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert score == expected_score, f"Expected {expected_score}, but got {score}"


# Test compare_two_words function with no match
def test_compare_two_words_no_match():
    word = "world"
    ref = "guess"
    expected_hint = Hint.MISS.value * len(word)
    expected_score = 0  # No match at all

    hint, score = compare_two_words(word, ref)

    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert score == expected_score, f"Expected {expected_score}, but got {score}"


# Test get_highest_word function
def test_get_highest_word():
    word = "world"
    candidates = ["fancy", "panic", "crazy", "buggy"]
    expected_highest = ["crazy"]
    expected_hint = [
        Hint.MISS.value + Hint.MISS.value + Hint.PRESENT.value + Hint.MISS.value + Hint.MISS.value
    ]

    highest, hint = get_highest_words(word, candidates)

    assert highest == expected_highest, f"Expected {expected_highest}, but got {highest}"
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"


# Test filter_candidates function
def test_filter_candidates():
    word = "crazy"
    hint = (
        Hint.MISS.value + Hint.MISS.value + Hint.PRESENT.value + Hint.MISS.value + Hint.MISS.value
    )
    candidates = ["fancy", "panic", "crazy", "buggy"]
    expected_candidates = ["fancy", "panic", "buggy"]

    filtered_candidates = filter_candidates(word, hint, candidates)

    assert (
        filtered_candidates == expected_candidates
    ), f"Expected {expected_candidates}, but got {filtered_candidates}"


# Test get_lowest_words function
def test_get_lowest_words():
    guess = "scare"
    words_list = ["hello", "world", "fresh", "panic", "scare"]
    expected_lowest = ["hello", "world"]
    expected_hint = [
        Hint.MISS.value + Hint.MISS.value + Hint.MISS.value + Hint.MISS.value + Hint.PRESENT.value,
        Hint.MISS.value + Hint.MISS.value + Hint.MISS.value + Hint.PRESENT.value + Hint.MISS.value,
    ]

    lowest, lowest_hint = get_lowest_words(guess, words_list)

    assert lowest == expected_lowest, f"Expected {expected_lowest}, but got {lowest}"
    assert lowest_hint == expected_hint, f"Expected {expected_hint}, but got {lowest_hint}"


def test_filter_by_history_removes_word():
    word = "apple"
    hint = Hint.MISS.value * len(word)
    candidates = ["apple", "banana", "cherry", "buggy"]
    expected_candidates = ["buggy"]

    filtered_candidates = filter_by_history(word, hint, candidates)
    assert (
        filtered_candidates == expected_candidates
    ), f"Expected {expected_candidates}, but got {filtered_candidates}"


def test_filter_by_history_removes_word2():
    word = "apple"
    hint = Hint.MISS.value * len(word)
    candidates = ["buggy", "foggy", "crazy", "daisy"]
    expected_candidates = ["buggy", "foggy"]

    filtered_candidates = filter_by_history(word, hint, candidates)
    assert (
        filtered_candidates == expected_candidates
    ), f"Expected {expected_candidates}, but got {filtered_candidates}"


def test_filter_by_history_removes_word3():
    word = "apple"
    hint = Hint.MISS.value + Hint.MISS.value + Hint.PRESENT.value + Hint.MISS.value + Hint.HIT.value
    candidates = ["buggy", "foggy", "crazy", "daisy", "apple", "ahead"]
    expected_candidates = ["buggy", "foggy"]

    filtered_candidates = filter_by_history(word, hint, candidates)
    assert (
        filtered_candidates == expected_candidates
    ), f"Expected {expected_candidates}, but got {filtered_candidates}"


class MockHistoryRecord:
    def __init__(self, word: str, hint: str):
        self.word = word
        self.hint = hint


def test_guess_in_history():
    history = [MockHistoryRecord(word="hello", hint=Hint.MISS.value * 5)]
    guess = "world"
    candidates = ["fancy", "panic", "crazy", "buggy"]
    expected_hint = Hint.MISS.value * 5
    expected_candidates = ["fancy", "panic", "buggy"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history2():
    history = [
        MockHistoryRecord(word="hello", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="world", hint=Hint.MISS.value * 5),
    ]
    guess = "fresh"
    candidates = ["fancy", "panic", "buggy"]
    expected_hint = Hint.MISS.value * 5
    expected_candidates = ["panic", "buggy"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history3():
    history = [
        MockHistoryRecord(word="hello", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="world", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="fresh", hint=Hint.MISS.value * 5),
    ]
    guess = "crazy"
    candidates = ["panic", "buggy"]
    expected_hint = f"{Hint.PRESENT.value}{Hint.MISS.value}{Hint.PRESENT.value}{Hint.MISS.value}{Hint.MISS.value}"
    expected_candidates = ["panic"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history4():
    history = [
        MockHistoryRecord(word="hello", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="world", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="fresh", hint=Hint.MISS.value * 5),
        MockHistoryRecord(
            word="crazy",
            hint=f"{Hint.PRESENT.value}{Hint.MISS.value}{Hint.PRESENT.value}{Hint.MISS.value}{Hint.MISS.value}",
        ),
    ]
    guess = "quite"
    candidates = ["panic"]
    expected_hint = (
        f"{Hint.MISS.value}{Hint.MISS.value}{Hint.PRESENT.value}{Hint.MISS.value}{Hint.MISS.value}"
    )
    expected_candidates = ["panic"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history5():
    history = [
        MockHistoryRecord(word="hello", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="world", hint=Hint.MISS.value * 5),
        MockHistoryRecord(word="fresh", hint=Hint.MISS.value * 5),
        MockHistoryRecord(
            word="crazy",
            hint=f"{Hint.PRESENT.value}{Hint.MISS.value}{Hint.PRESENT.value}{Hint.MISS.value}{Hint.MISS.value}",
        ),
        MockHistoryRecord(
            word="quite",
            hint=f"{Hint.MISS.value}{Hint.MISS.value}{Hint.PRESENT.value}{Hint.MISS.value}{Hint.MISS.value}",
        ),
    ]
    guess = "fancy"
    candidates = ["panic"]
    expected_hint = (
        f"{Hint.MISS.value}{Hint.HIT.value}{Hint.HIT.value}{Hint.PRESENT.value}{Hint.MISS.value}"
    )
    expected_candidates = ["panic"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history6():
    history = []
    guess = "buggy"
    candidates = ["hello", "world", "quite", "fancy", "fresh", "panic", "crazy", "buggy", "scare"]
    expected_hint = Hint.MISS.value * 5
    expected_candidates = ["hello", "world", "fresh", "panic", "scare"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint == expected_hint, f"Expected {expected_hint}, but got {hint}"
    assert set(remaining_candidates) == set(
        expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"


def test_guess_in_history7():
    history = [
        MockHistoryRecord(word="buggy", hint=Hint.MISS.value * 5),
    ]
    guess = "scare"
    candidates = ["hello", "world", "fresh", "panic", "scare"]
    expected_hints = [
        Hint.MISS.value * 4 + Hint.PRESENT.value,
        Hint.MISS.value * 3 + Hint.PRESENT.value + Hint.MISS.value,
    ]
    expected_candidates = ["hello", "world"]

    hint, remaining_candidates = update_candidate_by_host_cheating_rule(history, guess, candidates)
    assert hint in expected_hints, f"Expected one of {expected_hints}, but got {hint}"
    assert (
        remaining_candidates[0] in expected_candidates
    ), f"Expected {expected_candidates}, but got {remaining_candidates}"
