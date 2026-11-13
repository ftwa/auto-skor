// api/catch.js - Cloud Scoring & Live Sync Engine for Roblox Executor
// Runs autonomously on Vercel Serverless (Zero localhost Python required)

const NTFY_URL = 'https://ntfy.sh/galatama_auto_skor_live_bus_v1';

// In-memory buffer of recent catches (persists across warm serverless invocations)
const RECENT_CATCHES = [];
const MAX_RECENT = 100;

// Konfigurasi Dinamis Ikan Khusus & Poin Khusus
let CONFIG_KHUSUS = {
  nama: '',
  poin: 5,
  bigVal: 2,
  shinyVal: 2,
  mutasiVal: 3
};

function hitungPoin(tierStr, namaIkan, varianStr, customKhusus = null) {
  const tierClean = String(tierStr || '').toLowerCase().trim();
  const namaClean = String(namaIkan || '').toLowerCase().trim();
  const varianClean = String(varianStr || '').toLowerCase().trim();

  const cfg = customKhusus || CONFIG_KHUSUS;
  const targetKhusus = String(cfg.nama || '').toLowerCase().trim();

  // 1. Deteksi Fitur Ikan Khusus (Fleksibel)
  let isKhusus = false;
  if (targetKhusus && namaClean) {
    const list = targetKhusus.split(',').map(s => s.trim()).filter(Boolean);
    if (list.some(k => namaClean.includes(k))) {
      isKhusus = true;
    }
  }

  if (isKhusus || tierClean.includes('khusus') || tierClean.includes('special')) {
    const base = Number(cfg.poin) || 5;
    let total = base;
    const rincian = [`ikan khusus +${base}`];
    const teksCek = `${namaIkan} ${varianStr}`.toUpperCase();

    if (/\bBIG\b/.test(teksCek)) {
      const b = Number(cfg.bigVal) || 2;
      total += b;
      if (b > 0) rincian.push(`big +${b}`);
    }
    if (/\bSHINY\b/.test(teksCek)) {
      const s = Number(cfg.shinyVal) || 2;
      total += s;
      if (s > 0) rincian.push(`shiny +${s}`);
    }
    const bukanMutasi = ["none", "-", "no", "normal", "", "shiny", "big"];
    if (varianClean && !bukanMutasi.includes(varianClean)) {
      const m = Number(cfg.mutasiVal) || 3;
      total += m;
      if (m > 0) rincian.push(`mutasi +${m}`);
    }
    return {
      poin: total,
      rincian: rincian.join(', '),
      kategori: 'khusus',
      valid: true
    };
  }

  // 2. Tentukan Kategori Tier Standar (Secret, Mitos, Legend)
  let kategori = 'legend';
  if (tierClean.includes('secret')) {
    kategori = 'secret';
  } else if (tierClean.includes('mythic') || tierClean.includes('mitos')) {
    kategori = 'mitos';
  } else if (tierClean.includes('legend') || tierClean.includes('legendary')) {
    kategori = 'legend';
  } else if (['normal', 'rare', 'common', 'uncommon'].includes(tierClean)) {
    return { poin: 0, rincian: 'Bukan Tier Turnamen', kategori: 'normal', valid: false };
  } else {
    kategori = 'legend';
  }

  // 3. Poin Dasar Sesuai Tier
  const POIN_DASAR = { secret: 3, mitos: 2, legend: 1 };
  const basePoint = POIN_DASAR[kategori] || 1;
  let total = basePoint;
  const rincian = [`${kategori} +${basePoint}`];

  // 4. Bonus Big, Shiny, dan Mutasi
  const teksCek = `${namaIkan} ${varianStr}`.toUpperCase();

  // Bonus Big
  if (/\bBIG\b/.test(teksCek)) {
    total += 1;
    rincian.push('big +1');
  }

  // Bonus Shiny
  if (/\bSHINY\b/.test(teksCek)) {
    total += 1;
    rincian.push('shiny +1');
  }

  // Bonus Mutasi
  const bukanMutasi = ["none", "-", "no", "normal", "", "shiny", "big"];
  if (varianClean && !bukanMutasi.includes(varianClean)) {
    total += 1;
    rincian.push('mutasi +1');
  }

  return {
    poin: total,
    rincian: rincian.join(', '),
    kategori: kategori,
    valid: true
  };
}

export default async function handler(req, res) {
  // CORS Headers - Izinkan akses dari Roblox Executor, Browser, TikTok Studio
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // GET: Mengambil riwayat tangkapan terbaru untuk inisialisasi awal
  if (req.method === 'GET') {
    return res.status(200).json({
      sukses: true,
      mode: 'CLOUD_AUTONOMOUS',
      configKhusus: CONFIG_KHUSUS,
      total: RECENT_CATCHES.length,
      catches: RECENT_CATCHES.slice(-30)
    });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ sukses: false, pesan: 'Method Not Allowed' });
  }

  try {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (_) {}
    }
    body = body || {};

    // Update konfigurasi Ikan Khusus jika disertakan dalam request
    if (body.ikanKhususNama !== undefined) {
      CONFIG_KHUSUS.nama = String(body.ikanKhususNama).trim();
      if (body.ikanKhususPoin !== undefined) CONFIG_KHUSUS.poin = Number(body.ikanKhususPoin) || 5;
    } else if (body.warnaPoin?.matrix?.khusus) {
      const k = body.warnaPoin.matrix.khusus;
      CONFIG_KHUSUS.nama = String(k.nama || '').trim();
      CONFIG_KHUSUS.poin = Number(k.base) || 5;
      CONFIG_KHUSUS.bigVal = Number(k.bigVal) || 2;
      CONFIG_KHUSUS.shinyVal = Number(k.shinyVal) || 2;
      CONFIG_KHUSUS.mutasiVal = Number(k.mutasiVal) || 3;
    }

    const player = String(body.player || body.username || '').trim();
    const rawFish = String(body.fish || body.ikan || '').trim();
    const rawVariant = String(body.variant || body.varian || '').trim();
    const rawTier = String(body.tier || '').trim();

    if (!player || !rawFish) {
      return res.status(400).json({
        sukses: false,
        pesan: 'Data tidak lengkap (player dan fish wajib disertakan)'
      });
    }

    const variantClean = (rawVariant && !['none', '-', ''].includes(rawVariant.toLowerCase())) ? rawVariant : '';
    const fullFishName = variantClean ? `${variantClean} ${rawFish}` : rawFish;

    const kalkulasi = hitungPoin(rawTier, rawFish, variantClean, CONFIG_KHUSUS);

    if (!kalkulasi.valid || kalkulasi.poin <= 0) {
      return res.status(200).json({
        status: 'ignored',
        pesan: `Ikan '${fullFishName}' bukan tier turnamen (0 poin)`
      });
    }

    const catchEvent = {
      id: `catch_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
      type: 'SYNC_CATCH',
      user: player,
      ikan: fullFishName,
      fish: rawFish,
      variant: variantClean,
      rincian: kalkulasi.rincian,
      poin: kalkulasi.poin,
      kategori: kalkulasi.kategori,
      tier: kalkulasi.kategori,
      timestamp: Date.now()
    };

    // Simpan di riwayat tangkapan cloud
    RECENT_CATCHES.push(catchEvent);
    if (RECENT_CATCHES.length > MAX_RECENT) RECENT_CATCHES.shift();

    // Broadcast kilat ke ntfy.sh (Live SSE Bus untuk semua browser & TikTok Studio)
    try {
      await fetch(NTFY_URL, {
        method: 'POST',
        headers: {
          'Title': 'Galatama Auto Skor Catch',
          'Priority': 'urgent'
        },
        body: JSON.stringify(catchEvent)
      });
    } catch (ntfyErr) {
      console.warn('[Cloud Bus] ntfy broadcast failed:', ntfyErr.message);
    }

    return res.status(200).json({
      status: 'ok',
      sukses: true,
      data: catchEvent
    });

  } catch (err) {
    console.error('[Cloud Catch] Serverless Error:', err);
    return res.status(500).json({
      sukses: false,
      pesan: 'Internal Server Error: ' + err.message
    });
  }
}
