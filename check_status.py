from housekeeping.models.database import housekeeping_db

def check_online_status():
    print("--- Checking Online Status for Worker 39 ---")
    hk_db = housekeeping_db
    is_online = hk_db.get_worker_online_status(39)
    print(f"Worker 39 Online Status: {is_online}")

if __name__ == "__main__":
    check_online_status()
