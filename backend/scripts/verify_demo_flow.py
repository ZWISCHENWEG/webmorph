import sys

import httpx

BASE_URL = "http://localhost:8000"

def verify_endpoints():
    print("🔍 Verifying MVP Demo API Endpoints...")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # Wait for the API to be up
        try:
            health = client.get("/api/health")
            health.raise_for_status()
            print("✅ API is up and running.")
        except Exception as e:
            print(f"❌ API is unreachable at {BASE_URL}: {e}")
            sys.exit(1)

        # Collectors
        print("\n--- Collectors ---")
        res = client.get("/api/collectors")
        res.raise_for_status()
        collectors = res.json()["data"]
        print(f"✅ GET /api/collectors returned {len(collectors)} items.")
        
        collector_id = collectors[0]["id"]
        res = client.get(f"/api/collectors/{collector_id}")
        res.raise_for_status()
        print(f"✅ GET /api/collectors/{collector_id} successful.")

        res = client.get(f"/api/collectors/{collector_id}/snapshots")
        res.raise_for_status()
        print(f"✅ GET /api/collectors/{collector_id}/snapshots successful.")

        # Incidents
        print("\n--- Incidents ---")
        res = client.get("/api/incidents")
        res.raise_for_status()
        incidents = res.json()["data"]
        print(f"✅ GET /api/incidents returned {len(incidents)} items.")
        
        incident_id = incidents[0]["id"]
        res = client.get(f"/api/incidents/{incident_id}")
        res.raise_for_status()
        print(f"✅ GET /api/incidents/{incident_id} successful.")

        # Trigger run
        print("\n--- Runs ---")
        res = client.post(f"/api/collectors/{collector_id}/runs")
        res.raise_for_status()
        run_data = res.json()
        print(f"✅ POST /api/collectors/{collector_id}/runs triggered run ID {run_data.get('id')} successfully.")

        # Heal Request (Should succeed or say already requested)
        print("\n--- Healing ---")
        res = client.post(f"/api/incidents/{incident_id}/heal")
        if res.status_code in (200, 202):
            print(f"✅ POST /api/incidents/{incident_id}/heal requested successfully.")
        elif res.status_code == 400 and "Incident must be DIAGNOSING" in res.text:
            print(f"✅ POST /api/incidents/{incident_id}/heal handled correctly (already processed).")
        else:
            res.raise_for_status()

        # Approve Heal
        res = client.post(f"/api/incidents/{incident_id}/approve", json={"approved": True})
        res.raise_for_status()
        print(f"✅ POST /api/incidents/{incident_id}/approve succeeded.")

        # Wait for worker to finish processing the approval in demo mode
        import time
        time.sleep(2)

        # Verify Heal (Might be handled by worker instantly in demo mode)
        res = client.post(f"/api/incidents/{incident_id}/verify")
        if res.status_code in (200, 202):
            print(f"✅ POST /api/incidents/{incident_id}/verify succeeded.")
        elif res.status_code == 400 and ("got RECOVERED" in res.text or "got VERIFYING" in res.text):
             print(f"✅ POST /api/incidents/{incident_id}/verify handled correctly (already verifying/recovered).")
        else:
            res.raise_for_status()

        print("\n🎉 All endpoints verified successfully!")

if __name__ == "__main__":
    verify_endpoints()
