import { useEffect, useState } from "react";
import "./App.css";

function App() {
  //configurable api url
  const API_URL = import.meta.env.VITE_API_URL;

  // Unique ID representing this browser/client
  const [clientId, setClientId] = useState("");

  // Documents belonging to this client
  const [documents, setDocuments] = useState([]);

  // PDFs currently selected in the file picker
  const [selectedFiles, setSelectedFiles] = useState([]);

  // Selected chunking strategy
  const [strategy, setStrategy] = useState("semantic");

  // Selected documents for querying
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  // Query
  const [query, setQuery] = useState("");

  // Response
  const [answer, setAnswer] = useState("");

  // Cache status
  const [cached, setCached] = useState(null);

  // Query loading state
  const [loading, setLoading] = useState(false);

  // Upload loading state
  const [uploadLoading, setUploadLoading] = useState(false);

  // Evaluation results
  const [evaluation, setEvaluation] = useState(null);

  // Evaluation loading state
  const [evaluationLoading, setEvaluationLoading] = useState(false);

  //Upload limits
  const [uploadError, setUploadError] = useState("");

  //LLM error handling
  const [queryError, setQueryError] = useState("");

  //chunk size input
  const [chunkSize, setChunkSize] = useState(200);

  //chunk overlap variable
  const [chunkOverlap, setChunkOverlap] = useState(40);

  // --------------------------------------------------
  // FETCH DOCUMENTS
  // --------------------------------------------------

  const fetchDocuments = async (id) => {
    try {
      const response = await fetch(`${API_URL}/documents`, {
        method: "GET",
        headers: {
          "X-Client-ID": id,
        },
      });

      const data = await response.json();

      setDocuments(data);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
    }
  };

  // --------------------------------------------------
  // UPLOAD DOCUMENTS
  // --------------------------------------------------

  const uploadDocuments = async () => {
    if (selectedFiles.length === 0) {
      return;
    }

    if (
      (strategy === "token" || strategy === "recursive") &&
      chunkOverlap >= chunkSize
    ) {
      setUploadError("Chunk overlap must be smaller than chunk size.");
      return;
    }

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    if (strategy === "token" || strategy === "recursive") {
      formData.append("chunk_size", chunkSize);
      formData.append("chunk_overlap", chunkOverlap);
    }

    setUploadError("");
    setUploadLoading(true);

    try {
      const response = await fetch(`${API_URL}/upload/${strategy}`, {
        method: "POST",
        headers: {
          "X-Client-ID": clientId,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed. Please try again.");
      }

      await fetchDocuments(clientId);

      setSelectedFiles([]);
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadError(error.message);
    } finally {
      setUploadLoading(false);
    }
  };

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const deleteDocument = async (documentHash) => {
    try {
      const response = await fetch(`${API_URL}/documents/${documentHash}`, {
        method: "DELETE",
        headers: {
          "X-Client-ID": clientId,
        },
      });

      const data = await response.json();

      console.log(data);

      setSelectedDocuments((currentDocuments) =>
        currentDocuments.filter((hash) => hash !== documentHash),
      );

      await fetchDocuments(clientId);
    } catch (error) {
      console.error("Delete failed:", error);
    }
  };

  // --------------------------------------------------
  // SELECT / DESELECT DOCUMENT
  // --------------------------------------------------

  const toggleDocumentSelection = (documentHash) => {
    setSelectedDocuments((currentDocuments) => {
      if (currentDocuments.includes(documentHash)) {
        return currentDocuments.filter((hash) => hash !== documentHash);
      }

      return [...currentDocuments, documentHash];
    });
  };

  // --------------------------------------------------
  // ASK QUESTION
  // --------------------------------------------------

  const askQuestion = async () => {
    if (!query.trim()) {
      return;
    }

    if (selectedDocuments.length === 0) {
      return;
    }

    // Remove old evaluation when a new query begins
    setEvaluation(null);

    setQueryError("");

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-ID": clientId,
        },
        body: JSON.stringify({
          query: query,
          documents: selectedDocuments,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Query failed. Please try again.");
      }

      setAnswer(data.response);
      setCached(data.cached);
    } catch (error) {
      console.error("Query failed:", error);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // EVALUATE RESPONSE
  // --------------------------------------------------

  const evaluateResponse = async () => {
    setEvaluationLoading(true);

    try {
      const response = await fetch(`${API_URL}/evaluate`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          "X-Client-ID": clientId,
        },

        body: JSON.stringify({
          query: query,
          answer: answer,
          documents: selectedDocuments,
        }),
      });

      const data = await response.json();

      setEvaluation(data);
    } catch (error) {
      console.error("Evaluation failed:", error);
    } finally {
      setEvaluationLoading(false);
    }
  };

  // --------------------------------------------------
  // INITIAL APPLICATION LOAD
  // --------------------------------------------------

  useEffect(() => {
    let storedClientId = localStorage.getItem("client_id");

    if (!storedClientId) {
      storedClientId = crypto.randomUUID();

      localStorage.setItem("client_id", storedClientId);
    }

    setClientId(storedClientId);

    fetchDocuments(storedClientId);
  }, []);

  return (
    <div className="app">
      {/* HEADER */}

      <div className="header">
        <h1>DocuMind</h1>

        <p>Chat with your documents.</p>
      </div>

      {/* DEMO NOTICE */}

      <div className="data-warning">
        <span>⚠️</span>

        <div>
          <strong>Demo Notice</strong>

          <p>
            DocuMind is a portfolio demonstration and does not currently provide
            authenticated user accounts. Do not upload confidential, sensitive,
            or personally identifiable documents.
          </p>
        </div>
      </div>

      <br></br>

      {/* UPLOAD */}

      <div className="card">
        <h2>Upload Documents</h2>

        <h3>Up to 5 PDFs / 30 pages total per upload</h3>

        <div className="upload-controls">
          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={(event) => {
              setSelectedFiles(Array.from(event.target.files));
            }}
          />

          <select
            value={strategy}
            onChange={(event) => {
              const newStrategy = event.target.value;

              setStrategy(newStrategy);

              if (newStrategy === "token") {
                setChunkSize(200);
                setChunkOverlap(40);
              }

              if (newStrategy === "recursive") {
                setChunkSize(100);
                setChunkOverlap(40);
              }
            }}
          >
            <option value="semantic">Semantic</option>
            <option value="token">Token</option>
            <option value="sentence">Sentence</option>
            <option value="recursive">Recursive</option>
          </select>

          {(strategy === "token" || strategy === "recursive") && (
            <div className="chunk-settings">
              <div className="chunk-setting">
                <label>Chunk Size</label>

                <input
                  type="number"
                  min="50"
                  max="500"
                  value={chunkSize}
                  onChange={(event) => {
                    setChunkSize(Number(event.target.value));
                  }}
                />

                <small>Amount of text included in each chunk.</small>
              </div>

              <div className="chunk-setting">
                <label>Chunk Overlap</label>

                <input
                  type="number"
                  min="0"
                  value={chunkOverlap}
                  onChange={(event) => {
                    setChunkOverlap(Number(event.target.value));
                  }}
                />

                <small>Context shared between adjacent chunks.</small>
              </div>
            </div>
          )}

          <button onClick={uploadDocuments} disabled={uploadLoading}>
            Upload
          </button>
        </div>

        {uploadError && <div className="upload-error">⚠️ {uploadError}</div>}
      </div>

      {/* DOCUMENTS */}

      <div className="card">
        <h2>Documents</h2>

        {documents.length === 0 ? (
          <div className="empty-state">No documents uploaded.</div>
        ) : (
          <div className="documents-list">
            {documents.map((document) => (
              <div key={document.document_hash} className="document-item">
                <div className="document-info">
                  <p className="document-name">{document.filename}</p>

                  <p className="document-strategy">{document.strategy}</p>
                </div>

                <div className="document-actions">
                  <input
                    type="checkbox"
                    checked={selectedDocuments.includes(document.document_hash)}
                    onChange={() =>
                      toggleDocumentSelection(document.document_hash)
                    }
                  />

                  <button
                    className="delete-button"
                    onClick={() => deleteDocument(document.document_hash)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="data-warning">
          <span className="warning-icon">⚠️</span>

          <div>
            <strong>Data & Access Notice</strong>

            <p>
              DocuMind uses a browser-generated identifier to associate your
              documents with this browser. Clearing this site's browser data or
              local storage, using Incognito mode, switching browsers or
              devices, or resetting your browser may cause you to lose access to
              previously uploaded documents.
            </p>

            <p>
              User accounts and cross-device document recovery are not currently
              supported.
            </p>
          </div>
        </div>
      </div>

      {/* QUERY */}

      <div className="card">
        <h2>Ask a Question</h2>

        <div className="query-section">
          <input
            type="text"
            value={query}
            placeholder="Ask something about your selected documents..."
            onChange={(event) => {
              setQuery(event.target.value);
            }}
          />

          <button
            className="ask-button"
            onClick={askQuestion}
            disabled={loading}
          >
            {loading ? <span className="spinner"></span> : "Ask"}
          </button>
        </div>

        {queryError && <div className="upload-error">⚠️ {queryError}</div>}

        {/* ANSWER */}

        {answer && (
          <div className="answer-card">
            <h3>Answer</h3>

            <p>{answer}</p>

            <button
              className="evaluate-button"
              onClick={evaluateResponse}
              disabled={evaluationLoading}
            >
              {evaluationLoading ? (
                <>
                  <span className="spinner"></span>
                  Evaluating...
                </>
              ) : (
                "Evaluate Response"
              )}
            </button>
          </div>
        )}

        {/* CACHE STATUS */}

        {cached !== null && (
          <span className="cache-status">
            {cached ? "⚡ Retrieved from cache" : "Generated by DocuMind"}
          </span>
        )}

        {/* EVALUATION RESULTS */}

        {evaluation && (
          <div className="evaluation-card">
            <h3>Evaluation Results</h3>

            <div className="evaluation-grid">
              <div className="metric">
                <span>Coherence</span>

                <strong>{evaluation["Coherence"]?.toFixed(3)}</strong>
              </div>

              <div className="metric">
                <span>Window Coherence</span>

                <strong>
                  {evaluation[
                    "Window coherence for slow context drifting"
                  ]?.toFixed(3)}
                </strong>
              </div>

              <div className="metric">
                <span>Readability</span>

                <strong>{evaluation["Readability score"]?.toFixed(3)}</strong>
              </div>

              <div className="metric">
                <span>Faithfulness</span>

                <strong>
                  {evaluation["Deep Eval Metrics"]?.FaithfulnessMetric?.toFixed(
                    3,
                  )}
                </strong>
              </div>

              <div className="metric">
                <span>Answer Relevancy</span>

                <strong>
                  {evaluation[
                    "Deep Eval Metrics"
                  ]?.AnswerRelevancyMetric?.toFixed(3)}
                </strong>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* UPLOAD LOADING OVERLAY */}

      {uploadLoading && (
        <div className="upload-overlay">
          <div className="upload-loader">
            <div className="brain-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <h2>Indexing your documents</h2>

            <p>Chunking, embedding and preparing your knowledge base...</p>

            <div className="processing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
