// api/weather.js - Cloud Weather & Potion Alert for Roblox Executor
// Runs on Vercel Serverless

const NTFY_URL = 'https://ntfy.sh/galatama_auto_skor_live_bus_v1';

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

  const player = body.player || body.username || 'Server Global';
  const weather = body.weather || body.event || 'Unknown Event';
  const timestamp = body.timestamp || Date.now();

  try {
    await fetch(NTFY_URL, {
      method: 'POST',
      body: JSON.stringify({
        type: 'WEATHER_EVENT',
        player,
        weather,
        timestamp
      })
    });
  } catch (_) {}

  return res.status(200).json({
    status: 'ok',
    player,
    event: weather
  });
}
