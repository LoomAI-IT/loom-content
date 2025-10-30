class ErrInsufficientBalance(Exception):
    def __init__(self, message="Insufficient balance"):
        self.message = message
        super().__init__(self.message)


class ErrNoImageData(Exception):
    def __init__(self, message="No image data returned from AI"):
        self.message = message
        super().__init__(self.message)