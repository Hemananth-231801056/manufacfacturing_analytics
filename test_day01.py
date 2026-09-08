import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.main import app

client = TestClient(app)

def test_day_01():
    day1_path = os.path.join(os.path.dirname(__file__), "synthetic_api_batch_testing_data", "Day_01.csv")
    with open(day1_path, "rb") as f:
        file_bytes = f.read()

    print("[Test Day 01] Uploading Day_01.csv...")
    upload_res = client.post("/api/upload", files={"file": ("Day_01.csv", file_bytes, "text/csv")})
    print(f"[Test Day 01] Upload Status: {upload_res.status_code}")
    print("[Test Day 01] Upload Response:")
    upload_json = upload_res.json()
    print(upload_json)

    doc_id = upload_json.get("document_id")
    if doc_id:
        print(f"[Test Day 01] Processing document {doc_id}...")
        proc_res = client.post(f"/api/process/{doc_id}")
        print(f"[Test Day 01] Process Status: {proc_res.status_code}")
        proc_json = proc_res.json()
        print(f"[Test Day 01] Total Processed: {proc_json.get('total_processed')}")
        results = proc_json.get("results", [])
        for r in results[:5]:
            print(f"  - Batch {r['batch_id']}: Decision = {r['decision']} (Confidence: {r['confidence']:.2f})")
    else:
        print("[Test Day 01] Failed to get document_id!")

if __name__ == "__main__":
    test_day_01()
