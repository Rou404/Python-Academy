# Computer Vision Rock - Paper - Scissors Demo

This classroom demo pairs a Python computer-vision backend with a small React dashboard.

## Project layout

```
part1/
|-- backend/
|   |-- main.py                # FastAPI app orchestrating the game/session flow
|   |-- vision_monitor.py      # Continuous MediaPipe capture for preview + aggregation
|   |-- gesture_recognition.py # Hand gesture classification helpers
|   |-- expression_recognition.py # Facial expression heuristics (happy/sad/angry/neutral)
|   |-- requirements.txt       # Python dependencies
|   |-- logs/
|       |-- game_history.json  # Session history exported for the React UI
|-- frontend/
|   |-- index.html
|   |-- package.json
|   |-- src/
|   |   |-- App.jsx            # UI logic and timers/countdowns
|   |   |-- components/
|   |   |   |-- RoundCard.jsx
|   |   |   |-- SessionLog.jsx
|   |   |-- services/api.js    # HTTP client helpers
|   |   |-- styles.css
|   |-- public/
|       |-- cats/              # Drop emotion-matched cat images here (happy.jpg etc.)
|-- README.md (this file)
```

## Backend setup (Python + OpenCV + MediaPipe)

```powershell
cd "M4 - Python Advanced\lesson4 Computer Vision\part1\backend"
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

> **Note:** MediaPipe relies on a recent Microsoft Visual C++ Redistributable on Windows.
> If the import fails, install the [VC++ runtime](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist).
> For Linux, install `libgl1` (`sudo apt install libgl1`).
> When uvicorn starts for the first time on Windows, accept the webcam permission pop-up so the live preview works.

The API runs on `http://localhost:8000`. Key endpoints:

- `POST /api/session/start` - create a session (optional player name).
- `POST /api/session/{id}/play-round` - triggers a 5s webcam capture to pick rock/paper/scissors.
- `POST /api/session/{id}/final-expression` - runs a 4s facial expression capture (happy/sad/angry/neutral).
- `GET /api/preview/stream` - continuous MJPEG feed for the always-on webcam preview.
- `GET /api/preview/status` - current live gesture/expression labels for the dashboard.
- `GET /api/logs` - returns the session history stored in `logs/game_history.json`.

The backend also writes granular events to `backend/logs/backend.log` so you can show real-time logging during class.

## Frontend setup (React + Vite)

```powershell
cd "M4 - Python Advanced\lesson4 Computer Vision\part1\frontend"
copy .env.example .env   # adjust VITE_API_BASE_URL if the backend runs on a different host
npm install
npm run dev
```

The Vite dev server defaults to `http://localhost:5173`. It calls the backend via `VITE_API_BASE_URL`.
The dashboard opens the live preview immediately on load using `/api/preview/stream`, so start the FastAPI server first and allow the OS camera prompt when it appears.

### Cat reactions

Drop four images of your own cats (or memes!) into `frontend/public/cats/` with the following names:

```
happy.jpg
sad.jpg
angry.jpg
neutral.jpg
```

When the backend responds with the dominant expression, the UI swaps in the respective cat photo.

## Teaching workflow

1. **Start session** - Optional player name is saved in the log.
2. **Play round** - UI launches a 5-second countdown while the backend tallies the live gesture stream (the preview stays running the whole time).
   - `vision_monitor.py` keeps the MediaPipe pipeline alive, overlays labels on the MJPEG feed, and majority-votes the gesture when a round is triggered.
   - FastAPI returns frame counts so students can see how many samples influenced the vote.
3. **Three rounds vs. bot** - Bot picks randomly; scoreboard updates live.
4. **Capture expression** - The same monitor aggregates face metrics over 4 seconds before locking the final label.
   - Heuristics map those metrics to *happy*, *sad*, *angry*, or *neutral*, and the preview card swaps to your chosen cat photo so the class sees the reaction instantly.
   - Weighted scores in `expression_recognition.py` make sad/angry easier to hit; tweak the thresholds if you need to calibrate for your lighting or camera.
   - Result is stored with the session and surfaced in the React UI alongside your curated cat photo.
5. **Review logs** - Both the backend JSON log and on-screen table show the full history for discussion about persistence.

## Troubleshooting tips

- Use good lighting and keep your hand fully in frame for reliable gesture classification.
- If MediaPipe cannot access your webcam, verify no other application is using it.
- On Windows, recalibrate exposure/white balance in the Camera app if detection is jittery.
- Expression heuristics are deliberately simple for teaching. Encourage students to tweak thresholds in `expression_recognition.py`.

