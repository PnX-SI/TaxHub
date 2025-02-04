# coding: utf8
"""
Fonctions utilitaires
"""
import collections.abc


def dict_merge(dct, merge_dct):
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.items():
        if (
            k in dct
            and isinstance(dct[k], dict)
            and isinstance(merge_dct[k], collections.abc.Mapping)
        ):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


def build_query_order(model, query, parameters):
    # Ordonnancement
    # L'ordonnancement se base actuellement sur une seule colonne
    #   et prend la forme suivante : nom_colonne[:ASC|DESC]
    if parameters.get("orderby", "").replace(" ", ""):
        order_by = parameters.get("orderby")
        col, *sort = order_by.split(":")
        if getattr(model, col, None):
            ordel_col = getattr(model, col)
            if (sort[0:1] or ["ASC"])[0].lower() == "desc":
                ordel_col = ordel_col.desc()
            return query.order_by(ordel_col)
    return query
