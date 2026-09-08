import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadBatchFile, processBatches } from '../services/api';

const STEPS = [
  'Upload', 'Read', 'Extract', 'Validate', 'Clean', 'Predict', 'Done'
];

function StepTracker({ step }) {
  return (
    <div className="step-tracker">
      {STEPS.map((label, i) => (
        <div key={label} className="step-item">
          {i > 0 && (
            <div className={`step-connector${i <= step ? ' done' : ''}`} />
          )}
          <div className="step-wrap">
            <div className={`step-circle${i === step ? ' active' : i < step ? ' done' : ''}`}>
              {i < step ? '✓' : i + 1}
            </div>
            <span className="step-label">{label}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function ValidationPanel({ reports }) {
  const errors   = reports.filter(r => !r.is_valid);
  const warnings = reports.flatMap(r => r.warnings.map(w => ({ batch: r.batch_id, msg: w })));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {errors.length > 0 && (
        <div className="alert alert-warning">
          <span>⚠</span>
          <div>
            <strong>{errors.length} batch(es) have validation errors</strong>
            <ul style={{ marginTop: 6, paddingLeft: 18 }}>
              {errors.slice(0, 5).map((r, i) => (
                <li key={i} style={{ fontSize: '0.82rem', marginBottom: 2 }}>
                  <span style={{ fontFamily: 'var(--mono)', color: 'var(--accent-2)' }}>
                    {r.batch_id || `Row ${r.batch_index + 1}`}
                  </span>{': '}
                  {r.errors.join('; ')}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      {warnings.length > 0 && (
        <div className="alert alert-warning" style={{ background: 'rgba(245,158,11,0.05)' }}>
          <span>⚡</span>
          <div>
            <strong>{warnings.length} out-of-range warning(s)</strong>
            <ul style={{ marginTop: 6, paddingLeft: 18 }}>
              {warnings.slice(0, 5).map((w, i) => (
                <li key={i} style={{ fontSize: '0.82rem', marginBottom: 2 }}>
                  <span style={{ fontFamily: 'var(--mono)', color: 'var(--accent-2)' }}>{w.batch}</span>{': '}{w.msg}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      {errors.length === 0 && warnings.length === 0 && (
        <div className="alert alert-success"><span>✓</span> All {reports.length} batch records passed validation.</div>
      )}
    </div>
  );
}

function DataPreview({ preview, columnMap }) {
  if (!preview || preview.length === 0) return null;

  // Get all unique keys across all rows
  const allKeys = Array.from(
    new Set(preview.flatMap(p => Object.keys(p.data)))
  ).slice(0, 30); // cap columns

  const remapped = Object.fromEntries(
    Object.entries(columnMap || {}).map(([k, v]) => [v, k])
  );

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: 600 }}>
          Cleaned Data Preview
          <span style={{ color: 'var(--text-muted)', fontWeight: 400, marginLeft: 8, fontSize: '0.8rem' }}>
            {preview.length} batch(es) · {allKeys.length} column(s)
          </span>
        </h3>
        {Object.keys(columnMap || {}).length > 0 && (
          <span className="badge badge-warning" style={{ fontSize: '0.7rem' }}>
            {Object.keys(columnMap).length} columns renamed
          </span>
        )}
      </div>
      <div className="preview-wrap">
        <table className="preview-table">
          <thead>
            <tr>
              <th>Batch ID</th>
              {allKeys.map(k => (
                <th key={k} title={remapped[k] ? `Renamed from: ${remapped[k]}` : k}>
                  {k}
                  {remapped[k] && <span style={{ color: 'var(--warning)', marginLeft: 4 }}>*</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.map((row, i) => (
              <tr key={i}>
                <td style={{ fontFamily: 'var(--mono)', color: 'var(--accent-2)' }}>{row.batch_id}</td>
                {allKeys.map(k => {
                  const v = row.data[k];
                  const display = v === null || v === undefined ? '—' : String(v);
                  const isMissing = v === null || v === undefined;
                  return (
                    <td key={k} className={isMissing ? 'cell-warn' : ''}>
                      {display}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {Object.keys(columnMap || {}).length > 0 && (
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 8 }}>
          * Column was renamed from its original label to the standard model feature name.
        </p>
      )}
    </div>
  );
}

export default function UploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [step, setStep]           = useState(0);
  const [dragging, setDragging]   = useState(false);
  const [file, setFile]           = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState(null);
  const [preview, setPreview]     = useState(null); // UploadPreviewResponse
  const [processingMsg, setProcessingMsg] = useState('');

  const handleFile = useCallback((f) => {
    setFile(f);
    setError(null);
    setPreview(null);
    setStep(1);
  }, []);

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const onFileChange = (e) => {
    const f = e.target.files[0];
    if (f) handleFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      setStep(2); // Reading
      await new Promise(r => setTimeout(r, 300));
      setStep(3); // Extracting
      const result = await uploadBatchFile(file);
      setStep(4); // Validating → cleaning done server-side
      setPreview(result);
      setStep(5);
    } catch (e) {
      setError(e.message);
      setStep(1);
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    if (!preview) return;
    setLoading(true);
    setError(null);
    setProcessingMsg(`Running 9-Agent AI Pipeline on ${preview.total_extracted} batch(es)…`);
    try {
      setStep(6);
      await processBatches(preview.document_id);
      setStep(7);
      navigate(`/results/${preview.document_id}`);
    } catch (e) {
      setError(e.message);
      setStep(5);
    } finally {
      setLoading(false);
      setProcessingMsg('');
    }
  };

  const reset = () => {
    setStep(0); setFile(null); setPreview(null); setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const isPreviewReady = preview && step >= 5;

  return (
    <main className="page-content fade-up">
      <div className="page-header">
        <div className="page-header-left">
          <h1>Batch File Upload</h1>
          <p>Upload your pharmaceutical batch lab-test file to start the AI evaluation pipeline.</p>
        </div>
        {file && (
          <button className="btn btn-outline" onClick={reset}>↺ Reset</button>
        )}
      </div>

      <StepTracker step={step} />

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 24 }}>
          <span>✕</span> <div><strong>Error:</strong> {error}</div>
        </div>
      )}

      {/* Upload Zone */}
      {!isPreviewReady && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div
            className={`upload-zone${dragging ? ' drag-active' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
          >
            <div className="upload-icon">📂</div>
            {file ? (
              <>
                <h3 style={{ color: 'var(--accent-2)' }}>📄 {file.name}</h3>
                <p>{(file.size / 1024).toFixed(1)} KB &nbsp;·&nbsp; Ready to upload</p>
              </>
            ) : (
              <>
                <h3>Drag & drop your batch file here</h3>
                <p>or click to browse from your computer</p>
              </>
            )}
            <div className="file-types">
              {['.csv', '.xlsx', '.xls', '.pdf', '.docx'].map(t => (
                <span key={t} className="file-type-chip">{t}</span>
              ))}
            </div>
          </div>
          <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls,.pdf,.docx" style={{ display: 'none' }} onChange={onFileChange} />

          {file && !loading && step < 2 && (
            <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center' }}>
              <button className="btn btn-primary btn-lg" onClick={handleUpload}>
                ⚡ Start Pipeline — Upload & Analyse
              </button>
            </div>
          )}

          {loading && (
            <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
              <div className="spinner spinner-lg" />
              <p className="pulse" style={{ color: 'var(--text-secondary)' }}>
                {step === 2 ? 'Reading file…' : step === 3 ? 'Extracting batch records…' : step === 4 ? 'Validating & cleaning…' : 'Processing…'}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Preview Panel */}
      {isPreviewReady && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Stats */}
          <div className="stats-row">
            {[
              { label: 'Batches Extracted', value: preview.total_extracted, cls: 'stat-total' },
              { label: 'Valid Batches',      value: preview.validation_reports.filter(r => r.is_valid).length, cls: 'stat-approved' },
              { label: 'With Warnings',      value: preview.validation_reports.filter(r => !r.is_valid).length, cls: 'stat-rework' },
              { label: 'File Format',        value: preview.file_format.toUpperCase(), cls: 'stat-total' },
            ].map(s => (
              <div key={s.label} className="stat-card">
                <div className="stat-label">{s.label}</div>
                <div className={`stat-value ${s.cls}`}>{s.value}</div>
              </div>
            ))}
          </div>

          {/* Validation Report */}
          <div className="card">
            <h3 style={{ marginBottom: 16, fontSize: '0.95rem', fontWeight: 600 }}>
              Agent 3: Validation Report
            </h3>
            <ValidationPanel reports={preview.validation_reports} />
          </div>

          {/* Cleaning Log */}
          {preview.cleaning_log?.length > 0 && (
            <div className="card">
              <h3 style={{ marginBottom: 12, fontSize: '0.95rem', fontWeight: 600 }}>
                Agent 4: Cleaning Log
              </h3>
              <div className="pipeline-log">
                {preview.cleaning_log.map((line, i) => (
                  <div key={i} className="log-line">
                    <span className="log-time">[{String(i+1).padStart(2,'0')}]</span>
                    <span>{line}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Data Preview */}
          <div className="card">
            <DataPreview preview={preview.cleaned_preview} columnMap={preview.column_map || {}} />
          </div>

          {/* Action */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: 12, paddingBottom: 32 }}>
            <button className="btn btn-outline" onClick={reset}>↺ Upload Different File</button>
            <button
              className="btn btn-success btn-lg"
              onClick={handleProcess}
              disabled={loading}
            >
              {loading
                ? <><div className="spinner" style={{ width: 18, height: 18 }} /> {processingMsg || 'Processing…'}</>
                : `▶ Run AI Pipeline on ${preview.total_extracted} Batch(es)`
              }
            </button>
          </div>
        </div>
      )}

      {/* How it works */}
      {step === 0 && (
        <div className="card" style={{ marginTop: 24 }}>
          <h3 style={{ marginBottom: 20, fontWeight: 600, fontSize: '1rem' }}>How the Pipeline Works</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 16 }}>
            {[
              ['1. File Reader',      'Detects format and reads CSV, Excel, PDF, or DOCX'],
              ['2. Extraction',       'Pulls structured batch records from tables or key-value text'],
              ['3. Validation',       'Checks columns, ranges, types and flags anomalies'],
              ['4. Cleaning',         'Imputes missing values, removes duplicates, standardises names'],
              ['5. Feature Eng.',     'Derives 7 composite pharmaceutical process features'],
              ['6. ML Prediction',    'Random Forest predicts Approved / Rework / Rejected'],
              ['7. Decision',         'Applies confidence thresholds for release status'],
              ['8. Recommendation',   'Generates CAPA plan and investigation guidance'],
              ['9. QC Report',        'Compiles downloadable PDF Quality Control report'],
            ].map(([title, desc]) => (
              <div key={title} style={{ display: 'flex', gap: 12 }}>
                <div style={{ color: 'var(--accent-2)', fontWeight: 700, minWidth: 24, fontFamily: 'var(--mono)', fontSize: '0.8rem' }}>⬡</div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: 4 }}>{title}</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );
}
