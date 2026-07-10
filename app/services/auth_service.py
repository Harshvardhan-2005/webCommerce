from app.clients.magento_client import magento_client
from app.core.config import settings
from app.core.logger import logger


class AuthService:
    """
    Handles Magento authentication and salesman identity.
    """

    async def authenticate_salesman(self) -> dict:
        """
        Authenticate the configured salesman with Magento,
        fetch admin information, and load assigned customers.
        """

        logger.info("Starting salesman authentication.")

        # Step 1: Login to Magento
        token = await magento_client.login(
            username=settings.MAGENTO_ADMIN_USERNAME,
            password=settings.MAGENTO_ADMIN_PASSWORD,
        )

        # Step 2: Fetch authenticated admin information
        admin_info = await magento_client.get_admin_info(
            token=token,
        )

        success_data = admin_info.get("sucess", {})

        admin_id = success_data.get("admin_id")
        username = success_data.get("username")

        if not admin_id:
            logger.error(
                "Admin ID not found in Magento admin response."
            )

            raise ValueError(
                "Magento response does not contain admin_id"
            )

        logger.info(
            "Salesman authenticated successfully. "
            f"Admin ID: {admin_id}, "
            f"Username: {username}"
        )

        # Step 3: Fetch customers assigned to salesman
        customers = await magento_client.get_salesman_customers(
            token=token,
            admin_id=int(admin_id),
        )

        logger.info(
            f"Successfully fetched customers for admin ID: {admin_id}"
        )

        return {
            "token": token,
            "admin": admin_info,
            "customers": customers,
        }


auth_service = AuthService()