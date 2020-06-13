#!/usr/bin/env python3
"""
Test des moteurs EV3.

Auteur : André-Pierre LIMOUZIN
Version : 1.0 - 06.2020
"""
from surveyor import RobotSurveyor, SurveyTask
from httpd import WebServerTask
from explorer_tasks import StartStopTask

if __name__ == '__main__':
    robot = RobotSurveyor()
    WebServerTask(robot)
    survey = SurveyTask(robot)
    StartStopTask(robot, survey)
    #IRControlledTankTask(robot)
    #robot.surveyTour()
    robot.run()