// api/player-event.js - Cloud Player Join/Leave Tracking (Auto Absen)
// Runs on Vercel Serverless

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (_) {}
  }
  body = body || {};

  const player = String(body.player || body.username || '').trim();
  const event = String(body.event || 'JOIN').trim().toUpperCase();
  const displayName = String(body.displayName || player).trim();
  const userId = body.userId || 0;

  if (!player) {
    return res.status(400).json({ status: 'error', pesan: 'Player wajib diisi' });
  }

  const payload = {
    id: `presence_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
    type: 'PLAYER_PRESENCE',
    player,
    username: player,
    displayName,
    userId,
    event,
    timestamp: Date.now()
  };

  try {
    await fetch('https://ntfy.sh/galatama_auto_skor_live_bus_v1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Priority': 'urgent' },
      body: JSON.stringify(payload)
    });
  } catch (_) {}

  return res.status(200).json({
    status: 'ok',
    sukses: true,
    data: payload
  });
}
