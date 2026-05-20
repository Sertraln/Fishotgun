
from enum import Flag, auto
from shared.parser import Parser
from shared.packetlib import register_parser

@register_parser
class FishList(Flag,Parser):
    #Normal fish
    BAR = auto()
    SARDINE = auto()
    BARRACOUDA = auto()
    PIRANHA = auto()
    POISSON_CLOW = auto()
    POISSON_LUNE = auto()
    #Crustace / molluscque
    CREVETTE = auto()
    MOULE = auto()
    BULOT = auto()
    CRABE = auto()
    ARAIGNEE_DE_MER = auto()
    HOMARD = auto()
    CALAMAR = auto()
    #Sharks
    REQUIN_BLANC = auto()
    REQUIN_MARTEAU = auto()
    REQUIN_SCIE = auto()
    REQUIN_TOURNEVIS = auto()
    REQUIN_GOBELIN = auto()
    BABY_SHARK = auto()
    REQUIN_TIGRE = auto()
    #Magical fish
    POISSON_ARC_EN_CIEL = auto()
    FISHOBUS = auto()
    RAIE_ECTOPLASME = auto()
    POISSON_RADIOACTIF = auto()

    def get_size(self) -> int:
        return (self.value.bit_length() + 7) // 8
    
    def unlock(self, fish:'FishList'):
        self.value |= fish.value

    def is_unlocked(self, fish:'FishList') -> bool:
        return (self.value & fish.value) != 0
    
    def ordinal(flag_member):
        return flag_member.value.bit_length() - 1
    
    @staticmethod
    def decode(data:bytes):
        return FishList(int.from_bytes(data, 'big'))

    @staticmethod
    def encode(data:'FishList') -> str:
        return data.value.to_bytes((data.value.bit_length() + 7) // 8, 'big')


    