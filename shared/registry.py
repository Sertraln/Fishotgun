from shared.parsedata.fishlist import FishList
from enum import IntEnum

class Rarity(IntEnum):
    ABONDANTS = 0
    DISCRETS = 1
    INSAISISSABLES = 2

class FishData:
    def __init__(self, fish:FishList,name:str,descritpion:str,rarity:Rarity):
        self.fishid = fish
        self.name = name
        self.description = descritpion
        self.rarity = rarity

# name, description
fish_list : list[(str,str)] = [
    #Poissons de base
    FishData(FishList.BAR,"bar","Un prédateur discret aux reflets d’argent, rapide comme l’éclair sous les vagues.",Rarity.ABONDANTS),
    FishData(FishList.SARDINE,"sardine","Petite mais insaisissable, elle nage toujours là où on ne l’attend pas.",Rarity.ABONDANTS),
    FishData(FishList.BARRACOUDA,"barracouda","Une torpille vivante aux dents acérées et au regard glacé.",Rarity.ABONDANTS),
    FishData(FishList.PIRANHA,"piranha","Minuscule monstre des rivières, capable de transformer la panique en carnage.",Rarity.DISCRETS),
    FishData(FishList.POISSON_CLOW,"poisson_clown","Le roi coloré des récifs, aussi drole qu’imprévisible.",Rarity.DISCRETS),
    FishData(FishList.POISSON_LUNE,"poisson_lune","Un géant paisible qui dérive dans l’océan comme une planète perdue.",Rarity.INSAISISSABLES),
    #Crustacés et mollusques
    FishData(FishList.CREVETTE,"crevette","Petite acrobate marine, toujours prête à bondir hors du danger.",Rarity.ABONDANTS),
    FishData(FishList.MOULE,"moule","Bien accrochée à son rocher, elle traverse les tempêtes sans bouger d’un pouce.",Rarity.ABONDANTS),
    FishData(FishList.BULOT,"bulot","Un aventurier à coquille, explorant les fonds marins avec curiosité.",Rarity.DISCRETS),
    FishData(FishList.CRABE,"crabe","Un guerrier à pinces, toujours prêt à défendre son territoire avec férocité.",Rarity.DISCRETS),
    FishData(FishList.ARAIGNEE_DE_MER,"araignee_de_mer","Un prédateur à huit pattes, se faufilant dans les recoins sombres pour attraper ses proies.",Rarity.INSAISISSABLES),
    FishData(FishList.HOMARD,"homard","Un noble crustacé, arborant une armure rouge et des pinces redoutables.",Rarity.INSAISISSABLES),
    FishData(FishList.CALAMAR,"calamar","Un maître de la furtivité, capable de disparaître dans un nuage d’encre pour échapper à ses ennemis.",Rarity.INSAISISSABLES),
    #Requins
    FishData(FishList.REQUIN_BLANC,"requin_blanc","Le roi des océans, un prédateur redoutable au sourire terrifiant.",Rarity.DISCRETS),
    FishData(FishList.REQUIN_MARTEAU,"requin_marteau","Un chasseur à la tête en forme de T, utilisant son crâne pour détecter les moindres vibrations dans l’eau.",Rarity.DISCRETS),
    FishData(FishList.REQUIN_SCIE,"requin_scie","Un prédateur à la mâchoire en forme de scie, capable de trancher ses proies en un clin d’œil.",Rarity.INSAISISSABLES),
    FishData(FishList.REQUIN_TOURNEVIS,"requin_tournevis","Un requin rare avec une spirale sur la tête, se déplaçant dans l’eau avec une grâce hypnotique.",Rarity.INSAISISSABLES),
    FishData(FishList.REQUIN_GOBELIN,"requin_gobelin","Un prédateur des profondeurs, avec un museau allongé et des dents proéminentes, se faufilant dans les abysses à la recherche de proies inattendues.",Rarity.INSAISISSABLES),
    FishData(FishList.BABY_SHARK,"baby_shark","Un petit requin espiègle, nageant joyeusement dans les eaux peu profondes, apportant un sourire à tous ceux qui le croisent.",Rarity.ABONDANTS),
    FishData(FishList.REQUIN_TIGRE,"requin_tigre","Un prédateur redoutable avec des rayures distinctives, capable de s’attaquer à une grande variété de proies, même les plus coriaces.",Rarity.INSAISISSABLES),
    #Poissons magiques
    FishData(FishList.POISSON_ARC_EN_CIEL,"poisson_arc_en_ciel","Un poisson légendaire aux écailles chatoyantes, capable de nager à travers les arcs-en-ciel et d’apporter la chance à ceux qui le trouvent.",Rarity.INSAISISSABLES),
    FishData(FishList.FISHOBUS,"fishobus","Un poisson magique en forme de bus, transportant les voyageurs à travers les océans vers des destinations mystérieuses et enchantées.",Rarity.INSAISISSABLES),
    FishData(FishList.RAIE_ECTOPLASME,"raie_ectoplasme","Une raie fantomatique, glissant silencieusement à travers les eaux sombres, laissant derrière elle une traînée d’éctoplasme luminescent.",Rarity.INSAISISSABLES),
    FishData(FishList.POISSON_RADIOACTIF,"poisson_radioactif","Un poisson irradié, émettant une lueur étrange et possédant des pouvoirs mystérieux, capable de survivre dans les environnements les plus hostiles.",Rarity.INSAISISSABLES),
]