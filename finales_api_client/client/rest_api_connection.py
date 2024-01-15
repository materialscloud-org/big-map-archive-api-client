import requests


class FinalesRestAPIConnection:
    """Internal auxiliary class that handles the base connection."""
    def __init__(self, ip_address, port):
        """
        Initializes internal fields
        """
        self._base_url = f'https://{ip_address}:{port}'

    def post(self, resource_path, token=None, payload=None, content_type='application/json'):
        """
        Sends a POST request and returns a response
        """
        url = self._base_url + resource_path

        kwargs = {}

        if payload is not None:
            kwargs['data'] = payload

        request_headers = {
            'Accept': 'application/json',
            'Content-type': f'{content_type}',
        }

        if token is not None:
            request_headers['Authorization'] = f'Bearer {token}'

        kwargs['headers'] = request_headers

        response = requests.post(url, **kwargs)
        return response

    def get(self, resource_path, token, query_string='', payload=None, stream=False):
        """
        Sends a GET request and returns a response
        """
        url = self._base_url + resource_path + '?' + query_string
        kwargs = {}

        request_headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        kwargs['headers'] = request_headers
        kwargs['stream'] = stream

        if payload is not None:
            kwargs['data'] = payload

        response = requests.get(url, **kwargs)
        return response
