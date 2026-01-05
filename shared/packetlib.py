if __name__ == "__main__" :
    import os
    import sys
    _ROOT = os.path.dirname(os.path.dirname(__file__))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)

from shared.parser import Parser,Wrapper
import struct
from typing import Callable, Any,get_type_hints, Dict, Type, TypeVar

T = TypeVar("T", bound=Parser)

registry: Dict[str, Type[Parser]] = {}

def register_parser(cls: Type[T]) -> Type[T]:
    """Decorator to register a Parser subclass
    *Exemple* : `@register_parser`"""
    if not issubclass(cls, Parser):
        raise ParsingException("Can only register subclasses of Parser")
    return _register(cls)

class ParsingException(Exception):   
    def __init__(self, message: str):
        super().__init__("packet : "+message)

class HandlelingExeption(Exception):   
    def __init__(self, message: str):
        super().__init__("packet handling : "+message)

#init parser
def init():
    global _id_type
    import shared.parsedata.vec3data
    import shared.parsedata.input
    # Générer type_id avec les indices
    global _type_id
    _type_id = {cls: idx for idx, cls in enumerate(_id_type)}

clientBoundDataPacket : list[bool] = []
serverBoundDataPacket : list[bool] = []

def unparse(data:bytes,clientbound:bool) -> list[tuple[int,list]]:
    """Decode une série de packets encodés"""
    result = []
    try:
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
    except IndexError:
        raise ParsingException("Error while unparse packet data, probably packet list different from the client and server")
    return result

def one_unparse(data:bytes) -> tuple[int,list]:
    """Decode a encoded packet"""
    id = data[0]
    if len(data) == 1:
        return id,[]
    return id,unparse_blob(data[1:])

def unparse_blob(data:bytes) -> list:
    """Decode a list/tuple encoded"""
    nb = data[0]
    elements = data[1+nb:]
    count = 0
    out = []
    for i in range(nb):
        size = data[i+1]
        out.append(_unparse_data(elements[count:count+size]))
        count += size
    return out

def parser(id:int,data:list | tuple) -> bytes:
    """Encode a list/tuple or any parsing type"""
    data_type = data.__class__
    if data_type not in (list,tuple,dict):
        return _parse_data(data)
    return bytes([id]) + _parse_blob(data)

def _parse_blob(data:list) -> bytes:
    """Encode a list/tuple"""
    size = len(data)
    prefix = [size]
    encode = b''
    for e in data:
        encoded = _parse_data(e)
        encode += encoded
        prefix.append(len(encoded))
    return bytes(prefix)+ encode

def _parse_int(data:int) -> bytes:
    size = (data.bit_length() + 8) // 8
    if size >= 256:
        raise ParsingException("Integer too large to parse")
    return data.to_bytes(size, "big", signed=True)

_parse_table : dict[type,Callable[[Any],bytes]] = {
    str: lambda s: bytes(s,"utf-8"),
    int: _parse_int,
    float: lambda f: struct.pack('>f',f),
    list: lambda l: _parse_blob(l),
    tuple: lambda t: _parse_blob(t),
}

_unparse_table = {
    str: lambda b: b.decode("utf-8"),
    int: lambda b: int.from_bytes(b, "big", signed=True),
    float: lambda b: struct.unpack('>f',b)[0],
    list: lambda b: unparse_blob(b),
    tuple: lambda b: tuple(unparse_blob(b)),
}

_id_type = [float,int,list,tuple,str]

_type_id = {}

def _insert_sorted_by_qualname(cls):
    """Insert cls into id_type sorted by __qualname__"""
    if cls in _id_type:
        return
    
    qualname = cls.__qualname__
    insert_pos = len(_id_type)
    
    for i, existing_cls in enumerate(_id_type):
        if existing_cls.__qualname__ > qualname:
            insert_pos = i
            break
    
    _id_type.insert(insert_pos, cls)

def register_wrapper(original):
    """Decorator to register a Wrapper subclass\n 
    *Exemple* : `@register_wrapper(Vec3)`"""
    def decorator(cls):
        if not issubclass(cls, Wrapper):
            raise ParsingException("Can only register subclasses of Wrapper")
        return _register(cls,original)
    
    return decorator

def _generate_func(func:Callable[[Any],bytes | list | tuple], *owner_types:type | None) -> Callable[[Any],bytes]:
    """Wrap parser encode helpers while resolving forward references safely."""
    localns: Dict[str, type] = {}
    for owner in owner_types:
        if owner is None:
            continue
        localns[owner.__name__] = owner

    try:
        return_type = get_type_hints(
            func,
            globalns=getattr(func, "__globals__", {}),
            localns=localns or None,
        ).get("return", None)
    except NameError:
        # If annotations reference symbols not yet defined, fall back gracefully.
        return_type = None
    if return_type == list or return_type == tuple or None:
        def wrapper(data:Any) -> bytes:
            return parser(func(data))
        return wrapper
    elif return_type == bytes:
        return func
    else:
        raise ParsingException("Unsupported return type for parser function : " + str(return_type))

def _register(cls: Type[T], wcls: type | None = None) -> Type[T]:
    if wcls is None:
        wcls = cls
    
    _insert_sorted_by_qualname(wcls)
    
    if hasattr(cls, "encode") and callable(getattr(cls, "encode")):
        _parse_table[wcls] = _generate_func(cls.encode, wcls)
    if hasattr(cls, "decode") and callable(getattr(cls, "decode")):
        _unparse_table[wcls] = cls.decode
    return cls

def _parse_data(data)->bytes:
    """Local methode to parse data"""
    data_type = data.__class__
    type_byte = _type_id.get(data_type)
    if type_byte is None:
        raise ParsingException(f"Unsupported data type/non regitered: {data_type}")
    return bytes([type_byte]) + _parse_table[data_type](data)

def _unparse_data(data:bytes):
    type_byte = data[0]
    if type_byte >= len(_id_type):
        raise ParsingException(f"Unsupported data type/non regitered: {type_byte}")
    data_type = _id_type[type_byte]
    return _unparse_table[data_type](data[1:])

if __name__ == "__main__":
    from ursina import Vec3
    import time
    sys.modules["shared.packetlib"] = sys.modules[__name__]
    from shared.parsedata.input import KeyStates
    init()
    print("table :",_id_type)
    print("parser : out : ",parser(1,KeyStates()))
    print(_unparse_data(b'\x05\x02\x02\t\x00\x00\x03\x18\x87\xe9\xb9\xdb\xe2\x83D'))