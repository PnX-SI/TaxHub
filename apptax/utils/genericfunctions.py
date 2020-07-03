'''
    Fichier contenant des fonctions utilisées
    par l'ensemble de l'application
'''


def calculate_offset_page(limit, offset, page):
    """
        fonction qui calcul les paramètres
            offset et page
        Si un offset est défini
            il prend le pas sur le paramètre page
    """
    if offset is not None:
        page = int(offset / limit)
        return (limit, offset, page)
    else:
        offset = (page-1) * limit
        return (limit, offset, page)
