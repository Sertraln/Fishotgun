from shared.parser import Parser
from shared.packetlib import register_parser

@register_parser
class FishingSessionData(Parser):
    def __init__(self, fish_ids: list[int] = None):
        self.fish_ids = fish_ids if fish_ids else [0, 0, 0, 0]

    @staticmethod
    def decode(data: bytes) -> 'FishingSessionData':
        session = FishingSessionData()
        # Conversion du flux binaire en liste de 4 entiers
        session.fish_ids = list(data)
        return session

    @staticmethod
    def encode(data: 'FishingSessionData') -> bytes:
        # Transformation de la liste de 4 entiers en tableau de bytes bruts
        return bytes(data.fish_ids)