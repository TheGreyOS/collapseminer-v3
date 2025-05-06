"""
RPC client for CollapseMiner v3
Supports real HSD node or mock mining mode.
"""
import requests
import random
from config import RPC_URL, MOCK_MODE

class RPCClient:
    def __init__(self):
        self.mock = MOCK_MODE
        self.url = RPC_URL

    def get_header_and_target(self):
        try:
            # Standard HSD API: get block template
            resp = requests.post(self.url, json={
                "method": "getblocktemplate",
                "params": [],
                "id": 1
            })
            data = resp.json()['result']
            header = bytes.fromhex(data['header'])
            target = data['target']
            return header, target
        except Exception as e:
            raise RuntimeError(f"Failed to fetch header/target from HSD RPC: {e}")


    def submit_solution(self, nonce: int, header: bytes):
        try:
            # Standard HSD API: submit mining solution
            payload = {
                "method": "submitwork",
                "params": [header.hex(), nonce],
                "id": 1
            }
            resp = requests.post(self.url, json=payload)
            result = resp.json()
            if 'error' in result and result['error']:
                raise RuntimeError(f"HSD RPC error: {result['error']}")
            print(f"[HSD] Solution submitted: nonce={nonce}")
            return True
        except Exception as e:
            print(f"Failed to submit solution to HSD RPC: {e}")
            return False

