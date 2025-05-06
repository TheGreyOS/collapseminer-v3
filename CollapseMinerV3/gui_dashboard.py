"""
Tkinter GUI dashboard for CollapseMiner v3
Displays fold stats, hash rate, entropy heatmap (placeholder)
"""
import tkinter as tk
import threading
import time
import psutil

class CollapseMinerDashboard:
    def __init__(self, miner):
        self.miner = miner
        self.root = tk.Tk()
        self.root.title('CollapseMiner v3 Dashboard')
        self.stats_label = tk.Label(self.root, text='Initializing...', font=('Consolas', 12), justify='left')
        self.stats_label.pack(padx=10, pady=10)
        self.heatmap_canvas = tk.Canvas(self.root, width=300, height=100, bg='white')
        self.heatmap_canvas.pack(padx=10, pady=10)
        self.running = True
        threading.Thread(target=self.update_stats, daemon=True).start()

    def update_stats(self):
        while self.running:
            stats = self.miner.fold_stats[-1] if self.miner.fold_stats else {}
            text = '\n'.join([
                f"Fold: {stats.get('fold', '-')}",
                f"Entropy: {stats.get('entropy', '-')}",
                f"Hashes: {stats.get('hashes_done', '-')}",
                f"Hash/sec: {stats.get('hash_rate', '-')}",
                f"CPU: {stats.get('cpu', '-')}%",
                f"Skipped: {stats.get('skipped', '-')}"
            ])
            self.stats_label.config(text=text)
            # Draw FFT heatmap if available
            self.heatmap_canvas.delete('all')
            spectrum = getattr(self.miner, 'last_spectrum', None)
            if spectrum is not None and len(spectrum) > 0:
                max_val = max(spectrum)
                bar_width = 300 // len(spectrum)
                for i, val in enumerate(spectrum):
                    x0 = i * bar_width
                    x1 = x0 + bar_width - 1
                    y0 = 100
                    y1 = 100 - int((val / max_val) * 90) if max_val > 0 else 100
                    self.heatmap_canvas.create_rectangle(x0, y1, x1, y0, fill='blue')
            else:
                self.heatmap_canvas.create_text(150, 50, text='No FFT data', fill='gray')
            time.sleep(0.5)

    def run(self):
        self.root.mainloop()

    def stop(self):
        self.running = False
        self.root.quit()
