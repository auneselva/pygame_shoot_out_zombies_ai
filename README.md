# Shoot out zombies

Simple game made as a uni project with basic AI behaviors implemented (seek, wander, flee, pursuit, flee, evade, hide, avoid round obstacles, avoid walls, group attack) based on Mat Buckland's book "Programming Game AI by Example".

You are steering your rocket. Your task is to shoot out all the enemies represented by red circles. You can also collect coins to gain score. Physical contact with enemies makes you die.

***
RUNNING THE GAME

Double-click on run.py file.

You can also import project to PyCharm IDE. Once your project is open, go to File->Settings->Project->Python Interpreter. You have to set correct Python Interpreter to python 3.9. If you don't have python 3.9 on your computer, you have to first download it from its official website and run. After you set the Python Interpreter, add following modules: pip, pygame and setuptools. Then run the run.py file in the editor.
***

Currently, the behavior of enemies is switching in few seconds long intervals - hiding, fleeing and wandering with avoiding walls and obstacles. You can check how a single behavior works by uncommenting a given line of code from run.py file (lines 68 - 75) and running the game.

by Agnieszka Konopka
