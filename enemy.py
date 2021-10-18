import pygame
from pygame.math import Vector2
import math
import random


class Enemy(object):

    def __init__(self, game, r, pos_x, pos_y, color):
        self.game = game
        self.speed = 0.1
        self.max_speed = 1
        self.color = color
        self.pos = Vector2(pos_x, pos_y)
        self.r = r
        self.hp = 100
        self.mass = 3.1415 * r * r
        vel_x = random.randint(-2, 2)
        vel_y = random.randint(-2, 2)
        while vel_x == 0 and vel_y == 0:
            vel_x = random.randint(-2, 2)
            vel_y = random.randint(-2, 2)
        self.vel = Vector2(vel_x, vel_y).normalize()
        self.heading = self.vel

        # Wander
        self.wander_jitter = 0.15
        self.wander_radius = 1
        self.wander_distance = Vector2(self.vel.x * 2, self.vel.y * 2)
        self.wander_target = Vector2(self.vel.x, self.vel.y).normalize()

        # helpers
        self.collided = False
        self.released = True
        self.counter = 0
        self.behavior_counter = 0
        self.another_counter = 0
        self.group_attack = False
        self.n_ticks = 1800
        self.speed = 1.3
        self.coll_normal = Vector2(1, 0)

    def add_force(self, force):
        self.pos += force

    def tick(self):
        if self.behavior_counter > self.n_ticks:
            self.behavior_counter = 0
        self.behavior_counter += 1
        if self.another_counter > (self.n_ticks * 5):
            self.another_counter = 0
        self.another_counter += 1

        # Position, velocity, and acceleration
        if self.vel.x > 0.01 or self.vel.y > 0.01:
            self.heading = self.vel.normalize()

        self.collided = self.collisions()
        # Handling collisions
        if self.collided is False:
            # if there is no collision update velocity according to current behavior set
            self.vel = self.get_vel(self.game.current_behavior)
            self.counter = 0
        else:
            normal = self.coll_normal
            self.vel = self.vel.reflect(normal)
            self.collided = False

        self.vel = self.vel.normalize() * self.speed

    def change_pos(self):
        self.pos += self.vel

    def draw(self):
        pygame.draw.circle(self.game.screen, self.color, (int(self.pos.x), int(self.pos.y)), self.r, 3)

    def get_vel(self, behavior):
        if behavior == 0:
            return (self.seek(self.game.player.pos) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 1:
            return (self.pursuit(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 2:
            return (self.flee(self.game.player.pos) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 3:
            return (self.evade(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 4:
            return (self.wander() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 5:
            return (self.hide() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 6:
            return (self.wander() + 10 * self.avoid_obstacles()).normalize()
        elif behavior == 7:
            return (self.wander() + 10 * self.avoid_walls()).normalize()
        elif behavior == 8:
            if self.group_attack is False:
                if self.behavior_counter < self.n_ticks / 3:
                    return (self.hide() + self.flee(self.game.player.pos) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
                elif self.behavior_counter < self.n_ticks * 2 / 3:
                    return (self.flee(self.game.player.pos) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
                else:
                    return (self.wander() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
            else:
                return (self.seek(self.game.player.pos + (self.game.leader.pos - self.pos)) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 9:
            if self.group_attack is False:
                if self.behavior_counter < self.n_ticks / 3:
                    return (self.evade(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
                elif self.behavior_counter < self.n_ticks * 2 / 3:
                    return (self.wander() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
                else:
                    return (self.pursuit(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
            else:
                return (self.seek(self.game.player.pos + (self.game.leader.pos - self.pos)) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 10:
            if self.another_counter < (self.n_ticks * 2):
                return (self.evade(self.game.player) + 10 * self.avoid_obstacles() + 7 * self.avoid_walls()).normalize()
            elif self.another_counter < (self.n_ticks * 4):
                return (self.wander() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
            else:
                return (self.pursuit(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        elif behavior == 11:
            if self.another_counter < (self.n_ticks * 2):
                return (self.evade(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
            elif self.another_counter < (self.n_ticks * 4):
                return (self.hide() + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
            else:
                return (self.flee(self.game.player) + 10 * self.avoid_obstacles() + 6 * self.avoid_walls()).normalize()
        else:
            return self.vel

    def collisions(self):

        # This method returns True if a collision is detected
        # Returns False if it is not

        # Collisions with walls
        #new_vel = self.vel.angle_to()
        if self.pos.x - self.r < 0:
            self.coll_normal = Vector2(1, 0)
            return True
        elif self.pos.x + self.r > self.game.res[0]:
            self.coll_normal = Vector2(-1, 0)
            return True
        elif self.pos.y - self.r < 0:
            self.coll_normal = Vector2(0, 1)
            return True
        elif self.pos.y + self.r > self.game.res[1]:
            self.coll_normal = Vector2(0, -1)
            return True

        # Collisions with circles [radius, x, y]

        # v[0] - radius
        # v[1] - x
        # v[2] - y

        # p.x - x of the currently checked vertex of the player's triangle
        # p.y - y of the currently checked vertex of the player's triangle

        for obst in self.game.obstacles:
            dx = obst.pos.x - self.pos.x
            dy = obst.pos.y - self.pos.y
            distance = math.sqrt((dx * dx) + (dy * dy))
            if distance < self.r + obst.r:
                self.coll_normal = (self.pos - obst.pos).normalize()
                return True

        # Collisions with other enemies
        for enemy in self.game.enemies:
            dx = enemy.pos.x - self.pos.x
            dy = enemy.pos.y - self.pos.y
            distance = math.sqrt((dx * dx) + (dy * dy))
            if distance < self.r + enemy.r and enemy != self:
                self.coll_normal = (self.pos - enemy.pos).normalize()
                return True

        return False

    def seek(self, target_pos):
        dist = self.pos - target_pos
        desired_vel = dist.normalize() * self.max_speed
        return desired_vel.rotate(180)

    def flee(self, target_pos):
        dist = self.pos - target_pos
        panic_dist = self.game.res[0]/4
        if dist.length() > panic_dist:
            return self.vel

        desired_vel = dist.normalize() * self.max_speed
        return desired_vel

    def pursuit(self, evader):
        to_evader = evader.pos - self.pos
        relative_heading = self.heading.dot(evader.heading)
        if to_evader.dot(self.heading) > 0 and relative_heading < -0.95:
            # acos0.95 = 18 degrees
            return self.seek(evader.pos)
        look_ahead_time = to_evader.length() / self.max_speed + evader.vel.length()
        return self.seek(evader.pos + evader.vel * look_ahead_time)

    def wander(self):
        self.wander_target = Vector2(self.vel.x, self.vel.y).normalize()
        self.wander_target += Vector2(self.random_clamped() * self.wander_jitter, self.random_clamped() * self.wander_jitter)
        self.wander_target.normalize()
        self.wander_target *= self.wander_radius
        if self.wander_target.length() == 0:
            self.wander_target = self.vel
        self.wander_target.normalize()
        return self.wander_target

    def random_clamped(self):
        return random.uniform(-1, 1)

    def evade(self, pursuer):
        to_pursuer = pursuer.pos - self.pos
        look_ahead_time = to_pursuer.length() / (self.max_speed + pursuer.vel.length())
        return self.flee(pursuer.pos + pursuer.vel * look_ahead_time)

    def avoid_obstacles(self):
        space = 20
        ext_rad = self.r + space
        # Detection box
        angle = self.vel.angle_to(Vector2(1, 0))
        p1 = self.pos + Vector2(0, ext_rad)
        #p2 = self.pos + Vector2(0, -ext_rad)
        p3 = self.pos + Vector2(self.vel.length() * 70, ext_rad)
        #p4 = self.pos + Vector2(self.vel.length() * 70, -ext_rad)
        colliding = []

        for obst in self.game.obstacles:

            # v[0] is radius of an obstacle
            # v[1] is pos_x
            # v[2] is pos_y

            # changing coordinates of the obstacle to local position in relation to our player
            vec_to_obst = Vector2(obst.pos.x, obst.pos.y) - self.pos
            rel_pos_obst = self.pos + vec_to_obst.rotate(angle)
            if rel_pos_obst.x + obst.r > p1.x:
                if rel_pos_obst.x - obst.r < p3.x:
                    if math.fabs(rel_pos_obst.y - self.pos.y) < obst.r + ext_rad:
                        colliding.append((obst.r, obst.pos.x, obst.pos.y))
            #elif (p3 - (rel_pos_obst.x, rel_pos_obst.y)).length() < v[0]:
            #    colliding.append((v[0], rel_pos_obst.x, rel_pos_obst.y))
            #elif (p4 - (rel_pos_obst.x, rel_pos_obst.y)).length() < v[0]:
            #    colliding.append((v[0], rel_pos_obst.x, rel_pos_obst.y))

        # avoiding collision with other enemies
        for enemy in self.game.enemies:

            # v[0] is radius of an obstacle
            # v[1] is pos_x
            # v[2] is pos_y

            # changing coordinates of the obstacle to local position in relation to our player
            if enemy != self:
                vec_to_obst = Vector2(enemy.pos.x, enemy.pos.y) - self.pos
                rel_pos_obst = self.pos + vec_to_obst.rotate(angle)
                if rel_pos_obst.x + enemy.r > p1.x:
                    if rel_pos_obst.x - enemy.r < p3.x:
                        if math.fabs(rel_pos_obst.y - self.pos.y) < enemy.r + ext_rad:
                            colliding.append((enemy.r, enemy.pos.x, enemy.pos.y))

        if not colliding:
            return self.vel

        # calculating the closest intersection point

        inters_pt = p3.x
        go_down = False
        for obst in colliding:
            z = obst[0] + ext_rad
            y = obst[2] - self.pos.y
            x = math.sqrt(math.fabs(z * z - y * y))

            # if the closest point is to the rear of the vehicle we discard it
            if obst[1] - x > self.pos.x:
                closest_x = obst[1] - x
                if closest_x < inters_pt:
                    inters_pt = closest_x
                    if obst[2] < self.pos.y:
                        go_down = True

        dist = inters_pt - self.pos.x
        coeff = 0.8
        if go_down is True:
            lateral_force = Vector2(0, 1/dist * coeff)
        else:
            lateral_force = Vector2(0, -1/dist * coeff)

        colliding.clear()
        return (lateral_force + self.vel.rotate(angle)).normalize().rotate(-angle)

    def avoid_walls(self):
        dist = self.r + 40
        space = self.r + 10
        x_predict = self.vel.x * dist
        y_predict = self.vel.y * dist
        net_force = Vector2(0.0, 0.0)
        angle = 30
        walls = 0
        # left wall
        if self.pos.x + x_predict < space:
            walls += 1
            # going down
            if self.vel.y > 0:
                net_force += (self.vel + self.vel.rotate(-angle))
            # going up
            else:
                net_force += (self.vel + self.vel.rotate(angle))
        # right wall
        elif self.pos.x + x_predict > self.game.res[0] - space:
            walls += 1
            # going down
            if self.vel.y > 0:
                net_force += (self.vel + self.vel.rotate(angle))
            # going up
            else:
                net_force += (self.vel + self.vel.rotate(-angle))
        # upper wall
        if self.pos.y + y_predict < space:
            walls += 1
            # going right
            if self.vel.x > 0:
                net_force += (self.vel + self.vel.rotate(angle))
            # going left
            else:
                net_force += (self.vel + self.vel.rotate(-angle))
        # bottom wall
        elif self.pos.y + y_predict > self.game.res[1] - space:
            walls += 1
            # going right
            if self.vel.x > 0:
                net_force += (self.vel + self.vel.rotate(-angle))
            # going left
            else:
                net_force += (self.vel + self.vel.rotate(angle))
        # if an enemy approaches a corner
        if walls > 1:
            net_force = net_force.rotate(180)
        if net_force.length() > 0.001:
            net_force.normalize()
        return net_force

    def hide(self):

        # getting hiding positions
        hiding_pos = []
        space_dist = 20
        for obst in self.game.obstacles:
            vec_to_obst = (obst.pos - self.pos).normalize()
            hiding_pos.append(vec_to_obst * (space_dist + obst.r) + obst.pos)

        if not hiding_pos:
            return self.evade(self)

        closest = self.game.res[1]
        best_hiding_spot = hiding_pos[0]

        for v in hiding_pos:
            xd = self.pos.x - v.x
            yd = self.pos.y - v.y
            dist = math.sqrt(xd * xd + yd * yd)
            if closest > dist:
                closest = dist
                best_hiding_spot = v

        return self.seek(best_hiding_spot)
