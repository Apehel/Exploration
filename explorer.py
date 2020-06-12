#!/usr/bin/env python3
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
from robot import Robot


#
#
##############################################################################
class RobotExplorer(Robot):
    """
    Cette classe est relative au robot Explorer. Elle contient tous les
    éléments structurels du robot : capteurs, moteur et constantes
    géométriques.

    Aucune tâche, n'est définié par défaut. Mais celles-ci peuvent être
    ajoutées par la méthode add_task.

    Cette classe peut aussi être surchargée pour ajouter des méthodes
    de contrôle pour chaque tâche individuellement.

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
    DEFAULT_US_MOTOR = MediumMotor(OUTPUT_A)
    DEFAULT_IR_SENSOR = InfraredSensor(INPUT_4)
    DEFAULT_US_SENSOR = UltrasonicSensor(INPUT_3)
    US_ECCENTRICITY = (0, 12 * lego.U)
    US_DISTORTION = 4 * lego.U
    CATERPILLAR_SPACING = 22 * lego.U
    CATERPILLAR_RADIUS = 2 * lego.U
    US_GEARS_REDUCTION = -3

    def __init__(self, motors=DEFAULT_MOVING_MOTORS, usmotor=DEFAULT_US_MOTOR,
                irsensor=DEFAULT_IR_SENSOR, ussensor=DEFAULT_US_SENSOR):
        """
        Construction du robot.
        :param motors: Jeu de moteurs utilisés pour déplacer le robot.
        :param usmotors:  Moteur utilisé pour la rotation du capteur Ultra-sons.
        :param irsensor: Capteur Infra-rouge utilisé par la télécommande.
        :param ussensor: Capteur Ultra-son uutilisé pour la télémetrie.
        """
        super().__init__()
        self.__motors = motors
        self.__usmotor = usmotor
        self.__ussensor = ussensor
        self.__irsensor = irsensor

    @property
    def Motors(self):
        return self.__motors

    @property
    def USMotor(self):
        return self.__usmotor

    @property
    def USSensor(self):
        return self.__ussensor

    @property
    def IRSensor(self):
        return self.__irsensor

#
#
##############################################################################
if __name__ == '__main__':
    pass
