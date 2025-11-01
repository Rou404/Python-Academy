"""
FastAPI backend orchestrating the computer-vision rock/paper/scissors demo.

This version keeps a shared MediaPipe pipeline running so the React UI can
stream a live camera preview at all times while the backend aggregates gesture
and expression predictions for gameplay and teaching commentary.
"""

from __future__ import annotations

import json
import logging
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from vision_monitor import monitor

TOTAL_ROUNDS = 3
MOVES = ("rock", "paper", "scissors")

BASE_DIR = Path(__file__).resolve().parent
LOG_PATH = BASE_DIR / "logs" / "game_history.json"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "logs" / "backend.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("cv_rps_app")


class StartSessionRequest(BaseModel):
    player_name: str | None = Field(default=None, description="Optional label used in the log")


class SessionStartResponse(BaseModel):
    session_id: str
    total_rounds: int
    status: str


class RoundResponse(BaseModel):
    session_id: str
    round_number: int
    player_move: str
    bot_move: str
    outcome: str
    stats: Dict[str, int]
    remaining_rounds: int
    status: str
    message: str | None = None


class ExpressionResponse(BaseModel):
    session_id: str
    expression: str
    stats: Dict[str, float]
    cat_image_url: str
    session_summary: Dict[str, object]


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    rounds_played: int
    total_rounds: int


app = FastAPI(title="Computer Vision Rock-Paper-Scissors", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, Dict[str, object]] = {}


@app.on_event("startup")
async def startup_event() -> None:  # pragma: no cover - simple boot strap helper
    try:
        monitor.ensure_started()
    except RuntimeError as exc:
        logger.warning("Camera monitor failed to start immediately: %s", exc)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/preview/stream")
def preview_stream():
    try:
        generator = monitor.iter_preview_frames()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return StreamingResponse(
        generator,
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
        },
    )


@app.get("/api/preview/status")
def preview_status() -> Dict[str, object]:
    try:
        return monitor.get_labels()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/session/start", response_model=SessionStartResponse)
def start_session(payload: StartSessionRequest) -> SessionStartResponse:
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    sessions[session_id] = {
        "session_id": session_id,
        "player_name": payload.player_name,
        "created_at": now,
        "rounds": [],
        "status": "active",
    }
    logger.info("Started session %s for %s", session_id, payload.player_name or "anonymous")
    return SessionStartResponse(
        session_id=session_id,
        total_rounds=TOTAL_ROUNDS,
        status="active",
    )


@app.get("/api/session/{session_id}", response_model=SessionStatusResponse)
def get_session(session_id: str) -> SessionStatusResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionStatusResponse(
        session_id=session_id,
        status=session["status"],
        rounds_played=len(session["rounds"]),
        total_rounds=TOTAL_ROUNDS,
    )


@app.post("/api/session/{session_id}/play-round", response_model=RoundResponse)
def play_round(session_id: str) -> RoundResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["status"] not in {"active", "needs_expression"}:
        raise HTTPException(status_code=400, detail="Session already completed")

    if len(session["rounds"]) >= TOTAL_ROUNDS:
        session["status"] = "needs_expression"
        raise HTTPException(status_code=400, detail="All rounds played; capture expression")

    try:
        monitor.start_round()
    except RuntimeError as exc:
        detail = str(exc)
        if "round capture" in detail.lower():
            raise HTTPException(status_code=400, detail=detail) from exc
        logger.exception("Gesture detection failed: %s", exc)
        raise HTTPException(status_code=500, detail=detail) from exc

    try:
        player_move, stats = monitor.wait_round_result(timeout=7.0)
    except TimeoutError as exc:
        monitor.cancel_round()
        raise HTTPException(status_code=500, detail="Timed out waiting for gesture data") from exc

    if player_move not in MOVES:
        logger.info("No gesture detected for session %s", session_id)
        return RoundResponse(
            session_id=session_id,
            round_number=len(session["rounds"]) + 1,
            player_move="none",
            bot_move="pending",
            outcome="retry",
            stats=stats,
            remaining_rounds=TOTAL_ROUNDS - len(session["rounds"]),
            status=session["status"],
            message="No clear gesture detected. Adjust lighting or hold your hand steadier.",
        )

    bot_move = random.choice(MOVES)
    outcome = _decide_winner(player_move, bot_move)

    round_entry = {
        "round_number": len(session["rounds"]) + 1,
        "player_move": player_move,
        "bot_move": bot_move,
        "outcome": outcome,
        "stats": stats,
        "captured_at": datetime.utcnow().isoformat(),
    }
    session["rounds"].append(round_entry)

    if len(session["rounds"]) >= TOTAL_ROUNDS:
        session["status"] = "needs_expression"

    logger.info(
        "Session %s round %s: player=%s bot=%s outcome=%s",
        session_id,
        round_entry["round_number"],
        player_move,
        bot_move,
        outcome,
    )

    return RoundResponse(
        session_id=session_id,
        round_number=round_entry["round_number"],
        player_move=player_move,
        bot_move=bot_move,
        outcome=outcome,
        stats=stats,
        remaining_rounds=TOTAL_ROUNDS - len(session["rounds"]),
        status=session["status"],
    )


@app.post("/api/session/{session_id}/final-expression", response_model=ExpressionResponse)
def capture_expression(session_id: str) -> ExpressionResponse:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(session["rounds"]) < TOTAL_ROUNDS:
        raise HTTPException(status_code=400, detail="You must finish all rounds first")

    if session.get("status") == "completed":
        raise HTTPException(status_code=400, detail="Expression already captured")

    try:
        monitor.start_expression_capture()
    except RuntimeError as exc:
        detail = str(exc)
        if "expression capture" in detail.lower():
            raise HTTPException(status_code=400, detail=detail) from exc
        logger.exception("Expression detection failed: %s", exc)
        raise HTTPException(status_code=500, detail=detail) from exc

    try:
        expression, stats = monitor.wait_expression_result(timeout=6.0)
    except TimeoutError as exc:
        raise HTTPException(status_code=500, detail="Timed out waiting for expression data") from exc

    cat_image = f"/cats/{expression}.jpg"

    session["expression"] = expression
    session["cat_image"] = cat_image
    session["status"] = "completed"
    created_at = datetime.fromisoformat(session["created_at"])
    session["duration_seconds"] = max((datetime.utcnow() - created_at).total_seconds(), 0.0)

    summary = _summarize_session(session)
    history = _load_history()
    history.append(summary)
    _write_history(history)

    logger.info("Session %s completed with expression %s", session_id, expression)

    return ExpressionResponse(
        session_id=session_id,
        expression=expression,
        stats=stats,
        cat_image_url=cat_image,
        session_summary=summary,
    )


@app.get("/api/logs")
def list_logs() -> Dict[str, List[Dict[str, object]]]:
    history = _load_history()
    return {"sessions": sorted(history, key=lambda x: x.get("played_at", ""), reverse=True)}


def _load_history() -> List[Dict[str, object]]:
    if not LOG_PATH.exists():
        return []
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Log file was corrupted; starting a new history list")
        return []


def _write_history(history: List[Dict[str, object]]) -> None:
    LOG_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")


def _decide_winner(player: str, bot: str) -> str:
    if player == bot:
        return "draw"
    wins_against = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    return "player" if wins_against[player] == bot else "bot"


def _summarize_session(session: Dict[str, object]) -> Dict[str, object]:
    rounds: List[Dict[str, object]] = session["rounds"]
    scoreboard = {"player": 0, "bot": 0, "draws": 0}
    for rnd in rounds:
        outcome = rnd["outcome"]
        if outcome == "player":
            scoreboard["player"] += 1
        elif outcome == "bot":
            scoreboard["bot"] += 1
        else:
            scoreboard["draws"] += 1

    return {
        "session_id": session["session_id"],
        "player_name": session.get("player_name"),
        "played_at": session["created_at"],
        "rounds": rounds,
        "scoreboard": scoreboard,
        "final_expression": session.get("expression"),
        "cat_image": session.get("cat_image"),
        "duration_seconds": session.get("duration_seconds"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
