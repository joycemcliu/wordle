import logging
import random
from uuid import UUID

from config import DEFAULT_LEN_WORD, DEFAULT_MAX_ATTEMPTS, DEFAULT_WORD_LIST, ENV  # noqa
from fastapi import APIRouter, Depends, HTTPException
from models.game import Game as GameModel
from models.game_history import GameHistory
from models.session import get_db_session
from models.user import User as UserModel
from models.vocab import Vocabulary as VocabModel
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.game_guess import (  # noqa
    Hint,
    compare_two_words,
    filter_candidates,
    get_highest_word,
    get_lowest_words,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/game")


class NewGameResp(BaseModel):
    id: UUID
    user_id: UUID
    max_rounds: int
    num_attempts: int
    is_end: bool

    class Config:
        orm_mode = True  # Allows Pydantic to work with SQLAlchemy models


class GuessResp(NewGameResp):
    is_end: bool
    hint: str
    answer: str = ""

    class Config:
        orm_mode = True


class GameHistoryItem(BaseModel):
    word: str
    hint: str

    class Config:
        orm_mode = True


class GetGameHistoryResp(NewGameResp):
    answer: str = ""
    history: list[GameHistoryItem] = []


@router.get("/new", response_model=NewGameResp)
async def new_game(
    user_id: str | None = None,
    num_attempts: int | None = None,
    mode: str = "hard",
    db: AsyncSession = Depends(get_db_session),
):
    if not user_id:
        user = await UserModel.create(db)
    else:
        user = await UserModel.get(db, user_id)

    if not num_attempts or num_attempts < 1:
        num_attempts = DEFAULT_MAX_ATTEMPTS

    if mode != "hard":
        # Get Single word
        vocab = await VocabModel.get_random_word(db, DEFAULT_LEN_WORD)
        candidates = vocab.word
        # for development testing
        if ENV == "dev":
            candidates = VocabModel.get_random_word_from_list(DEFAULT_WORD_LIST)
    else:
        # Get multiple words
        words = await VocabModel.get_random_words(db, DEFAULT_LEN_WORD, max(num_attempts - 2, 5))
        candidates = ",".join([w.word for w in words])
        # for development testing
        if ENV == "dev":
            candidates = ",".join(DEFAULT_WORD_LIST)

    log.debug(f"{candidates=}")
    game = await GameModel.create(db, user_id=user.id, answer=candidates, max_rounds=num_attempts)
    log.info(f"New game created: {game}")
    return game


@router.get("/submit", response_model=GuessResp)
async def submit_guess(
    id: str,
    guess: str,
    db: AsyncSession = Depends(get_db_session),
):
    # Validate guess and game status
    guess = guess.lower()
    game = await GameModel.get(db, id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.num_attempts >= game.max_rounds or game.is_end:
        raise HTTPException(status_code=400, detail="Game is over")

    vocab = await VocabModel.get(db, guess)
    if vocab is None:
        raise HTTPException(status_code=400, detail="Not a valid word")

    history = await GameHistory.get_by_game_id(db, game.id)
    last_history = history[-1] if history else None
    candidates = []
    if last_history is None:
        candidates: list[str] = game.answer.split(",")
    else:
        candidates: list[str] = last_history.answer.split(",")
    log.debug(f"current: {candidates=}")

    if len(guess) != len(candidates[0]):
        raise HTTPException(status_code=400, detail="Invalid guess length")

    hint = ""
    # Not update candidates if the guess is already in the history
    for h in history:
        if guess == h.word:
            log.debug(f"Found guess in history: {h}")
            hint = h.hint
            break

    # Compare guess with answer
    if hint == "":
        if len(candidates) == 1:
            # Normal wordle game comparison
            hint, _ = compare_two_words(word=guess, ref=candidates[0])
        else:
            highest, hint = get_highest_word(guess, candidates)
            update = filter_candidates(highest, hint, candidates)
            if len(update) > 0:
                candidates = update
            lowest, hints = get_lowest_words(guess, candidates)
            hint = hints[0]
            if len(lowest) > 1:
                answer = random.choice(lowest)
                hint = hints[lowest.index(answer)]
                candidates = [answer]

    # Update game status
    history = GameHistory(game_id=game.id, word=guess, answer=",".join(candidates))
    history.hint = hint
    history.hit_count = hint.count(Hint.HIT.value)
    history.present_count = hint.count(Hint.PRESENT.value)
    history.miss_count = hint.count(Hint.MISS.value)

    answer_to_player = ""
    if hint == Hint.HIT.value * len(candidates[0]):
        game.is_end = True
        answer_to_player = candidates[0]

    if not game.is_end:
        game.num_attempts += 1
        if game.num_attempts >= game.max_rounds:
            game.is_end = True
            answer_to_player = random.choice(candidates)

    history.answer = ",".join(candidates)
    await db.commit()
    await history.insert(db)

    return GuessResp(
        id=game.id,
        user_id=game.user_id,
        max_rounds=game.max_rounds,
        num_attempts=game.num_attempts,
        is_end=game.is_end,
        hint=hint,
        answer=answer_to_player,
    )


@router.get("/{id}", response_model=GetGameHistoryResp)
async def get_game(
    id: str,
    db: AsyncSession = Depends(get_db_session),
):
    game = await GameModel.get(db, id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    history = await GameHistory.get_by_game_id(db, game.id)
    if history is None:
        history = GameHistory(game_id=game.id, word=game.answer, answer="")

    history_list = []
    for h in history:
        history_list.append(GameHistoryItem(word=h.word, hint=h.hint))

    # Not display answer if game is not ended
    game_dict = game.__dict__
    game_dict.pop("answer")
    if game.is_end:
        answer = history[-1].answer
        if "," in answer:
            answer = random.choice(answer.split(","))
        game_dict["answer"] = history[-1].answer

    return GetGameHistoryResp(
        **game_dict,
        history=history_list,
    )
