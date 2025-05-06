"""
Core fold mining engine for CollapseMiner v3
"""
import time
import json
import psutil
from config import FOLD_SIZE, SAMPLE_SIZE, TARGET_HEX
from utils import blake2b_hash, hex_to_int
from hash_analyzer import hash_entropy_fft
from predictor import should_fold_be_mined

class CollapseMiner:
    def __init__(self, header: bytes, target_hex: str, rpc_client=None):
        self.header = header
        self.target = hex_to_int(target_hex)
        self.rpc_client = rpc_client
        self.fold_stats = []

    def mine(self, start_nonce=0, max_folds=10, log_json=False):
        for fold_idx in range(max_folds):
            fold_start = start_nonce + fold_idx * FOLD_SIZE
            fold_end = fold_start + FOLD_SIZE
            t0 = time.time()
            # Sample hashes for entropy analysis
            sample_nonces = [fold_start + i * (FOLD_SIZE // SAMPLE_SIZE) for i in range(SAMPLE_SIZE)]
            sample_hashes = [blake2b_hash(self.header, n) for n in sample_nonces]
            # FFT spectrum for GUI heatmap
            arr = np.array([list(h) for h in sample_hashes], dtype=np.uint8)
            spectrum = np.abs(np.fft.fft(arr, axis=0)).mean(axis=1)
            self.last_spectrum = spectrum.tolist()
            entropy_score = hash_entropy_fft(sample_hashes)
            # Predict if this fold is worth mining
            if not should_fold_be_mined(entropy_score):
                self.log_fold(fold_idx, entropy_score, fold_start, fold_end, 0, 0, skipped=True, log_json=log_json)
                continue
            solution_found = False
            hashes_done = 0
            for nonce in range(fold_start, fold_end):
                h = blake2b_hash(self.header, nonce)
                hashes_done += 1
                if int.from_bytes(h, 'big') < self.target:
                    solution_found = True
                    self.log_solution(nonce, h)
                    if self.rpc_client:
                        self.rpc_client.submit_solution(nonce, self.header)
                    break
            t1 = time.time()
            hash_rate = hashes_done / max((t1-t0), 1e-6)
            cpu = psutil.cpu_percent(interval=0.1)
            self.log_fold(fold_idx, entropy_score, fold_start, fold_end, hashes_done, hash_rate, skipped=False, log_json=log_json, cpu=cpu)

    def log_fold(self, fold_idx, entropy_score, fold_start, fold_end, hashes_done, hash_rate, skipped, log_json=False, cpu=0):
        stat = {
            'fold': fold_idx,
            'entropy': entropy_score,
            'start_nonce': fold_start,
            'end_nonce': fold_end,
            'hashes_done': hashes_done,
            'hash_rate': hash_rate,
            'cpu': cpu,
            'skipped': skipped,
        }
        self.fold_stats.append(stat)
        if log_json:
            print(json.dumps(stat))
        else:
            print(f"Fold {fold_idx}: entropy={entropy_score:.3f} hashes={hashes_done} hash/sec={hash_rate:.1f} cpu={cpu}% skipped={skipped}")

    def log_solution(self, nonce, hash_bytes):
        print(f"[SOLUTION] Nonce: {nonce} Hash: {hash_bytes.hex()}")
        with open('solutions.txt', 'a') as f:
            f.write(f"Nonce: {nonce} Hash: {hash_bytes.hex()}\n")
