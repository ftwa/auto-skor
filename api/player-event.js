// api/player-event.js - Cloud Player Join/Leave Tracking
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

  const player = (body.player || '').trim();
  const event = (body.event || '').trim().toUpperCase();

  return res.status(200).json({
    status: 'ok',
    player,
    event
  });
}
