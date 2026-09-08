import httpx

try:
    r = httpx.get("http://localhost:8000/api/model-info", timeout=3.0)
    print("Localhost 8000 status:", r.status_code)
except Exception as e:
    print("Localhost 8000 error:", e)

try:
    r = httpx.get("http://127.0.0.1:8000/api/model-info", timeout=3.0)
    print("127.0.0.1 8000 status:", r.status_code)
except Exception as e:
    print("127.0.0.1 8000 error:", e)
