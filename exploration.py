#!/usr/bin/env python3
"""
Test des moteurs EV3.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 11.2019
"""
from robot import Robot, RobotTask
from explorer import RobotExplorer

if __name__ == '__main__':
    robot = RobotExplorer()
    robot.run()

