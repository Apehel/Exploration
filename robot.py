#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes de base d'un robot Lego MindStorm EV3
développé avec l'API ev3dev2.

Auteur : André-Pierre LIMOUZIN
Version : 1.1 - 01.2020
"""
import time, sys
from threading import Thread

#
#
##############################################################################
class RobotError(Exception):
    """
    Cette classe définit les exceptions générée par les classes de robot.
    """
    TYPE_ERROR = "{0} n'est pas une instance de la classe {1}."
    ADD_TASK_ERROR = "Impossible d'ajouter une tâche à un robot en marche."

    def __init__(self, message, *args):
        """
        Constructeur de l'erreur.

        :param message: Chaine de caractères consituant le message.
        :param args: Argument pouvant être formattés dans le message.
        """
        super().__init__(message.format(*args))

#
#
##############################################################################
class RobotTask():
    """
    Cette classe définit la classe de base pour toutes les taches exécutée
    par le robot.

    Une tache comprend un jeu d'instructions exécuté dans une boucle.
    """

    DEFAULT_NAME = "Main"

    def __init__(self, robot, name=DEFAULT_NAME, auto=True):
        """
        Initialisation de tâche.

        Le paramètre auto permet de péciser si la tâche doit être lancée
        au démarrage du robot. Si True, la tâche sera lancée par la méthode
        run() du robot. Si False, la tâche devra être lancée explicitement
        par l'invocation de la méthode start() de celle-ci.

        :param robot: Robot propriétaire de de la tâche.
        :param name: Nom de la tâche ("Main" par défaut).
        :param auto: Indicateur si la tâche est automaitquement démarrée.
        """
        if not(isinstance(robot, Robot)):
            raise RobotError(RobotError.TYPE_ERROR, repr(robot), Robot)
        self.__robot = robot
        self.__is_running = False
        self.__name = name
        self.__auto = auto
        robot.add_task(self)

    @property
    def robot(self):
        return self.__robot

    @property
    def isRunning(self):
        return self.__is_running

    def __task(self):
        """
        Traitement de la tâche.
        """
        print("Task {0} started !".format(self.__name), file=sys.stderr)
        self.setup()
        while self.__is_running:
            self.loop()

    def start(self):
        """
        Lancement en parallèle de la tâche d'exécution.
        """
        if not self.__is_running:
            self.__is_running = True
            task = Thread(target=self.__task)
            task.start()

    def stop(self):
        """
        Arrêt de la tâche d'exécution.
        """
        if self.__is_running:
            self.__is_running = False

    def setup(self):
        """
        Jeu d'instructions exécuté pour l'initialisation de la tâche.

        Cette méthode peut être surchargée pour initialiser la tâche.
        """
        pass

    def loop(self):
        """
        Jeu d'instructions exécuté de façon répétitive dans la boucle de la tâche.

        Cette méthode doit être surchargée pour définirla liste des instructions
        qui vont être exécutées en boucle.
        """
        self.stop()


    @property
    def name(self):
        """
        :return: Nom de la tâche
        """
        return self.__name

    @property
    def owner(self):
        """
        :return: Robot propriétaire de la tâche.
        """
        return self.__robot

    @property
    def auto(self):
        """
        :return: Indicateur si la tâche doit être démarrée automatiquement.
        """
        return self.__auto

    @property
    def running(self):
        """
        Cette propriété en lecture seule indique  si la tâche est en cours
        d'exécution.

        :return: True si la tâche a été démarrée et est en cours d'exécution.
        """
        return self.__is_running


#
#
##############################################################################
class Robot():
    """
    Cette class définit la classe de base pour tous les robots.

    Le tâches sont exécutées en parallèle. Elle sont associées au robot
    dans un dictionnaire dans lequel elles sont repérées par leur nom.
    Par défaut, au moins une tâche est présente (sinon le robot ne fait rien).
    """

    def __init__(self):
        """
        Constructeur du robot.
        """
        self._is_running = False
        self.__tasks = {}

    def add_task(self, task):
        """
        Ajoute une tâche en parallèle pour le robot.

        :param task: Objet RobotTask à ajouter.
        """
        if not(isinstance(task, RobotTask)):
            raise RobotError(RobotError.TYPE_ERROR, repr(task), RobotTask)
        if self.running:
            raise RobotError(RobotError.ADD_TASK_ERROR)
        if task.name in self.__tasks:
            self.__tasks[task.name].stop()
        self.__tasks[task.name] = task

    def getTask(self, name):
        """
        Renvoie la tâche dont le nom est name.
        :param name: Nom de la tâche.
        :return: Tâche du robot dont le nom est passé en paramètre.
        """
        return self.__tasks[name]

    def run(self):
        """
        Cette méthode permet de désolidariser la construction de l'objet robot
        de son lancement effectif.
        Pour fonctionner, la classe du robot doit donc être d'abord instanciée,
        puis lancé en invoquant la méthode run sur l'instance créée.

        Un robot peut être composé de plusieurs tâches en parallèle, au moins
        une. Au démarrage du robot, toutes les tâches doivent être démarrées.
        """
        for key in self.__tasks:
            if not self.__tasks[key].running and self.__tasks[key].auto:
                self.__tasks[key].start()

    def stop(self):
        """
        Cette méthode arrête toute les tâches attachées au robot.
        """
        for key in self.__tasks:
            if self.__tasks[key].running:
                self.__tasks[key].stop()

    @property
    def running(self):
        """
        Cette propriété en lecture seule indique si le robot est en marche.

        On considère que le robot est en marche dès qu'au moins l'une de
        ses tâches est en marche.

        :return: True si au moins une tâche est running.
        """
        is_running = False
        for key in self.__tasks:
            is_running |= self.__tasks[key].running
        return is_running


#
#
##############################################################################
if __name__ == '__main__':
    robot = Robot()
    task = RobotTask(robot)
    robot.run()
    time.sleep(180)
    robot.stop()
