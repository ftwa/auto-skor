# 🏆 Auto Skor Esports & Grand Winner Stage (TikTok LIVE Studio & Vercel)

Papan Skor Turnamen Roblox dengan **Mode Match 20 Kursi**, **Podium 3 Besar Mode 4 Holographic Gyro-Rings**, **Stadium Chronometer Cyber Capsule Timer**, **Toast Catch Alert Notification**, dan **3D Winner Celebration Stage** yang dirancang khusus untuk **TikTok LIVE Studio**, **OBS Studio**, dan Operator Host.

## 🌟 Fitur Utama
- **Tampilan Khusus TikTok LIVE Studio (Browser Source)**:
  - `/?view=overlay` : Overlay lengkap (Podium 3 Besar Gyro-Rings + Stadium Timer Capsule + Tabel Mode Match + Toast Alert + 3D Winner Stage) dengan latar belakang transparan / clean tanpa tombol admin.
  - `/?view=podium` : Overlay khusus Panggung 3D Winner / Juara.
  - `/?view=notif` : Overlay khusus Notifikasi Tangkapan (Toast Alert).
  - `/` (default) : Dashboard Operator Host untuk kontrol poin, timer, notifikasi, dan sesi.
- **Sinkronisasi Real-Time Dual-Engine**:
  - `BroadcastChannel` untuk sinkronisasi 0ms saat dijalankan di komputer yang sama.
  - `ntfy.sh Cloud SSE Bus` untuk sinkronisasi real-time instan saat operator mengontrol dari HP / browser lain.
- **Serverless API Roblox di Vercel**:
  - `/api/cari-roblox` : Resolusi otomatis akun Roblox & foto profil.
  - `/api/roblox-3d-model` : Model 3D avatar Roblox (.OBJ & tekstur resmi).

## 🚀 Deployment ke Vercel
1. Repository GitHub: `https://github.com/ftwa/auto-skor`
2. Import repository di [Vercel](https://vercel.com/new).
3. Selesai! Web akan langsung aktif di Vercel.
