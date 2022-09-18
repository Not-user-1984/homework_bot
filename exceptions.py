class APIUnexpectedHTTPStatus(Exception):
    pass


class NonStatusException(APIUnexpectedHTTPStatus):
    pass


class CriticalException(Exception):
    pass


class EndpointUnexpected(APIUnexpectedHTTPStatus):
    pass


class CheckResponseException(APIUnexpectedHTTPStatus):
    pass


class ParseStatusException(APIUnexpectedHTTPStatus):
    pass


class NoTokensException(CriticalException):
    pass
