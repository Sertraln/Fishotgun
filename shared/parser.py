class Parser:
    @staticmethod
    def decode(data:str):
        raise NotImplementedError("You must implement decode method")

    def encode(self) -> str:
        raise NotImplementedError("You must implement encode method")