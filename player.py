import pygame
from pygame.math import Vector2
import math

class Player(object):

    def __init__(self, game):
        self.game = game
        self.speed = 0.1
        size = self.game.screen.get_size()

        self.pos = Vector2(size[0]/2, size[1]/2)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.heading = self.vel

        self.starting_pos_points = [Vector2(0, 10), Vector2(5, -5), Vector2(-5, -5)]

        self.pos_points = self.starting_pos_points
        # let's assume mass is equal to the size
        self.mass = 75

        self.hp = 100
        self.score = 0
        self.flag = False
        self.counter = 0
        self.draw_counter = 0
        self.btn_released = True
        self.btn_was_released = True
        self.dont_remove = False
        self.closest_shot_point = Vector2(0, 0)
        self.gun_counter = 0

    def add_force(self, force):

        # Changing acceleration in reaction to force
        self.acc += force

    def tick(self):
        # Handling pressed keys
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.add_force(Vector2(0, -self.speed))
        if pressed[pygame.K_s]:
            self.add_force(Vector2(0, self.speed))
        if pressed[pygame.K_a]:
            self.add_force(Vector2(-self.speed, 0))
        if pressed[pygame.K_d]:
            self.add_force(Vector2(self.speed, 0))

        # handling shooting
        self.shooter_handle()

        # Physics
        # Air resistance
        self.acc *= 0.8
        self.vel *= 0.965
        mouse_pos = pygame.mouse.get_pos()
        self.heading = (mouse_pos - self.pos).normalize()
        # Position, velocity, and acceleration
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        # Handling collisions

        if self.flag is False:
            self.flag = self.collisions()
            self.counter = 0
        else:
            if self.counter == 0:
                # bouncing off the obstacles
                if self.vel.length() != 0:
                    self.pos = self.pos - 3 * self.vel.normalize()
                self.vel = -self.vel
            self.counter += 1
            if self.counter == 12:
                self.flag = False
                self.counter = 0

        # Physical contact with an enemy causes player's health decrease
        if self.getting_physical(self.game.enemies) is True:
            self.hp -= 1
        if self.getting_spawns(self.game.spawns) is True:
            self.score += 1

    def draw(self):

        # rotating the player to his heading direction
        angle = Vector2(0, 1).angle_to(self.heading)
        self.pos_points = [p.rotate(angle) for p in self.starting_pos_points]
        self.pos_points = [self.pos + p for p in self.pos_points]
        pygame.draw.polygon(self.game.screen, (191, 191, 0), self.pos_points)

        # drawing shooting line
        m_btn = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if m_btn[0] == 0:
            self.btn_released = True
            self.gun_counter = 0
        if m_btn[0] == 1 and self.btn_released is True:
            self.btn_released = False
            self.gun_counter = 0
        if m_btn[0] == 1 and self.btn_released is False:
            if self.gun_counter != 25:
                intersecting_pt = self.hindsight()
                pygame.draw.line(self.game.screen, (0, 128, 0), self.pos, intersecting_pt, 2)
                self.gun_counter += 1


    def collisions(self):

        # Returns True if a collision is detected
        # Returns False otherwise

        # Collisions with walls
        for p in self.pos_points:
            if p[0] < 0:
                return True
            elif p[0] > self.game.res[0]:
                return True
            elif p[1] < 0:
                return True
            elif p[1] > self.game.res[1]:
                return True

        # Collisions with objects [radius, x, y]
        # v[0] - radius
        # v[1] - x
        # v[2] - y
        # p.x - x of the currently checked vertex of the player's triangle
        # p.y - y of the currently checked vertex of the player's triangle
        for v in self.game.obstacles:
            for p in self.pos_points:
                if abs(v[1] - p.x) < v[0]:
                    y = math.sqrt(abs(v[0] * v[0] - (v[1] - p.x) * (v[1] - p.x)))
                    if y > abs(p.y - v[2]):
                        return True

        return False

    def getting_physical(self, objects):

        # if an enemy overlaps the player, the player's health gets lower
        for v in objects:
            for p in self.pos_points:
                if abs(v.pos.x - p.x) < v.r:
                    y = math.sqrt(abs(v.r * v.r - (v.pos.x - p.x) * (v.pos.x - p.x)))
                    if y > abs(p.y - v.pos.y):
                        return True
        return False

    def getting_spawns(self, spawns):

        # if an enemy overlaps the player, the player's health gets lower
        for v in spawns:
            for p in self.pos_points:
                if abs(v[1] - p.x) < v[0]:
                    y = math.sqrt(abs(v[0] * v[0] - (v[1] - p.x) * (v[1] - p.x)))
                    if y > abs(p.y - v[2]):
                        self.game.spawns.remove(v)
                        return True
        return False

    def shooter_handle(self):

        m_btn = pygame.mouse.get_pressed()
        if m_btn[0] == 0 and self.btn_was_released is False:
            self.btn_was_released = True
        if m_btn[0] == 1 and self.btn_was_released is True:
            click_pos = Vector2(pygame.mouse.get_pos())
            for enemy in self.game.enemies:
                # if we clicked the point within the circle of an enemy
                if (click_pos - enemy.pos).length() < enemy.r:
                    # checking if the shooting line passes through any obstacle
                    # dist = (Axr + Byr + C) / sqrt(A * A  + B * B) must > radius of every obstacle
                    p1 = self.pos
                    p2 = click_pos
                    A = p2.y - p1.y
                    B = p1.x - p2.x
                    C = p2.x * p1.y - p1.x * p2.y
                    under = math.sqrt(A * A + B * B)
                    if under != 0:
                        for obst in self.game.obstacles:
                            if self.in_range(obst, self.pos, click_pos) is True:
                                dist = math.fabs(A * obst[1] + B * obst[2] + C) / under
                                if dist < obst[0]:
                                    self.dont_remove = True
                                    break
                        if self.dont_remove is False:
                            self.game.enemies.remove(enemy)
                        else:
                            self.dont_remove = False
                    break
            self.btn_was_released = False

    # The method below checks if there's an obstacle between the player's position and
    # position of the mouse when the player clicked

    def in_range(self, obst, my_pos, click_pos):
        if my_pos.y > click_pos.y:
            if (obst[2] - obst[0] > my_pos.y) or (obst[2] + obst[0] < click_pos.y):
                return False
            if my_pos.x > click_pos.x:
                if (obst[1] - obst[0] > my_pos.x) or (obst[1] + obst[0] < click_pos.x):
                    return False
            else:
                if (obst[1] + obst[0] < my_pos.x) or (obst[1] - obst[0] > click_pos.x):
                    return False
        else:
            if (obst[2] + obst[0] < my_pos.y) or (obst[2] - obst[0] > click_pos.y):
                return False
            if my_pos.x > click_pos.x:
                if (obst[1] - obst[0] > my_pos.x) or (obst[1] + obst[0] < click_pos.x):
                    return False
            else:
                if (obst[1] + obst[0] < my_pos.x) or (obst[1] - obst[0] > click_pos.x):
                    return False
        return True

    # Returns the x coord of the closest point intersecting with the line
    # in cartesian way
    # doesn't seem to work properly

    def closest_pt_cart(self, D, E, F, r, pos_x, pos_y):

        # Ax + By + C = 0
        # (x - pos_x) * (x - pos_x) + (y - pos_y) * (y - pos_y) = r * r

        # y = (- C - A * x) / B
        # (x - pos_x) * (x - pos_x) + ((- C - A * x) / B - pos_y) * ((- C - A * x) / B - pos_y) = r * r
        # x * x - 2 * x * pos_x + pos_x * pos_x +
        # + ((C * C + 2 * C * A * x) / B * B + 2 * pos_y * (C + Ax) / B + pos_y * pos_y - r * r = 0
        # (1 + A * A / (B * B)) x * x  + ( - 2 * pos_x + 2 * C * A / B + 2 * pos_y * A / B) x +
        # + pos_x * pos_x - r * r + (C / B + pos_y * pos_y)^2 = 0

        a = 1 + D * D / (E * E)
        b = 2 * (-pos_x + D / E * (F + pos_y))
        c = pos_x * pos_x - r * r + (F / (E * E) + pos_y * pos_y) * (F / (E * E) + pos_y * pos_y)
        delta = b * b - 4 * a * c

        if delta == 0:
            x1 = -b / (2 * a)
            return x1
        elif delta < 0:
            return None
        else:
            x1 = (-b + math.sqrt(delta)) / (2 * a)
            x2 = (-b - math.sqrt(delta)) / (2 * a)
            if self.pos.x > x1:
                if x1 > x2:
                    return x1
                else:
                    return x2
            else:
                if x1 > x2:
                    return x2
                else:
                    return x1

    # Returns the x coord of the closest point intersecting with the line
    # using vectors

    def closest_pt_vec(self, p1, p2, r, pos_x, pos_y):

        line_vec = p2 - p1
        circle_pos = Vector2(pos_x, pos_y)

        a = line_vec.dot(line_vec)
        b = 2 * line_vec.dot(p1 - circle_pos)
        c = p1.dot(p1) + circle_pos.dot(circle_pos) - 2 * p1.dot(circle_pos) - r ** 2
        delta = b * b - 4 * a * c

        if delta < 0:
            return None
        elif delta == 0:
            t1 = -b / (2 * a)
            if 0 <= t1 <= 1:
                return p1 + t1 * line_vec
            else:
                return None
        else:
            t1 = (-b + math.sqrt(delta)) / (2 * a)
            t2 = (-b - math.sqrt(delta)) / (2 * a)

            if not (0 <= t1 <= 1):
                if not (0 <= t2 <= 1):
                    return None
                return p1 + t2 * line_vec
            if not (0 <= t2 <= 1):
                if not (0 <= t1 <= 1):
                    return None
                return p1 + t1 * line_vec

            if t1 < t2:
                return p1 + t1 * line_vec
            else:
                return p1 + t2 * line_vec

    def hindsight(self):
        mouse_pos = Vector2(pygame.mouse.get_pos())
        p1 = self.pos
        p2 = mouse_pos
        closest_pt = mouse_pos

        for obst in self.game.obstacles:
            if self.in_range(obst, self.pos, mouse_pos) is True:
                pt = self.closest_pt_vec(p1, p2, obst[0], obst[1], obst[2])
                if pt is not None:
                    if (self.pos - pt).length() < (self.pos - closest_pt).length():
                        closest_pt = pt
        return closest_pt

    def find_y(self, p1, p2, x3):
        a = (p2.y - p1.y)/(p2.x - p1.x)
        b = p1.y - a * p1.x
        y3 = a * x3 + b
        return y3

