#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes nécessaire pour créer le fichier XML destinnés
à stocker, dans un fichier XML, les données collectées par les capteurs d'un
robot.

Auteur : André Pierre LIMOUZIN
Version : 1.1 - 05.2020
"""
import sys
import xml.dom.minidom as XMLDOM
from common_apl.xmlio import XmlDocumentLoader, XmlObjectAdapter, XmlParser
from survey_model import SurveyMap, SurveyNode, SurveyPoint, Wall, Angle


#
#
##############################################################################
class SurveyPointAdapter(XmlObjectAdapter):
    """
    Cette classe est un adapteur pour permettre la lecture et l'écriture
    d'un SurveyPoint.
    """
    TAG_NAME = "point"
    ATTR_X = "x"
    ATTR_Y = "y"
    ATTR_ANGLE = "angle"
    ATTR_DISTANCE = "distance"
    ATTR_VALID = "valid"

    def __init__(self, surveyNode):
        """
        Constructeur de l'adaptateur.

        :param surveyNode: SurveyNode propriétaire de SurveyPoint.
        """
        super().__init__()
        self.__node = surveyNode

    def read(self, element):
        """
        Lecture du SurveyPoint.
        :param element: Eléménet XML du SurveyPoint.
        """
        x = XmlParser.get_float_attribute(element, SurveyPointAdapter.ATTR_X, 0.0)
        y = XmlParser.get_float_attribute(element, SurveyPointAdapter.ATTR_Y, 0.0)
        angle = XmlParser.get_float_attribute(element, SurveyPointAdapter.ATTR_ANGLE, 0.0)
        dist = XmlParser.get_float_attribute(element, SurveyPointAdapter.ATTR_DISTANCE, 0.0)
        surveyPoint = SurveyPoint(self.__node, angle, dist, x, y)
        surveyPoint.isValid = XmlParser.get_bool_attribute(element, SurveyPointAdapter.ATTR_VALID, False)
        return surveyPoint


    def write(self, xmlDocument, surveyPoint):
        """
        Ecriture d'un SurveyPoint.
        :param xmlDocument: Document XML dans lequel doit être écrit le SurveyPoint.
        :param surveyPoint: Objet SurveyPoint à écrire.
        :return: Element XML créé pour l'objet SurveyPoint.
        """
        elPoint = xmlDocument.createElement(SurveyPointAdapter.TAG_NAME)
        XmlParser.set_float_attribute(elPoint, SurveyPointAdapter.ATTR_X, float(surveyPoint.X))
        XmlParser.set_float_attribute(elPoint, SurveyPointAdapter.ATTR_Y, float(surveyPoint.Y))
        XmlParser.set_float_attribute(elPoint, SurveyPointAdapter.ATTR_ANGLE, float(surveyPoint.rawAngle))
        XmlParser.set_float_attribute(elPoint, SurveyPointAdapter.ATTR_DISTANCE, float(surveyPoint.rawDistance))
        XmlParser.set_bool_attribute(elPoint, SurveyPointAdapter.ATTR_VALID, surveyPoint.isValid)
        return elPoint

#
#
##############################################################################
class WallAdapter(XmlObjectAdapter):
    """
    Cette classe est adpateur pour permettre la lecture et l'écriture
    d'un objet Wall.
    """
    TAG_NAME = "wall"
    ATTR_A = "A"
    ATTR_B = "B"
    ATTR_C = "C"
    ATTR_Q = "Q"
    ATTR_ISLEFTWALL = "isLeftWall"
    ATTR_ISFRONTWALL = "isFrontWall"
    ATTR_ISRIGHTWALL = "isRightWall"
    PT1_TAG_NAME = "Pt1"
    PT2_TAG_NAME = "Pt2"

    def __init__(self, surveyNode):
        """
        Constructeur de l'adapteur.
        :param surveyMap: SurveyMap propriétaire de SurveyNode.
        """
        super().__init__()
        self.__node = surveyNode

    def read(self, element):
        """
        Lecture du SurveyNode.

        Cette méthode ne edoit pas être utilisée. Les objets Wall ne doivent
        pas être à partir du fichier XML, mais construits par calcul par
        l'invocation de la méthode computeWalls() de la classe SurveyNode.
        """
        return None

    def write(self, xmlDocument, wall):
        """
        Ecriture d'un Wall.
        :param xmlDocument: Document XML dans lequel doit être écrit le SurveyNode.
        :param wall: Objet Wall à écrire.
        :return: Element XML créé pour l'objet Wall.
        """
        elWall = xmlDocument.createElement(WallAdapter.TAG_NAME)
        XmlParser.set_float_attribute(elWall, WallAdapter.ATTR_A, float(wall.A))
        XmlParser.set_float_attribute(elWall, WallAdapter.ATTR_B, float(wall.B))
        XmlParser.set_float_attribute(elWall, WallAdapter.ATTR_C, float(wall.C))
        XmlParser.set_float_attribute(elWall, WallAdapter.ATTR_Q, float(wall.Q))
        XmlParser.set_bool_attribute(elWall, WallAdapter.ATTR_ISLEFTWALL, wall.isLeftWall)
        XmlParser.set_bool_attribute(elWall, WallAdapter.ATTR_ISFRONTWALL, wall.isFrontWall)
        XmlParser.set_bool_attribute(elWall, WallAdapter.ATTR_ISRIGHTWALL, wall.isRightWall)
        for iPoint in range(len(wall)):
            pointAdapter = SurveyPointAdapter(wall)
            elPoint =  pointAdapter.write(xmlDocument, wall[iPoint])
            elWall.appendChild(elPoint)
        elPt1 = xmlDocument.createElement(WallAdapter.PT1_TAG_NAME)
        XmlParser.set_float_attribute(elPt1, SurveyPointAdapter.ATTR_X, float(wall.Pt1.X))
        XmlParser.set_float_attribute(elPt1, SurveyPointAdapter.ATTR_Y, float(wall.Pt1.Y))
        elWall.appendChild(elPt1)
        elPt2 = xmlDocument.createElement(WallAdapter.PT2_TAG_NAME)
        XmlParser.set_float_attribute(elPt2, SurveyPointAdapter.ATTR_X, float(wall.Pt2.X))
        XmlParser.set_float_attribute(elPt2, SurveyPointAdapter.ATTR_Y, float(wall.Pt2.Y))
        elWall.appendChild(elPt2)
        return elWall


#
#
##############################################################################
class SurveyNodeAdapter(XmlObjectAdapter):
    """
    Cette classe est un adapteur pour permettre la lecture et l'écriture
    d'un SurveyNode.
    """
    TAG_NAME = "node"
    ATTR_X = "x"
    ATTR_Y = "y"
    ATTR_ORIENTATION = "orientation"
    ATTR_OFFSET = "offset"

    def __init__(self, surveyMap):
        """
        Constructeur de l'adaptateur.

        :param surveyMap: SurveyMap propriétaire de SurveyNode.
        """
        super().__init__()
        self.__map = surveyMap


    def read(self, element):
        """
        Lecture du SurveyNode.
        :param element: Eléménet XML du SurveyNode.
        """
        x = XmlParser.get_float_attribute(element, SurveyNodeAdapter.ATTR_X, 0.0)
        y = XmlParser.get_float_attribute(element, SurveyNodeAdapter.ATTR_Y, 0.0)
        orientation = Angle(degrees=XmlParser.get_float_attribute(element, SurveyNodeAdapter.ATTR_ORIENTATION, 0.0))
        offset = XmlParser.get_tuple_attribute(element, SurveyNodeAdapter.ATTR_OFFSET, (0,0))
        surveyNode = SurveyNode(self.__map, x, y, orientation, offset)
        elPoints = element.getElementsByTagName(SurveyPointAdapter.TAG_NAME)
        for iPoint in range(elPoints.length):
            pointAdapter = SurveyPointAdapter(surveyNode)
            surveyNode.addPoint(pointAdapter.read(elPoints[iPoint]))
        surveyNode.computeWallData()
        return surveyNode

    def write(self, xmlDocument, surveyNode):
        """
        Ecriture d'un SurveyNode.
        :param xmlDocument: Document XML dans lequel doit être écrit le SurveyNode.
        :param surveyNode: Objet SurveyNode à écrire.
        :return: Element XML créé pour l'objet SurveyNode.
        """
        elNode = xmlDocument.createElement(SurveyNodeAdapter.TAG_NAME)
        XmlParser.set_float_attribute(elNode, SurveyNodeAdapter.ATTR_X, float(surveyNode.X))
        XmlParser.set_float_attribute(elNode, SurveyNodeAdapter.ATTR_Y, float(surveyNode.Y))
        XmlParser.set_float_attribute(elNode, SurveyNodeAdapter.ATTR_ORIENTATION, float(surveyNode.orientation.degrees))
        XmlParser.set_tuple_attribute(elNode, SurveyNodeAdapter.ATTR_OFFSET, surveyNode.offset)
        for iPoint in range(len(surveyNode)):
            pointAdapter = SurveyPointAdapter(surveyNode)
            elPoint =  pointAdapter.write(xmlDocument, surveyNode[iPoint])
            elNode.appendChild(elPoint)
        for iWall in range(len(surveyNode.walls)):
            wallAdapter = WallAdapter(surveyNode)
            elWall = wallAdapter.write(xmlDocument, surveyNode.walls[iWall])
            elNode.appendChild(elWall)
        return elNode


#
#
##############################################################################
class SurveyMapAdapter(XmlObjectAdapter):
    """
    Cette classe est un adaptateur pour permettre la lecture et
    l'écriture d'une SurveyMap.
    """
    TAG_NAME = "map"
    ATTR_MINX = "minX"
    ATTR_MAXX = "maxX"
    ATTR_MINY = "minY"
    ATTR_MAXY = "maxY"

    def __init__(self):
        """
        Constructeur de l'adaptateur.
        """
        super().__init__()

    def read(self, element):
        """
        Lecture d'une SurveyMap.
        :param element: Elément XML du SurveyMap.
        :return: Objet SurveyMap lu.
        """
        surveyMap = SurveyMap()
        elNodes = element.getElementsByTagName(SurveyNodeAdapter.TAG_NAME)
        for iNode in range(elNodes.length):
            nodeAdapter = SurveyNodeAdapter(surveyMap)
            surveyMap.addNode(nodeAdapter.read(elNodes[iNode]))
        return surveyMap

    def write(self, xmlDocument, surveyMap):
        """
        Ecriture d'une SurveyMap.

        :param xmlDocument: Document XML dans lequel doit être écrit le SurveyMap.
        :param surveyMap: Objet SurveyMap à écrire.
        :return: Element XML créé pour l'objet SurveyMap.
        """
        elMap = xmlDocument.documentElement
        if (surveyMap.minX != None):
             XmlParser.set_float_attribute(elMap, SurveyMapAdapter.ATTR_MINX, float(surveyMap.minX))
        if (surveyMap.maxX != None):
            XmlParser.set_float_attribute(elMap, SurveyMapAdapter.ATTR_MAXX, float(surveyMap.maxX))
        if (surveyMap.minY != None):
            XmlParser.set_float_attribute(elMap, SurveyMapAdapter.ATTR_MINY, float(surveyMap.minY))
        if (surveyMap.maxY != None):
            XmlParser.set_float_attribute(elMap, SurveyMapAdapter.ATTR_MAXY, float(surveyMap.maxY))
        for iNode in range(len(surveyMap)):
            nodeAdapter = SurveyNodeAdapter(surveyMap)
            elNode =  nodeAdapter.write(xmlDocument, surveyMap[iNode])
            elMap.appendChild(elNode)
        return elMap



#
#
##############################################################################
class SurveyMapDocument(XmlDocumentLoader):
    """
    Cette classe permet de gérer un document XML contenant une SurveyMap.
    """

    def __init__(self, xml_document_name=None, root_name=SurveyMapAdapter.TAG_NAME):
        """
        Constructeur du chargeur de document XML.

        :param xml_document_name: Nom du fichier du document XML.
        """
        super().__init__(xml_document_name, root_name)

    def load(self):
        """
        Charge un objet SurveyMap à partir du documentXML.
        :return: Objet SurveyMap chargé.
        """
        mapAdapter = SurveyMapAdapter()
        return mapAdapter.read(doc.rootElement)

    def save(self, surveyMap, mapDocumentName=None):
        """
        Enregistrement d'une SurveyMap dans un document XML.
        Par défaut, le fichier est enregistré avec le nom utilisé à
        l'initialisation.

        :param mapDocumentName: Nom du fichier à enregistrer.
        """
        mapAdapter = SurveyMapAdapter()
        mapAdapter.write(self.xmlDocument, surveyMap)
        super().save(mapDocumentName)


#
#
##############################################################################
if __name__ == '__main__':
    doc = SurveyMapDocument("www/map.xml")
    surveyMap = doc.load()
    for iNode in range(len(surveyMap)):
        print("Node {0} : x={1}, y={2}".format(iNode, surveyMap[iNode].X, surveyMap[iNode].Y), file=sys.stderr)
        for iPoint in range(len(surveyMap[iNode])):
            print("\tPoint {0} : x={1}, y={2}".format(iPoint, surveyMap[iNode][iPoint].X, surveyMap[iNode][iPoint].Y), file=sys.stderr)
    doc2 = SurveyMapDocument()
    doc2.save(surveyMap, "www/mapres.xml")

