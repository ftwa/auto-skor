# ==============================================================================
# LOCAL MASTER ENGINE - AUTO SKOR ESPORTS DESKTOP CONTROLLER (1-CLICK ALL-IN-ONE)
# Menjalankan Python Flask Server Lokal + Edge WebView2 GUI dalam 1 Aplikasi Standalone
# ==============================================================================
import sys
import os
import re
import json
import queue
import threading
import logging
import time
import socket
import urllib.request
import urllib.parse
from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from flask_cors import CORS
import webview

def get_bundle_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

bundle_dir = get_bundle_dir()
public_dir = os.path.join(bundle_dir, 'public')
if not os.path.exists(public_dir):
    public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# ==============================================================================
# LOGIKA SCORING & DATABASE IKAN RINGAN
# ==============================================================================
DEFAULT_CONFIG_POIN = {
    "secret": 3,
    "mitos": 2,
    "legend": 1,
    "bonusBig": 1,
    "bonusShiny": 1,
    "bonusMutasi": 1,
    "ikanKhususNama": "",
    "ikanKhususPoin": 5,
    "khususBigOn": True,
    "khususBigVal": 2,
    "khususShinyOn": True,
    "khususShinyVal": 2,
    "khususMutasiOn": True,
    "khususMutasiVal": 3
}

# Kamus koreksi nama ikan
KAMUS_KOREKSI_NAMA = {
    "stone evolved enchant": "Evolved Enchant Stone",
    "evolved enchant stone": "Evolved Enchant Stone",
    "aurora manatee": "Aurora Manatee",
    "aurora butterfly fish": "Aurora Butterfly Fish"
}

DATABASE_IKAN = {}
db_path = os.path.join(bundle_dir, 'fish_database.json')
if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fish_database.json')

if os.path.exists(db_path):
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            DATABASE_IKAN = json.load(f)
    except Exception:
        pass

def hitung_poin_lokal(tier_str, nama_ikan, varian_str, config_poin):
    tier_clean = str(tier_str).lower().strip()
    nama_clean = str(nama_ikan).lower().strip()
    varian_clean = str(varian_str).lower().strip()

    # 1. Cek Fitur Ikan Khusus (Fleksibel)
    ikan_khusus_nama = str(config_poin.get("ikanKhususNama") or "").strip().lower()
    poin_khusus = int(config_poin.get("ikanKhususPoin", 5))
    khusus_big_on = bool(config_poin.get("khususBigOn", True))
    khusus_big_val = int(config_poin.get("khususBigVal", 2))
    khusus_shiny_on = bool(config_poin.get("khususShinyOn", True))
    khusus_shiny_val = int(config_poin.get("khususShinyVal", 2))
    khusus_mutasi_on = bool(config_poin.get("khususMutasiOn", True))
    khusus_mutasi_val = int(config_poin.get("khususMutasiVal", 3))

    is_ikan_khusus = False
    if ikan_khusus_nama and nama_clean:
        target_list = [k.strip() for k in ikan_khusus_nama.split(",") if k.strip()]
        if any(t in nama_clean for t in target_list):
            is_ikan_khusus = True

    if is_ikan_khusus or "khusus" in tier_clean or "special" in tier_clean:
        kategori = "khusus"
        total = poin_khusus
        rincian = [f"ikan khusus +{poin_khusus}"]

        teks_cek = f"{nama_ikan} {varian_str}".upper()
        if khusus_big_on and re.search(r"\bBIG\b", teks_cek):
            total += khusus_big_val
            if khusus_big_val > 0:
                rincian.append(f"big +{khusus_big_val}")

        if khusus_shiny_on and re.search(r"\bSHINY\b", teks_cek):
            total += khusus_shiny_val
            if khusus_shiny_val > 0:
                rincian.append(f"shiny +{khusus_shiny_val}")

        bukan_mutasi = ["none", "-", "no", "normal", "", "shiny", "big"]
        if khusus_mutasi_on and varian_clean and varian_clean not in bukan_mutasi:
            total += khusus_mutasi_val
            if khusus_mutasi_val > 0:
                rincian.append(f"mutasi +{khusus_mutasi_val}")

        return total, ", ".join(rincian), kategori

    # 2. Tentukan Kategori Tier Standar
    if "secret" in tier_clean:
        kategori = "secret"
    elif "mythic" in tier_clean or "mitos" in tier_clean:
        kategori = "mitos"
    elif "legend" in tier_clean or "legendary" in tier_clean:
        kategori = "legend"
    elif tier_clean in ["normal", "rare", "common", "uncommon"]:
        return 0, "Bukan Tier Turnamen", "normal"
    else:
        kategori = "legend"

    poin_dasar = config_poin.get(kategori, 1)
    total = poin_dasar
    rincian = [f"{kategori} +{poin_dasar}"]

    teks_cek = f"{nama_ikan} {varian_str}".upper()
    if re.search(r"\bBIG\b", teks_cek):
        b = config_poin.get("bonusBig", 1)
        total += b
        rincian.append(f"big +{b}")

    if re.search(r"\bSHINY\b", teks_cek):
        s = config_poin.get("bonusShiny", 1)
        total += s
        rincian.append(f"shiny +{s}")

    bukan_mutasi = ["none", "-", "no", "normal", "", "shiny", "big"]
    if varian_clean and varian_clean not in bukan_mutasi:
        m = config_poin.get("bonusMutasi", 1)
        total += m
        rincian.append(f"mutasi +{m}")

    return total, ", ".join(rincian), kategori

# ==============================================================================
# STATE & CACHE BACKEND
# ==============================================================================
data_lock = threading.Lock()
daftar_peserta_raw = []
antrean_tangkapan = []
sse_listeners = []
mode_sistem = "MATCH"              # Langsung MATCH agar siap terima tangkapan
mode_sumber_aktif = "ROBLOX LANGSUNG"
auto_register_aktif = True         # Auto-register otomatis kursi kosong
config_poin = dict(DEFAULT_CONFIG_POIN)
pemain_online_server = set()
roblox_cache = {}

def bersihkan_nama_kanonikal(nama):
    if not nama:
        return ""
    teks = str(nama).strip().lstrip('@').lower()
    teks = teks.replace("0", "o")
    return re.sub(r"[^a-z0-9]", "", teks)

# ==============================================================================
# FLASK BACKEND SERVER
# ==============================================================================
logging.getLogger('werkzeug').setLevel(logging.ERROR)
app = Flask(__name__, static_folder=public_dir)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def route_index():
    index_file = os.path.join(public_dir, 'index.html')
    if os.path.exists(index_file):
        return send_file(index_file)
    return "<h1>Auto Skor Papan Skor Ready</h1>"

@app.route('/<path:filename>')
def route_static(filename):
    file_path = os.path.join(public_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return route_index()

@app.route('/catch', methods=['POST', 'OPTIONS'])
@app.route('/api/catch', methods=['POST', 'GET', 'OPTIONS'])
def route_catch():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    if request.method == 'GET':
        with data_lock:
            catches = list(antrean_tangkapan[-20:])
        return jsonify({"status": "ok", "mode": mode_sistem, "catches": catches})

    data = request.get_json(silent=True) or {}
    nama_pemain = str(data.get("player") or data.get("username") or "").strip()
    nama_ikan = str(data.get("fish") or data.get("ikan") or "").strip()
    varian = str(data.get("variant") or data.get("varian") or "").strip()
    tier = str(data.get("tier") or "").strip()

    if not nama_pemain or not nama_ikan:
        return jsonify({"status": "error", "pesan": "Player dan fish wajib diisi"}), 400

    gabungan_mentah = f"{varian} {nama_ikan}".strip().lower()
    if gabungan_mentah in KAMUS_KOREKSI_NAMA:
        nama_ikan_bersih = KAMUS_KOREKSI_NAMA[gabungan_mentah]
        varian_bersih = ""
    else:
        nama_ikan_bersih = nama_ikan
        varian_bersih = varian if varian.lower() not in ["none", "-", ""] else ""

    nama_lengkap = f"{varian_bersih} {nama_ikan_bersih}".strip() if varian_bersih else nama_ikan_bersih

    with data_lock:
        cfg = dict(config_poin)

    total_poin, rincian_popup, tier_kategori = hitung_poin_lokal(tier, nama_ikan_bersih, varian_bersih, cfg)

    if total_poin <= 0:
        return jsonify({"status": "ignored", "pesan": f"Ikan '{nama_lengkap}' bukan tier turnamen (0 poin)"})

    payload = {
        "id": f"catch_{int(time.time()*1000)}_{os.urandom(3).hex()}",
        "type": "SYNC_CATCH",
        "user": nama_pemain,
        "ikan": nama_lengkap,
        "fish": nama_ikan_bersih,
        "variant": varian_bersih,
        "rincian": rincian_popup,
        "poin": total_poin,
        "kategori": tier_kategori,
        "tier": tier_kategori,
        "timestamp": int(time.time() * 1000)
    }

    # Distribusikan ke listener lokal SSE
    with data_lock:
        antrean_tangkapan.append(payload)
        if len(antrean_tangkapan) > 50:
            del antrean_tangkapan[:-50]
        for q in list(sse_listeners):
            try:
                q.put_nowait(payload)
            except Exception:
                pass

    # Distribusikan juga ke Cloud Bus (ntfy.sh) secara background non-blocking
    def sync_cloud():
        try:
            req = urllib.request.Request(
                'https://ntfy.sh/galatama_auto_skor_live_bus_v1',
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'Priority': 'urgent'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=3):
                pass
        except Exception:
            pass

    threading.Thread(target=sync_cloud, daemon=True).start()

    return jsonify({"status": "ok", "sukses": True, "data": payload})

@app.route('/stream-poin')
def route_stream_poin():
    def event_generator():
        q = queue.Queue()
        with data_lock:
            sse_listeners.append(q)
        try:
            # Kirim initial ping
            yield "event: connected\ndata: {\"status\":\"ok\"}\n\n"
            while True:
                try:
                    item = q.get(timeout=25)
                    yield f"data: {json.dumps(item)}\n\n"
                except queue.Empty:
                    yield ": ping\n\n"
        finally:
            with data_lock:
                if q in sse_listeners:
                    sse_listeners.remove(q)

    return Response(event_generator(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no'
    })

@app.route('/ambil-poin-baru')
def route_ambil_poin():
    with data_lock:
        data_kirim = list(antrean_tangkapan)
        antrean_tangkapan.clear()
    return jsonify(data_kirim)

@app.route('/set-mode', methods=['POST', 'OPTIONS'])
def route_set_mode():
    global mode_sistem
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    mode_baru = (data.get("mode") or "MATCH").upper()
    with data_lock:
        mode_sistem = mode_baru
        mode_payload = {"tipe": "MODE_CHANGE", "mode": mode_baru, "sumber": "LOCALHOST"}
        for q in list(sse_listeners):
            try:
                q.put_nowait(mode_payload)
            except Exception:
                pass
    return jsonify({"status": "ok", "mode": mode_sistem})

@app.route('/sync-peserta', methods=['POST', 'OPTIONS'])
def route_sync_peserta():
    global daftar_peserta_raw, config_poin, auto_register_aktif
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    peserta_masuk = data.get("peserta", [])
    custom_poin = data.get("warnaPoin")
    is_auto = data.get("autoRegister")

    with data_lock:
        if isinstance(peserta_masuk, list):
            daftar_peserta_raw = [p.strip() for p in peserta_masuk if p and p.strip()]
        if isinstance(custom_poin, dict):
            # Parse matrix jika dikirim dari frontend
            matrix = custom_poin.get("matrix", {})
            if isinstance(matrix, dict):
                for tier_name in ["secret", "mitos", "legend"]:
                    t_obj = matrix.get(tier_name)
                    if isinstance(t_obj, dict):
                        config_poin[tier_name] = int(t_obj.get("base", 1))
                k_obj = matrix.get("khusus")
                if isinstance(k_obj, dict):
                    config_poin["ikanKhususNama"] = str(k_obj.get("nama") or "").strip().lower()
                    config_poin["ikanKhususPoin"] = int(k_obj.get("base", 5))
                    config_poin["khususBigOn"] = bool(k_obj.get("bigOn", True))
                    config_poin["khususBigVal"] = int(k_obj.get("bigVal", 2))
                    config_poin["khususShinyOn"] = bool(k_obj.get("shinyOn", True))
                    config_poin["khususShinyVal"] = int(k_obj.get("shinyVal", 2))
                    config_poin["khususMutasiOn"] = bool(k_obj.get("mutasiOn", True))
                    config_poin["khususMutasiVal"] = int(k_obj.get("mutasiVal", 3))

            for k, v in custom_poin.items():
                if k in config_poin and not isinstance(v, (dict, list)):
                    try:
                        config_poin[k] = int(v)
                    except Exception:
                        pass
        if is_auto is not None:
            auto_register_aktif = bool(is_auto)

    return jsonify({"status": "ok", "total_peserta": len(daftar_peserta_raw)})

@app.route('/cari-roblox', methods=['GET', 'OPTIONS'])
@app.route('/api/cari-roblox', methods=['GET', 'OPTIONS'])
def route_cari_roblox():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    username = request.args.get('username', '').strip().lstrip('@').strip()
    if not username:
        return jsonify({"sukses": False, "pesan": "Username kosong"}), 400

    cache_key = username.lower()
    if cache_key in roblox_cache:
        return jsonify(roblox_cache[cache_key])

    try:
        uid = None
        user_name = username
        display_name = username

        # 1. Jika angka murni, cari User ID Roblox langsung
        if username.isdigit():
            try:
                id_req = urllib.request.Request(
                    f'https://users.roblox.com/v1/users/{username}',
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                with urllib.request.urlopen(id_req, timeout=4) as id_resp:
                    id_data = json.loads(id_resp.read().decode())
                    if id_data and id_data.get('id'):
                        uid = id_data.get('id')
                        user_name = id_data.get('name', username)
                        display_name = id_data.get('displayName', user_name)
            except Exception:
                pass

        # 2. Cari via usernames/users (Roblox resmi lalu Roproxy)
        if not uid:
            req_data = json.dumps({"usernames": [username], "excludeBannedUsers": False}).encode('utf-8')
            endpoints = [
                'https://users.roblox.com/v1/usernames/users',
                'https://users.roproxy.com/v1/usernames/users'
            ]
            for ep in endpoints:
                try:
                    req = urllib.request.Request(
                        ep,
                        data=req_data,
                        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        u_res = json.loads(resp.read().decode())
                    users = u_res.get('data', [])
                    if users:
                        u = users[0]
                        uid = u.get('id')
                        user_name = u.get('name', username)
                        display_name = u.get('displayName', user_name)
                        break
                except Exception:
                    continue

        if not uid:
            res_obj = {"sukses": False, "pesan": "User Roblox tidak ditemukan"}
            return jsonify(res_obj), 404

        # 3. Avatar Headshot (150x150)
        avatar_url = ""
        thumb_endpoints = [
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={uid}&size=150x150&format=Png&isCircular=true",
            f"https://thumbnails.roproxy.com/v1/users/avatar-headshot?userIds={uid}&size=150x150&format=Png&isCircular=true"
        ]
        for tep in thumb_endpoints:
            try:
                treq = urllib.request.Request(tep, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(treq, timeout=4) as t_resp:
                    t_data = json.loads(t_resp.read().decode())
                if t_data.get('data') and len(t_data['data']) > 0:
                    avatar_url = t_data['data'][0].get('imageUrl', '')
                    if avatar_url:
                        break
            except Exception:
                continue

        # 4. Avatar Full Body 3D HD (720x720)
        avatar3d_url = ""
        thumb3d_endpoints = [
            f"https://thumbnails.roblox.com/v1/users/avatar?userIds={uid}&size=720x720&format=Png&isCircular=false",
            f"https://thumbnails.roproxy.com/v1/users/avatar?userIds={uid}&size=720x720&format=Png&isCircular=false"
        ]
        for t3dep in thumb3d_endpoints:
            try:
                t3dreq = urllib.request.Request(t3dep, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(t3dreq, timeout=4) as t3d_resp:
                    t3d_data = json.loads(t3d_resp.read().decode())
                if t3d_data.get('data') and len(t3d_data['data']) > 0:
                    avatar3d_url = t3d_data['data'][0].get('imageUrl', '')
                    if avatar3d_url:
                        break
            except Exception:
                continue

        if not avatar3d_url:
            avatar3d_url = avatar_url
        if not avatar_url:
            avatar_url = f"https://ui-avatars.com/api/?name={urllib.parse.quote(display_name)}&background=0284c7&color=fff&rounded=true"

        result = {
            "sukses": True,
            "userId": uid,
            "username": user_name,
            "userName": user_name,
            "displayName": display_name,
            "avatarUrl": avatar_url,
            "avatar3dUrl": avatar3d_url
        }
        roblox_cache[cache_key] = result
        return jsonify(result)
    except Exception as e:
        fallback = {
            "sukses": True,
            "userId": 0,
            "username": username,
            "userName": username,
            "displayName": username,
            "avatarUrl": f"https://ui-avatars.com/api/?name={urllib.parse.quote(username)}&background=0284c7&color=fff&rounded=true",
            "avatar3dUrl": f"https://ui-avatars.com/api/?name={urllib.parse.quote(username)}&background=0284c7&color=fff&rounded=true"
        }
        return jsonify(fallback)

@app.route('/weather', methods=['POST', 'OPTIONS'])
@app.route('/api/weather', methods=['POST', 'OPTIONS'])
def route_weather():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    player = data.get("player") or "Server Global"
    weather = data.get("weather") or data.get("event") or "Weather Event"
    return jsonify({"status": "ok", "player": player, "event": weather})

@app.route('/player-event', methods=['POST', 'OPTIONS'])
@app.route('/api/player-event', methods=['POST', 'OPTIONS'])
def route_player_event():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    player = (data.get("player") or "").strip()
    event = (data.get("event") or "").strip().upper()
    return jsonify({"status": "ok", "player": player, "event": event})

# ==============================================================================
# RUNNER BACKGROUND & WEBVIEW GUI
# ==============================================================================
def is_port_in_use(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def start_flask_server():
    if is_port_in_use(5000):
        print("[INFO] Server port 5000 sudah berjalan.")
        return
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"[WARN] Flask runner: {e}")

def log_local_error(msg):
    try:
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "master_lokal_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def main():
    # 1. Jalankan server Python Flask di background thread
    try:
        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()
    except Exception as e:
        log_local_error(f"Gagal memulai Flask server thread: {e}")

    # Tunggu sebentar sampai port 5000 siap
    time.sleep(0.6)

    target_url = "http://127.0.0.1:5000/"
    profile_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'AutoSkor_Lokal_Profile')
    try:
        os.makedirs(profile_dir, exist_ok=True)
    except Exception:
        pass

    gui_success = False
    try:
        window = webview.create_window(
            title='[LOKAL / OFFLINE] Auto Skor Galatama - Anti-Lag Localhost 5000',
            url=target_url,
            width=1360,
            height=860,
            min_size=(960, 640),
            background_color='#f8fafc',
            text_select=True,
            confirm_close=False
        )
        webview.start(private_mode=False, storage_path=profile_dir)
        gui_success = True
    except Exception as e:
        log_local_error(f"WebView2 GUI init failed ({e}). Mengaktifkan fallback browser...")

    # Fallback Otomatis: Jika WebView2 belum terpasang atau gagal dibuka di PC user,
    # buka otomatis di browser default (Chrome / Edge / dll) sehingga TIDAK PERNAH MACET!
    if not gui_success:
        try:
            import webbrowser
            print(f"[INFO] Membuka Auto Skor di browser default: {target_url}")
            webbrowser.open(target_url)
            # Jaga proses agar server Flask tetap berjalan
            while True:
                time.sleep(1)
        except Exception as e2:
            log_local_error(f"Browser fallback failed: {e2}")
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, f"Auto Skor Localhost aktif di:\n{target_url}\n\nSilakan buka link tersebut di Chrome atau Edge.", "Auto Skor Ready", 0x40)
                while True:
                    time.sleep(1)
            except Exception:
                pass

    sys.exit(0)

if __name__ == '__main__':
    main()
