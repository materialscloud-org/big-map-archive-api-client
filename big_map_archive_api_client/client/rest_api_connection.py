import requests

class RestAPIConnection:
    """Internal auxiliary class that handles the base connection."""

    def __init__(self, domain_name, port):
        """
        Initializes internal fields
        """
        self.domain_name = domain_name
        if domain_name=='127.0.0.1':
            self._base_url = f'https://{domain_name}:{port}'
        else:
            self._base_url = f'https://{domain_name}'

    def get(self, resource_path, token):
        """
        Sends a GET request and returns a response
        """
        url = self._base_url + resource_path

        kwargs = {}

        request_headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        kwargs['headers'] = request_headers
        kwargs['verify'] = True
        if self.domain_name == "127.0.0.1":
            kwargs['verify'] = False

        response = requests.get(url, **kwargs)
        return response

    def post(self, resource_path, token, payload=None):
        """
        Sends a POST request and returns a response
        """
        url = self._base_url + resource_path

        kwargs = {}

        if payload is not None:
            kwargs['data'] = payload

        request_headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        kwargs['headers'] = request_headers
        kwargs['verify'] = True
        if self.domain_name == "127.0.0.1":
            kwargs['verify'] = False

        response = requests.post(url, **kwargs)
        return response

    def put(self, resource_path, token, payload=None, content_type='application/json'):
        """
        Sends a PUT request and returns a response
        """
        url = self._base_url + resource_path

        kwargs = {}

        if payload is not None:
            kwargs['data'] = payload

        request_headers = {
            'Accept': 'application/json',
            'Content-type': f'{content_type}',
            'Authorization': f'Bearer {token}'
        }
        kwargs['headers'] = request_headers
        kwargs['verify'] = True
        if self.domain_name == "127.0.0.1":
            kwargs['verify'] = False

        response = requests.put(url, **kwargs)
        return response

    def delete(self, resource_path, token):
        """
        Sends a DELETE request and returns a response
        """
        url = self._base_url + resource_path

        kwargs = {}

        request_headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        kwargs['headers'] = request_headers
        kwargs['verify'] = True
        if self.domain_name == "127.0.0.1":
            kwargs['verify'] = False

        response = requests.delete(url, **kwargs)
        return response
