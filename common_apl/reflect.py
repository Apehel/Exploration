#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes de reflexivité pour construire des objets à partir de classes définie par leur nom
sous forme de chaine de caractères.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 08.2019
"""
from common_apl.errors import *


class Factory(object):
    """
    Cette classe implémente une fabrique d'objets dont la classe est connue par son nom.
    Ce nom, incluant le nom du package est passé en paramètre du constructeur.
    """

    def __init__(self, classinfo):
        """
        Construction de la fabrique.

        :param classinfo: Tuple de trois éléments : (nom du package, nom du module, nom de la classe)
        """
        self._pname = classinfo[0]
        self._mname = classinfo[1]
        self._cname = classinfo[2]
        self._package = __import__("{0}.{1}".format(self._pname, self._mname))
        self._module = self._package.__dict__[self._mname]
        self._class = self._module.__dict__[self._cname]


    @staticmethod
    def class_exists(classinfo):
        """
        Teste si la classe dont le nom est passé en paramètre existe dans le mdocule indiqué.

        :param classinfo: Tuple de trois éléments : (nom du package, nom du module, nom de la classe)
        :return: Vrai si la classe est trouvée dans le module et le package passés en paramètre.
        :rtype: bool
        """
        try:
            __import__(classinfo[0]).__dict__[classinfo[1]].__dict__[classinfo[2]]
            return True
        except (ModuleNotFoundError, KeyError):
            return False

    def create(self, *args, **kwargs):
        """
        Instanciation d'un objet par la fabrique.
        L'objet est instancié dans la classe correspondant aux noms passés au constructeur de la fabrique.

        :param args: liste d'arguments.
        :param kwargs: Liste d'arguments key=value.
        :return: Instance de l'objet
        """
        inst = object.__new__(self._class)
        try:
            inst.__init__(*args, **kwargs)
            return inst
        except Exception:
            raise ConstructorError(inst, *args, **kwargs)

    @staticmethod
    def invoke_method(o, methodname, *args, **kwargs):
        """
        Invoque la méthode dont le nom est passé en paramètre sur l'objet o.

        :param o: Objet sur lequel est invqué la méthode.
        :param methodname: Nom de la méthode.
        :param args: Liste d'arguments.
        :param kwargs: Liste d'arguments key=value.
        :return: Le résultat retourné par la méthode invoquée.
        """
        try:
            return type(o).__dict__["create"].__call__(o)
        except Exception:
            raise MethodError(o, methodname, *args, **kwargs)


#
#
#######################################################################################################################
class SingletonFactory(object):
    """
    Cette classe implémente, une fabrique d'objet.
    Les fabriques sont des singletons. C'est à dire que pour une classe donnée, il n'y a qu'une et une seule fabrique
    instanciée.
    Cette classe est particulièrement utile lorsque un fabrique est souvent utilisée pour une même classe d'objets.
    """
    _class_map = {}  # Dictionnaire des classes déjà instanciées.

    @staticmethod
    def get(classinfo):
        """
        Instanciateur de la fabrique.
        Si la fabrique existe déjà dans le dictionnaire, pour les noms de parckage, module et classe passés en
        paramètres, elle est renvoyée en résultat de la méthode.
        Sinon, une nouvelle fabrique est instanciée.

        :param classinfo: Tuple de trois éléments : (nom du package, nom du module, nom de la classe)
        :return: Instance de la fabrique correspondant à la classe.
        :rtype: Factory
        """
        key = "{0}.{1}.{2}".format(classinfo[0], classinfo[1], classinfo[2])
        if key not in SingletonFactory._class_map:
            fact = Factory(classinfo)
            SingletonFactory._class_map[key] = fact
        return SingletonFactory._class_map[key]