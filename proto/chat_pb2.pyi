from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("username", "ip", "port")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    username: str
    ip: str
    port: int
    def __init__(self, username: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = ("success", "body")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    success: bool
    body: str
    def __init__(self, success: bool = ..., body: _Optional[str] = ...) -> None: ...

class GetInfoRequest(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class GetInfoResponse(_message.Message):
    __slots__ = ("ip", "port")
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    port: int
    def __init__(self, ip: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...

class ConnectionRequest(_message.Message):
    __slots__ = ("username",)
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class ConnectionResponse(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("username", "body", "time")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    username: str
    body: str
    time: str
    def __init__(self, username: _Optional[str] = ..., body: _Optional[str] = ..., time: _Optional[str] = ...) -> None: ...
