from finales_api_client.client.rest_api_connection import \
    FinalesRestAPIConnection


class FinalesAPIClient:
    """
    Class to interact with BMA's API
    """

    def __init__(self, ip_address, port, username, password, database_endpoint_access_key):
        """
        Initialize internal variables
        """
        self._connection = FinalesRestAPIConnection(ip_address, port)
        self._username = username
        self._password = password
        self._database_endpoint_access_key = database_endpoint_access_key

    def post_authenticate(self):
        """
        Gets a personal access token from the Finales server
        Raises an HTTPError exception if the request fails
        """
        resource_path = '/user_management/authenticate'

        payload = {
            'username': self._username,
            'password': self._password
        }

        response = self._connection.post(resource_path=resource_path,
                                         payload=payload,
                                         content_type='application/x-www-form-urlencoded')
        return response.json()

    def get_capabilities(self, token):
        """
        Gets all capabilities stored in the FINALES database
        Note that a capability corresponds to a tuple (quantity, method),
        where 'quantity' is the physical property to be evaluated and 'method' is the approach used to evaluate the property
        Raises an HTTPError exception if the request fails
        """
        resource_path = '/capabilities/'
        response = self._connection.get(resource_path, token, query_string='currently_available=false')
        response.raise_for_status()
        return response.json()

    def get_all_requests(self, token):
        """
        Gets all requests stored in the FINALES database
        Raises an HTTPError exception if the request fails
        """
        resource_path = '/all_requests/'
        response = self._connection.get(resource_path, token)
        response.raise_for_status()
        return response.json()

    def get_results_requested(self, token):
        """
        Gets all results associated with requests stored in the FINALES database
        Note that:
        (a) a request is associated with a capability and posted to the FINALES server by a FINALES tenant
        that wishes to have a specific property evaluated using a specific method
        (b) a result is associated with a request and posted to the FINALES server by a FINALES tenant that has performed
        an evaluation of the specific property using the specific method
        Raises an HTTPError exception if the request fails
        """
        resource_path = '/results_requested/'
        response = self._connection.get(resource_path, token)
        response.raise_for_status()
        return response.json()

    def get_database_file(self, token, stream):
        """
        Downloads a copy of the SQLite database file
        This is done in chunks if stream is set to True
        Raises an HTTPError exception if the request fails
        """
        access_key = self._database_endpoint_access_key
        resource_path = f'/database_dump/{access_key}'
        response = self._connection.get(resource_path, token, stream=stream)
        response.raise_for_status()
        return response
