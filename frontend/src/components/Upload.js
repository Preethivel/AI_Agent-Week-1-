import React, { useState } from 'react';
import { uploadFile, getResults, getLogs } from '../api';

function Upload({ setResults, setLogs, setLoading, loading }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setSuccess(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await uploadFile(file);
      
      const resultsRes = await getResults();
      setResults(resultsRes.data);
      
      const logsRes = await getLogs();
      setLogs(logsRes.data);
      
      setSuccess('✅ File processed successfully!');
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-area">
      <h2>📂 Upload CSV File</h2>
      <p>Upload a CSV file with columns: <strong>date, description, amount</strong></p>
      
      <input type="file" accept=".csv" onChange={handleFileChange} />
      
      <button onClick={handleUpload} disabled={loading}>
        {loading ? '⏳ Processing...' : '🚀 Process File'}
      </button>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      
      <div className="info-text">
        <p>📄 Sample format: <code>date,description,amount</code></p>
        <p>🧠 Agent uses RAG memory + Ollama LLM for categorization</p>
      </div>
    </div>
  );
}

export default Upload;