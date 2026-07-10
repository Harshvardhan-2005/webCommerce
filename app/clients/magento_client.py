import httpx

from app.core.config import settings
from app.core.logger import logger


class MagentoClient:
    """
    Client responsible for communicating with the
    Hnak UAT Magento REST APIs.
    """

    def __init__(self):
        self.base_url = settings.MAGENTO_URL.rstrip("/")

    async def login(
        self,
        username: str,
        password: str,
    ) -> str:
        """
        Authenticate a Magento admin/salesman and return
        the Magento Bearer token.
        """

        url = f"{self.base_url}/V1/integration/admin/token"

        payload = {
            "username": username,
            "password": password,
        }

        logger.info("Authenticating admin with Magento.")
        logger.info(f"Magento endpoint: {url}")

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                url=url,
                json=payload,
            )

        logger.info(
            f"Magento login status code: {response.status_code}"
        )

        if response.status_code >= 400:
            logger.error(
                f"Magento login failed: {response.text}"
            )

        response.raise_for_status()

        token = response.json()

        logger.info("Magento authentication successful.")

        return token

    async def get_admin_info(
        self,
        token: str,
    ) -> dict:
        """
        Fetch authenticated Magento admin information.
        """

        url = f"{self.base_url}/V1/integration/admin/me"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        logger.info("Fetching Magento admin information.")
        logger.info(f"Magento endpoint: {url}")

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url=url,
                headers=headers,
            )

        logger.info(
            f"Magento admin info status code: "
            f"{response.status_code}"
        )

        if response.status_code >= 400:
            logger.error(
                f"Magento admin info failed: {response.text}"
            )

        response.raise_for_status()

        return response.json()

    async def get_salesman_customers(
        self,
        token: str,
        admin_id: int,
    ) -> dict:
        """
        Fetch customers assigned to the authenticated salesman.
        """

        url = (
            f"{self.base_url}"
            f"/V1/integration/admin/customer"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "admin_id": admin_id,
        }

        logger.info(
            f"Fetching customers for admin ID: {admin_id}"
        )
        logger.info(f"Magento endpoint: {url}")

        async with httpx.AsyncClient(
            timeout=30,
            follow_redirects=True,
        ) as client:
            response = await client.post(
                url=url,
                headers=headers,
                json=payload,
            )

        logger.info(
            f"Magento customer API status code: "
            f"{response.status_code}"
        )

        if response.status_code >= 400:
            logger.error(
                f"Magento customer API failed: {response.text}"
            )

        response.raise_for_status()

        return response.json()


magento_client = MagentoClient()