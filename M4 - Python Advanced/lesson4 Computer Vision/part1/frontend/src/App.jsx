import { useEffect, useMemo, useState } from 'react';
import RoundCard from './components/RoundCard.jsx';
import SessionLog from './components/SessionLog.jsx';
import {
  startSession,
  playRound,
  captureExpression,
  fetchLogs,
  fetchPreviewStatus,
  API_BASE_URL,
} from './services/api.js';

const TOTAL_ROUNDS = 3; // Keep in sync with backend constant
const PREVIEW_POLL_MS = 900;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export default function App() {
  const [playerName, setPlayerName] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [rounds, setRounds] = useState([]);
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');
  const [countdown, setCountdown] = useState(null);
  const [expressionResult, setExpressionResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isWorking, setIsWorking] = useState(false);
  const [cameraReminder, setCameraReminder] = useState(true);
  const [handStreamUrl, setHandStreamUrl] = useState(`${API_BASE_URL}/api/preview/stream?${Date.now()}`);
  const [previewStatus, setPreviewStatus] = useState({
    gesture_label: 'searching',
    expression_label: 'neutral',
    timestamp: null,
  });

  useEffect(() => {
    refreshLogs();
  }, []);

  useEffect(() => {
    let ignore = false;

    const pollStatus = async () => {
      try {
        const data = await fetchPreviewStatus();
        if (!ignore) {
          setPreviewStatus(data);
        }
      } catch (error) {
        if (!ignore) {
          setPreviewStatus((prev) => ({ ...prev, error: error.message }));
        }
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, PREVIEW_POLL_MS);
    return () => {
      ignore = true;
      clearInterval(interval);
    };
  }, []);

  const scoreboard = useMemo(() => rounds.reduce((acc, round) => {
    if (!round) {
      return acc;
    }
    if (round.outcome === 'player') acc.player += 1;
    if (round.outcome === 'bot') acc.bot += 1;
    if (round.outcome === 'draw') acc.draws += 1;
    return acc;
  }, { player: 0, bot: 0, draws: 0 }), [rounds]);

  const refreshLogs = async () => {
    try {
      const data = await fetchLogs();
      setLogs(data);
    } catch (error) {
      setMessage(error.message);
    }
  };

  const handleStart = async () => {
    setIsWorking(true);
    setMessage('Setting up session...');
    try {
      const data = await startSession({ playerName });
      setSessionId(data.session_id);
      setRounds([]);
      setStatus(data.status);
      setExpressionResult(null);
      setMessage('Session started. Play round when ready.');
      setCameraReminder(false);
      setHandStreamUrl(`${API_BASE_URL}/api/preview/stream?${Date.now()}`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsWorking(false);
    }
  };

  const runCountdown = async (seconds) => {
    for (let i = seconds; i >= 1; i -= 1) {
      setCountdown(i);
      await sleep(1000);
    }
    setCountdown(null);
  };

  const handlePlayRound = async () => {
    if (!sessionId) {
      setMessage('Start a game session first.');
      return;
    }

    setIsWorking(true);
    setMessage('Countdown started. Show your gesture clearly!');
    await runCountdown(5);
    setMessage('Capturing hand pose...');

    try {
      const result = await playRound(sessionId);
      setStatus(result.status);

      if (result.outcome === 'retry') {
        setMessage(result.message);
        return;
      }

      setRounds((prev) => {
        const next = [...prev];
        next[result.round_number - 1] = result;
        return next;
      });

      if (result.status === 'needs_expression') {
        setMessage(`Bot chose ${result.bot_move}. All rounds done! Time to capture your victory pose.`);
      } else {
        setMessage(`Bot played ${result.bot_move}. Round ${result.round_number} captured. Ready for the next one.`);
      }
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsWorking(false);
    }
  };

  const handleExpression = async () => {
    if (!sessionId) {
      setMessage('No active session.');
      return;
    }

    setIsWorking(true);
    setMessage('Hold your face for 4 seconds...');

    try {
      const result = await captureExpression(sessionId);
      setExpressionResult(result);
      setStatus('completed');
      setMessage(`Expression captured: ${result.expression}. Enjoy your cat!`);
      await refreshLogs();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIsWorking(false);
    }
  };

  const canPlayRound = status === 'active' && !isWorking;
  const canCaptureExpression = status === 'needs_expression' && !isWorking;

  return (
    <div>
      <h1>Computer Vision Rock - Paper - Scissors</h1>
      <p className="small-text">
        Web UI controls a FastAPI backend. Each action triggers live CV inference so you can narrate the pipeline.
      </p>
      {cameraReminder && (
        <div className="status-banner" style={{ background: 'rgba(34,197,94,0.15)', borderColor: 'rgba(34,197,94,0.45)' }}>
          <strong>Tip:</strong> When Windows prompts, allow Python (uvicorn) to access the webcam so the preview works.
        </div>
      )}

      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <label htmlFor="name-input" className="small-text">
            Player name
          </label>
          <input
            id="name-input"
            value={playerName}
            onChange={(event) => setPlayerName(event.target.value)}
            placeholder="Optional for logs"
            style={{
              background: 'rgba(30, 41, 59, 0.6)',
              borderRadius: '999px',
              border: '1px solid rgba(148, 163, 184, 0.35)',
              color: '#fff',
              padding: '0.6rem 1rem',
            }}
          />
          <button type="button" onClick={handleStart} disabled={isWorking}>
            Start session
          </button>
        </div>
        {status !== 'idle' && (
          <div className="status-banner">
            <strong>Status:</strong> {status}
          </div>
        )}
        {message && <div className="small-text">{message}</div>}
        {countdown && <div className="countdown">{countdown}</div>}

        <div className="preview-card">
          <div className="preview-header">
            <span className="small-text">Live camera preview (MediaPipe overlays on server)</span>
            <span className="small-text">Labels update in real time while you move.</span>
          </div>
          <div className="preview-frame">
            {handStreamUrl ? (
              <img src={handStreamUrl} alt="Live hand tracking" />
            ) : (
              <div className="small-text">Camera preview unavailable.</div>
            )}
          </div>
          <div className="preview-metrics">
            <span className="tag">Gesture: {previewStatus.gesture_label ?? 'searching'}</span>
            <span className="tag">Expression: {previewStatus.expression_label ?? 'neutral'}</span>
          </div>
          {previewStatus.error && <div className="small-text">{previewStatus.error}</div>}
        </div>

        <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button type="button" onClick={handlePlayRound} disabled={!canPlayRound}>
            Play next round
          </button>
          <button type="button" onClick={handleExpression} disabled={!canCaptureExpression}>
            Capture expression
          </button>
        </div>
        <div className="small-text" style={{ marginTop: '0.75rem' }}>
          Tip: ensure good lighting and keep your hand inside the webcam frame.
        </div>
      </div>

      <div className="card">
        <h2>Round tracker</h2>
        <p className="small-text">
          Backend records the majority vote across ~5 seconds of frames. Stats below come directly from the API.
        </p>
        <div className="tag">
          Scoreboard -> You {scoreboard.player} | Bot {scoreboard.bot} | Draws {scoreboard.draws}
        </div>
        <div className="rounds-grid" style={{ marginTop: '1rem' }}>
          {Array.from({ length: TOTAL_ROUNDS }).map((_, index) => (
            <RoundCard
              key={`round-${index + 1}`}
              roundNumber={index + 1}
              result={rounds[index]}
            />
          ))}
        </div>
        {expressionResult && (
          <div className="cat-preview">
            <div className="tag">Final expression: {expressionResult.expression}</div>
            <img
              src={expressionResult.cat_image_url}
              alt={`${expressionResult.expression} cat`}
              onError={(event) => {
                event.currentTarget.style.display = 'none';
              }}
            />
            <div className="small-text">Place your cat photo under public/cats/{'{'}emotion{'}'}.jpg</div>
          </div>
        )}
      </div>

      <SessionLog sessions={logs} onRefresh={refreshLogs} />
    </div>
  );
}
