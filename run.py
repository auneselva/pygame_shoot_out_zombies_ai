import pygame
import thorpy
import random
import sys
import math

# my modules
from circle import Circle
from player import Player
from enemy import Enemy


class Game(object):

    def __init__(self):

        pygame.init()
        self.res = (1280, 720)
        self.screen = pygame.display.set_mode(self.res)
        self.tps_max = 100.0
        self.tps_clock = pygame.time.Clock()
        self.tps_delta = 0.0

        self.n_obstacles = 20
        self.blue = (63, 127, 191)
        self.n_enemies = 2
        self.red = (255, 0, 0)
        self.n_spawns = 3
        self.yellow = (255, 255, 0)
        self.obstacles = self.create_objects(Circle, self.n_obstacles, 40, self.blue, [], 50)
        self.enemies = []
        self.enemies = self.create_objects(Enemy, self.n_enemies, 15, self.red, self.obstacles, 5)
        self.spawns = []
        self.spawns = self.create_objects(Circle, self.n_spawns, 8, self.yellow, self.obstacles + self.enemies, 5)

        self.player = Player(self)
        self.leader = self.enemies[0]
        self.counter_reset = 10000
        self.time_counter = 0

        while True:

        # Handle events

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    sys.exit(0)

            # Ticking

            self.tps_delta += self.tps_clock.tick()/1000.0
            while self.tps_delta > 1 / self.tps_max:
                self.tick()
                self.tps_delta -= 1 / self.tps_max

            # Drawing
            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

    def tick(self):

        if not self.enemies:
            print("You won!")
            print("Coins collected: ", self.player.score)
            print("Enemies shot: ", self.player.kills)

        if self.player.hp == 0:
            print("Game over")
            print("Coins collected: ", self.player.score)
            print("Enemies shot: ", self.player.kills)

        self.player.tick()
        for enemy in self.enemies:
            enemy.tick()
        for enemy in self.enemies:
            enemy.change_pos()

        self.time_counter += 1
        if self.time_counter == self.counter_reset:
            self.time_counter = 0
        if self.time_counter % 100 == 0:
            new_sp = self.create_objects(Circle, 1, 8, self.yellow, self.obstacles + self.enemies, 5).pop(0)
            self.spawns.append(new_sp)
        if self.time_counter % 200 == 50:
            self.spawns.pop(0)
        if not self.enemies and self.player.kills < 100:
            self.n_enemies *= 2
            self.enemies = self.create_objects(Enemy, self.n_enemies, 15, self.red, self.obstacles, 5)

        # tag those who are close enough to each other to perform a group attack
        self.tag_enemies()

    def draw(self):

        self.player.draw()
        for obst in self.obstacles:
            obst.draw()
        for enemy in self.enemies:
            enemy.draw()
        for spawn in self.spawns:
            spawn.draw()

    def create_objects(self, obj_type, n_objects, r, color, objects_check_coll, dist):

        # wall_dist is a minimum distance between an obstacle and the walls
        # player_dist is a minimum distance between an obstacle and the starting position of the player
        wall_dist = 20
        player_dist = self.res[0]/20 + 10
        objects = []

        for i in range(n_objects):
            pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
            pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)
            while self.check_collisions(pos_x, pos_y, r + dist, objects_check_coll + objects) is True or self.check_player_dist(player_dist, pos_x, pos_y, r) is True:
                pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
                pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)
            objects.append(obj_type(self, r, pos_x, pos_y, color))

        return objects

    # the method below checks if the object is too close to player's starting position
    def check_player_dist(self, player_dist, pos_x, pos_y, r):
        if self.res[0] / 2 - player_dist < pos_x < self.res[0] / 2 + player_dist:
            if self.res[1] / 2 - player_dist < pos_y < self.res[1] / 2 + player_dist:
                return True
        return False

    def check_collisions(self, pos_x, pos_y, r, circles):
        for circle in circles:
            dx = circle.pos.x - pos_x
            dy = circle.pos.y - pos_y
            distance = math.sqrt((dx * dx) + (dy * dy))
            if distance < r + circle.r:
                return True
        return False

    def tag_enemies(self):

        gathered = []
        circle_r = self.res[0] / 10
        n_min_gath = 7
        for enemy_1 in self.enemies:
            for enemy_2 in self.enemies:
                if enemy_1 is not enemy_2:
                    if (enemy_1.pos - enemy_2.pos).length() < circle_r:
                        gathered.append(enemy_2)
            gathered.append(enemy_1)
            if len(gathered) >= n_min_gath:
                for enemy in gathered:
                    enemy.group_attack = True
                self.leader = gathered[0]
            gathered = []


if __name__ == "__main__":
    Game()