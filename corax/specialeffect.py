import itertools
from corax.animation import SpriteSheet
from corax.coordinate import Coordinate, flip_position
from corax.core import LOOP_TYPES
from corax.iterators import shuffle
from corax.mathutils import sum_num_arrays


class SpecialEffectsEmitter:
    def __init__(
            self, name, spritesheet_filename, layers, alpha,
            animation_iteration_type, deph, repeat_delay=0, persistents=True):

        self.name = name
        self.deph = deph
        self.alpha = alpha
        self.layers = layers
        self.visible = True

        self.special_effects = []
        self.spritesheet = SpriteSheet.from_filename(
            f'{name}-spritesheet', spritesheet_filename)
        self.repeat_delay = repeat_delay
        self.shoot_cooldown = 0
        self.persistents = persistents

        moves = list(self.spritesheet.moves_data)
        self.animation_iterator = (
            itertools.cycle(moves)
            if animation_iteration_type == LOOP_TYPES.CYCLE else
            shuffle(moves))

    def throw(self, pixel_position, flip=False):
        if self.shoot_cooldown > 0:
            return
        move = next(self.animation_iterator)
        animation = self.spritesheet.build_animation(
            move, flip, self.layers)
        self.special_effects.append(SpecialEffect(animation, pixel_position))
        self.shoot_cooldown = self.repeat_delay

    def throw_from(self, character, pixel_offset):
        animation = character.animation
        flip = character.coordinate.flip
        if flip:
            pixel_offset = flip_position(pixel_offset)
            pixel_offset[0] -= self.spritesheet.size[0]
        pixel_position = sum_num_arrays(pixel_offset, animation.pixel_center)
        pixel_position = sum_num_arrays(character.pixel_position, pixel_position)
        self.throw(pixel_position, flip)

    def evaluate(self):
        if not self.persistents:
            self.special_effects = [
                s for s in self.special_effects if not s.is_done]
        for special_effet in self.special_effects:
            special_effet.evaluate()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


class SpecialEffect:
    def __init__(self, animation, pixel_position):
        self.animation = animation
        self.position = pixel_position
        self.coordinate = Coordinate(pixel_position=pixel_position)

    @property
    def pixel_position(self):
        return self.coordinate.pixel_position

    @property
    def is_done(self):
        return self.animation.is_finished()

    def evaluate(self):
        self.animation.next()