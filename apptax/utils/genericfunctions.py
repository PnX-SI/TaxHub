"""
    Fichier contenant des fonctions utilisées
    par l'ensemble de l'application
"""


def calculate_offset_page(limit, offset, page):
    """
    fonction qui calcul les paramètres
        offset et page
    Si un offset est défini
        il prend le pas sur le paramètre page
    Le paramètre page est seulement indicatif, il commence à 1 et ne peut être < 1
    Le offset commence à 0 et ne peut pas être négatif
    """
    if offset:
        if offset < 0:
            offset = 0
        page = int(offset / limit)
        return (limit, offset, page)
    else:
        page = 1 if page < 1 else page
        offset = (page - 1) * limit
        return (limit, offset, page)
