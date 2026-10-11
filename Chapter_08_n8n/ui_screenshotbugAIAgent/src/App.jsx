import { useState } from 'react';
import './App.css';

function App() {
  const [screenshot, setScreenshot] = useState(null);
  const [logs, setLogs] = useState('');
  const [steps, setSteps] = useState('');
  const [severity, setSeverity] = useState('S3');
  const [environment, setEnvironment] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!screenshot) {
      setError('Please upload a screenshot.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();

      formData.append('screenshot', screenshot);
      formData.append('error_logs', logs);
      formData.append('steps_to_reproduce', steps);
      formData.append('severity', severity);
      formData.append('environment', environment);

      const response = await fetch('/api/report', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || 'Failed to generate bug report.'
        );
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Screenshot Bug Reporter</h1>

          <p>
            Upload a screenshot and let AI analyze it for a potential defect.
          </p>
        </div>

        <span className="badge">
          AI QA Agent
        </span>
      </header>

      <main className="container">
        <form
          className="card"
          onSubmit={handleSubmit}
        >
          <h2>Report a Bug</h2>

          <div className="field">
            <label htmlFor="screenshot">
              Screenshot *
            </label>

            <input
              id="screenshot"
              type="file"
              accept="image/*"
              onChange={(event) => {
                setScreenshot(
                  event.target.files?.[0] || null
                );
              }}
            />

            {screenshot && (
              <small className="file-name">
                Selected: {screenshot.name}
              </small>
            )}
          </div>

          <div className="field">
            <label htmlFor="logs">
              Error Logs
            </label>

            <textarea
              id="logs"
              value={logs}
              onChange={(event) => {
                setLogs(event.target.value);
              }}
              placeholder="Paste any relevant error logs..."
              rows="5"
            />
          </div>

          <div className="field">
            <label htmlFor="steps">
              Steps to Reproduce
            </label>

            <textarea
              id="steps"
              value={steps}
              onChange={(event) => {
                setSteps(event.target.value);
              }}
              placeholder="Describe what you did before the issue appeared..."
              rows="4"
            />
          </div>

          <div className="two-column">
            <div className="field">
              <label htmlFor="severity">
                Severity Guess
              </label>

              <select
                id="severity"
                value={severity}
                onChange={(event) => {
                  setSeverity(event.target.value);
                }}
              >
                <option value="S1">
                  S1 - Blocker
                </option>

                <option value="S2">
                  S2 - Major
                </option>

                <option value="S3">
                  S3 - Minor
                </option>

                <option value="S4">
                  S4 - Cosmetic
                </option>
              </select>
            </div>

            <div className="field">
              <label htmlFor="environment">
                Environment
              </label>

              <input
                id="environment"
                type="text"
                value={environment}
                onChange={(event) => {
                  setEnvironment(event.target.value);
                }}
                placeholder="e.g. Chrome / Windows 11"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
          >
            {loading
              ? 'Analyzing Screenshot...'
              : 'Generate Bug Report'}
          </button>

          {error && (
            <div className="message error">
              {error}
            </div>
          )}
        </form>

        {result && (
          <section className="card result">
            <h2>Bug Report Created</h2>

            <div className="result-row">
              <strong>Issue Key</strong>

              <span>
                {result.issue_key}
              </span>
            </div>

            <div className="result-row">
              <strong>Jira</strong>

              <a
                href={result.issue_url}
                target="_blank"
                rel="noreferrer"
              >
                Open Jira Issue
              </a>
            </div>

            <div className="message success">
              The screenshot was analyzed and the Jira bug was created
              successfully.
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
