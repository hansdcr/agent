"""领域基础异常"""


class DomainException(Exception):
    """领域异常基类"""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
