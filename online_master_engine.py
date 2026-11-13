# ==============================================================================
# ONLINE_MASTER_ENGINE.PY - Cloud Dedicated Desktop Controller for Vercel
# Turnamen Auto Skor Galatama (Bebas Bentrok Port - Zero Localhost Conflict)
# ==============================================================================
import os
import sys
import time
import webview

def log_online_error(msg):
    try:
        appdata = os.environ.get('LOCALAPPDATA', os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(appdata, "master_online_debug.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def main():
    cloud_url = "https://auto-skor.vercel.app/"
    gui_success = False

    try:
        window = webview.create_window(
            title='[ONLINE / CLOUD] Auto Skor Galatama - Vercel Realtime Studio',
            url=cloud_url,
            width=1360,
            height=860,
            min_size=(960, 640),
            background_color='#0f172a',
            text_select=True,
            confirm_close=False
        )
        window.events.closed += lambda: os._exit(0)
        webview.start(private_mode=False)
        gui_success = True
    except Exception as e:
        log_online_error(f"WebView2 GUI init failed: {e}. Mengaktifkan fallback browser...")

    # Fallback Otomatis: Buka langsung di browser jika WebView2 mengalami kendala
    if not gui_success:
        try:
            import webbrowser
            webbrowser.open(cloud_url)
            time.sleep(2)
        except Exception as e2:
            log_online_error(f"Browser fallback failed: {e2}")

    os._exit(0)

if __name__ == '__main__':
    main()
