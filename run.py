"""
Main Application Launcher for UMKM Geospatial & Product Scraper Suite + Shopee Studio
"""
import os
import sys
import socket
import uvicorn
from database.db_manager import DatabaseManager
from seed_data import seed_database

def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(preferred_ports=[8080, 8001, 8008, 8888, 5000, 8000]) -> int:
    for port in preferred_ports:
        if is_port_available(port):
            return port
    # Fallback to any free OS port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def setup_and_run():
    print("==================================================================")
    print("   PETA UMKM & Shopee Scraper Studio Intelligence Suite          ")
    print("==================================================================")
    
    # Initialize DB & seed if not present
    db = DatabaseManager()
    stats = db.get_stats()
    if stats["total_umkm"] == 0:
        print("[*] Database is empty. Seeding initial verified UMKM dataset...")
        seed_database()
    else:
        print(f"[*] Database initialized: {stats['total_umkm']} UMKM, {stats['total_products']} products.")

    port = find_available_port()
    
    print(f"\n[*] Starting FastAPI Server on http://127.0.0.1:{port}")
    print(f"[*] Access Shopee Scraper Studio at: http://127.0.0.1:{port}/shopee")
    print(f"[*] Access Actor Platform at:       http://127.0.0.1:{port}/")
    print("[*] Press Ctrl+C to terminate.\n")
    
    uvicorn.run("backend.server:app", host="127.0.0.1", port=port, reload=False)

if __name__ == "__main__":
    setup_and_run()
