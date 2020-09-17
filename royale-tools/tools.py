from typing import Any, Dict, Optional

import requests


class ClashRoyaleTools:
    def __init__(self):
        self.token = None

    def get_request(self, url: str, token: str, params: Optional[Any] = None) -> Dict:
        """Get request."""
        headers = {"Accept": "application/json", "authorization": f"Bearer {token}"}
        req = requests.get(url, headers=headers, params=params)

        return req.json()
