import React from 'react';

function Results({ results, loading }) {
  if (loading) {
    return <div className="loading">⏳ Loading results...</div>;
  }

  if (!results) {
    return (
      <div className="empty-state">
        <p>No results found. Please upload a CSV file first.</p>
      </div>
    );
  }

  if (results.error) {
    return (
      <div className="empty-state">
        <p>Error: {results.error}</p>
      </div>
    );
  }

  const { total_transactions, categorized_count, uncategorized_count, accuracy, categories } = results;

  return (
    <div>
      <h2>📊 Categorization Results</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="number">{total_transactions || 0}</div>
          <div className="label">Total Transactions</div>
        </div>
        <div className="stat-card green">
          <div className="number">{categorized_count || 0}</div>
          <div className="label">Categorized</div>
        </div>
        <div className="stat-card red">
          <div className="number">{uncategorized_count || 0}</div>
          <div className="label">Uncategorized</div>
        </div>
        <div className="stat-card blue">
          <div className="number">{accuracy ? Math.round(accuracy * 100) : 0}%</div>
          <div className="label">Accuracy</div>
        </div>
      </div>

      {categories && Object.keys(categories).length > 0 && (
        <div className="table-container">
          <h3>📂 Category Breakdown</h3>
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Percentage</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(categories).map(([cat, count]) => (
                <tr key={cat}>
                  <td>{cat}</td>
                  <td>{count}</td>
                  <td>{total_transactions ? Math.round(count / total_transactions * 100) : 0}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Results;