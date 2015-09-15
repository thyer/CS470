#!/usr/bin/python -tt

import sys
import random
import time
import math

from bzrc import BZRC, Command


class DumbAgent(object):
    def __init__(self, bzrc):
        self.bzrc = bzrc
        self.commands = []
        self.is_turning = True
        self.angles_are_initialized = False

        self.seconds_since_last_move = 0
        self.seconds_since_last_shot = 0
        self.next_move_target_time = 3
        self.next_shot_target_time = 2

        self.targetAngle = 0
        self.lastAngle = 0
        self.currentAngle = 0
        self.mytanks = []

    def tick(self, time_diff):
        self.seconds_since_last_move += time_diff
        self.seconds_since_last_shot += time_diff
        self.commands = []

        self.mytanks = self.bzrc.get_mytanks()
        current_tank = self.mytanks[0]

        if self.is_turning:
            if not self.angles_are_initialized:
                    self.init_angles(current_tank)

            self.currentAngle = current_tank.angle

            if abs(current_tank.angle - self.targetAngle) < 0.1:
                # Stop turning
                self.is_turning = False
                self.angles_are_initialized = False
                self.seconds_since_last_move = 0
                self.next_move_target_time = random.uniform(3, 8)
                command = Command(current_tank.index, 1, 0, False)

            else:
                # Continue turning
                angvel = self.calculate_angvel()
                command = Command(current_tank.index, 0, angvel, False)

            self.commands.append(command)
            self.lastAngle = self.currentAngle

        elif self.seconds_since_last_move <= self.next_move_target_time:
            # Move forward
            command = Command(current_tank.index, 1, 0, False)
            self.commands.append(command)
        else:
            # Stop moving forward and get ready to turn
            command = Command(current_tank.index, 0, 0, False)
            self.commands.append(command)
            self.is_turning = True

        if self.commands:
            self.bzrc.do_commands(self.commands)

        if self.seconds_since_last_shot > self.next_shot_target_time:
            # Fire off a shot
            self.bzrc.shoot(current_tank.index)
            self.seconds_since_last_shot = 0
            self.next_shot_target_time = random.uniform(1.5, 2.5)


    def init_angles(self, tank):
        self.currentAngle = tank.angle
        self.lastAngle = tank.angle
        self.targetAngle = self.normalize_angle(tank.angle + 1.047)
        self.angles_are_initialized = True

    def calculate_angvel(self):
        target = self.two_pi_normalize(self.targetAngle)
        current = self.two_pi_normalize(self.currentAngle)
        last = self.two_pi_normalize(self.lastAngle)

        return (target - current) - (current - last)

    def normalize_angle(self, angle):
        """Make any angle be between +/- pi."""
        angle -= 2 * math.pi * int (angle / (2 * math.pi))
        if angle <= -math.pi:
            angle += 2 * math.pi
        elif angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def two_pi_normalize(self, angle):
        """Make any angle between 0 to 2pi."""
        angle += 2 * math.pi
        return angle % (2 * math.pi)

def main():
    # Process CLI arguments.
    try:
        execname, host, port = sys.argv
    except ValueError:
        execname = sys.argv[0]
        print >>sys.stderr, '%s: incorrect number of arguments' % execname
        print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
        sys.exit(-1)

    # Connect.
    # bzrc = BZRC(host, int(port), debug=True)
    bzrc = BZRC(host, int(port))

    agent = DumbAgent(bzrc)

    prev_time = time.time()

    # Run the agent
    try:
        while True:
            time_diff = time.time() - prev_time
            prev_time = time.time()
            agent.tick(time_diff)
    except KeyboardInterrupt:
        print "Exiting due to keyboard interrupt."
        bzrc.close()


if __name__ == '__main__':
    main()
