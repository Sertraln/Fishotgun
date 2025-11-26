from shared.parser import Parser,Wrapper
import struct
from typing import cast, Callable
import zlib

clientBoundDataPacket : list[bool] = []
serverBoundDataPacket : list[bool] = []

def unparse(data:bytes,clientbound:bool) -> list[tuple[int,list[str]]]:
    result = []
    while len(data) > 0:
        packet_id = data[0]
        if clientbound and clientBoundDataPacket[packet_id]:
            taille = 2+sum(data[2:2+data[1]])+data[1]
            result.append(one_unparse(data[:taille]))
            data = data[taille:]
        elif clientbound and not clientBoundDataPacket[packet_id]:
            result.append(one_unparse(data[:1]))
            data = data[1:]
        elif not clientbound and serverBoundDataPacket[packet_id]:
            taille = 2+sum(data[2:2+data[1]])+data[1]
            result.append(one_unparse(data[:taille]))
            data = data[taille:]
        elif not clientbound and not serverBoundDataPacket[packet_id]:
            result.append(one_unparse(data[:1]))
            data = data[1:]
    return result

def one_unparse(data:bytes) -> tuple[int,list]:
    print("unparse : in ",data)
    id = data[0]
    if len(data) == 1:
        return id,[]
    return id,unparse_blob(data[1:])

def unparse_blob(data:bytes) -> list:
    nb = data[0]
    elements = data[1+nb:]
    count = 0
    out = []
    for i in range(nb):
        size = data[i+2]
        out.append(unparse_data(elements[count:count+size]))
        count += size
    return out

def parser(id:int,data:list | tuple) -> bytes:
    print("parser : ",data)
    size = len(data)
    prefix = [id,size]
    encode = [] * size
    for e in data:
        encode.append(parse_data(e))
        prefix.append(len(encode))
    return bytes(prefix)+encode

def parse_int(data:int) -> bytes:
    size = (data.bit_length() + 8) // 8
    if size >= 256:
        raise PacketException("Integer too large to parse")
    return data.to_bytes(size, "big", signed=True)

parse_table = {
    str: lambda s: bytes(s,"utf-8"),
    int: parse_int,
    float: lambda f: struct.pack('>f',f),
    list: lambda l: parser(type_id[l.__class__],l),
    tuple: lambda t: parser(type_id[t.__class__],t),
}

unparse_table = {
    str: lambda b: b.decode("utf-8"),
    int: lambda b: int.from_bytes(b, "big", signed=True),
    float: lambda b: struct.unpack('>f',b)[0],
    list: lambda b: unparse_blob(b),
    tuple: lambda b: tuple(unparse_blob(b)),
}

type_id = {
    str: zlib.crc32(b'str'),
    int: zlib.crc32(b'int'),
    float: zlib.crc32(b'float'),
    list: zlib.crc32(b'list'),
    tuple: zlib.crc32(b'tuple'),
}

id_type = {v: k for k, v in type_id.items()}

def register_wrapper(original):
    def decorator(cls):
        if not issubclass(cls, Wrapper):
            raise PacketException("Can only register subclasses of Wrapper")
        return register(cls,original)
    return decorator

def register_parser(cls):
    if not issubclass(cls, Parser):
        raise PacketException("Can only register subclasses of Parser")
    return register(cls)

def register(cls,wcls = None):
    if wcls is None:
        wcls = cls
    type_byte = zlib.crc32(wcls.__qualname__.encode('utf-8'))
    type_id[wcls] = type_byte
    id_type[type_byte] = wcls
    if hasattr(cls, "parse") and callable(getattr(cls, "parse")):
        parse_table[cls] = cls.parse
    if hasattr(cls, "unparse") and callable(getattr(cls, "unparse")):
        unparse_table[cls] = cls.unparse
    return cls

def parse_data(data)->bytes:
    data_type = data.__class__
    type_byte = type_id.get(data_type)
    if not type_byte :
        raise PacketException(f"Unsupported data type/non regitered: {data_type}")
    return bytes([type_byte]) + parse_table[data_type](data)

def unparse_data(data:bytes):
    type_byte = data[0]
    data_type = id_type.get(type_byte)
    if not data_type :
        raise PacketException(f"Unsupported data type/non regitered: {data_type}")
    return unparse_table[data_type](data[1:])

if __name__ == "__main__":
    print("parser : out : ",parser(0,["test","test2"]))
    print(unparse(parser(0,["test","test2"])))

class PacketException(Exception):   
    def __init__(self, message: str):
        super().__init__("packet : "+message)