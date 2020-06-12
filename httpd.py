#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
"""
Ce module définit les classes permettant d'activer un serveur Web en tâche
parallèle dans un robot.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 05.2020
"""

import sys
import os
import time
import http.server
from robot import RobotTask, Robot
import xml.etree.ElementTree as ET


#
#
##############################################################################
class WebServerTask(RobotTask):
    """
    Cette classe définit un Serveur Web lancé en parallèle pour exposer les
    données collectées par un robot.
    Les pages Web doivent se trouver dans le même répertoire que
    le script Python.
    """

    DEFAULT_NAME = "RobotWeb"

    def __init__(self, robot, webport=8000, name=DEFAULT_NAME, auto=True):
        """
        Initialisation de la tâche.

        Un serveur Web est instancié.
        :param robot: Robot propriétaire de de la tâche.
        :param webport: Port réseau utilisé par le serveur Web (8000 par défaut)
        :param name: Nom de la tâche ("RobotWeb" par défaut).
        :param auto: Indicateur si la tâche est automaitquement démarrée.
        """
        super().__init__(robot, name=name, auto=auto)
        server = http.server.HTTPServer
        self._httpd = server(("", webport), self._getHttpHandler())

    def _getHttpHandler(self):
        """
        Création d'un handler pour le service Web.
        :return: Handler du service HTTP.
        """
        return http.server.SimpleHTTPRequestHandler

    def setup(self):
        """
        Lancement de la boucle d'écoute du serveur Web.
        La boucle d'écoute est lancée par la méthode serve_forever().
        Celle-ci s'effectue une seule fois dans la méthode setup() de la tâche.
        Du coup la boucle loop() de la tâche n'a rien à faire.
        """
        self._httpd.serve_forever()

    def loop(self):
        """
        Par défault, la méthode loop() de la classe de base arrête la tâche
        à la première itération.
        Mais le serveur Web doit continuer à fonctionner jusqu'à ce que la tâche
        soit arrêtée.
        """
        pass

    def stop(self):
        """
        Par défaut, la méthode stop() arrête la boucle sans fin de la tâche.
        Cependant, le serveur Xeb continue à écouter.
        Pour l'arrêter, il faut aussi invoquer la méthode server_close().
        """
        super().stop()
        self._httpd.server_close()


#
#
##############################################################################
class CGIWebServerTask(WebServerTask):
    """
    Cette classe définit un Serveur Web CGI lancé en parallèle pour exposer
    les données collectées par un robot.
    Le serveur Web sert des scripts CGI écrits en Python. Les scripts CGI se
    trouvent dans le même répertoire que le projet.
    """
    DEFAULT_NAME = "RobotWeb"

    def __init__(self, robot, webport=8000, name=DEFAULT_NAME, auto=True):
        """
        Initialisation de la tâche.

        Un serveur Web CGI est instancié.
        :param robot: Robot propriétaire de de la tâche.
        :param webport: Port réseau utilisé par le serveur Web (8000 par défaut)
        :param name: Nom de la tâche ("RobotWeb" par défaut).
        :param auto: Indicateur si la tâche est automaitquement démarrée.
        """
        super().__init__(robot, webport=webport, name=name, auto=auto)

    def _getHttpHandler(self):
        """
        Création d'un handler pour le service Web.
        :return: Handler du service HTTP.
        """
        handler = http.server.CGIHTTPRequestHandler
        handler.cgi_directories = ["/"]
        return handler


#
#
##############################################################################
class ZoneContentTask2(RobotTask):
    """
    Cette classe définit une tâche chargée d'incrémenter la variable globale
    toutes les secondes.
    """
    DEFAULT_NAME = "IncZoneContent"

    def __init__(self, robot, delay=1, name=DEFAULT_NAME):
        """
        Initialisation de la tâche.

        Un serveur Web est instancié.
        Les pages Web doivent se trouver dans le même répertoire que le script
        Python.
        :param robot: Robot propriétaire de de la tâche.
        :param delay: Delais exprimé en secondes entre deux incrémentation
                      (1s par défaut)
        :param name: Nom de la tâche ("IncZoneContent" par défaut).
        """
        super().__init__(robot, name=name)
        self.__zoneContent = 0
        self.__delay = delay
        print(os.environ, file=sys.stderr)


    def loop(self):
        """
        A chaque itération, la variable globale ZONE_CONTENT est incrémentée.
        """
        self.__zoneContent += 1
        os.environ["ZONE_CONTENT"] = str(self.__zoneContent)
        time.sleep(1)
        print("Zone_content =", self.__zoneContent, file=sys.stderr)

class ZoneContentTask(RobotTask):
    """
    Cette classe définit une tâche chargée d'incrémenter la variable globale
    toutes les secondes.
    """
    DEFAULT_NAME = "IncZoneContent"

    def __init__(self, robot, delay=1, name=DEFAULT_NAME):
        """
        Initialisation de la tâche.

        Un serveur Web est instancié.
        Les pages Web doivent se trouver dans le même répertoire que le script
        Python.
        :param robot: Robot propriétaire de de la tâche.
        :param delay: Delais exprimé en secondes entre deux incrémentation
        (1s par défaut)
        :param name: Nom de la tâche ("IncZoneContent" par défaut).
        """
        super().__init__(robot, name=name)
        self.__delay = delay
        self.__zoneContent = 0
        self.__pageWeb = ET.parse("test.html")
        self.__zone = self.__pageWeb.find(".//*[@id='zone']")


    def loop(self):
        """
        A chaque itération, la variable globale ZONE_CONTENT est incrémentée.
        """
        self.__zoneContent += 1
        self.__zone.text = str(self.__zoneContent)
        self.__pageWeb.write("result.html")
        time.sleep(self.__delay)
        print("Zone_content =", self.__zoneContent, file=sys.stderr)

#
#
##############################################################################
if __name__ == '__main__':
    robot = Robot()
    WebServerTask(robot)
    ZoneContentTask2(robot)
    robot.run()
