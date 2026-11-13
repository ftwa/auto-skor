# ==============================================================================
# LOCAL DEV SERVER - PAPAN SKOR ROBLOX CYBER HUD
# Menjalankan frontend statis + API pencarian akun & API 3D Model Roblox
# ==============================================================================
import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

AUTO_SKOR_DIR = r"D:\galatamaapp\AUTO_SKOR"
if AUTO_SKOR_DIR not in sys.path:
    sys.path.append(AUTO_SKOR_DIR)

try:
    from roblox_api import cari_profil_roblox, ambil_avatar_3d_lengkap
except Exception as e:
    print(f"[WARN] roblox_api tidak dapat diimpor langsung: {e}")
    cari_profil_roblox = None
    ambil_avatar_3d_lengkap = None

PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CACHE_DIR = os.path.join(AUTO_SKOR_DIR, "roblox_3d_cache")

class SkorDevHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API Cari Akun Roblox
        if path == '/api/cari-roblox':
            username = query.get('username', [''])[0].strip()
            if not username:
                self.send_json({"sukses": False, "pesan": "Username wajib diisi"}, 400)
                return

            if cari_profil_roblox:
                res, status = cari_profil_roblox(username)
                self.send_json(res, status)
            else:
                self.send_json({"sukses": False, "pesan": "Modul roblox_api tidak aktif"}, 500)
            return

        # 2. API Model 3D Roblox (OBJ & Textures)
        if path == '/api/roblox-3d-model':
            target = query.get('username', [''])[0].strip() or query.get('userId', [''])[0].strip()
            if not target:
                self.send_json({"sukses": False, "pesan": "Parameter username atau userId diperlukan"}, 400)
                return

            if ambil_avatar_3d_lengkap:
                res, status = ambil_avatar_3d_lengkap(target)
                self.send_json(res, status)
            else:
                self.send_json({"sukses": False, "pesan": "Modul roblox_api tidak aktif"}, 500)
            return

        # 3. Serve roblox_3d_cache files
        if path.startswith('/roblox_3d_cache/'):
            rel_path = path[len('/roblox_3d_cache/'):]
            full_path = os.path.normpath(os.path.join(CACHE_DIR, rel_path))
            if full_path.startswith(CACHE_DIR) and os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if full_path.endswith('.obj'):
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                elif full_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif full_path.endswith('.json'):
                    self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(os.path.getsize(full_path)))
                self.end_headers()
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # Default: Static files from public/
        return super().do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def main():
    port = 8086
    server = HTTPServer(('127.0.0.1', port), SkorDevHandler)
    print(f"[INFO] Server Dev berjalan di http://localhost:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server dihentikan.")

if __name__ == '__main__':
    main()
