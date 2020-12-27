import pygame
import thorpy
import random
import sys
import math

# my modules
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
        self.n_enemies = 20
        self.n_spawns = 10
        self.obstacles = self.create_obstacles(self.n_obstacles)
        self.enemies = []
        self.enemies = self.create_enemies(self.n_enemies)
        self.spawns = []
        self.spawns = self.create_spawn(self.n_spawns)
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

        if self.player.hp == 0:
            print("Game over")

        self.player.tick()
        for enemy in self.enemies:
            enemy.tick()
        for enemy in self.enemies:
            enemy.change_pos()

        self.time_counter += 1
        if self.time_counter == self.counter_reset:
            self.time_counter = 0
        if self.time_counter % 100 == 0:
            new_sp = self.create_spawn(1).pop(0)
            self.spawns.append(new_sp)
        if self.time_counter % 100 == 50:
            self.spawns.pop(0)
        if self.time_counter % 200 == 30:
            new_en = self.create_enemies(1).pop(0)
            self.enemies.append(new_en)

        # tag those who are close enough to each other to perform a group attack
        self.tag_enemies()

    def draw(self):

        # drawing the player
        self.player.draw()

        # drawing obstacles (circles)
        for v in self.obstacles:
            pygame.draw.circle(self.screen,  (63, 127, 191), (v[1], v[2]), v[0], 3)

        # drawing enemies
        for enemy in self.enemies:
            enemy.draw()

        for spawn in self.spawns:
            pygame.draw.circle(self.screen,  (255, 255, 0), (spawn[1], spawn[2]), spawn[0], 2)

    def create_obstacles(self, n_obstacles):

        # wall_dist is a minimum distance between an obstacle and the walls
        # player_dist is a minimum distance between an obstacle and the starting position of the player

        wall_dist = 50
        player_dist = self.res[0]/20 + 10
        obstacles = []
        r = 40
        dist_other = 70
        empty = []

        for i in range(n_obstacles):

            # randomly setting the size and the position of an obstacle
            pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
            pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            while self.check_collisions(pos_x, pos_y, r + dist_other, obstacles, empty) is True or self.res[0]/2 - player_dist < pos_x < self.res[0]/2 + player_dist and self.res[1]/2 - player_dist < pos_y < self.res[1]/2 + player_dist:
                    pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
                    pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            obstacles.append([r, pos_x, pos_y])

        return obstacles

    def create_enemies(self, n_enemies):

        # wall_dist is a minimum distance between an obstacle and the walls
        # player_dist is a minimum distance between an obstacle and the starting position of the player

        wall_dist = 7
        r = 15
        player_dist = self.res[0]/20 + 10
        enemies = []

        for i in range(n_enemies):

            pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
            pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            while self.check_collisions(pos_x, pos_y, r, self.obstacles, enemies) is True or (self.res[0] / 2 - player_dist < pos_x < self.res[0] / 2 + player_dist and self.res[1] / 2 - player_dist < pos_y < self.res[1] / 2 + player_dist):
                    pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
                    pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            enemies.append(Enemy(self, r, pos_x, pos_y))

        return enemies

    def check_collisions(self, pos_x, pos_y, r, obstacles, enemies):
        for v in obstacles:
            distance = math.sqrt(((v[1] - pos_x) * (v[1] - pos_x)) + ((v[2] - pos_y) * (v[2] - pos_y)))
            if distance < r + v[0]:
                return True
        for enemy in enemies:
            distance = math.sqrt(((enemy.pos.x - pos_x) * (enemy.pos.x - pos_x)) + ((enemy.pos.y - pos_y) * (enemy.pos.y - pos_y)))
            if distance < r + enemy.r:
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

    def create_spawn(self, n_spawns):

        wall_dist = 7
        r = 5
        player_dist = self.res[0] / 20 + 10
        spawns = []

        for i in range(n_spawns):

            pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
            pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            while self.check_collisions(pos_x, pos_y, r, self.obstacles, self.enemies) is True:
                pos_x = random.randint(r + wall_dist, self.res[0] - wall_dist - r)
                pos_y = random.randint(r + wall_dist, self.res[1] - wall_dist - r)

            spawns.append([r, pos_x, pos_y])

        return spawns

if __name__ == "__main__":
    Game()