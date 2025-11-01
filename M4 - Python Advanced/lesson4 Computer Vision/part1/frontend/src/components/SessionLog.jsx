export default function SessionLog({ sessions, onRefresh }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>Game History</h2>
        <button type="button" onClick={onRefresh} style={{ padding: '0.5rem 1.4rem' }}>
          Refresh
        </button>
      </div>
      <p className="small-text">Pulled from backend log file to discuss persistence with the class.</p>
      <div style={{ overflowX: 'auto' }}>
        <table className="logs-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Player</th>
              <th>Score</th>
              <th>Expression</th>
              <th>Cat</th>
            </tr>
          </thead>
          <tbody>
            {sessions.length === 0 && (
              <tr>
                <td colSpan={5} className="small-text">
                  No sessions recorded yet.
                </td>
              </tr>
            )}
            {sessions.map((session) => (
              <tr key={session.session_id}>
                <td>{new Date(session.played_at).toLocaleString()}</td>
                <td>{session.player_name || 'Anonymous'}</td>
                <td>
                  {session.scoreboard.player}-{session.scoreboard.bot} (draws {session.scoreboard.draws})
                </td>
                <td>{session.final_expression}</td>
                <td>{session.cat_image}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
