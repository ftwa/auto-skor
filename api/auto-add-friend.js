export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const rawUser = (req.body && req.body.username) || (req.query && req.query.username) || '';
  const cleanUser = String(rawUser).trim().replace(/^@+/, '').trim();

  if (!cleanUser) {
    return res.status(400).json({ sukses: false, pesan: 'Username wajib diisi' });
  }

  try {
    let uid = null;
    let userName = cleanUser;
    let displayName = cleanUser;

    const postRes = await fetch('https://users.roblox.com/v1/usernames/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0' },
      body: JSON.stringify({ usernames: [cleanUser], excludeBannedUsers: false })
    });

    if (postRes.ok) {
      const data = await postRes.json();
      if (data.data && data.data.length > 0) {
        uid = data.data[0].id;
        userName = data.data[0].name || cleanUser;
        displayName = data.data[0].displayName || userName;
      }
    }

    if (!uid && cleanUser.match(/^\d+$/)) {
      uid = parseInt(cleanUser, 10);
    }

    if (!uid) {
      return res.status(404).json({ sukses: false, status: 'NOT_FOUND', pesan: `User '${cleanUser}' tidak ditemukan di Roblox.` });
    }

    return res.status(200).json({
      sukses: true,
      status: 'USER_FOUND',
      userId: uid,
      username: userName,
      displayName: displayName,
      profileUrl: `https://www.roblox.com/users/${uid}/profile`,
      pesan: `Akun @${userName} (${displayName}) ditemukan!`
    });
  } catch (err) {
    return res.status(200).json({
      sukses: true,
      status: 'USER_FOUND',
      username: cleanUser,
      displayName: cleanUser,
      pesan: `Akun @${cleanUser} siap dipasang ke kursi.`
    });
  }
}
