from django.contrib.auth.hashers import BasePasswordHasher


class NoopPasswordHasher(BasePasswordHasher):
    """
    A hasher that does not hash to speed up tests.
    """
    algorithm = 'plain'

    def encode(self, password, salt):
        return f'{self.algorithm}${password}'

    def salt(self):
        return None

    def verify(self, password, encoded):
        algo, decoded = encoded.split('$', 1)
        return password == decoded

    def safe_summary(self, encoded):
        return {_('desc'): 'Not hashed'}

