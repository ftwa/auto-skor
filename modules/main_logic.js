// Konfigurasi Cloud Bus
const CLOUD_BUS_URL = 'https://ntfy.sh/galatama_auto_skor_live_bus_v1/json';

function connectCloudBus() {
  console.log('📡 [CloudBus] Memulai koneksi...');
  const eventSource = new EventSource(CLOUD_BUS_URL);
  eventSource.onopen = () => console.log('📡 [CloudBus] Koneksi terbuka!');
  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data) {
        const display = data.displayName || data.user || 'Anonim';
        const ikan = data.ikan || data.fish || 'Unknown';
        const tier = data.kategori || data.tier || 'legend';
        const pts = data.poin || 0;
        const rinc = data.rincian || '';
        enqueueNotif(display, rinc, pts, pts, tier, '', ikan, true);
      }
    } catch (err) {
      console.error('📡 [CloudBus] Error parsing:', err);
    }
  };
  eventSource.onerror = (e) => console.error('📡 [CloudBus] Error koneksi:', e);
}

window.addEventListener('DOMContentLoaded', connectCloudBus);
