from shared.parser import Parser,Wrapper

clientBoundDataPacket : list[bool] = []
serverBoundDataPacket : list[bool] = []

def unparse(data:bytes,clientbound:bool) -> list[tuple[int,list[str]]]:
    result = []
    while len(data) > 0:
        if clientbound and clientBoundDataPacket[data[0]]:
            taille = 2+sum(data[2:2+data[1]])+data[1]
            result.append(one_unparse(data[:taille]))
            data = data[taille:]
        elif clientbound and not clientBoundDataPacket[data[0]]:
            result.append(one_unparse(data[:1]))
            data = data[1:]
        elif not clientbound and serverBoundDataPacket[data[0]]:
            taille = 2+sum(data[2:2+data[1]])+data[1]
            result.append(one_unparse(data[:taille]))
            data = data[taille:]
        elif not clientbound and not serverBoundDataPacket[data[0]]:
            result.append(one_unparse(data[:1]))
            data = data[1:]
    return result

def one_unparse(data:bytes) -> tuple[int,list[str]]:
    print("unparse : in ",data)
    id = data[0]
    if len(data) == 1:
        return id,[]
    nb = data[1]
    elements = data[2+nb:]
    count = 0
    out = []
    for i in range(nb):
        size = data[i+2]
        out.append(elements[count:count+size].decode("utf-8"))
        count += size
    return id,out

def parser(id:int,data:list[str | Parser | Wrapper]) -> bytes:
    print("parser : ",data)
    prefix = [id]
    parsed_data = []
    prefix.append(len(data))
    for e in data:
        if isinstance(e,Wrapper):
            encode = e.encode().encode("utf-8")
        elif isinstance(e,Parser):
            encode = e.encode().encode("utf-8")
        elif isinstance(e,str):
            encode = e.encode("utf-8")
        else:
            raise Exception("parser: unsupported data type :"+str(type(e)))
        prefix.append(len(encode))
        parsed_data.append(encode)
    return bytes(prefix)+b"".join(parsed_data)


if __name__ == "__main__":
    print("parser : out : ",parser(0,["test","test2"]))
    print(unparse(parser(0,["test","test2"])))

