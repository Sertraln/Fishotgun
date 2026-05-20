import client.data as data
from client.menus.mainmenu import join_menu,get_name,set_name

def _encode_string(s: str) -> bytes:
    encoded = s.encode("utf-8")
    length = len(encoded)
    if length >= 65536:
        raise ValueError("String too long to encode")
    return length.to_bytes(2, "big") + encoded

def _decode_string(data: bytes, offset: int) -> tuple[str, int]:
    if offset + 2 > len(data):
        raise ValueError("Not enough data to decode string length")
    length = int.from_bytes(data[offset:offset+2], "big")
    offset += 2
    if offset + length > len(data):
        raise ValueError("Not enough data to decode string content")
    s = data[offset:offset+length].decode("utf-8")
    return s, offset + length

def save_global_data():
    print("saving")
    with open(data.total_path,"wb") as f:
        f.write(_encode_string(get_name()))
        f.write(join_menu.save())

def load_global_data():
    try:
        with open(data.total_path,"rb") as f:
            raw = f.read()
        if len(raw) < 2:
            raise ValueError("Invalid data file")
        name, offset = _decode_string(raw, 0)
        set_name(name)
        offset = join_menu.load(raw[offset:])
    except FileNotFoundError as e:
        pass
    except Exception as e:
        print(f"Global data load error : {e}")