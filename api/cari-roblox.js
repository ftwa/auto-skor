export default async function handler(req, res) {
  // Header CORS agar bisa diakses dari domain frontend Vercel
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Menggunakan WHATWG URL API modern untuk parsing query parameter
  const requestUrl = new URL(req.url, `https://${req.headers.host || 'localhost'}`);
  const username = requestUrl.searchParams.get('username') || req.query.username;

  if (!username || !username.trim()) {
    return res.status(400).json({ sukses: false, pesan: 'Username wajib diisi' });
  }

  const cleanUser = username.trim().replace(/^@+/, '');

  try {
    // 1. Cari User ID ke API Roblox
    const userApiUrl = new URL('https://users.roblox.com/v1/usernames/users');
    const userRes = await fetch(userApiUrl.href, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ usernames: [cleanUser], excludeBannedUsers: false })
    });

    if (!userRes.ok) {
      return res.status(userRes.status).json({ sukses: false, pesan: 'Gagal menghubungi server Roblox' });
    }

    const userData = await userRes.json();
    const user = (userData.data || [])[0];

    if (!user || !user.id) {
      return res.status(404).json({ sukses: false, pesan: 'Akun Roblox tidak ditemukan' });
    }

    // 2. Ambil Avatar Headshot (untuk tabel kursi)
    let avatarUrl = '';
    const thumbApiUrl = new URL('https://thumbnails.roblox.com/v1/users/avatar-headshot');
    thumbApiUrl.searchParams.set('userIds', user.id);
    thumbApiUrl.searchParams.set('size', '150x150');
    thumbApiUrl.searchParams.set('format', 'Png');
    thumbApiUrl.searchParams.set('isCircular', 'true');

    const thumbRes = await fetch(thumbApiUrl.href);
    if (thumbRes.ok) {
      const thumbData = await thumbRes.json();
      if (thumbData.data && thumbData.data[0] && thumbData.data[0].imageUrl) {
        avatarUrl = thumbData.data[0].imageUrl;
      }
    }

    // 3. Ambil Avatar Full Body HD 720x720 (untuk Podium Juara 3D)
    let avatar3dUrl = '';
    const fullThumbUrl = new URL('https://thumbnails.roblox.com/v1/users/avatar');
    fullThumbUrl.searchParams.set('userIds', user.id);
    fullThumbUrl.searchParams.set('size', '720x720');
    fullThumbUrl.searchParams.set('format', 'Png');
    fullThumbUrl.searchParams.set('isCircular', 'false');

    const fullThumbRes = await fetch(fullThumbUrl.href);
    if (fullThumbRes.ok) {
      const fullThumbData = await fullThumbRes.json();
      if (fullThumbData.data && fullThumbData.data[0] && fullThumbData.data[0].imageUrl) {
        avatar3dUrl = fullThumbData.data[0].imageUrl;
      }
    }

    const fallbackAvatar = `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(cleanUser)}&backgroundColor=0284c7`;

    return res.status(200).json({
      sukses: true,
      userId: user.id,
      userName: user.name,
      displayName: user.displayName || user.name,
      avatarUrl: avatarUrl || fallbackAvatar,
      avatar3dUrl: avatar3dUrl || avatarUrl || fallbackAvatar
    });

  } catch (error) {
    return res.status(500).json({ sukses: false, pesan: 'Kesalahan Server: ' + error.message });
  }
}
