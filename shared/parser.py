class Parser:
    @staticmethod
    def decode(data:bytes):
        raise NotImplementedError("You must implement decode method for ", data)

    @staticmethod
    def encode(data) -> str:
        raise NotImplementedError("You must implement encode method for ", data.__class__.__name__)
    
class Wrapper:
    @staticmethod
    def decode(data:bytes):
        raise NotImplementedError("You must implement decode method for ", data)
    
    @staticmethod
    def encode(data) -> str:
        raise NotImplementedError("You must implement encode method for ", data.__class__.__name__)
