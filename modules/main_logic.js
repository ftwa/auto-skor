const CLOUD_BUS_URL = 'https://ntfy.sh/galatama_auto_skor_live_bus_v1/json';

function startPolling() {
  console.log('📡 [CloudBus] Memulai polling (alternatif EventSource)...');
  
  async function poll() {
    try {
      const response = await fetch(CLOUD_BUS_URL);
      if (!response.ok) throw new Error('Polling failed');
      const text = await response.text();
      const lines = text.trim().split('
');
      
      for (const line of lines) {
        if (!line) continue;
        try {
          const data = JSON.parse(line);
          if (data && typeof enqueueNotif === 'function') {
            const display = data.displayName || data.user || 'Anonim';
            const ikan = data.ikan || data.fish || 'Unknown';
            const tier = data.kategori || data.tier || 'legend';
            const pts = data.poin || 0;
            const rinc = data.rincian || '';
            enqueueNotif(display, rinc, pts, pts, tier, '', ikan, true);
          }
        } catch (e) { /* ignore parse error */ }
      }
    } catch (err) {
      console.error('📡 [CloudBus] Polling error:', err);
    }
  }

  // Polling setiap 3 detik
  setInterval(poll, 3000);
}

window.addEventListener('DOMContentLoaded', startPolling);
