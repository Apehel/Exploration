# Problèmes rencontrés
Cette version, en cours de développement, n'est pas aboutie.

En effet de nombreux problèmes techniques ont été rencontré quant à l'utilisation de EV3Dev2 sur PiStorms.

## Configuration utilisée pour cette branche

### Matériel
- Raspberry Pi 3B+
- PiStorms-v2 ([mindsensors.com](http://www.mindsensors.com/content/78-pistorms-lego-interface))

### Logiciel 
- Distribution EV3 ([ev3dev.org](https://www.ev3dev.org/downloads/)) : ev3dev-stretch-rpi2-generic-2020-04-10

##  Listes des problèmes 
- Les capteurs ne sont pas reconnus automatiquement. Pas de soucis avec ça. C'est documenté. Mais...
  - La séquence d'initialisation des ports des capteurs, telle que documentée, semble n'être pas toujours nécessaire. La modification de la propriété set_device met souvent le capteur en erreur sans qu'une règle puisse êtr emise en évidence. Par exemple :
    - Pour le capteur **TouchSensor EV3**, la modification de la propriété **set_device** avec **"lego-ev3-touch"** (comme documenté) plante le programme. Le capteur est vu comme étant déconnecté. Sans modifier le paramètre, le capteur est reconnu comme **"lego-ev3-touch"**.
    - Pour les capteurs **InfraredSensor EV3** et **UltrasonicSensor EV3**, la modification de la propriété **set_device** avec respectivement **"lego-ev3-ir"** et **"lego-ev3-us"** semble indispensable, mais pas toujours. Quelque fois, la modification de la propriété **set_device** plante le capteur. Les LED s'éteignent, malgré que le capteur soit vu comme connecté, le capteur renvoyant toujours la même valeur sans rapport avec la mesure effectuée. En revanche, omettre l'initialisation de la propriété lorsque c'est nécessaire voit le capteur comme étant non connecté. Malgré plusieurs solutions capellotractées suggérées dans les forums (en checkant les ports Linusx, par exemple), aucune règle ne permet de définir quand la propriété doit être modifiée. De plus, le programme ayant fonctionné une fois, peut ne pas fonctionner la fois suivante, malgré un reboot du système, puis refonctionner sans reboot.
- Pour les moteurs, ce n'est pas plus brillant. 
  - La modification de la propriété **set_device**, pour les deux moteurs Lego  EV3 **MediumMotor** et **LargeMotor**, avec les paramètres documentés **"lego-ev3-m-motor"** et **"lego-ev3-ml-motor"**, plante le programme. Ceux-ci sont vu comme déconnectés. En revanche, en omettant l'initialisation de la propriété, les deux moteurs sont vu comme **"lego-nxt-motor"**. Lego NXT étant une ancienne version du robot Lego, cela laisse supposer que la bibliothèque Ev3dev2 n'a pas été mise à jour pour la dernière version EV3 qui date pourtant de septembre 2013 alors que la distribution EV3Dev utilisée pour PiStorms est datée d'avril 2020.
  - L'usage des classes **LargeMotor** et **MediumMotor** ne fonctionne pas. Le programme plante en affichant une exception indiquant que les moteurs sont déconnectés. En revanche, en utilisant la classe générique **Motor** cela fonctionne.
  - Les méthodes **on_for_degrees()** et **on_for_rotations()** effectue un angle de rotation aléatoire sans rapport avec les paramètres passés. 
  - L'usage des classes pour les moteurs groupés **MoveTank** et **MoveSteering** déclenche un fonctionnement anarchique des moteurs rendant le robot incontrôlable.
    - Les moteurs se mettent en marche dès l'instanciation des classes. 
    - Les paramètres **speed** de la méthode **on()** déclenche la même vitesse de rotation quelque soit la valeur passée. En revanche, une valeur négative inverse le sens rotation sans pour autant modifier la vitesse de rotation. Une valeur nulle, qui devrait stopper les moteurs, n'a aucun effet.

