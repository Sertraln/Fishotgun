
from enum import Flag, auto
from shared.parser import Wrapper,Parser
from shared.packetlib import register_wrapper,register_parser
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from shared.registry import FishData

class FishList(Flag):
    #Normal fish
    BAR = auto()
    SARDINE = auto()
    BARRACUDA = auto()
    PIRANHA = auto()
    POISSON_CLOWN = auto()
    POISSON_LUNE = auto()
    #Crustace / mollusque
    CREVETTE = auto()
    MOULE = auto()
    CRABE = auto()
    HOMARD = auto()
    ARAIGNEE_DE_MER = auto()
    CRACKEN = auto()
    #Sharks
    BABY_SHARK = auto()
    REQUIN_TIGRE = auto()
    REQUIN_SCIE = auto()
    REQUIN_BLANC = auto()
    TRALALERO_TRALALA = auto()
    REQUIN_GOBELIN = auto()
    
    #Magical fish
    POISSON_ARC_EN_CIEL = auto()
    FISHOBUS = auto()
    POISSON_JOEL = auto()
    RAIE_ECTOPLASME = auto()
    POISSON_RADIOACTIF = auto()
    MAGIQUARPE = auto()

    def get_size() -> int:
        return (len(FishList) + 7) // 8
    
    def unlock(self, fish:'FishList'):
        return FishList(self.value | fish.value)

    def is_unlocked(self, fish:'FishList') -> bool:
        return (self.value & fish.value) != 0
    
    def ordinal(flag_member):
        return flag_member.value.bit_length() - 1
    
@register_wrapper(FishList)
class FishListWrapper(Wrapper):
    @staticmethod
    def decode(data:bytes) -> 'FishList':
        return FishList(int.from_bytes(data, 'big'))

    @staticmethod
    def encode(data:FishList) -> bytes:
        return data.value.to_bytes(FishList.get_size(), 'big') 

@register_parser
class FishInventory(Parser):
    size = FishList.get_size() + len(FishList)*4

    def __init__(self):
        self.fish_list = FishList(0)
        self.capacity = [0] * len(FishList)

    def add_fish(self, fish:FishList, quantity:int=1):
        self.fish_list = self.fish_list.unlock(fish)
        index = FishList.ordinal(fish)
        self.capacity[index] += quantity
    
    def clear_inventory(self):
        self.capacity = [0] * len(FishList)

    def get_total_price(self) -> int:
        from shared.registry import fish_list
        total = 0
        for i in range(len(FishList)):
            if self.capacity[i] > 0:
                fish_data = fish_list[i]
                # DEBUG : Vérifie ce qui est calculé
                print(f"Poisson {i}: {self.capacity[i]} x {fish_data.rarity[2]}")
                total += self.capacity[i] * fish_data.rarity[2]
        print(f"Total calculé : {total}")
        return total

    @staticmethod
    def decode(data:bytes) -> 'FishInventory':
        inventory = FishInventory()
        size = FishList.get_size()
        inventory.fish_list = FishListWrapper.decode(data[0:size])
        for i in range(len(FishList)):
            inventory.capacity[i] = int.from_bytes(data[size + i*4: size+4 + i*4], 'big')
        return inventory
        

    @staticmethod
    def encode(data: 'FishInventory') -> bytes:
        encoded = FishListWrapper.encode(data.fish_list)
        for i in range(len(data.capacity)):
            encoded += data.capacity[i].to_bytes(4, 'big')
        return encoded