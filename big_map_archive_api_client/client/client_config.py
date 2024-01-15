import yaml

from big_map_archive_api_client.client.api_client import ArchiveAPIClient
from pydantic import BaseModel


class ClientConfig(BaseModel):
    """Configuration data for a BMA API's client."""

    domain_name: str
    port: int
    token: str

    @classmethod
    def load_from_config_file(cls, file_path):
        """
        Creates a class instance
        Initializes internal fields from configuration file
        """
        with open(file_path) as f:
            # Get data from config.yaml file
            client_config = yaml.load(f, Loader=yaml.FullLoader)

        return ClientConfig(**client_config)

    def create_client(self):
        """
        Creates a client to interact with BMA's API
        Initializes internal fields
        """
        return ArchiveAPIClient(self.domain_name, self.port, self.token)
