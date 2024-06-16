# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/chat.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/chat.proto\"\x07\n\x05\x45mpty\"=\n\x0fRegisterRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\n\n\x02ip\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\x05\"1\n\x10RegisterResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0c\n\x04\x62ody\x18\x02 \x01(\t\"\"\n\x0eGetInfoRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"+\n\x0fGetInfoResponse\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\"%\n\x11\x43onnectionRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"$\n\x12\x43onnectionResponse\x12\x0e\n\x06\x61\x63\x63\x65pt\x18\x01 \x01(\x08\"7\n\x07Message\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0c\n\x04\x62ody\x18\x02 \x01(\t\x12\x0c\n\x04time\x18\x03 \x01(\t\"\x1c\n\x08Response\x12\x10\n\x08received\x18\x01 \x01(\x08\x32\x9d\x01\n\rCentralServer\x12\x1d\n\tHeartbeat\x12\x06.Empty\x1a\x06.Empty\"\x00\x12\x37\n\x0eRegisterClient\x12\x10.RegisterRequest\x1a\x11.RegisterResponse\"\x00\x12\x34\n\rGetClientInfo\x12\x0f.GetInfoRequest\x1a\x10.GetInfoResponse\"\x00\x32\x8d\x01\n\rClientService\x12\x1d\n\tHeartbeat\x12\x06.Empty\x1a\x06.Empty\"\x00\x12\x37\n\nConnection\x12\x12.ConnectionRequest\x1a\x13.ConnectionResponse\"\x00\x12$\n\x0bSendMessage\x12\x08.Message\x1a\t.Response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.chat_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_EMPTY']._serialized_start=20
  _globals['_EMPTY']._serialized_end=27
  _globals['_REGISTERREQUEST']._serialized_start=29
  _globals['_REGISTERREQUEST']._serialized_end=90
  _globals['_REGISTERRESPONSE']._serialized_start=92
  _globals['_REGISTERRESPONSE']._serialized_end=141
  _globals['_GETINFOREQUEST']._serialized_start=143
  _globals['_GETINFOREQUEST']._serialized_end=177
  _globals['_GETINFORESPONSE']._serialized_start=179
  _globals['_GETINFORESPONSE']._serialized_end=222
  _globals['_CONNECTIONREQUEST']._serialized_start=224
  _globals['_CONNECTIONREQUEST']._serialized_end=261
  _globals['_CONNECTIONRESPONSE']._serialized_start=263
  _globals['_CONNECTIONRESPONSE']._serialized_end=299
  _globals['_MESSAGE']._serialized_start=301
  _globals['_MESSAGE']._serialized_end=356
  _globals['_RESPONSE']._serialized_start=358
  _globals['_RESPONSE']._serialized_end=386
  _globals['_CENTRALSERVER']._serialized_start=389
  _globals['_CENTRALSERVER']._serialized_end=546
  _globals['_CLIENTSERVICE']._serialized_start=549
  _globals['_CLIENTSERVICE']._serialized_end=690
# @@protoc_insertion_point(module_scope)
