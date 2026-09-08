import os
import sys
import httpx

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_api_batch_testing_data")

def test_all():
    print("=" * 60)
    print("TESTING ALL 10 SYNTHETIC DAY FILES")
    print("=" * 60)
    
    passed_files = 0
    total_batches = 0
    
    for i in range(1, 11):
        filename = f"Day_{i:02d}.csv"
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[SKIP] {filename} not found.")
            continue
            
        with open(filepath, "rb") as f:
            file_bytes = f.read()
            
        # Phase 1: Upload
        try:
            up_res = httpx.post(
                f"{BASE_URL}/upload",
                files={"file": (filename, file_bytes, "text/csv")},
                timeout=30.0
            )
            if up_res.status_code != 200:
                print(f"[FAIL] {filename} upload failed: HTTP {up_res.status_code} - {up_res.text[:200]}")
                continue
                
            up_data = up_res.json()
            doc_id = up_data["document_id"]
            extracted = up_data["total_extracted"]
            has_errors = up_data.get("has_errors", False)
            print(f"[UPLOAD OK] {filename}: doc_id={doc_id}, extracted={extracted}, has_errors={has_errors}")
            
            # Phase 2: Process (longer timeout for 20 batches + SHAP + PDF)
            proc_res = httpx.post(f"{BASE_URL}/process/{doc_id}", timeout=300.0)
            if proc_res.status_code != 200:
                print(f"[FAIL] {filename} process failed: HTTP {proc_res.status_code} - {proc_res.text[:200]}")
                continue
                
            proc_data = proc_res.json()
            results = proc_data.get("results", [])
            
            decisions = {}
            for r in results:
                d = r["decision"]
                decisions[d] = decisions.get(d, 0) + 1
                
            passed_files += 1
            total_batches += len(results)
            print(f"[PASS] {filename}: Processed {len(results)}/{extracted} batches | Outcomes: {decisions}")
            
        except Exception as e:
            print(f"[FAIL] {filename} encountered exception: {e}")
            
    print("=" * 60)
    print(f"Summary: {passed_files}/10 files passed | Total {total_batches} batches processed")
    print("=" * 60)

if __name__ == "__main__":
    test_all()
