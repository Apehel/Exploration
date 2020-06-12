#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes relatives au robot Explorer.

Auteur : André-Pierre LIMOUZIN
Version : 1.1 - 05.2020
"""

import sys
import time
import math

from ev3dev2.motor import MoveTank, MoveSteering, OUTPUT_B, OUTPUT_C
from ev3dev2.motor import MediumMotor, OUTPUT_A
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.sensor import INPUT_3

import lego
from httpd import WebServerTask
from robot import Robot, RobotTask
from explorer import RobotExplorer
from explorer_tasks import IRControlledTankTask, StartStopTask
from survey_model import SurveyMap, SurveyNode, SurveyPoint, Wall
from survey_model import Angle, RIGHT_ANGLE, FLAT_ANGLE
from survey_xmlio import SurveyMapDocument


#
#
##############################################################################
class RobotSurveyor(RobotExplorer):
    """
    Cette classe est relative au robot Surveyor propgrammé pour effectuer
    un relevé topographique de son espace d'évolution. Elle hérite de tous les
    éléments structurels du RobotExplorer : capteurs, moteur et constantes
    géométriques.

    Le mouvement du robot est assuré par deux grand servo-moteurs EV3
    connectés respectivement sur les port B et C.
    Le mouvement rotatif du capteur ultra-son est assuré par une servo-
    moteur connecté sur le port A.
    Le capteur Infra-rouge, utilisé pour actionner le robot par la
    télécommande IR est connecté sur le port 4.
    Le capteur Ultra-son, utilisé pour la télémetrie, est connecté sur
    le port 3.
    L'axe de rotation du capteur Ultra-son est excentré de US_ECCENTRICITY
    par rapport à la position centrale du robot.
    Le capteur Ultra-Son est également excentré de US_DISTORTION par
    rapport à son axe de rotation.
    """
    DEFAULT_MOVING_MOTORS = MoveSteering(OUTPUT_B, OUTPUT_C)
    US_SPEED = 25
    MOTORS_SPEED = 25

    def __init__(self, motors=DEFAULT_MOVING_MOTORS,
                usmotor=RobotExplorer.DEFAULT_US_MOTOR,
                irsensor=RobotExplorer.DEFAULT_IR_SENSOR,
                ussensor=RobotExplorer.DEFAULT_US_SENSOR):
        """
        Construction du robot.
        :param motors: Jeu de moteurs utilisés pour déplacer le robot.
        :param usmotors:  Moteur utilisé pour la rotation du capteur Ultra-sons.
        :param irsensor: Capteur Infra-rouge utilisé par la télécommande.
        :param ussensor: Capteur Ultra-son uutilisé pour la télémetrie.
        """
        super().__init__(motors, usmotor, irsensor, ussensor)
        self._motors = motors
        self._usmotor = usmotor
        self._ussensor = ussensor
        self._irsensor = irsensor
        self._map = SurveyMap()
        self._position = (0, 0)
        self._orientation = Angle()
        doc2 = SurveyMapDocument()
        doc2.save(self._map, "www/map.xml")

    @property
    def position(self):
        return self._position

    @property
    def orientation(self):
        return self._orientation

    def surveyTour(self, a1=-180, a2=+180, step=10):
        """
        Effectue un tour d'horizon.

        La télémetrie du tour d'horizon est assurée par un capteur Ultra-Son.
        Chaque tour d'horizon est enregistré dans www/map.xml.

        :param a1: angle de départ (-180° par défaut)
        :param a2: angel de fin (+180° par défaut)
        :param step: pas de rotation (10° par défaut)
        :return: Objet station
        """
        station = SurveyNode(self._map, self._position[0], self._position[1],
            self._orientation, RobotExplorer.US_ECCENTRICITY)
        for a in range(a1, a2, step):
            if a == a1:
                self._usmotor.on_for_degrees(
                    RobotSurveyor.US_SPEED, a * RobotExplorer.US_GEARS_REDUCTION)
            else:
                self._usmotor.on_for_degrees(
                    RobotSurveyor.US_SPEED, 10 * RobotExplorer.US_GEARS_REDUCTION)
            time.sleep(0.5)
            r = self.telemeter()
            station.addPolarPoint(a, r)
            time.sleep(0.3)
        self._usmotor.on_for_degrees(RobotSurveyor.US_SPEED,
            (step - a2) * RobotExplorer.US_GEARS_REDUCTION)
        station.computeWallData()
        self._map.addNode(station)
        doc2 = SurveyMapDocument()
        doc2.save(self._map, "www/map.xml")
        return station

    def telemeter(self):
        """
        Effectue une mesure télémetrique par le capteur Ultra-Sons.
        La distance est calculée par rapport à l'axe de rotation du capteur.
        :return: Distance mesurée.
        """
        r = self._ussensor.distance_centimeters + RobotExplorer.US_DISTORTION
        return r

    def turn(self, angle):
        """
        Effectue une rotation horizontale de angle.
        Si angle est positif, le robot tourne vers la droite.
        Si angle est négatif, le robot tourne vers la gauche.
        L'orientation du robot est mise à jour par cette méthode.
        :param angle: Angle de rotation.
        :return: Nouvelle orientation.
        """
        print("Tourne de {0} degres".format(angle.degrees), file=sys.stderr)
        self._orientation += angle
        angleMotors = angle.degrees
        steering = 100
        if (angle.radians < 0):
            steering = -steering
            angleMotors = -angleMotors
        angleMotors *= RobotExplorer.CATERPILLAR_SPACING /(2 * RobotExplorer.CATERPILLAR_RADIUS)
        self._motors.on_for_degrees(steering, 25, angleMotors)
        return self._orientation

    def moveForward(self, distance):
        """
        Avance de de distance.
        La position du robot est  mise à jour par cette méthode.
        :param distance: Distance à parcourir en cm.
        :return: Nouvelle position.        """
        print("Avance de {0}cm".format(distance), file=sys.stderr)
        dx = distance * self._orientation.sin
        dy = distance * self._orientation.cos
        self._position = (self._position[0] + dx, self._position[1] + dy)
        angleMotors = math.degrees(distance / RobotExplorer.CATERPILLAR_RADIUS)
        self._motors.on_for_degrees(0, RobotSurveyor.MOTORS_SPEED, angleMotors)
        return self._position

    def goto(self, x=0, y=0, position=None):
        """
        Le robot se deplace vers la position absolue (x, y).
        L'orientation et la position du robot sont modifiées.
        Le déplacement (x,y) est exprimé dans le référentiel de l'espace.
        :param x: Abscisse (en cm) dans l'espace d'évolution du robot.
        :param y: Ordonnée (en cm) dans l'espace d'évolution du robot.
        """
        if (position != None):
            x = position[0]
            y = position[1]
        dx = x - self._position[0]
        dy = y - self._position[1]
        direction = Angle(radians=math.atan2(dx, dy))
        angle = direction - self._orientation
        distance = math.sqrt(dx * dx + dy * dy)
        print("Robot-Orientation={0}".format(self._orientation.degrees), file=sys.stderr)
        print("Direction={0}".format(direction.degrees), file=sys.stderr)
        print("(dx,dy)=({0},{1})".format(dx, dy), file=sys.stderr)
        print("Angle={0}".format(angle.degrees), file=sys.stderr)
        print("Distance={0}".format(distance), file=sys.stderr)
        self.turn(angle)
        self.moveForward(distance)


#
#
##############################################################################
class SurveyTask(RobotTask):
    """
    Cette tâche détecte l'état de  la balise de la télécommande.
    Le fait d'activer la balise démare le robot.
    Le fait desactiver la balise arrête le robot.
    """
    DEFAULT_NAME = "Survey"
    THRESHOLD = 50
    STATION_STEP = 50

    def __init__(self, robot, name=DEFAULT_NAME, auto=False):
        """
        Constructeur du robot.

        Par défaut, le groupe de moteurs est immplémenté par un MoveTank
        ev3dev. Les moteurs controlant les chenilles sont connecté aux
        ports OUTPUT_B et OUTPUT_C. Le capteur infra-rouge est connecté
        au port INPUT_4.

        :param robot: Robot prorpiétaire de la tâche.
        :param motors: Couple de moteur utilisé.
        :param irsenseor: Capteur infra-rouge utilisé.
        :param channel: Canal de la télécommande infra-rouge utilisé.
        :param speed: Vitesse de moteur.
        """
        super().__init__(robot, name, auto)
        self.__motors = robot.Motors
        self.__ussensor = robot.USSensor
        self.__usmotor = robot.USMotor

    def loop(self):
        """
        Instructions exécutées dans la boucle de façon répétitives.
        """
        station = self.robot.surveyTour()
        self.gotoNextStation(station)


    def gotoNextStation(self, station):
        print("Station-Orientation={0}".format(station.orientation.degrees), file=sys.stderr)
        nearestWall = station.getNearestWall()
        if nearestWall is None:
            nearestPoint = station.getNearestPoint()
            if nearestPoint is None:
                print("No wall found ! No point found !", file=sys.stderr)
                self.robot.moveForward(SurveyTask.STATION_STEP)
            else:
                print("No wall, but at least one point found !", file=sys.stderr)
                self.robot.turn(nearestPoint.rawAngle - robot.orientation)
                self.robot.moveForward(nearestPoint.rawDistance - SurveyTask.STATION_STEP)
        else:
            if nearestWall.isLeftWall:
                print("A wall was found on the left !", file=sys.stderr)
                self.robot.goto(position=self.__onLeftWall(nearestWall.Pt1, nearestWall.Pt2))
            elif nearestWall.isRightWall:
                print("A wall was found on the right !", file=sys.stderr)
                self.robot.goto(position=self.__onRightWall(nearestWall.Pt1, nearestWall.Pt2))
            elif nearestWall.isFrontWall:
                if station.hasRightWall and station.hasLeftWall:
                    print("Dead end found ! Go back !", file=sys.stderr)
                    robot.turn(FLAT_ANGLE)
                elif station.hasRightWall :
                    print("A wall was found straight ahead with a wall on the right !", file=sys.stderr)
                    self.robot.goto(position=self.__onRightWall(nearestWall.Pt1, nearestWall.Pt2))
                elif station.hasLeftWall:
                    print("A wall was found straight ahead with a wall on the left !", file=sys.stderr)
                    self.robot.goto(position=self.__onLeftWall(nearestWall.Pt1, nearestWall.Pt2))
                else:
                    print("A wall was found straight ahead !", file=sys.stderr)
                    self.robot.turn(RIGHT_ANGLE)
            else:
                print("Un mur bizare a ete trouve. Que faire ?", file=sys.stderr)

    def __onRightWall(self, p1, p2):
        """
        Calcul de la destination suivante lorqu'un mur est rencontré à droite.

        La nouvelle destination se trouve en face à gauche de la première
        extrémité à une distance de STATION_STEP.
        :param p1: Première extrémité du ur rencontré.
        :param p2: Seconde extrémité du mur rencontré.
        :return: Nouvelle destination.
        """
        dx = p1.X - p2.X
        dy = p1.Y - p2.Y
        R = math.sqrt(dx * dx + dy * dy)
        xDest = p1.X - dy * SurveyTask.STATION_STEP / R
        yDest = p1.Y + dx * SurveyTask.STATION_STEP / R
        print("onRightWall:", file=sys.stderr)
        print("P1 =", p1, file=sys.stderr)
        print("P2 =", p2, file=sys.stderr)
        print("Dest=({0},{1})".format(xDest, yDest), file=sys.stderr)
        print("(dx,dy)=({0},{1})".format(dx, dy), file=sys.stderr)
        print("R={0}".format(R), file=sys.stderr)
        return (xDest, yDest)

    def __onLeftWall(self, p1, p2):
        """
        Calcul de la destination suivante lorqu'un mur est rencontré à gauche.

        La nouvelle destination se trouve en face à droite de la seconde
        extrémité à une distance de STATION_STEP.
        :param p1: Première extrémité du ur rencontré.
        :param p2: Seconde extrémité du mur rencontré.
        :return: Nouvelle destination.
        """
        dx = p2.X - p1.X
        dy = p2.Y - p1.Y
        R = math.sqrt(dx * dx + dy * dy)
        xDest = p2.X + dy * SurveyTask.STATION_STEP / R
        yDest = p2.Y - dx * SurveyTask.STATION_STEP / R
        print("onLeftWall:", file=sys.stderr)
        print("P1 =", p1, file=sys.stderr)
        print("P2 =", p2, file=sys.stderr)
        print("Dest=({0},{1})".format(xDest, yDest), file=sys.stderr)
        print("(dx,dy)=({0},{1})".format(dx, dy), file=sys.stderr)
        print("R={0}".format(R), file=sys.stderr)
        return (xDest, yDest)

#
#
##############################################################################
if __name__ == '__main__':
    import time
    robot = RobotSurveyor()
    WebServerTask(robot)
    survey = SurveyTask(robot)
    StartStopTask(robot, survey)
    #IRControlledTankTask(robot)
    #robot.surveyTour()
    robot.run()
    """
    robot.turn(Angle(degrees=32))
    robot.moveForward(-41.0)
    robot.turn(Angle(degrees=-90.0))
    robot.moveForward(50.0)
    """
   #robot.turn(RIGHT_ANGLE)
