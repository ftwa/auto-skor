# ==============================================================================
# ROBLOX_API.PY - Modul Pencarian Akun & Avatar Roblox Resmi
# ==============================================================================
import requests

HEADERS_ROBLOX = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def cari_profil_roblox(username_mentah):
    """
    Mencari User ID, Display Name, dan URL Avatar Headshot langsung dari CDN Roblox.
    Dilengkapi penanganan rate limit (429) dan timeout jaringan.
    """
    username = str(username_mentah).strip().lstrip('@')
    if not username:
        return {"sukses": False, "pesan": "Username kosong"}, 400

    try:
        user_id = None
        user_name = username
        display_name = username

        if username.isdigit():
            # Coba cari sebagai user_id langsung
            try:
                u_res = requests.get(f"https://users.roblox.com/v1/users/{username}", headers=HEADERS_ROBLOX, timeout=4)
                if u_res.status_code == 200:
                    u_data = u_res.json()
                    if u_data and u_data.get('id'):
                        user_id = u_data.get('id')
                        user_name = u_data.get('name', username)
                        display_name = u_data.get('displayName', user_name)
            except Exception:
                pass

        if not user_id:
            # 1. Cari User ID berdasarkan Username resmi
            payload = {"usernames": [username], "excludeBannedUsers": False}
            res = requests.post("https://users.roblox.com/v1/usernames/users", json=payload, headers=HEADERS_ROBLOX, timeout=6)

            if res.status_code == 429:
                return {"sukses": False, "pesan": "Roblox API sedang sibuk (Rate Limit). Mohon tunggu beberapa detik."}, 429

            if res.status_code != 200:
                return {"sukses": False, "pesan": f"Gagal menghubungi server Roblox (HTTP {res.status_code})"}, res.status_code

            data = res.json().get('data', [])
            if not data:
                return {"sukses": False, "pesan": "Pemain tidak ditemukan di Roblox"}, 404

            user_info = data[0]
            user_id = user_info['id']
            user_name = user_info['name']
            display_name = user_info.get('displayName', user_name)

        # 2. Ambil Foto Avatar Headshot resmi dari CDN Roblox
        thumb_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=true"
        thumb_res = requests.get(thumb_url, headers=HEADERS_ROBLOX, timeout=6)
        avatar_url = ""

        if thumb_res.status_code == 200:
            try:
                thumb_data = thumb_res.json().get('data', [])
                if thumb_data and thumb_data[0].get('imageUrl'):
                    avatar_url = thumb_data[0]['imageUrl']
            except Exception:
                pass

        # 3. Ambil 3D Avatar Full Body resmi peserta (HD 720x720)
        avatar3d_url = ""
        try:
            url_3d = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false"
            res_3d = requests.get(url_3d, headers=HEADERS_ROBLOX, timeout=5)
            if res_3d.status_code == 200:
                d3d = res_3d.json().get('data', [])
                if d3d and d3d[0].get('imageUrl'):
                    avatar3d_url = d3d[0]['imageUrl']
        except Exception:
            pass

        if not avatar3d_url:
            avatar3d_url = avatar_url

        if not avatar_url:
            avatar_url = f"https://ui-avatars.com/api/?name={requests.utils.quote(display_name)}&background=0284c7&color=fff&rounded=true&bold=true"

        return {
            "sukses": True,
            "userId": user_id,
            "userName": user_name,
            "username": user_name,
            "displayName": display_name,
            "avatarUrl": avatar_url,
            "avatar3dUrl": avatar3d_url
        }, 200

    except requests.exceptions.Timeout:
        return {"sukses": False, "pesan": "Koneksi ke server Roblox timeout. Periksa koneksi internet Anda."}, 504
    except Exception as e:
        return {"sukses": False, "pesan": f"Terjadi kesalahan: {str(e)}"}, 500

# ==============================================================================
# EKSTRAKSI & CACHING AVATAR 3D RESMI PEMAIN (OBJ & TEXTURES)
# ==============================================================================
import os
import json
from config import ROBLOX_COOKIE

CACHE_3D_DIR = "roblox_3d_cache"
os.makedirs(CACHE_3D_DIR, exist_ok=True)

def ambil_avatar_3d_lengkap(username_or_id):
    """
    Mengambil model 3D utuh (Wavefront .OBJ) dan tekstur material asli dari akun Roblox pemain.
    Dilengkapi sistem cache lokal untuk kecepatan instan (0ms) pada pemanggilan berikutnya.
    """
    identifier = str(username_or_id).strip().lstrip('@')
    if not identifier:
        return {"sukses": False, "pesan": "Username atau User ID kosong"}, 400

    uid = None
    user_name = identifier
    display_name = identifier

    # 1. Cek jika identifier sudah berupa User ID angka
    if identifier.isdigit():
        uid = int(identifier)
    else:
        # Resolve username ke User ID resmi Roblox
        try:
            payload = {"usernames": [identifier], "excludeBannedUsers": False}
            r_user = requests.post("https://users.roblox.com/v1/usernames/users", json=payload, headers=HEADERS_ROBLOX, timeout=6)
            if r_user.status_code == 200 and r_user.json().get('data'):
                uinfo = r_user.json()['data'][0]
                uid = uinfo['id']
                user_name = uinfo['name']
                display_name = uinfo.get('displayName', user_name)
        except Exception as e:
            pass

    if not uid:
        return {"sukses": False, "pesan": f"Pemain '{identifier}' tidak ditemukan di Roblox"}, 404

    user_dir = os.path.join(CACHE_3D_DIR, str(uid))
    os.makedirs(user_dir, exist_ok=True)
    obj_file = os.path.join(user_dir, "avatar.obj")
    meta_file = os.path.join(user_dir, "meta.json")

    # Jika file sudah dicache dan valid, langsung kirim dari disk!
    if os.path.exists(obj_file) and os.path.exists(meta_file) and os.path.getsize(obj_file) > 1000:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if "materials" in meta and meta["materials"]:
                meta["cached"] = True
                return meta, 200
        except Exception:
            pass

    # 2. Ambil 3D Avatar Manifest menggunakan sesi Roblox Cookie
    try:
        cookie_val = ROBLOX_COOKIE
        if cookie_val.startswith('.ROBLOSECURITY='):
            cookies = {'.ROBLOSECURITY': cookie_val.split('=', 1)[1]}
        else:
            cookies = {'.ROBLOSECURITY': cookie_val}

        url_3d = f"https://thumbnails.roblox.com/v1/users/avatar-3d?userId={uid}"
        r_3d = requests.get(url_3d, cookies=cookies, headers=HEADERS_ROBLOX, timeout=7)
        if r_3d.status_code != 200 or not r_3d.json().get('imageUrl'):
            return {"sukses": False, "pesan": f"Roblox 3D API mengembalikan status {r_3d.status_code}"}, r_3d.status_code

        manifest_url = r_3d.json()['imageUrl']
        r_manifest = requests.get(manifest_url, headers=HEADERS_ROBLOX, timeout=7)
        if r_manifest.status_code != 200:
            return {"sukses": False, "pesan": "Gagal mengunduh manifest 3D Roblox"}, 502

        m_data = r_manifest.json()
        obj_hash = m_data.get('obj')
        mtl_hash = m_data.get('mtl')
        tex_hashes = m_data.get('textures', [])

        if not obj_hash:
            return {"sukses": False, "pesan": "Manifest 3D tidak memiliki objek mesh"}, 500

        # Helper downloader multi-subdomain
        def unduh_dari_cdn(item_hash, min_len=50):
            if not item_hash: return None
            for sub in ['t3', 't4', 't2', 't1', 't0', 't5', 't6', 't7']:
                try:
                    r = requests.get(f"https://{sub}.rbxcdn.com/{item_hash}", headers={'User-Agent': 'Roblox/WinInet'}, cookies=cookies, timeout=6)
                    if r.status_code == 200 and len(r.content) >= min_len:
                        return r.content
                except Exception:
                    pass
            return None

        # 3. Download OBJ file dari node CDN aktif
        obj_bytes = unduh_dari_cdn(obj_hash, min_len=1000)
        if not obj_bytes:
            return {"sukses": False, "pesan": "Gagal mengunduh file mesh 3D dari CDN Roblox"}, 502

        with open(obj_file, 'wb') as f:
            f.write(obj_bytes)

        # 4. Unduh & Parse Definisi Material MTL Resmi Roblox
        mtl_text = ""
        if mtl_hash:
            mtl_bytes = unduh_dari_cdn(mtl_hash, min_len=20)
            if mtl_bytes:
                mtl_text = mtl_bytes.decode('utf-8', errors='ignore')

        raw_materials = {}
        curr_mtl = None
        if mtl_text:
            for line in mtl_text.splitlines():
                line = line.strip()
                if line.startswith('newmtl '):
                    curr_mtl = line.split(maxsplit=1)[1]
                    raw_materials[curr_mtl] = {'kd': [1.0, 1.0, 1.0], 'map': None, 'overlay': False}
                elif curr_mtl:
                    if line.startswith('Kd '):
                        parts = line.split()
                        try:
                            raw_materials[curr_mtl]['kd'] = [float(parts[1]), float(parts[2]), float(parts[3])]
                        except Exception:
                            pass
                    elif line.startswith('map_Kd '):
                        raw_materials[curr_mtl]['map'] = line.split(maxsplit=1)[1]
                    elif 'alphamode overlay' in line:
                        raw_materials[curr_mtl]['overlay'] = True

        # 5. Download Texture files
        from PIL import Image
        tex_cache = {}
        all_th_needed = set(tex_hashes + [v['map'] for v in raw_materials.values() if v.get('map')])
        for th in all_th_needed:
            if not th: continue
            t_file = os.path.join(user_dir, f"{th}.png")
            if not os.path.exists(t_file) or os.path.getsize(t_file) < 50:
                t_bytes = unduh_dari_cdn(th, min_len=50)
                if t_bytes:
                    with open(t_file, 'wb') as f:
                        f.write(t_bytes)
            if os.path.exists(t_file):
                tex_cache[th] = t_file

        # 6. Susun Pemetaan Material Akurat
        final_materials = {}
        for mat_name, mat_info in raw_materials.items():
            th = mat_info.get('map')
            if not th or th not in tex_cache:
                continue
            tex_path = tex_cache[th]
            final_tex_filename = f"{th}.png"

            # Jika material berupa decal wajah overlay, lekatkan di atas warna kulit asli (Kd)
            if mat_info.get('overlay'):
                try:
                    face_im = Image.open(tex_path).convert('RGBA')
                    kd = mat_info['kd']
                    bg_color = (int(kd[0] * 255), int(kd[1] * 255), int(kd[2] * 255), 255)
                    comp = Image.new('RGBA', face_im.size, bg_color)
                    comp.paste(face_im, (0, 0), face_im)
                    comp_filename = f"comp_{th}.png"
                    comp.save(os.path.join(user_dir, comp_filename))
                    final_tex_filename = comp_filename
                except Exception as comp_err:
                    print("Composite face error:", comp_err)

            final_materials[mat_name] = {
                'textureUrl': f"/roblox_3d_cache/{uid}/{final_tex_filename}",
                'color': mat_info['kd'],
                'overlay': mat_info['overlay'],
                'isAccessory': mat_name.lower().startswith('handle')
            }

        texture_urls = [m['textureUrl'] for m in final_materials.values()]

        meta_result = {
            "sukses": True,
            "userId": uid,
            "userName": user_name,
            "username": user_name,
            "displayName": display_name,
            "objUrl": f"/roblox_3d_cache/{uid}/avatar.obj",
            "materials": final_materials,
            "textureUrls": texture_urls,
            "aabb": m_data.get('aabb'),
            "camera": m_data.get('camera'),
            "cached": False
        }

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta_result, f, indent=2)

        return meta_result, 200

    except requests.exceptions.Timeout:
        return {"sukses": False, "pesan": "Timeout saat menghubungi CDN Roblox"}, 504
    except Exception as e:
        return {"sukses": False, "pesan": f"Terjadi kesalahan saat memproses 3D avatar: {str(e)}"}, 500
