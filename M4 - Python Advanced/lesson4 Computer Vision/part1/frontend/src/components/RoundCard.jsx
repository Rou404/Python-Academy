const outcomeLabel = {
  player: 'You won the round ??',
  bot: 'Bot took this one ??',
  draw: 'It\'s a draw',
  retry: 'Gesture not detected',
  pending: 'Awaiting play',
};

const badgeColor = {
  player: 'rgba(16, 185, 129, 0.2)',
  bot: 'rgba(248, 113, 113, 0.2)',
  draw: 'rgba(148, 163, 184, 0.25)',
  retry: 'rgba(250, 204, 21, 0.25)',
  pending: 'rgba(59, 130, 246, 0.2)',
};

export default function RoundCard({ roundNumber, result }) {
  const status = result?.outcome ?? 'pending';
  const moveText = result?.player_move ? result.player_move : '?';
  const botMove = result?.bot_move && result.bot_move !== 'pending' ? result.bot_move : '?';
  const stats = result?.stats ?? {};

  return (
    <div className="round-card">
      <div className="small-text">Round {roundNumber}</div>
      <div
        className="tag"
        style={{
          background: badgeColor[status],
          borderColor: 'transparent',
          color: '#f8fafc',
        }}
      >
        {outcomeLabel[status]}
      </div>
      <div style={{ marginTop: '0.75rem' }}>
        <div className="small-text">Your move</div>
        <strong style={{ fontSize: '1.25rem' }}>{moveText}</strong>
      </div>
      <div style={{ marginTop: '0.75rem' }}>
        <div className="small-text">Bot move</div>
        <strong style={{ fontSize: '1.25rem' }}>{botMove}</strong>
      </div>
      {result?.stats && (
        <div className="small-text" style={{ marginTop: '0.75rem' }}>
          Frame votes ? rock: {stats.rock ?? 0} | paper: {stats.paper ?? 0} | scissors: {stats.scissors ?? 0}
        </div>
      )}
      {result?.captured_at && (
        <div className="small-text" style={{ marginTop: '0.5rem' }}>
          Captured at {new Date(result.captured_at).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}
