import sys
import random
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QFrame, QGridLayout, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont
import pyqtgraph as pg
import psutil

# --- Stat Getter Abstractions (to be replaced by real mining logic) ---
def get_fold_count():
    return random.randint(0, 1000)
def get_entropy():
    return random.uniform(0.5, 1.0)
def get_hashes_completed():
    return random.randint(0, 10**7)
def get_hashrate():
    return random.uniform(1e3, 1e5)
def get_cpu_usage():
    return psutil.cpu_percent()
def get_skipped_keys():
    return random.randint(0, 10000)
def get_fft_data():
    # Simulate a noisy signal
    t = np.linspace(0, 1, 256)
    signal = np.sin(2 * np.pi * 10 * t) + np.random.normal(0, 0.3, 256)
    fft = np.abs(np.fft.fft(signal))[:128]
    return fft

# --- Main Dashboard Widget ---
class CollapseMinerDashboardModern(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CollapseMiner v3 Dashboard')
        self.resize(950, 650)
        self.setFont(QFont('Consolas', 11))
        self.dark_mode = True
        self.init_ui()
        self.init_timers()
        self.status = 'Idle'
        self.update_status('Idle')

    def init_ui(self):
        self.set_dark_palette()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        # Status Banner
        self.status_banner = QLabel('Idle')
        self.status_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_banner.setFixedHeight(38)
        self.status_banner.setStyleSheet('font-size: 22px; font-weight: bold; border-radius: 12px; background: #232b2b; color: #00ffd0;')
        main_layout.addWidget(self.status_banner)
        # Stats Grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(12)
        # Fold count
        self.fold_label = self._stat_label('Folds', neon='#00ffd0')
        stats_grid.addWidget(self.fold_label, 0, 0)
        # Entropy
        self.entropy_label = self._stat_label('Entropy', neon='#ff00c8')
        self.entropy_meter = QProgressBar()
        self.entropy_meter.setRange(0, 100)
        self.entropy_meter.setStyleSheet('QProgressBar {background: #232b2b; border-radius: 8px;} QProgressBar::chunk {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #ff00c8, stop:1 #00ffd0); border-radius: 8px;}')
        stats_grid.addWidget(self.entropy_label, 0, 1)
        stats_grid.addWidget(self.entropy_meter, 1, 1)
        # Hashes completed
        self.hashes_label = self._stat_label('Hashes', neon='#00ffd0')
        stats_grid.addWidget(self.hashes_label, 0, 2)
        # Hashrate
        self.hashrate_label = self._stat_label('H/s', neon='#ffea00')
        stats_grid.addWidget(self.hashrate_label, 0, 3)
        # CPU usage
        self.cpu_label = self._stat_label('CPU', neon='#ff00c8')
        self.cpu_ring = QProgressBar()
        self.cpu_ring.setRange(0, 100)
        self.cpu_ring.setFixedHeight(18)
        self.cpu_ring.setStyleSheet('QProgressBar {background: #232b2b; border-radius: 8px;} QProgressBar::chunk {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #ff00c8, stop:1 #00ffd0); border-radius: 8px;}')
        stats_grid.addWidget(self.cpu_label, 1, 3)
        stats_grid.addWidget(self.cpu_ring, 2, 3)
        # Skipped keys
        self.skipped_label = self._stat_label('Skipped', neon='#ffea00')
        stats_grid.addWidget(self.skipped_label, 1, 2)
        main_layout.addLayout(stats_grid)
        # FFT Visualization
        self.fft_panel = pg.PlotWidget()
        self.fft_panel.setBackground('#1a1a1a')
        self.fft_curve = self.fft_panel.plot(pen=pg.mkPen('#00ffd0', width=2))
        self.fft_panel.setYRange(0, 40)
        self.fft_panel.setFixedHeight(160)
        main_layout.addWidget(self.fft_panel)
        # Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start Mining')
        self.pause_btn = QPushButton('Pause')
        self.reset_btn = QPushButton('Reset')
        self.export_btn = QPushButton('Export Log')
        self.theme_btn = QPushButton('Toggle Theme')
        for b in [self.start_btn, self.pause_btn, self.reset_btn, self.export_btn, self.theme_btn]:
            b.setStyleSheet('QPushButton {background: #232b2b; color: #00ffd0; border: 2px solid #00ffd0; border-radius: 8px; padding: 6px 16px; font-weight: bold;} QPushButton:hover {background: #00ffd0; color: #232b2b;}')
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.theme_btn)
        main_layout.addLayout(btn_layout)
        # Terminal Log
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(140)
        self.console.setStyleSheet('background: #161616; color: #00ffd0; border-radius: 8px; font-size: 13px;')
        main_layout.addWidget(self.console)
        self.setLayout(main_layout)
        # Button actions
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.start_btn.clicked.connect(lambda: self.update_status('Mining'))
        self.pause_btn.clicked.connect(lambda: self.update_status('Paused'))
        self.reset_btn.clicked.connect(lambda: self.update_status('Idle'))
        self.export_btn.clicked.connect(self.export_log)

    def _stat_label(self, text, neon='#00ffd0'):
        lbl = QLabel(f'{text}: 0')
        lbl.setStyleSheet(f'font-size: 18px; font-weight: bold; color: {neon}; background: transparent;')
        return lbl

    def set_dark_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#181c20'))
        palette.setColor(QPalette.ColorRole.WindowText, QColor('#00ffd0'))
        palette.setColor(QPalette.ColorRole.Base, QColor('#181c20'))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#00ffd0'))
        palette.setColor(QPalette.ColorRole.Text, QColor('#00ffd0'))
        palette.setColor(QPalette.ColorRole.Button, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('#00ffd0'))
        palette.setColor(QPalette.ColorRole.Highlight, QColor('#ff00c8'))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#232b2b'))
        self.setPalette(palette)

    def set_light_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#f0f0f0'))
        palette.setColor(QPalette.ColorRole.WindowText, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.Base, QColor('#ffffff'))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#e0e0e0'))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#e0e0e0'))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.Text, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.Button, QColor('#e0e0e0'))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor('#232b2b'))
        palette.setColor(QPalette.ColorRole.Highlight, QColor('#00ffd0'))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#181c20'))
        self.setPalette(palette)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.set_dark_palette()
        else:
            self.set_light_palette()

    def update_status(self, status):
        self.status = status
        color = {
            'Idle': '#232b2b',
            'Mining': '#00ffd0',
            'Paused': '#ffea00',
            'Completed': '#00ff44',
            'Error': '#ff003c',
        }.get(status, '#232b2b')
        text_color = '#232b2b' if status in ['Mining', 'Completed'] else '#00ffd0'
        self.status_banner.setText(status)
        self.status_banner.setStyleSheet(f'font-size: 22px; font-weight: bold; border-radius: 12px; background: {color}; color: {text_color};')
        self.log(f'Status: {status}')

    def log(self, msg):
        self.console.append(msg)

    def export_log(self):
        with open('collapseminer_log.txt', 'w') as f:
            f.write(self.console.toPlainText())
        self.log('Log exported.')

    def init_timers(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(500)
        self.fft_timer = QTimer()
        self.fft_timer.timeout.connect(self.update_fft)
        self.fft_timer.start(120)

    def update_stats(self):
        self.fold_label.setText(f'Folds: {get_fold_count()}')
        entropy = get_entropy()
        self.entropy_label.setText(f'Entropy: {entropy:.2f}')
        self.entropy_meter.setValue(int(entropy * 100))
        self.hashes_label.setText(f'Hashes: {get_hashes_completed():,}')
        self.hashrate_label.setText(f'H/s: {get_hashrate():,.0f}')
        self.cpu_label.setText(f'CPU: {get_cpu_usage():.1f}%')
        self.cpu_ring.setValue(int(get_cpu_usage()))
        self.skipped_label.setText(f'Skipped: {get_skipped_keys():,}')

    def update_fft(self):
        fft = get_fft_data()
        self.fft_curve.setData(fft)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dash = CollapseMinerDashboardModern()
    dash.show()
    sys.exit(app.exec())
