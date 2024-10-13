from game_guess import (
    Hint,
    compare_two_words,
    filter_by_history,
    filter_candidates,
    get_highest_words,
    get_lowest_words,
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
