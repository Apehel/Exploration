# Exploration
Programmation du robot **Explorer**  en langage Python pour le rendre capable d'explorer son environnement et d'en créer la cartographie.

## Sur cette branche Git
Cette branche constitue un fork de la branche initiale pour faire fonctionner le robot, non plus sur la brique Lego EV3, mais sur le contrôleur PiStorms-v2.

L'idée est de profiter des performances du Raspberry Pi très supérieures à celles de la briques EV3, nottament en termes de parallélisme, puisque le Raspberry Pi est doté de quatre coeurs. Ce qui améliore de façon significative le temps de réponse du serveur Web embarqué.

## Description du robot
Le robot **Explorer** est un robot Lego Midstorms EV3. Sa construction, effectuée à partir des briques Lego Mindstorms EV3, est décrite [ici](https://drive.google.com/file/d/1o4Ani40mJifT6TNoeGGL2Pljm8mlWL_S/view).

## Architecture de l'application
L'application **Exploration** comprend quatre parties :
1. Une partie définit la structure physique du robot pour initialiser et configurer les moteurs et les capteurs qui le composent. Elle définit aussi les constantes relatives à la géométrie du robot. 
2. Une autre partie définit les objets métiers relatifs à la cartographie.
3. Une autre partie définit le fonctionnement d'un serveur Web embarqué sur le robot pour exposer la carte de son environnement dans un canvas consultable à distance dans un navigateur Web. L'url à invoquer est http://xxx.xxx.xxx.xxx:8000/map.html, où xxx.xxx.xxx.xxx est l'adresse IP de la brique EV3.
4. Une dernière partie difinit l'IA (le système de décision) qui régit le déplacement dans son environnement pour en effectuer le relevé topographique.  

## Fichiers de l'application
- **exploration.py** - Module principal de l'application.
- **robot.py** - Framework qui définit les classes de bases utilisée pour le robot. Cela permet d'écrire une application propre en objets.
- **explorer.py** - Classe du robot **Explorer**. Cette classe est relative à la partie 1 ci-dessus.
- **surveyor.py** - Cette classe, dérivvée de la précédent, définit l'IA du robot. Cette classe est relative à la partie 4 ci-dessus.
- **survey_model.py** - Ce module définit les classes Python relatives au modèle objet d'une carte telle que relevée par le robot. Il est relatif à la partie 2 ci-dessus.
- **survey_xmlio.py** - Ce module définit les classes destinée à la sérialisation des objets métiers en XML.
- **httpd.py** - Framework qui définit les classes permettant de faire fonctionner un serveur Web dans une tâche parallèle du robot. Il est relatif à la partie 3 ci-dessus.
- **explorer_tasks.py** - Bibliothèques de tâches pouvant être exécutées en parallèle par le robot Explorer.
- **lego.py** - Constantes relatives aux briques Lego.
- **www** - Dossier (relatif à lapartie 3 ci-dessus) contenant le site Web.
  - **map.html** - Page Web à invoquer pour visuliser en temps réel la carte relevée par le robot.
  - **map.xml** - Fichier XML construit dynamiquement au fur et à mesure de l'exploration du robot.
  - **map.css** - Couche présentation du site Web en CSS3.
  - **robot-explorer.model.js** - Modèle objet de la carte en JavaScript.
- **common_apl** - Framework comment à mes applications.
  - **errors.py** - Module pour standardiser le format des exceptions de l'applications.
  - **reflect.py** - Module pour standardiser les introspections reflexives pour la sérialisation des objets métier.
  - **xmlio.py** - Module pour standardiser la sérialisation des objets métiers.