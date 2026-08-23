import React, { useState } from 'react';
import './App.css';
import Upload from './components/Upload';
import Results from './components/Results';
import Logs from './components/Logs';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [results, setResults] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  return (
    <div className="app">
      <header>
        <h1>🤖 AI Agent - Expense Categorizer</h1>
        <p>Upload your CSV and let AI categorize your expenses</p>
      </header>

      <nav>
        <button 
          className={activeTab === 'upload' ? 'active' : ''} 
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload
        </button>
        <button 
          className={activeTab === 'results' ? 'active' : ''} 
          onClick={() => setActiveTab('results')}
        >
          📊 Results
        </button>
        <button 
          className={activeTab === 'logs' ? 'active' : ''} 
          onClick={() => setActiveTab('logs')}
        >
          📋 Logs
        </button>
      </nav>

      <div className="content">
        {activeTab === 'upload' && (
          <Upload 
            setResults={setResults} 
            setLogs={setLogs} 
            setLoading={setLoading}
            loading={loading}
          />
        )}
        {activeTab === 'results' && <Results results={results} loading={loading} />}
        {activeTab === 'logs' && <Logs logs={logs} loading={loading} />}
      </div>
    </div>
  );
}

export default App;