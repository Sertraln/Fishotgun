from shared.parsedata.fishlist import FishList
from enum import EnumDict
from ursina import color,Color

class Rarity(EnumDict):
    ABONDANTS = (color.white, "Abondants", 100)
    DISCRETS = (color.gold, "Discrets", 300)
    INSAISISSABLES = (color.violet, "Insaississables", 1000)

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
    FishData(FishList.BAR,"bar_commun","Bar Commun","Un prédateur discret aux reflets d’argent, c'est aussi le préféré des alcoolos.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.SARDINE,"sardine","Sardine","Petite mais insaisissable, pour ne pas finir sérrée.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.BARRACUDA,"barracuda","Barracuda","Une torpille vivante aux dents acérées et au regard glacé.",Rarity.ABONDANTS, "COMMUN"),
    FishData(FishList.PIRANHA,"piranha","Piranha","Minuscule monstre des rivières, capable de transformer la panique en carnage.",Rarity.DISCRETS, "COMMUN"),
    FishData(FishList.POISSON_CLOWN,"poisson_clown","Poisson Clown","Le roi comme le bouffon des récifs colorés.",Rarity.DISCRETS, "COMMUN"),
    FishData(FishList.POISSON_LUNE,"poisson_lune","Poisson Lune","Un géant paisible qui n'orbite plus autour de la terre.",Rarity.INSAISISSABLES, "COMMUN"),

    #Crustacés et mollusques
    FishData(FishList.CREVETTE,"crevette","Crevette","Petite acrobate marine, toujours prête à bondir hors du danger.",Rarity.ABONDANTS, "CRUSTACE"),
    FishData(FishList.MOULE,"moule","Moule","Bien accrochée à son rocher, elle traverse les tempêtes sans bouger d’un pouce.",Rarity.ABONDANTS, "CRUSTACE"),
    FishData(FishList.CRABE,"crabe","Crabe","Un guerrier à pinces, toujours prêt à défendre son territoire avec férocité.",Rarity.DISCRETS, "CRUSTACE"),
    FishData(FishList.HOMARD,"homard","Homard","Un noble crustacé, arborant une armure rouge et des pinces redoutables.",Rarity.DISCRETS, "CRUSTACE"),
    FishData(FishList.ARAIGNEE_DE_MER,"araignee_de_mer","Araignée de mer","Un prédateur à huit pattes, se faufilant dans les recoins sombres pour attraper ses proies.",Rarity.INSAISISSABLES, "CRUSTACE"),
    FishData(FishList.CRACKEN,"cracken","Cracken","Un titan des abysses aux tentacules colossaux, terreur des mers… soumis à quelques problèmes d'addiction.",Rarity.INSAISISSABLES, "CRUSTACE"),

    #Requins
    FishData(FishList.BABY_SHARK,"baby_shark","Baby Shark","Un petit requin espiègle, ayant traumatisé toute une génération à lui tout seul...",Rarity.ABONDANTS, "REQUIN"),
    FishData(FishList.REQUIN_TIGRE,"requin_tigre","Requin Tigre","Un prédateur redoutable avec des rayures distinctives, capable de s’attaquer à une grande variété de proies, même les plus coriaces.",Rarity.ABONDANTS, "REQUIN"),
    FishData(FishList.REQUIN_SCIE,"requin_scie","Requin Scie","Un prédateur à la mâchoire en forme de scie, capable de trancher ses proies en un clin d’œil.",Rarity.ABONDANTS, "REQUIN"),
    FishData(FishList.REQUIN_BLANC,"requin_blanc","Requin Blanc","Le roi des océans, un prédateur redoutable au sourire terrifiant.",Rarity.DISCRETS, "REQUIN"),
    FishData(FishList.TRALALERO_TRALALA,"tralalero_tralala","Tralalero Tralala","Un terrible monstre à 3 pattes, il sème la terreur sur internet et porte des... sneakers?",Rarity.INSAISISSABLES, "REQUIN"),
    FishData(FishList.REQUIN_GOBELIN,"requin_gobelin","Requin Gobelin","Un prédateur des profondeurs, aussi connu comme le plus hideux des requins.",Rarity.INSAISISSABLES, "REQUIN"),
    
    #Poissons magiques
    FishData(FishList.POISSON_ARC_EN_CIEL,"poisson_arc_en_ciel","Poisson Arc-en-ciel","Un poisson légendaire capable de nager à travers les arcs-en-ciel, autrefois connu par tous.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.FISHOBUS,"fishobus","Fishobus","Un poisson magique en forme de bus, transportant les voyageurs à travers les océans vers des destinations mystérieuses.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.POISSON_JOEL,"poisson_joel","Poisson Joel","Un poisson marginal, très réaliste, et surtout ressemblant étrangement au porte-clés de Joël...",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.RAIE_ECTOPLASME,"raie_ectoplasme","Raie Éctoplasme","Une raie fantomatique, glissant silencieusement à travers les eaux sombres, laissant derrière elle une traînée d’éctoplasme luminescent.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.POISSON_RADIOACTIF,"poisson_radioactif","Poisson Radioactif","Un poisson irradié, émettant une lueur étrange, capable de survivre dans les environnements les plus hostiles.",Rarity.INSAISISSABLES, "MAGIQUE"),
    FishData(FishList.MAGIQUARPE,"magiquarpe","Magiquarpe","Décevant comme prise... Mais ce poisson cache bien des secrets.",Rarity.INSAISISSABLES, "MAGIQUE"),
]