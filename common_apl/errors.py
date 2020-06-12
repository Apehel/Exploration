#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes d'erreurs pour la bibliothèque WinApl.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - O8.2019
"""


class Error(Exception):
    """
    Cette classe est la classe de base pour toutes les erreurs générée par le package winapl.
    """

    def __init__(self, message, *args):
        """
        Constructeur de l'erreur.

        :param message: Message à afficher.
        :param args: Liste des arguments à insérer dans le message.
        """
        super().__init__(message.format(*args))

    def _args2str(self, *args, **kwargs):
        """
        Formate les arguments passés en paramètre dans une chaine de caractères.

        :param args: Liste d'arguments.
        :param kwargs: Liste d'argument key=value.
        :return: Chaine de caractères.
        """
        args_list = ""
        for i in range(len(args)):
            if i != 0:
                args_list += ","
            args_list += type(args[i]).__name__
        keys = list(kwargs)
        for i in range(len(keys)):
            if len(args_list) > 0:
                args_list += ","
            args_list += keys[i] + "=" + type(kwargs[keys[i]]).__name__
        return args_list


#
#
######################################################################################################################
class ConstructorError(Error):
    """
    Erreur généré à la construction d'un objet lorsque les paramètres de construction sont érronés.
    """
    MESSAGE = "No constructor for {0}({1})."

    def __init__(self, built_objet, *args, **kwargs):
        """
        Constructeur de l'erreur.

        :param built_objet: Classe du contructeur.
        :param args: Paramètres passés au constructeur.
        :param kwargs: Paramètres key=value passés au constructeur.
        """
        super().__init__(ConstructorError.MESSAGE, type(built_objet).__name__, self._args2str(*args, **kwargs))


#
#
######################################################################################################################
class OperatorError(Error):
    """
    Erreur générée lorsqu'un opérateur surchargé en utilisé avec des opérandes inapropriées.
    """
    MESSAGE = "Unsupported operand type(s) for {0}: {1} and {2}"

    def __init__(self, operator_name, left_operand, right_operande):
        """
        Constructeur de l'erreur.

        :param operator_name: Nom de l'opérateur.
        :param left_operand: Operande à gauche.
        :param right_operande: Opérande à droite.
        """
        super().__init__(OperatorError.MESSAGE, operator_name,
                         type(left_operand).__name__, type(right_operande).__name__)


#
#
######################################################################################################################
class AttributeError(Error):
    """
    Erreur générée lorsqu'un attribut n'existe pas pour une classe dérivée alors qu'il existait pour la classe parente.
    """
    MESSAGE = "{0} object has no attribute {1}."

    def __init__(self, instance, attribute_name):
        """
        Constructeur de l'erreur.

        :param instance: Objet sur lequel est invoqué l'attribut.
        :param attribute_name: Nom de l'attribut.
        """
        super().__init__(AttributeError.MESSAGE, type(instance).__name__, attribute_name)


#
#
######################################################################################################################
class ClassMethodError(Error):
    """
    Erreur générée lorsque les paramètres passés à une méthode ne sont pas appropriés.
    """
    MESSAGE = "No method {1}({2}) for the {0} object."

    def __init__(self, object_class, method_name, *args, **kwargs):
        """
        Constructeur de l'erreur.

        :param object_class: Classe sur laquel est invoquée la méthode statique.
        :param method_name: Nom de la methode.
        :param args: Paramètres de la méthode.
        :param kwargs: Paramètres key=value de la méthode.
        """
        super().__init__(ClassMethodError.MESSAGE, object_class.__name__, method_name, self._args2str(*args, **kwargs))


#
#
######################################################################################################################
class MethodError(ClassMethodError):
    """
    Erreur générée lorsque les paramètres passés à une méthode ne sont pas appropriés.
    """
    def __init__(self, instance, method_name, *args, **kwargs):
        """
        Constructeur de l'erreur.

        :param instance: Objet sur lequel est invoqué la méthode.
        :param method_name: Nom de la methode.
        :param args: Paramètres de la méthode.
        :param kwargs: Paramètres key=value de la méthode.
        """
        super().__init__(type(instance), method_name, *args, **kwargs)


#
#
#
######################################################################################################################
class TypeError(Error):
    """
    Erreur générée lorsqu'une donnée n'est pas de la classe attendue.
    """
    MESSAGE = "{0} is not a {1}."

    def __init__(self, arg, object_class):
        """

        :param arg: Valeur de la donnée
        :param object_class: Classe de l'objet attendue.
        """
        super().__init__(TypeError.MESSAGE, repr(arg), object_class)
