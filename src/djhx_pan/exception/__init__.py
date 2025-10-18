
class ClientError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message  # 方便访问


class ServerError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message