#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes des tâches qui peuvent être affectées au robot Explorer.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 05.2020
"""

import sys
import time

from ev3dev2.motor import MoveTank, MoveSteering, OUTPUT_B, OUTPUT_C
from ev3dev2.motor import MediumMotor, OUTPUT_A
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.sensor import INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.sensor import INPUT_3

import lego
from httpd import WebServerTask
from robot import Robot, RobotTask


#
#
##############################################################################
class IRControlledTankTask(RobotTask):
    """
    Cette classe définie la tâche d'un robot à chenille piloté par la
    télécommande infra-rouge.
    Le deux moteurs qui controlent les chenilles sont connectés par défaut
    aux ports OUTPUT_B et OUTPUT_C.
    Le capteur IR est connecté par défaut au port INPUT_4.
    La telecommande du robot est positionnée sur le canal 1.
    La chenille de gauche est commandée par les boutons rouges de la
    télécommande, la chenille de droite par les boutons bleus.
    """
    DEFAULT_MOTORS = MoveTank(OUTPUT_B, OUTPUT_C)
    DEFAULT_CHANNEL = 1
    DEFAULT_SPEED = 50

    def __init__(self, robot, motors=DEFAULT_MOTORS, channel=DEFAULT_CHANNEL,
                speed=DEFAULT_SPEED):
        """
        Constructeur du robot.

        Par défaut, le groupe de moteurs est immplémenté par un MoveTank
        ev3dev. Les moteurs controlant les chenilles sont connecté aux
        ports OUTPUT_B et OUTPUT_C. Le capteur infra-rouge est connecté
        au port INPUT_4.

        :param robot: Robot prorpiétaire de la tâche.
        :param irsenseor: Capteur infra-rouge utilisé.
        :param channel: Canal de la télécommande infra-rouge utilisé.
        :param speed: Vitesse de moteur.
        """
        super().__init__(robot)
        self._motors = motors
        self._irsensor = robot.IRSensor
        self._channel = channel
        self._speed = speed

    def loop(self):
        """
        Instructions exécutées dans la boucle de façon répétitives.
        """
        speed_left, speed_right = 0, 0
        if self._irsensor.top_left(self._channel):
            speed_left = self._speed
        if self._irsensor.bottom_left(self._channel):
            speed_left = -self._speed
        if self._irsensor.top_right(self._channel):
            speed_right = self._speed
        if self._irsensor.bottom_right(self._channel):
            speed_right = -self._speed
        self._motors.on(speed_left, speed_right)


#
#
##############################################################################
class StartStopTask(RobotTask):
    """
    Cette tâche détecte l'état de  la balise de la télécommande.
    Le fait d'activer la balise démare le robot.
    Le fait desactiver la balise arrête le robot.
    """
    DEFAULT_NAME = "StartStopSurvey"
    DEFAULT_CHANNEL = 2

    def __init__(self, robot, task, name=DEFAULT_NAME, channel=DEFAULT_CHANNEL, auto=True):
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
        self._task = task
        self._irsensor = robot.IRSensor
        self._channel = channel

    def loop(self):
        """
        Instructions exécutées dans la boucle de façon répétitives.
        """
        if self._irsensor.top_right(self._channel):
            self._task.start()
        if self._irsensor.top_left(self._channel):
            self._task.stop()


#
#
##############################################################################
class IRBeaconFollowingTask(RobotTask):
    """
    Dans cette tâche, le robot suit la télécommande tant que la balise de
    celle-ci est activée.
    """
    DEFAULT_CHANNEL = 1
    DEFAULT_MOTORS = MoveSteering(OUTPUT_B, OUTPUT_C)

    def __init__(self, robot, channel=DEFAULT_CHANNEL, motors=DEFAULT_MOTORS):
        super().__init__(robot)
        self._irsensor = robot.IRSensor
        self._channel = channel
        self._motors = motors


    def loop(self):
        print("mode =", self._irsensor.mode, file=sys.stderr)
        self._irsensor.mode = self._irsensor.MODE_IR_REMOTE
        beacon = self._irsensor.beacon(self._channel)
        print("beacon=", beacon, file=sys.stderr)
        if beacon:
            self._irsensor.mode = self._irsensor.MODE_IR_SEEK
            heading = self._irsensor.heading(self._channel)
            distance = self._irsensor.distance(self._channel)
            steering = -heading * 5
            if steering > 100:
                steering = 100
            if steering < -100:
                steering = -100
            if distance > 5:
                self._motors.on(steering, -50)
            else:
                self.owner.stop()
            print("heading=", heading, file=sys.stderr)
            print("distance=", distance, file=sys.stderr)
        else:
            self._motors.on(0, 0)
        time.sleep(0.1)

