import enum
import logging
from uuid import UUID

from config import DEFAULT_LEN_WORD, DEFAULT_MAX_ATTEMPTS  # noqa
from fastapi import APIRouter, Depends, HTTPException
from models.game import Game as GameModel
from models.game_history import GameHistory
from models.session import get_db_session
from models.user import User as UserModel
from models.vocab import Vocabulary as VocabModel
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger(__name__)

router = APIRouter(prefix="/game")


class Hint(enum.Enum):
    HIT = "0"
    PRESENT = "?"
    MISS = "_"


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


words_list = ["hello", "world", "quite", "fancy", "fresh", "panic", "crazy", "buggy"]


def check_guess(guess: str, answer: str) -> str:
    hint = ""
    for i in range(len(answer)):
        if answer[i] == guess[i]:
            hint += Hint.HIT.value
        elif guess[i] in answer:
            hint += Hint.PRESENT.value
        else:
            hint += Hint.MISS.value
    return hint


@router.get("/new", response_model=NewGameResp)
async def new_game(user_id: str | None = None, db: AsyncSession = Depends(get_db_session)):
    if not user_id:
        user = await UserModel.create(db)
    else:
        user = await UserModel.get(db, user_id)

    # vocab = await VocabModel.get_random_word(db, DEFAULT_LEN_WORD)
    # word = vocab.word
    word = VocabModel.get_random_word_from_list(words_list)  # for testing
    game = await GameModel.create(db, user_id=user.id, answer=word, max_rounds=DEFAULT_MAX_ATTEMPTS)
    log.info(f"New game created: {game}")
    return game


@router.get("/submit", response_model=GuessResp)
async def submit_guess(
    id: str,
    guess: str,
    db: AsyncSession = Depends(get_db_session),
):
    guess = guess.lower()
    game = await GameModel.get(db, id)
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.num_attempts >= game.max_rounds or game.is_end:
        raise HTTPException(status_code=400, detail="Game is over")

    if len(guess) != len(game.answer):
        raise HTTPException(status_code=400, detail="Invalid guess length")

    vocab = await VocabModel.get(db, guess)
    if vocab is None:
        raise HTTPException(status_code=400, detail="Not a valid word")

    history = GameHistory(game_id=game.id, word=guess, answer=game.answer)

    hint = check_guess(guess=guess, answer=game.answer)

    history.hit_count = hint.count(Hint.HIT.value)
    history.present_count = hint.count(Hint.PRESENT.value)
    history.miss_count = hint.count(Hint.MISS.value)

    answer = ""
    if hint == Hint.HIT.value * len(game.answer):
        game.is_end = True
        answer = game.answer
    if not game.is_end:
        game.num_attempts += 1
        if game.num_attempts >= game.max_rounds:
            game.is_end = True
            answer = game.answer

    await db.commit()
    await history.insert(db)

    return GuessResp(
        id=game.id,
        user_id=game.user_id,
        max_rounds=game.max_rounds,
        num_attempts=game.num_attempts,
        is_end=game.is_end,
        hint=hint,
        answer=answer,
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
        history_list.append(
            GameHistoryItem(word=h.word, hint=check_guess(guess=h.word, answer=h.answer))
        )
    game_dict = game.__dict__
    if game.is_end:
        game_dict["answer"] = game.answer

    return GetGameHistoryResp(
        **game_dict,
        history=history_list,
    )
