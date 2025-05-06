"""
Main entry point for CollapseMiner v3
Starts mining engine and GUI dashboard.
"""
from config import HEADER, TARGET_HEX, MOCK_MODE
from collapse_engine import CollapseMiner
from rpc_client import RPCClient
from gui_dashboard import CollapseMinerDashboard
import threading


def main():
    rpc_client = RPCClient()
    header, target = (HEADER, TARGET_HEX)
    if not MOCK_MODE:
        header, target = rpc_client.get_header_and_target()
    miner = CollapseMiner(header, target, rpc_client=rpc_client)
    # Start mining in a thread
    mining_thread = threading.Thread(target=miner.mine, kwargs={'start_nonce':0, 'max_folds':100, 'log_json':False}, daemon=True)
    mining_thread.start()
    # Start GUI dashboard
    dashboard = CollapseMinerDashboard(miner)
    dashboard.run()

if __name__ == '__main__':
    main()
