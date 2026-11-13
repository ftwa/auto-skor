// ==============================================================================
// VERCEL SERVERLESS FUNCTION - 3D ROBLOX AVATAR MODEL (OBJ & MATERIALS)
// Mengambil model 3D nyata (.OBJ) dan material langsung dari CDN resmi Roblox
// ==============================================================================

const FALLBACK_COOKIE = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEQAhoGCAIQBBgBIhsKBGR1aWQSEzE5NTExMDAyNjE3ODUxNTc4NDYiFgoFdW5hbWUSDWJsdWVwcmludDAwNzUiEQoDdWlkEgo5OTc0OTIwMzU1KAM.5fJL9qYfjEUy2YVZE_OwlFDpsFD1yV0hJAokzedqqz-6dHV7Pq22DLdoNPukrIyPq-l7pAfeEz_-YkoaHi18pRaCZpqMG_NeMinp9RWJpEH6rtwBXcGpyv2vtE88q6lCZACNC1ubPMdB5BaEe8KdS-SVlx4btzsSydFD2DmM9xgDmkoW59TPKFvWncx0qIsw4ngd7BRq5fn5016-81ibeuEg8Yje3NL-HJHzqThYUEE_LMS4AWaCHtaxATQlTFrrCSV0PefHCok27Z1i0yI8wsUpFIOdfMNwxlFQ6Fj54FbB4_5uN8fzBnWhoo90t0Hf2RzrLZ0Q2yRJ3wpU8IqP54cIPqZxvrovmTxddmlSqZw86dKroBkPi2buxi0kUyeTKStHk42FWYPgrpdvL-D4oPffsFKeDiRgSkVHC166qY92KGp69ObB73V308lc-5gE2vkCoX-dV5SprysVD_E-zvbAswTbazQTTrCRwXbyCJWq1-EwYi-RiShH5izMNjT-D6djnb6D6cqEjDax79_UVQO79mwvdTi72FdXIfTVfchK8OLoT2WTnU-V3Pi11XLeZjl3YCmq_qw0T316xIdZTBuHxCk91-p1AwAr7vjPAlx26yUk87S7uCh7KECQ0ln5SLR_LmgHxR1vYN8HZt33LFIi8UK73ySzRZCubVNgV4CMpgO2-eMgN0CAXAuEVHa-qEKT4mKRqU7I7Yn4YkEJDP0srv0Bad-PyYbOnwhTGbmXopl_W55MlUXHslZl7uBfGFkrs931du0APjSiJrPkKV71qIMB61XxfeIG-vKXCbL3zWyWKi97_gPl38r76ScpVhaXzE3D9p5gGShqORjyTuqLooSg14dhWmdaaiGcNZDsbtOQ46AuxH0rvayWhmbfmUouJt8Jqp8bUkjT3osPkYIphc2uacwbXjeYtLoNw_A.ESSDPPuevKB6FjQceq8yafCCP0";

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const requestUrl = new URL(req.url, `https://${req.headers.host || 'localhost'}`);
  const target = (requestUrl.searchParams.get('username') || requestUrl.searchParams.get('userId') || req.query.username || req.query.userId || '').trim().replace(/^@+/, '');

  if (!target) {
    return res.status(400).json({ sukses: false, pesan: 'Parameter username atau userId wajib diisi' });
  }

  const cookie = process.env.ROBLOX_COOKIE || FALLBACK_COOKIE;

  try {
    let userId = null;
    let userName = target;
    let displayName = target;

    // 1. Resolve User ID jika input berupa username
    if (/^\d+$/.test(target)) {
      userId = target;
    } else {
      const uRes = await fetch('https://users.roblox.com/v1/usernames/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ usernames: [target], excludeBannedUsers: false })
      });
      if (uRes.ok) {
        const uData = await uRes.json();
        if (uData.data && uData.data[0]) {
          userId = uData.data[0].id;
          userName = uData.data[0].name;
          displayName = uData.data[0].displayName || userName;
        }
      }
    }

    if (!userId) {
      return res.status(404).json({ sukses: false, pesan: `Pemain '${target}' tidak ditemukan di Roblox` });
    }

    // 2. Ambil 3D Avatar Manifest dari Roblox
    const r3d = await fetch(`https://thumbnails.roblox.com/v1/users/avatar-3d?userId=${userId}`, {
      headers: {
        'Cookie': `.ROBLOSECURITY=${cookie}`,
        'User-Agent': 'Roblox/WinInet'
      }
    });

    if (!r3d.ok) {
      return res.status(r3d.status).json({ sukses: false, pesan: `Roblox API 3D error HTTP ${r3d.status}` });
    }

    const r3dData = await r3d.json();
    const manifestUrl = r3dData.imageUrl;
    if (!manifestUrl) {
      return res.status(502).json({ sukses: false, pesan: 'Manifest 3D tidak tersedia untuk akun ini' });
    }

    const mRes = await fetch(manifestUrl);
    if (!mRes.ok) {
      return res.status(502).json({ sukses: false, pesan: 'Gagal mengunduh manifest 3D' });
    }

    const mData = await mRes.json();
    const objHash = mData.obj;
    const mtlHash = mData.mtl;
    const texHashes = mData.textures || [];

    if (!objHash) {
      return res.status(500).json({ sukses: false, pesan: 'Objek mesh 3D tidak ditemukan dalam manifest' });
    }

    // Helper fetch multi-subdomain CDN Roblox
    async function fetchFromCdn(hash, asText = true) {
      if (!hash) return null;
      for (const sub of ['t4', 't3', 't2', 't1', 't0']) {
        try {
          const cRes = await fetch(`https://${sub}.rbxcdn.com/${hash}`, {
            headers: { 'Cookie': `.ROBLOSECURITY=${cookie}`, 'User-Agent': 'Roblox/WinInet' }
          });
          if (cRes.ok) {
            if (asText) return await cRes.text();
            const arr = await cRes.arrayBuffer();
            return Buffer.from(arr).toString('base64');
          }
        } catch (_) {}
      }
      return null;
    }

    // 3. Unduh OBJ Text
    const objText = await fetchFromCdn(objHash, true);
    if (!objText) {
      return res.status(502).json({ sukses: false, pesan: 'Gagal mengunduh file .OBJ dari CDN' });
    }

    // 4. Unduh & Parse MTL
    let rawMaterials = {};
    if (mtlHash) {
      const mtlText = await fetchFromCdn(mtlHash, true);
      if (mtlText) {
        let currMtl = null;
        for (const line of mtlText.split('\n')) {
          const l = line.trim();
          if (l.startsWith('newmtl ')) {
            currMtl = l.split(/\s+/)[1];
            rawMaterials[currMtl] = { kd: [1, 1, 1], map: null };
          } else if (currMtl) {
            if (l.startsWith('Kd ')) {
              const p = l.split(/\s+/);
              rawMaterials[currMtl].kd = [parseFloat(p[1]) || 1, parseFloat(p[2]) || 1, parseFloat(p[3]) || 1];
            } else if (l.startsWith('map_Kd ')) {
              rawMaterials[currMtl].map = l.split(/\s+/)[1];
            }
          }
        }
      }
    }

    // 5. Unduh Tekstur & Konversi ke Base64 Data URL
    const materialsResult = {};
    for (const [matName, matInfo] of Object.entries(rawMaterials)) {
      const th = matInfo.map;
      if (!th) continue;
      const b64 = await fetchFromCdn(th, false);
      if (b64) {
        materialsResult[matName] = {
          textureData: `data:image/png;base64,${b64}`,
          color: matInfo.kd,
          isAccessory: matName.toLowerCase().includes('handle')
        };
      }
    }

    // Fallback jika MTL kosong: ambil tekstur pertama langsung
    if (Object.keys(materialsResult).length === 0 && texHashes.length > 0) {
      const firstB64 = await fetchFromCdn(texHashes[0], false);
      if (firstB64) {
        materialsResult['default'] = {
          textureData: `data:image/png;base64,${firstB64}`,
          color: [1, 1, 1],
          isAccessory: false
        };
      }
    }

    return res.status(200).json({
      sukses: true,
      userId,
      userName,
      displayName,
      objText,
      materials: materialsResult,
      aabb: mData.aabb,
      camera: mData.camera
    });

  } catch (error) {
    return res.status(500).json({ sukses: false, pesan: 'Server error 3D model: ' + error.message });
  }
}
