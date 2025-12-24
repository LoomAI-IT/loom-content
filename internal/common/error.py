class ErrInsufficientBalance(Exception):
    def __init__(self, message="Insufficient balance"):
        self.message = message
        super().__init__(self.message)


class ErrNoImageData(Exception):
    def __init__(self, message="No image data returned from AI"):
        self.message = message
        super().__init__(self.message)


class ErrExternalServiceError(Exception):
    def __init__(self, status_code: int, response_body: str = ""):
        self.status_code = status_code
        self.response_body = response_body
        self.message = f"External service error: {status_code}"
        super().__init__(self.message)