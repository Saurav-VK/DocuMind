import { useEffect, useState } from "react";
import "./App.css";

function App() {
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

  // Loading state
  const [loading, setLoading] = useState(false);

  //loading page
  const [uploadLoading, setUploadLoading] = useState(false);

  // --------------------------------------------------
  // FETCH DOCUMENTS
  // --------------------------------------------------

  const fetchDocuments = async (id) => {
    try {
      const response = await fetch("http://localhost:8000/documents", {
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

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    setUploadLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/upload/${strategy}`, {
        method: "POST",
        headers: {
          "X-Client-ID": clientId,
        },
        body: formData,
      });

      const data = await response.json();

      console.log(data);

      await fetchDocuments(clientId);

      setSelectedFiles([]);
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploadLoading(false);
    }
  };

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const deleteDocument = async (documentHash) => {
    try {
      const response = await fetch(
        `http://localhost:8000/documents/${documentHash}`,
        {
          method: "DELETE",
          headers: {
            "X-Client-ID": clientId,
          },
        },
      );

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

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/query", {
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

      setAnswer(data.response);
      setCached(data.cached);
    } catch (error) {
      console.error("Query failed:", error);
    } finally {
      setLoading(false);
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

        {/* <p className="client-id">Client ID: {clientId}</p> */}
      </div>

      {/* UPLOAD */}

      <div className="card">
        <h2>Upload Documents</h2>
        <h3>Up to 5 PDFs / 100 pages total per upload</h3>

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
              setStrategy(event.target.value);
            }}
          >
            <option value="semantic">Semantic</option>
            <option value="token">Token</option>
            <option value="sentence">Sentence</option>
            <option value="recursive">Recursive</option>
          </select>

          <button onClick={uploadDocuments} disabled={uploadLoading}>
            Upload
          </button>
        </div>
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

        {answer && (
          <div className="answer-card">
            <h3>Answer</h3>
            <p>{answer}</p>
          </div>
        )}

        {cached !== null && (
          <span className="cache-status">
            {cached ? "⚡ Retrieved from cache" : "Generated by DocuMind"}
          </span>
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
