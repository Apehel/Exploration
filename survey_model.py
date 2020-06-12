#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes des objets utilisés parle robot explorer.
Dans ce module, tous les angles sont exprimés en degrés et calculés dans
le sens topographique (sens des aiguilles d'une montre avec origine le nord,
donc l'axe des ordonnées).

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 05.2020
"""

from abc import abstractmethod
import math
import sys

#
#
##############################################################################
class Angle:
    """
    Cette classe modélise un angle compris entre -180° et +180°.
    """
    def __init__(self, radians=None, degrees=None, gradians=None):
        value = 0.0
        if radians is not None:
            value = radians
        elif degrees is not None:
            value = degrees * math.pi / 180.0
        elif gradians is not None:
            value = gradians * math.pi / 200.0
        self.__value = value
        self.__normalize()

    @property
    def radians(self):
        return self.__value

    @property
    def degrees(self):
        return self.__value * 180.0 / math.pi

    @property
    def gradians(self):
        return self.__value * 200.0 / math.pi

    @property
    def sin(self):
        return math.sin(self.__value)

    @property
    def cos(self):
        return math.cos(self.__value)

    @property
    def tan(self):
        return math.tan(self.__value)

    def __add__(self, other):
        return Angle(self.__value + other.__value)

    def __iadd__(self, other):
        self.__value += other.__value
        self.__normalize()
        return self

    def __sub__(self, other):
        return Angle(self.__value - other.__value)

    def __isub__(self, other):
        self.__value -= other.__value
        self.__normalize()
        return self

    def __neg__(self):
        return Angle(self.__value.__neg__())

    def __normalize(self):
        """
        Noramisation de l'angle entre -Pi et +Pi.
        """
        while self.__value > math.pi:
            self.__value -= 2.0 * math.pi
        while self.__value <= -math.pi:
            self.__value += 2.0 * math.pi


RIGHT_ANGLE = Angle(degrees=90)
FLAT_ANGLE = Angle(degrees=180)

#
#
##############################################################################
class SurveyObject:
    """
    Cette classe est la racine du polymorphisme des objets utilisés par le
    robot Explorer.
    Tous les objets de ce polymorphisme maintiennent une référence sur
    l'objet SurveyMap auquel ils appartiennent. Cet objet SurveyMap est
    exposé sous la forme d'une Property.
    """
    def __init__(self, surveyMap):
        """
        Initialisation d'un SurveyObject.

        :param map: Objet SurveyMap auquel appartient l'objet.
        """
        self._map = surveyMap

    @property
    def containerMap(self):
        return self._map


#
#
##############################################################################
class SurveyBasePoint(SurveyObject):
    """
    Cette classe modélise un point dans le référentiel de l'espace du robot.

    Les coordonnées sont définies en mode Prodected. Car elle ne doivent pas
    être modifiées. En effet, si les corrdonnées sont modifiées, il s'agit
    d'un autre point qui doit faire l'objet d'un nouvelle instanciation.
    Elle sont néanmoins exposées sour la forme de Property X et Y (en
    majuscules).
    Les coordonées sont modélisées en FLoat dans le référentiel de l'espace.
    """
    def __init__(self, surveyMap, x=0, y=0):
        """
        Initialisation d'un SurveyPoint.

        :param surveyMap: SurveyMap qui contient les objets.
        :param x:Abscisse du point.
        :param y:Ordonnée du point
        """
        super().__init__(surveyMap)
        self._x = x
        self._y = y

    @property
    def X(self):
        return self._x

    @property
    def Y(self):
        return self._y

    @property
    def position(self):
        return (self._x, self._y)


#
#
##############################################################################
class SurveyPoint(SurveyBasePoint):
    """
    Cette classe modélise un point relevé lors d'un tour d'horizon.
    Les données brutes du point sont définie par une anle et une distance
    mersurés dans le référentiel du robot.
    Ces données brutes sont converties dans le référentiel de l'espace
    en tenant compte de la géométrie, de la position et de l'orientation
    du robot.
    L'angle est exprimé en degré et calculé dans le sens topographique (dans
    le sens des aiguilles d'une montre).
    L'angle et la distance sont données dans le référentiel du robot par
    rapport au centre du tour d'horizon (axe du moteur pilotant le capteur
    ultra-son).
    Le centre du tour d'horizon peut être décalé par rapport à la position
    du robot (paramètre offset).
    """
    def __init__(self, surveyNode, angle, distance, x, y):
        """
        Initialisation d'un SurveyPoint.

        :param node: Tour d'horizon auquel appartient le point.
        :param angle: Angle en degré dans le référentiel du robot.
        :param distance: distance du point avec node
        :param x: Abscisse du point.
        :param y: Ordonnée du Point.
        """
        super().__init__(surveyNode._map, x, y)
        self.__node = surveyNode
        self.__angle = angle
        self.__dist = distance
        self.isValid = False

    @property
    def parentNode(self):
        return self.__node

    @property
    def rawAngle(self):
        return self.__angle

    @property
    def rawDistance(self):
        return self.__dist

    def __str__(self):
        return "({0},{1}) - [a={2}, d={3}, valid={4}]".format(self.X, self.Y, self.__angle, self.__dist, self.isValid)


#
#
##############################################################################
class Wall(SurveyObject):
    """
    Cette classe moédélise un mur ou un fragment de mur repéré lors d'une
    station.

    Un mur est constitué d'une collection de points successifs dont l'écart
    ne dépasse pas un seuil déterminé.
    """
    def __init__(self, surveyNode, points):
        """
        Initialisation du Wall.
        :param surveyNode: Sation de laquelle dépend le mur.
        """
        super().__init__(surveyNode._map)
        self.__points = points
        self.__isLeftWall = False
        self.__isFrontWall = False
        self.__isRightWall = False
        self.__computeWall()

    def __computeWall(self):
        """
        Calcul des éléments géométrique du mur à partir du tableau de points.
        L'alignement des points n'étant pas avéré du fait des imprécisions de
        mesure, un droite est calculée selon la loi des moindres carrés.
        A l'issus du calcul, la class Wall est en mesure d'exposer :
        * Les coéficients A et B de la droite Ax + By = C
        * Les point P1 et P2 correspondant aux extrémitésdu segment
        * Un coéfficient Q exprimant la corrélation de la droite.
        """
        Sx = 0.0
        Sy = 0.0
        Sxx = 0.0
        Syy = 0.0
        Sxy = 0.0
        countLeftPoints = 0
        countRightPoints = 0
        for iPoint in range (len(self.__points)):
            point = self.__points[iPoint]
            Sx += point.X
            Sy += point.Y
            Sxx += point.X * point.X
            Syy += point.Y * point.Y
            Sxy += point.X * point.Y
            if point.rawAngle < 0:
                countLeftPoints += 1
            if point.rawAngle > 0:
                countRightPoints +=1
        if countRightPoints/len(self.__points) > 0.6:
            self.__isRightWall = True
        elif countLeftPoints/len(self.__points) > 0.6:
            self.__isLeftWall = True
        else:
            self.__isFrontWall = True
        # Calcul des moyennes pour Xi et Yi
        Mx = Sx / len(self.__points)
        My = Sy / len(self.__points)
        # Calcul des variances pour Xi et Yi
        Vx = Sxx / len(self.__points) - Mx * Mx
        Vy = Syy / len(self.__points) - My * My
        # Calculde la covariance de Xi & Yi
        Cxy = Sxy /len(self.__points) - Mx * My
        point1 = self.__points[0]
        point2 = self.__points[len(self.__points) - 1]
        if (Vx > Vy):
            self.__A = Cxy / Vx
            self.__B = -1.0
            self.__C = self.__A * Mx - My
            self.__pt1 = SurveyPoint(point1.parentNode, point1.rawAngle, point1.rawDistance, point1.X, self.__A * point1.X - self.__C)
            self.__pt2 = SurveyPoint(point2.parentNode, point2.rawAngle, point2.rawDistance, point2.X, self.__A * point2.X - self.__C)
        else:
            self.__A = -1.0
            self.__B = Cxy / Vy
            self.__C = self.__B * My - Mx
            self.__pt1 = SurveyPoint(point1.parentNode, point1.rawAngle, point1.rawDistance, self.__B * point1.Y - self.__C, point1.Y)
            self.__pt2 = SurveyPoint(point2.parentNode, point2.rawAngle, point2.rawDistance, self.__B * point2.Y - self.__C, point2.Y)
        self.__Q = abs(Cxy / (math.sqrt(Vx) * math.sqrt(Vy)))
        dx = self.__pt2.X - self.__pt1.X
        dy = self.__pt2.Y - self.__pt1.Y
        self.__orientation = Angle(radians=math.atan2(dx, dy))

    @property
    def Pt1(self):
        return self.__pt1

    @property
    def Pt2(self):
        return self.__pt2

    @property
    def A(self):
        return self.__A

    @property
    def B(self):
        return self.__B

    @property
    def C(self):
        return self.__C

    @property
    def Q(self):
        return self.__Q

    @property
    def orientation(self):
        return self.__orientation

    @property
    def isRightWall(self):
        return self.__isRightWall

    @property
    def isLeftWall(self):
        return self.__isLeftWall

    @property
    def isFrontWall(self):
        return self.__isFrontWall

    def __len__(self):
        return len(self.__points)

    def __getitem__(self, key):
        return self.__points[key]

    def distanceFrom(self, point):
        """
        Calcule la distance du point passé en paramètre au mur.

        :param point: Point dont il faut calculer la distance.
        :return: Distance du point par rapport au mur.
        """
        return math.fabs(self.A * point.X + self.B * point.Y + self.C) / (math.sqrt(self.A * self.A + self.B * self.B))


#
#
##############################################################################
class SurveyNode(SurveyBasePoint):
    """
    Cette classe modélise une station sur laquelle est opérée un tour
    d'horizon.
    Cet objet est constitué d'un collection d'objets SurveyPoint qui
    correspondent à un point relevé par angle et distance.

    Le SurveyNode est une station topographique à partir de laquelle est
    effectué un tour d'horizon.
    Un SurveyNode et orienté. L'orientation correspond à l'origine des
    angles mesurés lors du tour d'horizon. L'orientation est exprimée en
    degrés dans le sens topographique à partir du Nord.
    De par la géométrie du robot, le centre du tour d'horizon est décalé
    de offset. Ce décalage est exprimé en centimètres dans le référentiel
    du robot.
    Le SurveyNode est exposé comme un tableau de SurveyPoint. Il est donc
    possible d'utiliser l'opérateur [] pour obtenir le point d'un rang
    donné.
    """
    THRESHOLD = 15

    def __init__(self, map, x, y, orientation, offset):
        """
        Initialisation d'un SurveyNode.

        :param map: Map à laquelle apparatient le SurveyNode.
        :param x: Abscisse du point.
        :param y: Ordonnée du Point.
        :param orientation: Orientation du tour d'horizon (en degrés).
        :param offset: Tuple exprimant le décalage du centre du tour d'horizon.
        """
        super().__init__(map, x, y)
        self.__orientation = Angle(orientation.radians)
        self.__points = []
        self.__walls = []
        self.__offset = offset
        self.__correction = (
            offset[0] * self.__orientation.cos + offset[1] * self.__orientation.sin,
            -offset[0] * self.__orientation.sin + offset[1] * self.__orientation.cos)
        self.__lastPoint = None
        self.__leftWall = None
        self.__frontWall = None
        self.__rightWall = None

    @property
    def orientation(self):
        return self.__orientation

    @property
    def offset(self):
        return self.__offset

    @property
    def lastPoint(self):
        return self.__lastPoint

    @property
    def walls(self):
        return self.__walls

    @property
    def hasLeftWall(self):
        return self.__leftWall is not None

    @property
    def leftWall(self):
        return self.__leftWall

    @property
    def hasFrontWall(self):
        return self.__frontWall is not None

    @property
    def frontWall(self):
        return self.__frontWall

    @property
    def hasRightWall(self):
        return self.__rightWall is not None

    @property
    def rightWall(self):
        return self.__rightWall

    def __len__(self):
        return len(self.__points)

    def __getitem__(self, key):
        return self.__points[key]

    def addPoint(self, point):
        """
        Ajout d'un point dans le tour d'horizon.
        Le point passé en paramètre doit êter instancié auparavant.
        :param point: Point à ajouter.
        """
        self.__points.append(point)
        self._map.updateSize(point.X, point.Y)
        self.validatePoint(point)
        self.__lastPoint = point

    def addPolarPoint(self, angle, distance):
        """
        Ajout d'un point dans le tour d'horizon.
        Les coordonnées passées en paramètre sont polaires.
        :param angle: Angle en degré dans le référentiel du robot.
        :param distance: Distance du point avec le centre du tour d'horizon.
        """
        rAngle = Angle(degrees=angle) + self.__orientation
        x = self._x + distance * rAngle.sin + self.__correction[0]
        y = self._y + distance * rAngle.cos + self.__correction[1]
        self.addPoint(SurveyPoint(self, angle, distance, x, y))

    def validatePoint(self, point):
        """
        Evalue la validité d'un point.

        Les capteurs utilisés pour la télémétrie étant imprécis, il est
        indispensable d'évaluer si un point est valide.
        L'algorithme utilisé est le suivant :
        1) Le premier point d'un tour d'horizon n'est pas valide (mais il
        peut être re-évalué à la mesure suivante).
        2) Si le point mésuré est à proche distance du point mesuré
        précédemment, alors il est valide.
        2) Dans ce cas, si le point précédent est invalide, mais qu'il
        se trouve à une faible distance du point évalué, il est ré-évalué
        à valide.

        :param point: Point à évaluer.
        """
        if self.__lastPoint is None:
            return
        dx = point.X - self.__lastPoint.X
        dy = point.Y - self.__lastPoint.Y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < SurveyNode.THRESHOLD:
            point.isValid = True
            self.__lastPoint.isValid = True

    def getNearestPoint(self):
        """
        :return: Point le plus proche de la station
        """
        dist = 0
        point = None
        for iPoint in range(len(self.__points)):
            if dist == 0 or dist > self.__points[iPoint].rawDistance:
                point = self.__points[iPoint]
                dist = point.rawDistance
        return point


    def computeWallData(self):
        """
        Calcule les coéficients d'équation d'éventuels murs relevés par la
        station.

        Un mur est la droite de corrélation entre une suite non interrompue
        de points valides trouvés dans une station.
        """
        wallPoints = None
        for iPoint in range(len(self.__points)):
            point = self.__points[iPoint]
            if point.isValid:
                if wallPoints is None:
                    wallPoints = []
                    wallPoints.append(point)
                else:
                    lastPoint = wallPoints[len(wallPoints) - 1]
                    dx = point.X - lastPoint.X
                    dy = point.Y - lastPoint.Y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < SurveyNode.THRESHOLD:
                        wallPoints.append(point)
                    else:
                        self.__addWall(wallPoints)
                        wallPoints = []
                        wallPoints.append(point)
            else:
                if wallPoints is not None:
                    self.__addWall(wallPoints)
                    wallPoints = None
        if wallPoints is not None:
            self.__addWall(wallPoints)

    def __addWall(self, wallPoints):
        """
        Ajoute un nouveau mur dans le tour d'horizon.
        Pour qu cela soit possible, il faut que le tableau de points
        passé en paramètre contienne au moins trois SurveyPoints.
        :param wallPoints: Tableau de SurveyPoint.
        """
        if wallPoints != None and len(wallPoints) > 2:
            wall = Wall(self, wallPoints)
            self.__walls.append(wall)
            if wall.isLeftWall:
                self.__leftWall = wall
            if wall.isFrontWall:
                self.__frontWall = wall
            if wall.isRightWall:
                self.__rightWall = wall

    def getNearestWall(self):
        """
        :return: Mur le plus proche de la station ou None si aucun mur trouvé.
        """
        wall = None
        dist = 0
        for iWall in range(len(self.__walls)):
            dist1 = self.__walls[iWall].distanceFrom(self)
            if dist == 0 or dist > dist1:
                wall = self.__walls[iWall]
                dist = dist1
        return wall

#
#
##############################################################################
class SurveyMap(SurveyObject):
    """
    Cette classe modélise la carte relevée par le robot explorer.
    Cette objet est constitué par une collection d'objets SurveyNode qui
    correspondent à des stations sur laquelle se réalise un tour d'horizon.

    De par la géométrie du robot, le centre du tour d'horizon est décalé
    de offset. Ce décalage est exprimé en centimètres dans le référentiel
    du robot.
    La SurveyMap est exposée comme un tableau de SurveyNode. Il est donc
    possible d'utiliser l'opérateur [] pour obtenir la station d'un rang
    donné.
    """
    def __init__(self):
        super().__init__(self)
        self.__nodes = []
        self.__minX = None
        self.__maxX = None
        self.__minY = None
        self.__maxY = None

    @property
    def minX(self):
        return self.__minX

    @property
    def maxX(self):
        return self.__maxX

    @property
    def minY(self):
        return self.__minY

    @property
    def maxY(self):
        return self.__maxY

    def __len__(self):
        return len(self.__nodes)


    def __getitem__(self, key):
        return self.__nodes[key]

    def updateSize(self, x, y):
        if self.__minX == None or x < self.__minX:
            self.__minX = x
        if self.__maxX == None or x > self.__maxX:
            self.__maxX = x
        if self.__minY == None or y < self.__minY:
            self.__minY = y
        if self.__maxY == None or y > self.__maxY:
            self.__maxY = y

    def addNode(self, node):
        """
        Ajout d'un Node à la Map.

        :param node: SurveyNode à ajouter.
        """
        self.__nodes.append(node)
        self.updateSize(node.X, node.Y)


#
#
##############################################################################
if __name__ == '__main__':
    map = SurveyMap()

