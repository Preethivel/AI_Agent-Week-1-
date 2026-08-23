import React from 'react';

function Logs({ logs, loading }) {
  if (loading) {
    return <div className="loading">⏳ Loading logs...</div>;
  }

  if (!logs || logs.length === 0) {
    return (
      <div className="empty-state">
        <p>No logs found. Upload a CSV file first.</p>
      </div>
    );
  }

  return (
    <div>
      <h2>📋 Iteration Logs</h2>
      <p>Total: {logs.length} iterations</p>
      
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Transaction</th>
              <th>Category</th>
              <th>Confidence</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {[...logs].reverse().map((entry) => (
              <tr key={entry.iteration}>
                <td>{entry.iteration}</td>
                <td>{entry.transaction}</td>
                <td><span className="badge">{entry.category}</span></td>
                <td>{Math.round(entry.confidence * 100)}%</td>
                <td>{entry.timestamp?.slice(0, 19) || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Logs;