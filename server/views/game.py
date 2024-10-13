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
    filter_by_history,
    filter_candidates,
    get_highest_words,
    get_lowest_words,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/game", tags=["game"])


class NewGameResp(BaseModel):
    id: UUID
    user_id: UUID
    max_rounds: int
    num_attempts: int
    word_length: int
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


class NewGameReq(BaseModel):
    user_id: str | None = None
    num_attempts: int | None = None
    word_length: int | None = None
    mode: str = "hard"


class GetGameHistoryResp(NewGameResp):
    answer: str = ""
    history: list[GameHistoryItem] = []


@router.get("/word_lengths")
async def get_all_word_lengths(
    db: AsyncSession = Depends(get_db_session),
) -> list[int]:
    if ENV in ["demo", "dev"]:
        return [DEFAULT_LEN_WORD]
    return await VocabModel.get_all_word_lengths(db)


@router.get("/new", response_model=NewGameResp)
async def new_game(
    req: NewGameReq = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    if not req.user_id:
        user = await UserModel.create(db)
    else:
        user = await UserModel.get(db, req.user_id)
        if user is None:
            user = await UserModel.create(db, id=req.user_id)

    if not req.num_attempts or req.num_attempts < 1:
        req.num_attempts = DEFAULT_MAX_ATTEMPTS

    if not req.word_length or req.word_length < 1:
        req.word_length = DEFAULT_LEN_WORD

    if req.mode != "hard":
        # Get a single word
        vocab = await VocabModel.get_random_word(db, req.word_length)
        candidates = [vocab.word] if vocab else []

        # for demo and testing
        if ENV in ["demo", "dev"]:
            candidates = [VocabModel.get_random_word_from_list(DEFAULT_WORD_LIST)]
    else:
        # Get multiple words
        words = await VocabModel.get_random_words(db, req.word_length, max(req.num_attempts - 2, 5))
        candidates = [w.word for w in words]

        # for demo and testing
        if ENV in ["demo", "dev"]:
            candidates = list(DEFAULT_WORD_LIST)

    log.debug(f"{candidates=}")
    if not candidates or len(candidates[0]) != req.word_length:
        raise HTTPException(status_code=500, detail="No words found")

    candidates = ",".join(candidates)
    game = await GameModel.create(
        db,
        user_id=user.id,
        answer=candidates,
        max_rounds=req.num_attempts,
        word_length=req.word_length,
    )
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
    log.debug(f"current: {candidates=} {guess=}")

    if len(guess) != len(candidates[0]):
        raise HTTPException(status_code=400, detail="Invalid guess length")

    hint = ""
    # Enhance host cheating wordle difficulty by
    # not update candidates if the guess is already in the history
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
            # Filter candidates by history
            # ensure the candidation not violate the history
            update = set(candidates)
            for record in history:
                remain = filter_by_history(record.word, record.hint, update)
                update = update.intersection(remain)
            candidates = list(update)
            log.debug(f"history: {update=}")

            if len(candidates) > 1:
                # Filter candidates by highest score words
                highest, hint = get_highest_words(guess, candidates)
                update = set(candidates)
                for i in range(len(highest)):
                    remain = filter_candidates(highest[i], hint[i], update)
                    update = update.intersection(remain)
                update = list(update)
                log.debug(f"highest: {update=}")

                if len(update) > 0:
                    candidates = update
                else:
                    update = list(candidates)
                    [update.remove(h) for h in highest]
                    lowest, _ = get_lowest_words(guess, update)
                    log.debug(f"lowest: {lowest=}")
                    candidates = [random.choice(lowest)]
                log.debug(f"remaining: {candidates=}")

            log.debug(f"final candidates: {candidates=}")
            if len(candidates) == 1:
                hint, _ = compare_two_words(word=guess, ref=candidates[0])
            else:
                # update hint
                hint = list(Hint.MISS.value * len(guess))
                for i in range(len(guess)):
                    w = guess[i]
                    # if all candidates have the same letter, then it's a PRESENT
                    log.debug(f"check {w=} {all(w in c for c in candidates)=}")
                    if all(w in c for c in candidates):
                        hint[i] = Hint.PRESENT.value
                hint = "".join(hint)
            log.debug(f"update hint: {hint=}")

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
        word_length=game.word_length,
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
