# ==============================================================================
# LOCAL MASTER ENGINE - AUTO SKOR ESPORTS DESKTOP CONTROLLER (1-CLICK ALL-IN-ONE)
# Menjalankan Python Flask Server Lokal + Edge WebView2 GUI dalam 1 Aplikasi Standalone
# ==============================================================================
import sys
import os
# Prevent PyInstaller windowed crash when sys.stdout is None
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
import re
import json
import queue
import collections
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

exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
bundle_dir = get_bundle_dir()
public_dir = os.path.join(bundle_dir, 'public')
if not os.path.exists(public_dir):
    public_dir = os.path.join(exe_dir, 'public')
if not os.path.exists(public_dir):
    public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')

# ==============================================================================
# LOGIKA SCORING & DATABASE IKAN RINGAN
# ==============================================================================
DEFAULT_CONFIG_POIN = {
    "forgotten": 4,
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


FISH_IMAGE_CACHE = {}

def build_fish_image_cache():
    global FISH_IMAGE_CACHE
    cache = {}
    search_dirs = [
        os.path.join(exe_dir, 'fish_images'),
        os.path.join(exe_dir, 'ikan'),
        os.path.join(exe_dir, 'Hasil_Ikan_Per_Pulau'),
        os.path.join(public_dir, 'fish_images'),
        os.path.join(bundle_dir, 'fish_images'),
        os.path.join(bundle_dir, 'Hasil_Ikan_Per_Pulau')
    ]
    for s_dir in search_dirs:
        if os.path.exists(s_dir):
            for root, _, files in os.walk(s_dir):
                for f in files:
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        full_p = os.path.join(root, f)
                        low_f = f.lower()
                        if low_f not in cache:
                            cache[low_f] = full_p
                        rel_p = os.path.relpath(full_p, s_dir).replace('\\', '/').lower()
                        cache[rel_p] = full_p
                        rel_p2 = f"{os.path.basename(s_dir)}/{rel_p}".lower()
                        cache[rel_p2] = full_p
    FISH_IMAGE_CACHE = cache

build_fish_image_cache()

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
    if "forgotten" in tier_clean:
        kategori = "forgotten"
    elif "secret" in tier_clean:
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
antrean_tangkapan_history = collections.deque(maxlen=100)
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
    candidates = [
        os.path.join(public_dir, 'index.html'),
        os.path.join(bundle_dir, 'index.html'),
        os.path.join(bundle_dir, 'papan_skor.html'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'papan_skor.html'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'index.html')
    ]
    for c in candidates:
        if os.path.exists(c):
            return send_file(c)
    return "<h1>Auto Skor Papan Skor Ready</h1>"

@app.route('/<path:filename>')
def route_static(filename):
    file_path = os.path.join(public_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return route_index()

@app.route('/fish_images/<path:filename>')
@app.route('/ikan/<path:filename>')
@app.route('/Hasil_Ikan_Per_Pulau/<path:filename>')
@app.route('/hasil_ikan_perpulau/<path:filename>')
def route_fish_images_serve(filename):
    clean_fn = urllib.parse.unquote(filename).strip().replace('\\', '/')
    low_fn = clean_fn.lower()
    base_low = os.path.basename(low_fn)

    # 1. Fast O(1) Memory Cache Lookup (Zero disk walk delay)
    cached_path = (
        FISH_IMAGE_CACHE.get(low_fn) or
        FISH_IMAGE_CACHE.get(base_low) or
        FISH_IMAGE_CACHE.get(low_fn.replace('_', ' ')) or
        FISH_IMAGE_CACHE.get(base_low.replace('_', ' '))
    )
    if cached_path and os.path.exists(cached_path):
        return send_file(cached_path)

    # 2. Direct relative path fallback
    for name_variant in [clean_fn, clean_fn.replace('_', ' ')]:
        for base_folder in [exe_dir, public_dir, bundle_dir, r"d:\galatamaapp\AUTO_SKOR"]:
            for sub in ['fish_images', 'ikan', 'Hasil_Ikan_Per_Pulau', '']:
                check_p = os.path.join(base_folder, sub, name_variant)
                if os.path.exists(check_p) and os.path.isfile(check_p):
                    FISH_IMAGE_CACHE[low_fn] = check_p
                    return send_file(check_p)

    return jsonify({"status": "not_found", "file": clean_fn}), 404

@app.route('/api/fish-database')
def route_api_fish_database():
    candidates = [
        os.path.join(bundle_dir, 'fish_database.json'),
        os.path.join(bundle_dir, 'ikan', 'fish_database.json'),
        os.path.join(exe_dir, 'fish_database.json'),
        os.path.join(exe_dir, 'ikan', 'fish_database.json'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fish_database.json'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ikan', 'fish_database.json')
    ]
    for c in candidates:
        if os.path.exists(c):
            return send_file(c, mimetype='application/json')
    return jsonify({})

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
    nama_pemain = str(data.get("player") or data.get("username") or data.get("user") or "").strip()
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

    # Ekstrak otomatis prefix varian jika varian kosong (Aman: lindungi ikan dengan nama kata varian)
    if not varian_bersih:
        # Cek apakah nama utuh sudah merupakan nama ikan resmi di database
        is_known_direct = (nama_ikan_bersih in DATABASE_IKAN) or (nama_ikan_bersih.lower() in [k.lower() for k in DATABASE_IKAN.keys()])
        if not is_known_direct:
            regex_prefix = r'^(big|shiny|mutasi|mutation|mutated|sparkling|rainbow|albino|radioactive|translucent|dark|electric|tiny|golden|ghostly|cosmic|aurora|giant|ikan)\s+'
            base_cand = re.sub(regex_prefix, '', nama_ikan_bersih, flags=re.IGNORECASE).strip()
            if base_cand != nama_ikan_bersih and base_cand:
                extracted_var = nama_ikan_bersih[:len(nama_ikan_bersih) - len(base_cand)].strip()
                varian_bersih = extracted_var
                nama_ikan_bersih = base_cand

    nama_lengkap = f"{varian_bersih} {nama_ikan_bersih}".strip() if varian_bersih else nama_ikan_bersih

    with data_lock:
        cfg = dict(config_poin)

    # Cek info database ikan jika tier kosong atau untuk gambar
    fish_info = DATABASE_IKAN.get(nama_ikan_bersih) or DATABASE_IKAN.get(nama_ikan)
    if not fish_info:
        n_low = nama_ikan_bersih.lower()
        for k, v in DATABASE_IKAN.items():
            if k.lower() == n_low:
                fish_info = v
                break

    if not tier and fish_info and fish_info.get("tier"):
        tier = fish_info.get("tier")

    total_poin, rincian_popup, tier_kategori = hitung_poin_lokal(tier, nama_ikan_bersih, varian_bersih, cfg)

    if total_poin <= 0:
        return jsonify({"status": "ignored", "pesan": f"Ikan '{nama_lengkap}' bukan tier turnamen (0 poin)"})

    img_filename = fish_info.get("filename") if fish_info else f"{nama_ikan_bersih}.png"

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
        "image": f"fish_images/{img_filename}",
        "timestamp": int(time.time() * 1000)
    }

    # Distribusikan ke listener lokal SSE
    with data_lock:
        antrean_tangkapan.append(payload)
        antrean_tangkapan_history.append(payload)
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
        q = queue.Queue(maxsize=50)
        with data_lock:
            if len(sse_listeners) >= 10:
                del sse_listeners[:len(sse_listeners)-9]
            sse_listeners.append(q)
        try:
            # Kirim initial ping
            yield "event: connected\ndata: {\"status\":\"ok\"}\n\n"
            for _ in range(40):
                try:
                    item = q.get(timeout=0.5)
                    yield f"data: {json.dumps(item)}\n\n"
                except queue.Empty:
                    yield ": ping\n\n"
        except GeneratorExit:
            pass
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
    since = request.args.get('since', 0, type=int)
    with data_lock:
        if since > 0:
            data_kirim = [item for item in antrean_tangkapan_history if item.get('timestamp', 0) > since]
            return jsonify(data_kirim)
        else:
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
                for tier_name in ["forgotten", "secret", "mitos", "legend"]:
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
        cached = roblox_cache[cache_key]
        status_code = 200 if cached.get("sukses", False) else 404
        return jsonify(cached), status_code

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
            roblox_cache[cache_key] = res_obj
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

def update_env_file_key(key, val):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(base_dir, '.env')
        lines = []
        found = False
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={val}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            if new_lines and not new_lines[-1].endswith('\n'):
                new_lines[-1] += '\n'
            new_lines.append(f"{key}={val}\n")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        log_local_error(f"Gagal update .env: {e}")
        return False

def verifikasi_roblox_cookie(cookie_str):
    if not cookie_str:
        return {"isValid": False, "pesan": "Cookie belum diatur."}
    clean_cookie = cookie_str.strip().strip('"').strip("'")
    if clean_cookie.startswith(".ROBLOSECURITY="):
        clean_cookie = clean_cookie.split("=", 1)[1].strip()
    
    if "MASUKKAN_" in clean_cookie or "KODE_COOKIE" in clean_cookie:
        return {"isValid": False, "pesan": "Cookie masih berupa teks placeholder."}

    try:
        req = urllib.request.Request(
            'https://users.roblox.com/v1/users/authenticated',
            headers={
                'Cookie': f'.ROBLOSECURITY={clean_cookie}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            uid = data.get('id')
            uname = data.get('name')
            dname = data.get('displayName') or uname
            avatar_url = ""
            try:
                av_req = urllib.request.Request(
                    f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={uid}&size=150x150&format=Png&isCircular=true',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(av_req, timeout=4) as av_resp:
                    av_data = json.loads(av_resp.read().decode())
                    if av_data.get('data') and len(av_data['data']) > 0:
                        avatar_url = av_data['data'][0].get('imageUrl', '')
            except Exception:
                pass
            masked = clean_cookie[:18] + "..." + clean_cookie[-8:] if len(clean_cookie) > 26 else "***"
            return {
                "isValid": True,
                "userId": uid,
                "username": uname,
                "displayName": dname,
                "avatarUrl": avatar_url,
                "masked": masked,
                "cookie": clean_cookie,
                "pesan": f"Akun @{uname} ({dname}) aktif terhubung!"
            }
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return {"isValid": False, "pesan": "Cookie kadaluarsa atau tidak valid (HTTP 401). Silakan ambil ulang dari browser."}
        return {"isValid": False, "pesan": f"Gagal verifikasi ke Roblox (HTTP {e.code})"}
    except Exception as e:
        return {"isValid": False, "pesan": f"Gagal terhubung ke Roblox: {e}"}

@app.route('/cookie-roblox', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@app.route('/api/cookie-roblox', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def route_cookie_roblox():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    
    if request.method == 'GET':
        c = os.environ.get("ROBLOX_COOKIE", "").strip()
        if not c:
            try:
                import config
                c = getattr(config, 'ROBLOX_COOKIE', '')
            except Exception:
                pass
        if not c:
            return jsonify({
                "hasCookie": False,
                "isValid": False,
                "pesan": "Cookie Roblox belum diatur. Klik tombol Cookie untuk menghubungkan akun Roblox."
            })
        res = verifikasi_roblox_cookie(c)
        res["hasCookie"] = bool(c)
        return jsonify(res)

    elif request.method == 'POST':
        data = request.get_json(silent=True) or {}
        new_cookie = str(data.get("cookie") or "").strip().strip('"').strip("'")
        if new_cookie.startswith(".ROBLOSECURITY="):
            new_cookie = new_cookie.split("=", 1)[1].strip()

        if not new_cookie:
            # Hapus cookie jika dikosongkan
            os.environ["ROBLOX_COOKIE"] = ""
            update_env_file_key("ROBLOX_COOKIE", "")
            try:
                import config
                config.ROBLOX_COOKIE = ""
            except Exception:
                pass
            return jsonify({
                "sukses": True,
                "hasCookie": False,
                "isValid": False,
                "pesan": "Cookie Roblox berhasil dihapus."
            })

        val_res = verifikasi_roblox_cookie(new_cookie)
        if not val_res.get("isValid"):
            return jsonify({
                "sukses": False,
                "isValid": False,
                "pesan": val_res.get("pesan", "Cookie tidak valid")
            }), 400

        # Jika valid, simpan ke environment dan file .env
        os.environ["ROBLOX_COOKIE"] = new_cookie
        update_env_file_key("ROBLOX_COOKIE", new_cookie)
        try:
            import config
            config.ROBLOX_COOKIE = new_cookie
        except Exception:
            pass

        val_res["sukses"] = True
        val_res["hasCookie"] = True
        return jsonify(val_res), 200

    elif request.method == 'DELETE':
        os.environ["ROBLOX_COOKIE"] = ""
        update_env_file_key("ROBLOX_COOKIE", "")
        try:
            import config
            config.ROBLOX_COOKIE = ""
        except Exception:
            pass
        return jsonify({
            "sukses": True,
            "hasCookie": False,
            "isValid": False,
            "pesan": "Cookie Roblox berhasil dihapus."
        })

@app.route('/auto-add-friend', methods=['POST', 'OPTIONS'])
@app.route('/api/auto-add-friend', methods=['POST', 'OPTIONS'])
def route_auto_add_friend():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    target_username = str(data.get("username") or "").strip().lstrip('@')
    if not target_username:
        return jsonify({"sukses": False, "pesan": "Username kosong"}), 400

    # 1. Cari info akun di Roblox untuk mendapatkan User ID
    user_id = None
    user_name = target_username
    display_name = target_username
    try:
        req_data = json.dumps({"usernames": [target_username], "excludeBannedUsers": False}).encode('utf-8')
        req = urllib.request.Request(
            'https://users.roblox.com/v1/usernames/users',
            data=req_data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            u_res = json.loads(resp.read().decode())
        users = u_res.get('data', [])
        if users:
            user_id = users[0].get('id')
            user_name = users[0].get('name', target_username)
            display_name = users[0].get('displayName', user_name)
    except Exception:
        pass

    if not user_id and target_username.isdigit():
        user_id = int(target_username)

    if not user_id:
        return jsonify({
            "sukses": False,
            "status": "NOT_FOUND",
            "pesan": f"User '{target_username}' tidak ditemukan di Roblox"
        }), 404

    profile_url = f"https://www.roblox.com/users/{user_id}/profile"

    # 2. Cek apakah ada cookie ROBLOSECURITY di payload JSON atau environment
    roblox_cookie = str(data.get("cookie") or "").strip().strip('"').strip("'")
    if roblox_cookie.startswith(".ROBLOSECURITY="):
        roblox_cookie = roblox_cookie.split("=", 1)[1].strip()
    if not roblox_cookie:
        roblox_cookie = os.environ.get("ROBLOX_COOKIE", "").strip()
    if not roblox_cookie:
        try:
            import config
            roblox_cookie = getattr(config, 'ROBLOX_COOKIE', '')
        except Exception:
            pass

    if not roblox_cookie or "MASUKKAN_" in roblox_cookie or "KODE_COOKIE" in roblox_cookie:
        return jsonify({
            "sukses": True,
            "status": "USER_FOUND",
            "userId": user_id,
            "username": user_name,
            "displayName": display_name,
            "profileUrl": profile_url,
            "pesan": f"Akun @{user_name} ({display_name}) ditemukan! (Cookie belum diatur, silakan atur di tombol Cookie)"
        })

    # 3. Verifikasi bot akun
    bot_res = verifikasi_roblox_cookie(roblox_cookie)
    if not bot_res.get("isValid"):
        return jsonify({
            "sukses": True,
            "status": "USER_FOUND",
            "userId": user_id,
            "username": user_name,
            "displayName": display_name,
            "profileUrl": profile_url,
            "pesan": f"Akun @{user_name} ({display_name}) ditemukan! (Cookie tersimpan tidak valid/kadaluarsa)"
        })

    bot_id = bot_res.get("userId")
    bot_name = bot_res.get("username")

    if bot_id == user_id:
        return jsonify({
            "sukses": True,
            "status": "SELF",
            "userId": user_id,
            "username": user_name,
            "displayName": display_name,
            "profileUrl": profile_url,
            "pesan": f"@{user_name} adalah akun Anda sendiri."
        })

    # 4. Periksa relasi pertemanan via friends/statuses
    try:
        status_req = urllib.request.Request(
            f'https://friends.roblox.com/v1/users/{bot_id}/friends/statuses?userIds={user_id}',
            headers={'Cookie': f'.ROBLOSECURITY={roblox_cookie}', 'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(status_req, timeout=5) as st_resp:
            st_data = json.loads(st_resp.read().decode())
            status_list = st_data.get('data', [])
            if status_list:
                rel_status = status_list[0].get('status')
                if rel_status == "Friends":
                    return jsonify({
                        "sukses": True,
                        "status": "FRIENDS",
                        "userId": user_id,
                        "username": user_name,
                        "displayName": display_name,
                        "profileUrl": profile_url,
                        "pesan": f"@{user_name} sudah berteman dengan akun @{bot_name} di Roblox."
                    })
                elif rel_status == "RequestSent":
                    return jsonify({
                        "sukses": True,
                        "status": "PENDING_SENT",
                        "userId": user_id,
                        "username": user_name,
                        "displayName": display_name,
                        "profileUrl": profile_url,
                        "pesan": f"Permintaan pertemanan ke @{user_name} sudah terkirim (Pending)."
                    })
                elif rel_status == "RequestReceived":
                    return jsonify({
                        "sukses": True,
                        "status": "REQUEST_RECEIVED",
                        "userId": user_id,
                        "username": user_name,
                        "displayName": display_name,
                        "profileUrl": profile_url,
                        "pesan": f"@{user_name} telah mengirim permintaan pertemanan ke akun @{bot_name}."
                    })
    except Exception:
        pass

    # 5. Jika NotFriends, coba kirim permintaan pertemanan
    try:
        csrf_req = urllib.request.Request(
            'https://auth.roblox.com/v1/logout',
            data=b'',
            headers={'Cookie': f'.ROBLOSECURITY={roblox_cookie}', 'User-Agent': 'Mozilla/5.0'}
        )
        csrf_token = None
        try:
            urllib.request.urlopen(csrf_req)
        except urllib.error.HTTPError as e:
            csrf_token = e.headers.get('x-csrf-token')

        friend_req = urllib.request.Request(
            f'https://friends.roblox.com/v1/users/{user_id}/request-friendship',
            data=b'{}',
            headers={
                'Cookie': f'.ROBLOSECURITY={roblox_cookie}',
                'X-CSRF-TOKEN': csrf_token or '',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0'
            }
        )
        with urllib.request.urlopen(friend_req, timeout=5) as fr_resp:
            return jsonify({
                "sukses": True,
                "status": "SENT_SUCCESS",
                "userId": user_id,
                "username": user_name,
                "displayName": display_name,
                "profileUrl": profile_url,
                "pesan": f"Permintaan pertemanan berhasil dikirim ke @{user_name} dari akun @{bot_name}!"
            })
    except urllib.error.HTTPError as e:
        pesan_err = "perlu verifikasi keamanan Roblox" if e.code == 403 else f"HTTP {e.code}"
        return jsonify({
            "sukses": True,
            "status": "CHALLENGE_REQUIRED",
            "userId": user_id,
            "username": user_name,
            "displayName": display_name,
            "profileUrl": profile_url,
            "pesan": f"Akun @{user_name} terdaftar! ({pesan_err}, kirim pertemanan di: {profile_url})"
        })
    except Exception as e:
        return jsonify({
            "sukses": True,
            "status": "USER_FOUND",
            "userId": user_id,
            "username": user_name,
            "displayName": display_name,
            "profileUrl": profile_url,
            "pesan": f"Akun @{user_name} ({display_name}) siap dipasang ke kursi."
        })

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
    player = str(data.get("player") or data.get("username") or "").strip()
    event = str(data.get("event") or "JOIN").strip().upper()
    display_name = str(data.get("displayName") or player).strip()
    user_id = data.get("userId") or 0

    if not player:
        return jsonify({"status": "error", "pesan": "Player wajib diisi"}), 400

    payload = {
        "id": f"presence_{int(time.time()*1000)}_{os.urandom(3).hex()}",
        "type": "PLAYER_PRESENCE",
        "player": player,
        "username": player,
        "displayName": display_name,
        "userId": user_id,
        "event": event,
        "timestamp": int(time.time() * 1000)
    }

    # Distribusikan ke antrean lokal
    with data_lock:
        antrean_tangkapan.append(payload)
        antrean_tangkapan_history.append(payload)
        if len(antrean_tangkapan) > 50:
            del antrean_tangkapan[:-50]
        for q in list(sse_listeners):
            try:
                q.put_nowait(payload)
            except Exception:
                pass

    # Distribusikan ke Cloud Bus (ntfy.sh) secara background
    def sync_presence_cloud():
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

    threading.Thread(target=sync_presence_cloud, daemon=True).start()

    print(f"📋 [AUTO ABSEN] Event {event}: @{player} ({display_name})")
    return jsonify({"status": "ok", "sukses": True, "data": payload})

def unduh_gambar_ke_folder_hasil(data):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(base_dir, 'hasil_ekstraksi_ikan')
        os.makedirs(out_dir, exist_ok=True)

        json_path = os.path.join(out_dir, 'data_ekstraksi_lengkap.json')
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        report_lines = [
            "============================================================",
            "  HASIL EKSTRAKSI GAMBAR IKAN FISH IT! ROBLOX",
            f"  Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Total Ikan Ditemukan: {len(data)}",
            "============================================================\n"
        ]

        downloaded = 0
        for clean_key, item in data.items():
            fish_name = item.get('fish_name', clean_key)
            tier = (item.get('tier') or 'secret').lower()
            if tier not in ['forgotten', 'secret', 'mitos', 'legend']:
                tier = 'secret'

            asset_id = str(item.get('asset_id') or '').strip()
            tier_folder = os.path.join(out_dir, tier)
            os.makedirs(tier_folder, exist_ok=True)

            safe_name = re.sub(r'[^a-zA-Z0-9]+', '_', fish_name.lower()).strip('_') + '.png'
            file_path = os.path.join(tier_folder, safe_name)

            img_url = item.get('web_png_url') or item.get('cdn_delivery')

            if asset_id and asset_id.isdigit():
                try:
                    api_url = f"https://thumbnails.roblox.com/v1/assets?assetIds={asset_id}&size=420x420&format=Png&isCircular=false"
                    req_api = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req_api, timeout=4) as resp:
                        api_data = json.loads(resp.read().decode())
                        if api_data.get('data') and api_data['data'][0].get('imageUrl'):
                            img_url = api_data['data'][0]['imageUrl']
                except Exception:
                    pass

            success = False
            if img_url:
                try:
                    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as img_resp:
                        if img_resp.status == 200:
                            content = img_resp.read()
                            if len(content) > 200:
                                with open(file_path, 'wb') as img_out:
                                    img_out.write(content)
                                success = True
                                downloaded += 1
                except Exception:
                    pass

            status_str = f"BERHASIL DISIMPAN -> {safe_name}" if success else "GAGAL DIUNDUH"
            report_lines.append(f"[{tier.upper()}] {fish_name} (Asset ID: {asset_id}) => {status_str}")

        report_path = os.path.join(out_dir, 'Daftar_Ikan_Ekstraksi.txt')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
        except Exception:
            pass

        # Buka folder otomatis di Windows Explorer
        try:
            import subprocess
            subprocess.Popen(['explorer.exe', out_dir])
        except Exception:
            try:
                os.system(f'explorer "{out_dir}"')
            except Exception:
                pass
    except Exception as e:
        log_local_error(f"Error in unduh_gambar_ke_folder_hasil: {e}")

@app.route('/api/save_to_folder', methods=['POST', 'OPTIONS'])
@app.route('/api/preview_fish_assets', methods=['POST', 'OPTIONS'])
def route_save_to_folder():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"status": "empty", "message": "No data received"}), 400

    threading.Thread(target=unduh_gambar_ke_folder_hasil, args=(data,), daemon=True).start()

    return jsonify({
        "status": "success",
        "message": "Sedang mengunduh dan membuka folder di Windows Explorer...",
        "total_items": len(data)
    }), 200

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

def check_auto_skor_responsive(port=5000):
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{port}/', headers={'User-Agent': 'LocalCheck'})
        with urllib.request.urlopen(req, timeout=0.6) as r:
            if r.status == 200:
                body = r.read().decode('utf-8', errors='ignore')
                return ('FISH IT' in body or 'Auto Skor' in body)
    except Exception:
        pass
    return False

def kill_stale_port_5000():
    try:
        import subprocess
        creationflags = 0x08000000 if os.name == 'nt' else 0
        out = subprocess.check_output('netstat -ano -p tcp', shell=True, text=True, errors='ignore', creationflags=creationflags)
        current_pid = os.getpid()
        for line in out.splitlines():
            if ':5000' in line and 'LISTENING' in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = int(parts[-1])
                    if pid != current_pid and pid > 0:
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True, creationflags=creationflags)
                        time.sleep(0.3)
    except Exception as e:
        log_local_error(f"kill_stale_port error: {e}")

def start_flask_server():
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        log_local_error(f"Flask runner error: {e}")

def log_local_error(msg):
    try:
        appdata = os.environ.get('LOCALAPPDATA', os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(appdata, "master_lokal_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def main():
    import tempfile, uuid

    # Set User Data Folder unik per PID agar WebView2 tidak pernah terkunci 0x800700AA
    wv2_dir = os.path.join(tempfile.gettempdir(), f"AutoSkor_WV2_{os.getpid()}_{uuid.uuid4().hex[:6]}")
    try:
        os.makedirs(wv2_dir, exist_ok=True)
        os.environ['WEBVIEW2_USER_DATA_FOLDER'] = wv2_dir
    except Exception:
        pass

    target_url = "http://127.0.0.1:5000/"

    # 1. Pastikan server Flask berjalan di port 5000
    if not check_auto_skor_responsive(5000):
        if is_port_in_use(5000):
            kill_stale_port_5000()

        flask_thread = threading.Thread(target=start_flask_server, daemon=True)
        flask_thread.start()

        for _ in range(30):
            if check_auto_skor_responsive(5000):
                break
            time.sleep(0.2)

    # 2. Inisialisasi UI WebView2 dengan auto-fallback anti-exit
    t_start = time.time()
    gui_ran_long = False
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
        webview.start(private_mode=False)
        if time.time() - t_start > 3.0:
            gui_ran_long = True
    except Exception as e:
        log_local_error(f"WebView2 GUI init failed ({e}). Mengaktifkan browser fallback...")

    # Jika WebView2 ditutup setelah digunakan lama (>3 detik), keluar secara normal
    if gui_ran_long:
        os._exit(0)

    # 3. Fallback Otomatis: Buka di browser Chrome/Edge dan jaga Flask tetap hidup
    try:
        import webbrowser
        webbrowser.open(target_url)
    except Exception as e2:
        log_local_error(f"Browser fallback failed: {e2}")

    # Jaga Flask tetap berjalan tanpa pernah mati
    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
