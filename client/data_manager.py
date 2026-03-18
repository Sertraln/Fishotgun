from typing import Any
import json

def save_data(file_path:str,data:Any):
    with open(file_path,"w") as f:
        f.write(json.dumps(data))

def load_data(file_path:str) -> Any:
    with open(file_path,"r") as f:
        data = json.loads(f.read())
    return data