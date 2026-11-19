// Konfigurasi Cloud Bus
const CLOUD_BUS_URL = 'https://ntfy.sh/galatama_auto_skor_live_bus_v1/json';

// Fungsi untuk inisialisasi koneksi Cloud Bus menggunakan Polling (lebih stabil)
function connectCloudBus() {
  console.log('📡 [CloudBus] Memulai polling...');
  
  async function fetchUpdates() {
    try {
      const response = await fetch(CLOUD_BUS_URL);
      if (!response.ok) throw new Error('Network response was not ok');
      const text = await response.text();
      
      // ntfy.sh sering mengirim data dalam bentuk ndjson (baris demi baris)
      const lines = text.trim().split('\n');
      for (const line of lines) {
        if (!line) continue;
        const data = JSON.parse(line);
        if (data) {
          const display = data.displayName || data.user || 'Anonim';
          const ikan = data.ikan || data.fish || 'Unknown';
          const tier = data.kategori || data.tier || 'legend';
          const pts = data.poin || 0;
          const rinc = data.rincian || '';
          if (typeof enqueueNotif === 'function') {
            enqueueNotif(display, rinc, pts, pts, tier, '', ikan, true);
          }
        }
      }
    } catch (err) {
      console.error('📡 [CloudBus] Error polling:', err);
    }
  }

  // Poll setiap 3 detik
  setInterval(fetchUpdates, 3000);
}

window.addEventListener('DOMContentLoaded', connectCloudBus);
