import requests
import user.config as config  # Assuming config.py is in the same directory

class UserAuthenticator:
    def __init__(self):
        self.host = config.HOST
        self.username = config.USER
        self.password = config.PASSWORD
        self.headers = self._authenticate()

    def _authenticate(self):
        auth = requests.post(self.host + '/users/' + self.username + '/login', params={'password': self.password})
        if auth.status_code == 200:
            token = auth.json()['session']
            headers = {'X-ArchivesSpace-Session': token}
            return headers
        else:
            return None

