#!/usr/bin/env python
# _*_ coding: utf-8 _*_
"""
Ce module contient les outils utilisés par les aplications pour exploiter des document XML.

Auteur : André-Pierre LIMOUZIN
Version : 2 - 05.2020
"""
from abc import abstractmethod
import xml.dom.minidom as XMLDOM
from common_apl.errors import ConstructorError, ClassMethodError


#
#
##############################################################################
class IXmlObject(object):
    """
    Cette classe définit une interface commune à tous les objets qui doivent être lu ou écrit dans un document XML avec
    XML DOM.

    Associé à chaque objet métier à sérializer dans un document XML, une classe wrapper, dérivée de cette classe,
    doit être crée en surchargeant les deux méthodes read et write pour définir la façon (le schéma) dont l'objet
    métier doit être lu ou écrit dans le document XML.

    Remarque : En python, cette interface semble faire double emploi avec la classe XmlObjectAdapter, du fait que
    l'héritage multiple est possible.
    """

    @abstractmethod
    def read(self, xml_element):
        """
        Cette méthode permet de lire l'élément XML passé en paramètre pour créer un objet métier.
        La méthode doit instancier un nouvel objet construit à partir des données contenuues dans l'élément XML.

        :param xml_element: Element XML DOM lu dans le document XML.
        :return: Objet métier instancié par la méthode.
        """
        pass

    @abstractmethod
    def write(self, xml_document, o):
        """
        Cette méthode permet d'écrire l'objet métier o passé en paramètre dans le document XML xml_document passé
        également en paramètre.
        Le document XML passé en paramètre est utilisé pour instancier les éléments XML qui doivent y être écrits.
        La méthode instancie un nouvel élément XML pour y rassembler les données de l'objet métier selon un schéma
        approprié. Cette élément XML est retourné comme résultat de la méthode.

        :param xml_document: Document XML dans lequel le nouvel élément XML est créé.
        :param o: Objet métier à écrire dans le document XML
        :return: Elément XML relatif à l'objet métier à écrire.
        """
        pass


#
#
##############################################################################
class XmlObjectAdapter(IXmlObject):
    """
    Cette classe abstraite définit le polymorphisme de toutes les classes
    adaptateur pour l'écriture et la lecture des objets métier de
    l'application.
    Elle implémente l'interface IXmlObject pour obliger les adapteurs à
    implémenter  une méthode read pour la lecture et une méthode write pour
    l'écriture.
    """
    def __init__(self):
        """
        Constructeur par défaut de l'adaptateur.
        """
        pass  # Il n'y a rien à faire pour le moment.

    def read(self, element):
        """
        Cette méthode permet de lire l'élément XML passé en paramètre pour
        créer un objet métier.
        La méthode doit instancier un nouvel objet construit à partir des
        données contenuues dans l'élément XML.

        :param element: Element XML DOM lu dans le document XML.
        :return: Objet métier instancié par la méthode.
        """
        return None

    def write(self, xml_document, o):
        """
        Cette méthode permet d'écrire l'objet métier o passé en paramètre dans le document XML xml_document passé
        également en paramètre.
        Le document XML passé en paramètre est utilisé pour instancier les éléments XML qui doivent y être écrits.
        La méthode instancie un nouvel élément XML pour y rassembler les données de l'objet métier selon un schéma
        approprié. Cette élément XML est retourné comme résultat de la méthode.

        :param xml_document: Document XML dans lequel le nouvel élément XML est créé.
        :param o: Objet métier à écrire dans le document XML
        :return: Elément XML relatif à l'objet métier à écrire.
        """
        return None


#
#
##############################################################################
class XmlDocumentLoader(object):
    """
    Cette classe permet de charger un document XML.
    """

    __DEFAULT_ROOT_NAME = "root"

    def __init__(self, xml_document_name=None, root_name=__DEFAULT_ROOT_NAME):
        """
        Constructeur du chargeur de document XML.


        :param xml_document_name: Nom du fichier du document XML.
        :param root_name: Nom de l'élément racine du document XML (root par défaut).
        """
        if xml_document_name == None:
            implementation = XMLDOM.getDOMImplementation()
            self.__document = implementation.createDocument(None, XmlDocumentLoader.__DEFAULT_ROOT_NAME, None)
            self.__doc_name = None
        else:
            self.__document = XMLDOM.parse(xml_document_name)
            self.__doc_name = xml_document_name
        self.__root = self.__document.documentElement

    @property
    def xmlDocument(self):
        """
        :return: Document XML du loader
        """
        return self.__document

    @property
    def rootElement(self):
        """
        :return: Element racine du document. None si le document n'a pas pu être chargé.
        """
        return self.__root

    def toXml(self):
        """
        :return: Chaine de caractère contenant le document en XML, balises comprises.
        """
        return self.__root.toprettyxml()

    def save(self, xml_document_name=None):
        """
        Enregistrement du document.

        Par défaut le document est enregistré dans le fichier dont le nom a été passé au constructeur.
        """
        if xml_document_name == None :
            xml_document_name = self.__doc_name
        newFile = open(xml_document_name, "w")
        print(self.toXml(), file=newFile)



#
#
##############################################################################
class XmlParser(object):
    """
    Cette classe définit un parser XML pour explorer les noeuuds XML enfants. Seuls les noeuds de type DOMElement
    sont pris en compte sur un seul niveau.
    A chaque élément ou attribut trouvé un handler est invoqué.

    En outre, cette classe expose des méthodes statiques pour manipuler des attributs typés.
    """
    def __init__(self, element, attribute_found_handler, element_found_handler):
        """
        A la construction, une exploration de tous les noeuds enfants est effectuée.
        A la construction du parser, on commence par effectuer une énumération de tous les attributs de l'élément XML
        exploré. Pour chaque attribut trouvé, la methode abstraite onAttributeFound est invoquée.
        Puis, on procède à une énumération du contenu de l'élément au premier niveau.
        Lorsqu'un noeud  de type DOMElement est trouvé, la méthode abstraite onElementFound est invoquée.
        La classe doit être dérivée pour surcharger les deux méthodes onAttributeFound et onElementFound pour effectuer
        le traitenement adéquat.

        Utilisation :
        XmlParser(parent,
                  lambda attribute: on_attribute_found(attribute),
                  lambda element: on_element_found(element)
        Les deux fonctions on_attribute_found et on_element_found doivent être définies par ailleurs pour effectuer
        le traitement approprié.

        :param element: Elément XML à explorer.
        :param attribute_found_handler: Handler exécuté lorsau'un attribut est trouvé.
        :param element_found_handler: Handler exécuté lorsqu'un élément fils est trouvé.
        """
        if not(element.__class__ is XMLDOM.Element
               and (callable(attribute_found_handler) or attribute_found_handler is None)
               and (callable(element_found_handler) or element_found_handler is None)):
            raise ConstructorError(self, element, attribute_found_handler, element_found_handler)
        if attribute_found_handler is not None:
            for i in range(element.attributes.length):
                attribute_found_handler(element.attributes.item(i))
        if element_found_handler is not None:
            for i in range(element.childNodes.length):
                if element.childNodes.item(i).nodeType == XMLDOM.Node.ELEMENT_NODE:
                    element_found_handler(element.childNodes.item(i))

    @staticmethod
    def get_single_element_from(element, element_name):
        """
        Recherche l'élément singleton contenu dans l'élément passé en paramètre  dont le nom est element_name.
        Si aucun élément n'est trouvé , la méthode retourne None.
        Si plusieurs élément sont trouvés, c'est le premier qui est retourné.

        :param element: Eléménet XML dans lequel il faut effectuer la recherche.
        :param element_name: Nom de l'élement recherché.
        :return: Elément trouvé ou None
        """
        if not (element.__class__ is XMLDOM.Element and element_name.__class__ is str):
            raise ClassMethodError(XmlParser, "get_single_element_from", element, element_name)
        for i in range(element.childNodes.length):
            node = element.childNodes.item(i)
            if node.nodeType == XMLDOM.Node.ELEMENT_NODE \
                    and node.nodeName == element_name:
                return node
        return None

    @staticmethod
    def get_text_content(element):
        """
        Recherche le texte contenu dans l'élément passé en paramètre.
        Le texte retourné est la concaténation des nodes de type Text trouvé.
        Si aucun node de type Text n'est trouvé, la valeur retournée est une chaine vide.

        :param element: Element XML contenant le texte recherché.
        :return: Chaine de caractères contenant le texte recherché.
        """
        if not (element.__class__ is XMLDOM.Element):
            raise ClassMethodError(XmlParser, "get_text_content", element)
        content = ""
        for i in range(element.childNodes.length):
            node = element.childNodes.item(i)
            if node.nodeType == XMLDOM.Node.TEXT_NODE:
                content = content + node.data
        return content

    @staticmethod
    def get_bool_attribute(element, attribute_name, default_value):
        """
        Récupération de la valeur d'un attribut XML au format booléen.
        Si l'attribut n'existe pas, c'est la valeur par défaut qui est retournée.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut.
        :param default_value: Valeur par défaut de l'attribut.
        :return: Valeur booléenne de l'attribut.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and default_value.__class__ is bool):
            raise ClassMethodError(XmlParser, "get_bool_attribute", element, attribute_name, default_value)
        if element.hasAttribute(attribute_name):
            value = element.getAttribute(attribute_name)
            return bool(value)
        else:
            return default_value

    @staticmethod
    def set_bool_attribute(element, attribute_name, value):
        """
        Modification d'un attribut XML booléen.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut
        :param value: Valeur de l'attribut.
        :return: Rien.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and value.__class__ is bool):
            raise ClassMethodError(XmlParser, "set_bool_attribute", element, attribute_name, value)
        element.setAttribute(attribute_name, str(value))
        return

    @staticmethod
    def get_int_attribute(element, attribute_name, default_value):
        """
        Récupération de la valeur d'un attribut XML au format Integer.
        Si l'attribut n'existe pas, c'est la valeur par défaut qui est retournée.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut.
        :param default_value: Valeur par défaut de l'attribut.
        :return: Valeur entière de l'attribut.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and default_value.__class__ is int):
            raise ClassMethodError(XmlParser, "get_int_attribute", element, attribute_name, default_value)
        if element.hasAttribute(attribute_name):
            value = element.getAttribute(attribute_name)
            return int(value)
        else:
            return default_value

    @staticmethod
    def set_int_attribute(element, attribute_name, value):
        """
        Modification d'un attribut XML entier.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut
        :param value: Valeur de l'attribut.
        :return: Rien.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and value.__class__ is int):
            raise ClassMethodError(XmlParser, "set_int_attribute", element, attribute_name, value)
        element.setAttribute(attribute_name, str(value))
        return

    @staticmethod
    def get_float_attribute(element, attribute_name, default_value):
        """
        Récupération de la valeur d'un attribut XML au format Float.
        Si l'attribut n'existe pas, c'est la valeur par défaut qui est retournée.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut.
        :param default_value: Valeur par défaut de l'attribut.
        :return: Valeur virgule flottante de l'attribut.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and default_value.__class__ is float):
            raise ClassMethodError(XmlParser, "get_float_attribute", element, attribute_name, default_value)
        if element.hasAttribute(attribute_name):
            value = element.getAttribute(attribute_name)
            return float(value)
        else:
            return default_value

    @staticmethod
    def set_float_attribute(element, attribute_name, value):
        """
        Modification d'un attribut XML virgule flottante.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut
        :param value: Valeur de l'attribut.
        :return: Rien.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and value.__class__ is float):
            raise ClassMethodError(XmlParser, "set_float_attribute", element, attribute_name, value)
        element.setAttribute(attribute_name, str(value))
        return

    @staticmethod
    def get_tuple_attribute(element, attribute_name, default_value, sep=","):
        """
        Récupération de la valeur d'un attribut XML au format Tuple.
        Si l'attribut n'existe pas, c'est la valeur par défaut qui est retournée.
        Chaque élément du tuple est séparé par le séparateur sep (virgule par défaut).
        Le séparateur ne peut être ni une apostrophe ni un guillemet. Par ailleurs, l'attribut ne peut contenir
        lui-même ni apostrophe ni guillement.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut.
        :param default_value: Valeur par défaut de l'attribut.
        :param sep : Caractère utilisé comme séparateur.
        :return: Valeur virgule flottante de l'attribut.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and default_value.__class__ is tuple and sep.__class__ is str):
            raise ClassMethodError(XmlParser, "get_tuple_attribute", element, attribute_name, default_value, sep)
        if element.hasAttribute(attribute_name):
            value = element.getAttribute(attribute_name)
            return tuple(value.split(sep))
        else:
            return default_value

    @staticmethod
    def set_tuple_attribute(element, attribute_name, value, sep=","):
        """
        Modification d'un attribut XML virgule flottante.

        :param element: Elément parent de l'attribut.
        :param attribute_name: Nom de l'attribut
        :param value: Valeur de l'attribut.
        :param sep : Caractère utilisé comme séparateur.
        :return: Rien.
        """
        if not (element.__class__ is XMLDOM.Element and attribute_name.__class__ is str
                and value.__class__ is tuple and sep.__class__ is str):
            raise ClassMethodError(XmlParser, "set_tuple_attribute", element, attribute_name, value, sep)
        text = ""
        for i in range(len(value)):
            if i > 0:
                text = text + sep
            text = text + str(value[i])
        element.setAttribute(attribute_name, text)
        return


if __name__ == "__main__":
    pass
