class ErrInsufficientBalance(Exception):
    def __init__(self, message="Insufficient balance"):
        self.message = message
        super().__init__(self.message)