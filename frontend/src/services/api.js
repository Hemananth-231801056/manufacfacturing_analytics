const BASE = 'http://127.0.0.1:8000/api';

const handle = async (res) => {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
};

export const uploadBatchFile = async (file) => {
  const form = new FormData();
  form.append('file', file);
  return handle(await fetch(`${BASE}/upload`, { method: 'POST', body: form }));
};

export const processBatches = async (documentId) =>
  handle(await fetch(`${BASE}/process/${documentId}`, { method: 'POST' }));

export const getDocuments = async () =>
  handle(await fetch(`${BASE}/documents`));

export const getDocumentPredictions = async (docId) =>
  handle(await fetch(`${BASE}/documents/${docId}/predictions`));

export const getPredictions = async (page = 1, perPage = 20, filter = 'all') =>
  handle(await fetch(`${BASE}/predictions?page=${page}&per_page=${perPage}&decision_filter=${filter}`));

export const getPredictionDetail = async (id) =>
  handle(await fetch(`${BASE}/predictions/${id}`));

export const downloadReport = async (predictionId, batchId) => {
  const res = await fetch(`${BASE}/reports/${predictionId}/download`);
  if (!res.ok) throw new Error('Report not found');
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `QC_Report_${batchId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};

export const downloadAllReports = async (documentId) => {
  const res = await fetch(`${BASE}/reports/download-all/${documentId}`);
  if (!res.ok) throw new Error('Zip file not found');
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `Batch_Reports_Doc_${documentId}.zip`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
};

export const getModelInfo = async () =>
  handle(await fetch(`${BASE}/model-info`));
