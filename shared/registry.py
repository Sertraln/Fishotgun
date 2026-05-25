from shared.parsedata.fishlist import FishList
from enum import EnumDict
from ursina import color,Color

class Rarity(EnumDict):
    ABONDANTS = (color.gray, "Abondants",100)
    DISCRETS = (color.orange, "Discrets",300)
    INSAISISSABLES = (color.violet, "Insaississables",1000)

    def __init__(self, color:'Color', name:str, sell_price:int):
        self.color = color
        self.name = name
        self.sell_price = sell_price


class FishData:
    def __init__(self, fish: FishList, id: str, name: str, description: str, rarity: Rarity, category: str):
        self.fishid = fish
        self.id = id
        self.name = name
        self.description = description
        self.rarity = rarity
        self.category = category

# name, description
fish_list : list[FishData] = [
    #Poissons communs
    FishData(FishList.BAR,"bar_commun","Bar Commun","Un prédateur discret aux reflets d’argent, rapide comme l’éclair sous les vagues.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.SARDINE,"sardine","Sardine","Petite mais insaisissable, elle nage toujours là où on ne l’attend pas.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.BARRACUDA,"barracuda","Barracuda","Une torpille vivante aux dents acérées et au regard glacé.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.PIRANHA,"piranha","Piranha","Minuscule monstre des rivières, capable de transformer la panique en carnage.",Rarity.DISCRETS, "COMMUN"),
    FishData(FishList.POISSON_CLOWN,"poisson_clown","Poisson Clown","Le roi coloré des récifs, aussi drole qu’imprévisible.",Rarity.DISCRETS, "COMMUN"),
    FishData(FishList.POISSON_LUNE,"poisson_lune","Poisson Lune","Un géant paisible qui dérive dans l’océan comme une planète perdue.",Rarity.INSAISISSABLES, "COMMUN"),
    #Crustacés et mollusques
    FishData(FishList.CREVETTE,"crevette","Crevette","Petite acrobate marine, toujours prête à bondir hors du danger.",Rarity.ABONDANTS, "CRUSTACE"),
    FishData(FishList.MOULE,"moule","Moule","Bien accrochée à son rocher, elle traverse les tempêtes sans bouger d’un pouce.",Rarity.ABONDANTS, "CRUSTACE"),
    FishData(FishList.BULOT,"bulot","Bulot","Un aventurier à coquille, explorant les fonds marins avec curiosité.",Rarity.DISCRETS, "CRUSTACE"),
    FishData(FishList.CRABE,"crabe","Crabe","Un guerrier à pinces, toujours prêt à défendre son territoire avec férocité.",Rarity.DISCRETS, "CRUSTACE"),
    FishData(FishList.ARAIGNEE_DE_MER,"araignee_de_mer","Araignée de mer","Un prédateur à huit pattes, se faufilant dans les recoins sombres pour attraper ses proies.",Rarity.INSAISISSABLES, "CRUSTACE"),
    FishData(FishList.HOMARD,"homard","Homard","Un noble crustacé, arborant une armure rouge et des pinces redoutables.",Rarity.INSAISISSABLES, "CRUSTACE"),
    FishData(FishList.CALAMAR,"calamar","Calamar","Un maître de la furtivité, capable de disparaître dans un nuage d’encre pour échapper à ses ennemis.",Rarity.INSAISISSABLES, "CRUSTACE"),
    #Requins
    FishData(FishList.REQUIN_BLANC,"requin_blanc","Requin Blanc","Le roi des océans, un prédateur redoutable au sourire terrifiant.",Rarity.DISCRETS, "REQUIN"),
    FishData(FishList.REQUIN_MARTEAU,"requin_marteau","Requin Marteau","Un chasseur à la tête en forme de T, utilisant son crâne pour détecter les moindres vibrations dans l’eau.",Rarity.DISCRETS, "REQUIN"),
    FishData(FishList.REQUIN_SCIE,"requin_scie","Requin Scie","Un prédateur à la mâchoire en forme de scie, capable de trancher ses proies en un clin d’œil.",Rarity.INSAISISSABLES, "REQUIN"),
    FishData(FishList.REQUIN_TOURNEVIS,"requin_tournevis","Requin Tournevis","Un requin rare avec une spirale sur la tête, se déplaçant dans l’eau avec une grâce hypnotique.",Rarity.INSAISISSABLES, "REQUIN"),
    FishData(FishList.REQUIN_GOBELIN,"requin_gobelin","Requin Gobelin","Un prédateur des profondeurs, avec un museau allongé et des dents proéminentes, se faufilant dans les abysses à la recherche de proies inattendues.",Rarity.INSAISISSABLES, "REQUIN"),
    FishData(FishList.BABY_SHARK,"baby_shark","Baby Shark","Un petit requin espiègle, nageant joyeusement dans les eaux peu profondes, apportant un sourire à tous ceux qui le croisent.",Rarity.ABONDANTS, "REQUIN"),
    FishData(FishList.REQUIN_TIGRE,"requin_tigre","Requin Tigre","Un prédateur redoutable avec des rayures distinctives, capable de s’attaquer à une grande variété de proies, même les plus coriaces.",Rarity.INSAISISSABLES, "REQUIN"),
    #Poissons magiques
    FishData(FishList.POISSON_ARC_EN_CIEL,"poisson_arc_en_ciel","Poisson Arc-en-ciel","Un poisson légendaire aux écailles chatoyantes, capable de nager à travers les arcs-en-ciel et d’apporter la chance à ceux qui le trouvent.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.FISHOBUS,"fishobus","Fishobus","Un poisson magique en forme de bus, transportant les voyageurs à travers les océans vers des destinations mystérieuses et enchantées.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.RAIE_ECTOPLASME,"raie_ectoplasme","Raie Éctoplasme","Une raie fantomatique, glissant silencieusement à travers les eaux sombres, laissant derrière elle une traînée d’éctoplasme luminescent.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.POISSON_RADIOACTIF,"poisson_radioactif","Poisson Radioactif","Un poisson irradié, émettant une lueur étrange et possédant des pouvoirs mystérieux, capable de survivre dans les environnements les plus hostiles.",Rarity.INSAISISSABLES, "MAGIQUE"),
]