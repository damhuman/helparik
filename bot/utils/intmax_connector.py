import aiohttp
import json
from typing import Dict, List, Optional, Any, Union

from configuration import INTMAX_BACKEND_URL

class IntMaxConnector:
    def __init__(self):
        self.base_url = INTMAX_BACKEND_URL
        self.session_id = None
        self._session = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.session_id:
            headers["x-session-id"] = self.session_id
        return headers

    async def login(self, eth_private_key: str) -> Dict[str, str]:
        """Login to the IntMax server with an Ethereum private key."""
        async with self.session.post(
            f"{self.base_url}/login",
            json={"eth_private_key": eth_private_key},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                self.session_id = data["sessionId"]
                return data
            raise Exception(data.get("error", "Login failed"))

    async def logout(self) -> Dict[str, str]:
        """Logout from the IntMax server."""
        async with self.session.post(
            f"{self.base_url}/logout",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                self.session_id = None
                return data
            raise Exception(data.get("error", "Logout failed"))

    async def get_balances(self) -> Dict[str, Any]:
        """Get token balances."""
        async with self.session.get(
            f"{self.base_url}/balances",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get balances"))

    async def sign_message(self, message: str) -> Dict[str, str]:
        """Sign a message."""
        async with self.session.post(
            f"{self.base_url}/sign",
            json={"message": message},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to sign message"))

    async def verify_signature(self, signature: str, message: str) -> Dict[str, bool]:
        """Verify a signature."""
        async with self.session.post(
            f"{self.base_url}/verify",
            json={"signature": signature, "message": message},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to verify signature"))

    async def get_tokens(self) -> Dict[str, List[Dict]]:
        """Get list of available tokens."""
        async with self.session.get(
            f"{self.base_url}/tokens",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get tokens"))

    async def estimate_deposit_gas(self, amount: float, token: Dict, address: Optional[str] = None) -> Dict[str, Any]:
        """Estimate gas for deposit."""
        async with self.session.post(
            f"{self.base_url}/deposit/estimate",
            json={"amount": amount, "token": token, "address": address},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to estimate deposit gas"))

    async def deposit(self, amount: float, token: Dict, address: Optional[str] = None) -> Dict[str, Any]:
        """Make a deposit."""
        async with self.session.post(
            f"{self.base_url}/deposit",
            json={"amount": amount, "token": token, "address": address},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to deposit"))

    async def withdraw(self, amount: float, token: Dict, address: str) -> Dict[str, Any]:
        """Make a withdrawal."""
        async with self.session.post(
            f"{self.base_url}/withdraw",
            json={"amount": amount, "token": token, "address": address},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to withdraw"))

    async def get_deposits(self) -> Dict[str, List[Dict]]:
        """Get deposit history."""
        async with self.session.get(
            f"{self.base_url}/deposits",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get deposits"))

    async def get_transfers(self) -> Dict[str, List[Dict]]:
        """Get transfer history."""
        async with self.session.get(
            f"{self.base_url}/transfers",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get transfers"))

    async def get_transactions(self) -> Dict[str, List[Dict]]:
        """Get transaction history."""
        async with self.session.get(
            f"{self.base_url}/transactions",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get transactions"))

    async def get_pending_withdrawals(self) -> Dict[str, List[Dict]]:
        """Get pending withdrawals."""
        async with self.session.get(
            f"{self.base_url}/pending-withdrawals",
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to get pending withdrawals"))

    async def claim_withdrawals(self, withdrawal_ids: List[str]) -> Dict[str, Any]:
        """Claim pending withdrawals."""
        async with self.session.post(
            f"{self.base_url}/claim-withdrawals",
            json={"withdrawalIds": withdrawal_ids},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to claim withdrawals"))

    async def broadcast_transaction(
        self, 
        transfers: List[Dict[str, Any]], 
        is_withdrawal: bool = False
    ) -> Dict[str, Any]:
        async with self.session.post(
            f"{self.base_url}/broadcast-transaction",
            json={"transfers": transfers, "isWithdrawal": is_withdrawal},
            headers=self._get_headers()
        ) as response:
            data = await response.json()
            if response.status == 200:
                return data
            raise Exception(data.get("error", "Failed to broadcast transaction"))
