"""A collection of all commands that a hero can use"""

import config
import time
import math
import settings
import utils
from components import Command
from vkeys import press, key_down, key_up


class Move(Command):
    """Moves to a given position using the shortest path based on the current Layout."""

    def __init__(self, x, y, max_steps=15):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        path = config.layout.shortest_path(config.player_pos, self.target)
        # config.path = path.copy()
        # config.path.insert(0, config.player_pos)
        for point in path:
            print("moving")
            counter = self._step(point, counter)

    @utils.run_if_enabled
    def _step(self, target, counter):
        toggle = True
        local_error = utils.distance(config.player_pos, target)
        global_error = utils.distance(config.player_pos, self.target)
        while config.enabled and \
                counter > 0 and \
                local_error > settings.move_tolerance and \
                global_error > settings.move_tolerance:
            if toggle:
                d_x = target[0] - config.player_pos[0]
                if abs(d_x) > settings.move_tolerance / math.sqrt(2):
                    if d_x < 0:
                        Jump('left').main()
                    else:
                        Jump('right').main()
                    counter -= 1
            else:
                d_y = target[1] - config.player_pos[1]
                if abs(d_y) > settings.move_tolerance / math.sqrt(2):
                    if d_y < 0:
                        Jump('up').main()
                    else:
                        Jump('down').main()
                    counter -= 1
            local_error = utils.distance(config.player_pos, target)
            global_error = utils.distance(config.player_pos, self.target)
            toggle = not toggle
        return counter


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        print("adjusting")
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                threshold = settings.adjust_tolerance / math.sqrt(2)
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(0.05)
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance / math.sqrt(2):
                    if d_y < 0:
                        press('w', 1)
                    else:
                        key_down('down')
                        time.sleep(0.05)
                        press('alt', 3, down_time=0.1)
                        key_up('down')
                        time.sleep(0.05)
                    counter -= 1
            error = utils.distance(config.player_pos, self.target)
            toggle = not toggle


class HopAttack(Command):
    """Makes a hop attack using the passed attack button and in certain direction for a certain amount of time."""

    def __init__(self, button, direction, duration):
        super().__init__(locals())
        self.button = button
        self.direction = settings.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        now = time.time()
        print(now)
        key_down(self.direction)

        print(time.time() - now)
        while time.time() - now < self.duration:
            press('alt', 1, up_time=0.6)
            time.sleep(0.06)
            press(self.button, 1, up_time=0.05)

        key_up(self.direction)


class Jump(Command):
    """Performs a flash jump or 'Rope Lift' in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        print("jumping")
        key_down(self.direction)
        if self.direction == 'up':
            key_up(self.direction)
            press('w', 1, up_time=1)
            return

        if self.direction == "down":
            press('alt', 1)
            key_up(self.direction)
            return

        time.sleep(0.1)
        press('alt', 1)
        press('alt', 1)
        key_up(self.direction)
        time.sleep(0.5)


class Buff(Command):
    """Uses buff macro on around 3-minute timer. Use buffs on CD when available."""

    def __init__(self):
        super().__init__(locals())
        self.buff_time = 0
        self.b_s_blade = 0
        self.e_adventurer = 0
        self.c_valhalla = 0
        self.i_combo = 0

    def main(self):
        print("buffing")
        now = time.time()

        # Handle buff macro
        if self.buff_time == 0 or now - self.buff_time > settings.buff_cooldown:
            print("passing buff macro")
            press('lshift', 1, up_time=4)
            self.buff_time = now

        # Handles Burning Soul Blade
        if self.b_s_blade == 0 or now - self.b_s_blade > 120:
            print("passing burning soul")
            press('r', 2)
            self.b_s_blade = now

        # Handles Epic Adventurer
        if self.e_adventurer == 0 or now - self.e_adventurer > 120:
            print("passing epic adventurer")
            press('2', 2)
            self.e_adventurer = now

        # Handles Cry Valhalla
        if self.c_valhalla == 0 or now - self.c_valhalla > 150:
            press('3', 2)
            self.c_valhalla = now

        # Handles Instinctual Combo
        if self.i_combo == 0 or now - self.i_combo > 240:
            press('4', 2)
            self.i_combo = now


class RagingBlows(Command):
    """Attack with Raging Blows."""

    def __init__(self, direction, attacks, repetitions):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)

    def main(self):
        print("attacking with raging blows")
        time.sleep(0.05)
        press(self.direction, 1)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        for _ in range(self.repetitions):
            press('ctrl', self.attacks, up_time=0.15)
        key_up(self.direction)
        if self.attacks > 2:
            time.sleep(0.3)
        else:
            time.sleep(0.2)


class Panic(Command):
    """Attach with Panic"""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        print("Attacking with Panic")
        time.sleep(0.05)
        press(self.direction, 1)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        press('a', 1)
        key_up(self.direction)
        time.sleep(0.2)


class Rupture(Command):
    """Attach with Rupture"""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        print("Attacking with Panic")
        time.sleep(0.05)
        press(self.direction, 1)
        time.sleep(0.05)
        if config.stage_fright and utils.bernoulli(0.7):
            time.sleep(utils.rand_float(0.1, 0.3))
        press('d', 1)
        key_up(self.direction)
        time.sleep(0.2)


class Shout(Command):
    """Attack with Roar."""

    def __init__(self):
        super().__init__(locals())
        self.cd_time = 0

    def main(self):
        print("Attacking with Roar")
        now = time.time()
        if self.cd_time == 0 or now - self.cd_time > 10:
            press('q', 1)
            self.cd_time = now
            time.sleep(1)


class Worldreaver(Command):
    """Attack with Worldreaver."""

    def __init__(self):
        super().__init__(locals())
        self.cd_time = 0

    def main(self):
        print("Attacking with Worldreaver")
        now = time.time()
        if self.cd_time == 0 or now - self.cd_time > 20:
            press('e', 1)
            self.cd_time = now
            time.sleep(1)


class RisingRage(Command):
    """Attack with Rising Rage."""

    def __init__(self):
        super().__init__(locals())
        self.cd_time = 0

    def main(self):
        print("Attacking with Rising Rage")
        now = time.time()
        if self.cd_time == 0 or now - self.cd_time > 10:
            press('f', 1)
            self.cd_time = now
            time.sleep(1)


class SwordIllusion(Command):
    """Attack with Sword Illusion."""

    def __init__(self):
        super().__init__(locals())
        self.cd_time = 0

    def main(self):
        print("Attacking with Sword Illusion")
        now = time.time()
        if self.cd_time == 0 or now - self.cd_time > 30:
            press('t', 1)
            self.cd_time = now
            time.sleep(0.5)
