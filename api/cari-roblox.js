export default async function handler(req, res) {
  // Header CORS agar bisa diakses dari domain frontend Vercel & localhost
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

  const cleanUser = username.trim().replace(/^@+/, '').trim();
  if (!cleanUser) {
    return res.status(400).json({ sukses: false, pesan: 'Username tidak valid' });
  }

  try {
    let uid = null;
    let userName = cleanUser;
    let displayName = cleanUser;

    // 1. Jika angka murni (Roblox User ID)
    if (/^\d+$/.test(cleanUser)) {
      try {
        const idRes = await fetch(`https://users.roblox.com/v1/users/${cleanUser}`, {
          headers: { 'User-Agent': 'Mozilla/5.0' },
          signal: AbortSignal.timeout(4000)
        });
        if (idRes.ok) {
          const idData = await idRes.json();
          if (idData && idData.id) {
            uid = idData.id;
            userName = idData.name || cleanUser;
            displayName = idData.displayName || userName;
          }
        }
      } catch (_) {}
    }

    // 2. Cari via usernames/users (Roblox resmi lalu Roproxy)
    if (!uid) {
      const endpoints = [
        'https://users.roblox.com/v1/usernames/users',
        'https://users.roproxy.com/v1/usernames/users'
      ];
      for (const ep of endpoints) {
        try {
          const userRes = await fetch(ep, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0' },
            body: JSON.stringify({ usernames: [cleanUser], excludeBannedUsers: false }),
            signal: AbortSignal.timeout(4000)
          });
          if (userRes.ok) {
            const userData = await userRes.json();
            const user = (userData.data || [])[0];
            if (user && user.id) {
              uid = user.id;
              userName = user.name || cleanUser;
              displayName = user.displayName || user.name || cleanUser;
              break;
            }
          }
        } catch (_) {}
      }
    }

    if (!uid) {
      return res.status(404).json({ sukses: false, pesan: 'Akun Roblox tidak ditemukan' });
    }

    // 3. Ambil Avatar Headshot (untuk tabel kursi)
    let avatarUrl = '';
    const thumbEndpoints = [
      `https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=${uid}&size=150x150&format=Png&isCircular=true`,
      `https://thumbnails.roproxy.com/v1/users/avatar-headshot?userIds=${uid}&size=150x150&format=Png&isCircular=true`
    ];
    for (const tep of thumbEndpoints) {
      try {
        const thumbRes = await fetch(tep, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(3500) });
        if (thumbRes.ok) {
          const thumbData = await thumbRes.json();
          if (thumbData.data && thumbData.data[0] && thumbData.data[0].imageUrl) {
            avatarUrl = thumbData.data[0].imageUrl;
            break;
          }
        }
      } catch (_) {}
    }

    // 4. Ambil Avatar Full Body HD 720x720 (untuk Podium Juara 3D)
    let avatar3dUrl = '';
    const thumb3dEndpoints = [
      `https://thumbnails.roblox.com/v1/users/avatar?userIds=${uid}&size=720x720&format=Png&isCircular=false`,
      `https://thumbnails.roproxy.com/v1/users/avatar?userIds=${uid}&size=720x720&format=Png&isCircular=false`
    ];
    for (const t3dep of thumb3dEndpoints) {
      try {
        const fullRes = await fetch(t3dep, { headers: { 'User-Agent': 'Mozilla/5.0' }, signal: AbortSignal.timeout(3500) });
        if (fullRes.ok) {
          const fullData = await fullRes.json();
          if (fullData.data && fullData.data[0] && fullData.data[0].imageUrl) {
            avatar3dUrl = fullData.data[0].imageUrl;
            break;
          }
        }
      } catch (_) {}
    }

    const fallbackAvatar = `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=0284c7&color=fff&rounded=true&bold=true`;

    return res.status(200).json({
      sukses: true,
      userId: uid,
      userName: userName,
      username: userName,
      displayName: displayName,
      avatarUrl: avatarUrl || fallbackAvatar,
      avatar3dUrl: avatar3dUrl || avatarUrl || fallbackAvatar
    });

  } catch (error) {
    return res.status(500).json({ sukses: false, pesan: 'Kesalahan Server: ' + error.message });
  }
}
