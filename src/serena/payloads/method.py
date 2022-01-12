from __future__ import annotations

import abc
import enum
from typing import Any, ClassVar, Dict, Generic, TypeVar

import attr

from serena.enums import ReplyCode
from serena.frame import Frame, FrameType
from serena.payloads.encoding import (
    aq_type,
    decode_attrs_attribute,
    encode_attrs_attribute,
)
from serena.utils.buffer import DecodingBuffer, EncodingBuffer


class ClassID(enum.IntEnum):
    """
    Enumeration of method class IDs.
    """

    CONNECTION = 10
    CHANNEL = 20
    EXCHANGE = 40
    QUEUE = 50
    BASIC = 60
    TX = 90


@attr.s(frozen=True, slots=True, init=True)
class MethodPayload(abc.ABC):
    """
    Base class for all method payloads.
    """

    #: The class ID for this payload.
    klass: ClassVar[ClassID]

    #: The method ID for this payload. These are shared between classes and are not unique.
    method: ClassVar[int]

    #: If this is a payload sent FROM the client. This may be True on payloads received by the
    #: client, too.
    is_client_side: ClassVar[bool]


_PAYLOAD_TYPE = TypeVar("_PAYLOAD_TYPE", bound=MethodPayload)


@attr.s(frozen=True, slots=True)
class MethodFrame(Frame, Generic[_PAYLOAD_TYPE]):
    """
    A frame that carries a method body.
    """

    type = FrameType.METHOD

    #: The payload for this frame.
    payload: _PAYLOAD_TYPE = attr.ib()


## == CONNECTION == ##
@attr.s(frozen=True, slots=True)
class StartPayload(MethodPayload):
    """
    Payload for the ``start`` method.
    """

    klass = ClassID.CONNECTION
    method = 10
    is_client_side = False

    #: The major version of the protocol.
    version_major: int = attr.ib(metadata=aq_type("octet"))

    #: The minor version of the protocol.
    version_minor: int = attr.ib(metadata=aq_type("octet"))

    #: The server properties.
    properties: Dict[str, Any] = attr.ib()

    #: The available security mechanisms.
    mechanisms: bytes = attr.ib()

    #: The available message locales.
    locales: bytes = attr.ib()


@attr.s(frozen=True, slots=True)
class StartOkPayload(MethodPayload):
    """
    Payload for the ``start-ok`` method.
    """

    klass = ClassID.CONNECTION
    method = 11
    is_client_side = True

    #: The client properties.
    properties: Dict[str, Any] = attr.ib()

    #: The selected security mechanism.
    mechanism: str = attr.ib()

    #: The security response data.
    response: bytes = attr.ib()

    #: The selected locale.
    locale: str = attr.ib()


@attr.s(frozen=True, slots=True)
class SecurePayload(MethodPayload):
    """
    Payload for the ``secure`` method.
    """

    klass = ClassID.CONNECTION
    method = 20
    is_client_side = False

    #: The security challenge data.
    challenge: bytes = attr.ib()


@attr.s(frozen=True, slots=True)
class SecureOkPayload(MethodPayload):
    """
    Payload for the ``secure-ok`` method.
    """

    klass = ClassID.CONNECTION
    method = 21
    is_client_side = True

    #: The security response data.
    response: bytes = attr.ib()


@attr.s(frozen=True, slots=True)
class TunePayload(MethodPayload):
    """
    Payload for the ``tune`` method.
    """

    klass = ClassID.CONNECTION
    method = 30
    is_client_side = False

    #: The server's proposed maximum channels.
    max_channels: int = attr.ib(metadata=aq_type("short"))

    #: The server's proposed maximum frame size.
    max_frame_size: int = attr.ib(metadata=aq_type("long"))

    #: The server's desired heartbeat delay.
    heartbeat_delay: int = attr.ib(metadata=aq_type("short"))


@attr.s(frozen=True, slots=True)
class TuneOkPayload(MethodPayload):
    """
    Payload for the ``tune-ok`` method.
    """

    klass = ClassID.CONNECTION
    method = 31
    is_client_side = True

    #: The client's negotiated maximum channels.
    max_channels: int = attr.ib(metadata=aq_type("short"))

    #: The client's negotiated maximum frame size.
    max_frame_size: int = attr.ib(metadata=aq_type("long"))

    #: The client's desired heartbeat delay.
    heartbeat_delay: int = attr.ib(metadata=aq_type("short"))


@attr.s(frozen=True, slots=True)
class ConnectionOpenPayload(MethodPayload):
    """
    Payload for the ``open`` method.
    """

    klass = ClassID.CONNECTION
    method = 40
    is_client_side = False

    #: The virtual host to open a connection to.
    virtual_host: str = attr.ib()

    reserved_1: str = attr.ib(default="")
    reserved_2: bool = attr.ib(default=True)


@attr.s(frozen=True, slots=True)
class ConnectionOpenOkPayload(MethodPayload):
    """
    Payload for the ``open-ok`` method.
    """

    klass = ClassID.CONNECTION
    method = 41
    is_client_side = True

    reserved_1: str = attr.ib()


@attr.s(frozen=True, slots=True)
class ClosePayload(MethodPayload):
    """
    Payload for the ``close`` method.
    """

    klass = ClassID.CONNECTION
    method = 50
    is_client_side = True

    #: The code for the error that caused this close.
    reply_code: ReplyCode = attr.ib(converter=ReplyCode, metadata=aq_type("short"))

    #: The text for the error that caused this close.
    reply_text: str = attr.ib()

    #: The class of the method that caused this close.
    class_id: int = attr.ib(metadata=aq_type("short"))

    #: The class of the method that caused this close.
    method_id: int = attr.ib(metadata=aq_type("short"))


@attr.s(frozen=True, slots=True)
class CloseOkPayload(MethodPayload):
    """
    Payload (empty) for the ``close-ok`` method.
    """

    klass = ClassID.CONNECTION
    method = 51
    is_client_side = True


## == CHANNEL == ##
@attr.s(frozen=True, slots=True)
class ChannelOpenPayload(MethodPayload):
    """
    Payload for the ``open`` method.
    """

    klass = ClassID.CHANNEL
    method = 10
    is_client_side = False

    reserved_1: str = attr.ib(default="")


@attr.s(frozen=True, slots=True)
class ChannelOpenOkPayload(MethodPayload):
    """
    Payload for the ``open-ok`` method.
    """

    klass = ClassID.CHANNEL
    method = 11
    is_client_side = True

    reserved_1: bytes = attr.ib()


@attr.s(frozen=True, slots=True)
class FlowPayload(MethodPayload):
    """
    Payload for the ``flow`` method.
    """

    klass = ClassID.CHANNEL
    method = 20
    is_client_side = True

    #: If the channel should start processing messages again or not.
    active: bool = attr.ib()


@attr.s(frozen=True, slots=True)
class FlowOkPayload(MethodPayload):
    """
    Payload for the ``flow-ok`` method.
    """

    klass = ClassID.CHANNEL
    method = 21
    is_client_side = True

    #: See :attr:`.FlowPayload.active`.
    active: bool = attr.ib()


@attr.s(frozen=True, slots=True)
class ChannelClosePayload(MethodPayload):
    """
    Payload for the ``close`` method.
    """

    klass = ClassID.CHANNEL
    method = 40
    is_client_side = True

    #: The code for the error that caused this close.
    reply_code: ReplyCode = attr.ib(converter=ReplyCode, metadata=aq_type("short"))

    #: The text for the error that caused this close.
    reply_text: str = attr.ib()

    #: The class of the method that caused this close.
    class_id: int = attr.ib(metadata=aq_type("short"))

    #: The class of the method that caused this close.
    method_id: int = attr.ib(metadata=aq_type("short"))


@attr.s(frozen=True, slots=True)
class ChannelCloseOkPayload(MethodPayload):
    """
    Payload for the ``close-ok`` method.
    """

    klass = ClassID.CHANNEL
    method = 41
    is_client_side = True

    # empty body


## QUEUE ##
@attr.s(frozen=True, slots=True)
class QueueDeclarePayload(MethodPayload):
    """
    Payload for the ``declare`` method.
    """

    klass = ClassID.QUEUE
    method = 10
    is_client_side = False

    reserved_1: int = attr.ib(metadata=aq_type("short"))

    #: The name of the queue being declared. May be empty.
    name: str = attr.ib()

    #: If True, the server will return a DeclareOk if the queue exists, and an error if it doesn't.
    passive: bool = attr.ib()

    #: If True, then the queue will persist through restarts.
    durable: bool = attr.ib()

    #: If True, then the queue is exclusive to this connection.
    exclusive: bool = attr.ib()

    #: If True, then the queue is automatically deleted when all consumers are finished using it.
    auto_delete: bool = attr.ib()

    #: If True, no Declare-Ok method will be sent by the server.
    no_wait: bool = attr.ib()

    #: Implementation-specific arguments for the declaration.
    arguments: Dict[str, Any] = attr.ib()


@attr.s(frozen=True, slots=True)
class QueueDeclareOkPayload(MethodPayload):
    """
    Payload for the ``declare-ok`` method.
    """

    klass = ClassID.QUEUE
    method = 11
    is_client_side = True

    #: The name of the queue.
    name: str = attr.ib()

    #: The number of the messages present in the queue.
    message_count: int = attr.ib(metadata=aq_type("long"))

    #: The number of consumers consuming from the queue.
    consumer_count: int = attr.ib(metadata=aq_type("long"))


## BASIC ##
@attr.s(frozen=True, slots=True)
class BasicPublishPayload(MethodPayload):
    """
    Payload for the ``publish`` method.
    """

    klass = ClassID.BASIC
    method = 40
    is_client_side = False

    reserved_1: int = attr.ib(metadata=aq_type("short"))

    #: The name of the exchange to publish the data to.
    name: str = attr.ib()

    #: The routing key to use.
    routing_key: str = attr.ib()

    #: If True, the server will return a Return message if the message is unrouteable.
    mandatory: bool = attr.ib()

    #: If True, the server will return a Return message if the message cannot be sent to a consumer
    #: immediately.
    immediate: bool = attr.ib()


class BasicDeliverPayload(MethodPayload):
    """
    Payload for the ``deliver`` method.
    """

    klass = ClassID.BASIC
    method = 60
    is_client_side = True

    #: The identifier for the consumer.
    consumer_tag: str = attr.ib()

    #: The server-assigned delivery tag.
    delivery_tag: int = attr.ib(metadata=aq_type("longlong"))

    #: Indicates that the message has been previously delivered.
    redelivered: bool = attr.ib()

    #: The name of the exchange the message was originally published to.
    exchange_name: str = attr.ib()

    #: The routing key for the message.
    routing_key: str = attr.ib()



PAYLOAD_TYPES = {
    ClassID.CONNECTION: {
        StartPayload.method: StartPayload,
        StartOkPayload.method: StartOkPayload,
        SecurePayload.method: SecurePayload,
        SecureOkPayload.method: SecureOkPayload,
        TunePayload.method: TunePayload,
        TuneOkPayload.method: TuneOkPayload,
        ConnectionOpenPayload.method: ConnectionOpenPayload,
        ConnectionOpenOkPayload.method: ConnectionOpenOkPayload,
        ClosePayload.method: ClosePayload,
        CloseOkPayload.method: CloseOkPayload,
    },
    ClassID.CHANNEL: {
        ChannelOpenPayload.method: ChannelOpenPayload,
        ChannelOpenOkPayload.method: ChannelOpenOkPayload,
        FlowPayload.method: FlowPayload,
        FlowOkPayload.method: FlowOkPayload,
        ChannelClosePayload.method: ChannelClosePayload,
        ChannelCloseOkPayload.method: ChannelCloseOkPayload,
    },
    ClassID.QUEUE: {
        QueueDeclarePayload.method: QueueDeclarePayload,
        QueueDeclareOkPayload.method: QueueDeclareOkPayload,
    },
    ClassID.BASIC: {
        BasicPublishPayload.method: BasicPublishPayload,
        BasicDeliverPayload.method: BasicDeliverPayload,
    },
}


def deserialise_payload(body: bytes) -> MethodPayload:
    """
    Deserialises a method payload.

    :param body: The body of the payload to decode.
    :return: A :class:`.MethodPayload` matching the returned payload.
    """

    klass, method, rest = (
        ClassID(int.from_bytes(body[0:2], byteorder="big")),
        int.from_bytes(body[2:4], byteorder="big"),
        body[4:],
    )

    payload_klass = PAYLOAD_TYPES[klass][method]
    attr.resolve_types(payload_klass)
    fields = attr.fields(payload_klass)
    init_params = {}
    buffer = DecodingBuffer(rest)

    for field in fields:
        init_params[field.name] = decode_attrs_attribute(buffer, field)

    return payload_klass(**init_params)  # type: ignore


def serialise_payload(payload: MethodPayload) -> bytes:
    """
    Serialises a payload into a bytearray.
    """

    typ = type(payload)
    attr.resolve_types(typ)

    header = typ.klass.to_bytes(2, byteorder="big") + typ.method.to_bytes(2, byteorder="big")

    buf = EncodingBuffer()
    fields = attr.fields(typ)
    for field in fields:
        encode_attrs_attribute(buf, field, getattr(payload, field.name))

    buf.force_write_bits()
    return header + buf.get_data()


def method_payload_name(payload: MethodPayload):
    """
    Gets the name of a method payload.
    """

    return f"{payload.klass.name}/{payload.method}/{type(payload).__name__}"
