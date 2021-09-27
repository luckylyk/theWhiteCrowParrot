"""
This module convert an action line to an interpretable job for the Theatre
evalutation. Basically, a job is a function which return the number of frames
it take to be done. Some job returns 0 (eg: variable set, scene changed) but
for instance if a job play an animations, it has to return the animation
length. This duration is needed to inform the theatre that the RUN_MODES can be
set back to RUN_MODES.NORMAL. As long as a job is running, the RUN_MODES is set
to RUN_MODES.SCRIPT which block the gameplay evaluation.
"""

from functools import partial

from corax.core import EVENTS, RUN_MODES
from corax.seeker import find_animated_set, find_player, find_zone

from corax.crackle.parser import (
    object_attribute, string_to_int_list, object_type, object_name)
from corax.crackle.action import (
    has_subject, filter_action, split_with_subject, extract_reach_arguments,
    is_nolock_action)


def create_job(line, theatre):
    nolock = is_nolock_action(line)
    if nolock:
        line = " ".join(line.split(" ")[1:])
    if not has_subject(line):
        result = create_job_without_subject(line, theatre)
    else:
        subject, function, arguments = split_with_subject(line)
        result = create_job_with_subject(subject, function, arguments, theatre)
    if not nolock:
        return result
    return partial(nolock_job, result)


def create_job_without_subject(line, theatre):
    function = filter_action(line)
    if function == "run":
        return partial(job_run_script, theatre, line.split(" ")[-1])
    elif function == "force":
        return partial(job_force_script, theatre, line.split(" ")[-1])
    elif function == "wait":
        return lambda: int(line.split(" ")[-1])
    elif function == "freeze":
        return partial(job_freeze_theatre, theatre, int(int(line.split(" ")[-1])))
    elif function == "flush":
        player_name = object_name(line.split(" ")[-1])
        return partial(job_flush_animation, theatre, player_name)
    elif function == "pin":
        player_name = object_name(line.split(" ")[-1])
        return partial(job_pin_play, theatre, player_name)
    elif function == "restart":
        return partial(job_restart, theatre)


def create_job_with_subject(subject, function, arguments, theatre):
    subject_type = object_type(subject)
    subject_name = object_name(subject)
    if subject_type == "theatre":
        if function == "set":
            if subject_name == "scene":
                return partial(job_set_scene, theatre, arguments)
            elif subject_name == "globals":
                key = object_attribute(subject)
                return partial(job_set_global, theatre, key, arguments)
        elif function == "move":
            if subject_name == "camera":
                position = string_to_int_list(arguments)
                return partial(job_move_camera, theatre, position)
    elif subject_type == "player":
        return create_player_job(theatre, subject_name, function, arguments)
    elif subject_type == "prop":
        if function == "play":
            animation = arguments
            prop = find_animated_set(theatre.scene, subject_name)
            return partial(job_play_animation, prop, animation, type_="prop")
    elif subject_type == "zone":
        zone = find_zone(theatre.scene, subject_name)
        rect = string_to_int_list(arguments)
        return partial(job_shift_zone, zone, rect)


def create_player_job(theatre, player_name, function, arguments):
    player = find_player(theatre, player_name)
    if function == "play":
        anim = arguments
        return partial(job_play_animation, player, anim, type_="player")
    elif function == "show":
        layer = arguments
        return partial(job_switch_layer, player, True, layer)
    elif function == "hide":
        layer = arguments
        return partial(job_switch_layer, player, False, layer)
    elif function == "move":
        position = string_to_int_list(arguments)
        return partial(job_move_player, player, position)
    elif function == "reach":
        pos, animations = extract_reach_arguments(arguments)
        return partial(job_reach, player, pos, animations)
    elif function == "aim":
        direction, move = arguments.split(" by ")
        return partial(job_aim, player, move, direction)
    elif function == "set":
        return partial(job_set_sheet, player, arguments)


def nolock_job(job):
    job()
    return 0


def job_aim(player, move, direction):
    data = player.animation_controller.data
    event = (
        data["moves"][move]["post_events"].get(EVENTS.FLIP) or
        data["moves"][move]["pre_events"].get(EVENTS.FLIP))

    if not event:
        msg = f"{move} has no flip event, can't be used for aim function"
        raise ValueError(msg)
    if (direction == "LEFT") == player.coordinate.flip:
        return 0

    player.animation_controller.set_move(move)
    return player.animation_controller.animation.length


def job_freeze_theatre(theatre, value):
    theatre.freeze += value
    return 1


def job_force_script(theatre, script_name):
    script = [
        script for script in theatre.scripts
        if script.name == script_name][0]
    theatre.run_script(script)
    return 50


def job_flush_animation(theatre, player_name):
    player = find_player(theatre, player_name)
    player.animation_controller.flush()
    return 0


def job_move_camera(theatre, pixel_position):
    theatre.scene.camera.set_center(pixel_position)
    return 0


def job_move_player(player, block_position):
    player.coordinate.block_position = block_position
    return 0


def job_pin_play(theatre, player_name):
    player = find_player(theatre, player_name)
    player.pin()
    return 0


def job_play_animation(animable, animation_name, type_="player"):
    animable.animation_controller.set_move(animation_name)
    return animable.animation_controller.animation.length


def job_reach(player, block_position, animations):
    sequence = player.reach(block_position, animations)
    data = player.animation_controller.data
    key = "frames_per_image"
    return sum(sum(data["moves"][move][key]) for move in sequence)


def job_restart(theatre):
    theatre.run_mode = RUN_MODES.RESTART
    return 0


def job_run_script(theatre, script_name):
    #todo
    return 0


def job_set_global(theatre, key, value):
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    theatre.globals[key] = value
    return 0


def job_set_scene(theatre, scene_name):
    theatre.set_scene(scene_name)
    return 0


def job_set_sheet(player, sheet_name):
    player.set_sheet(sheet_name)
    return 0


def job_shift_zone(zone, rect):
    zone.set_rect(rect)
    return 0


def job_switch_layer(player, state, layer):
    player.set_layer_visible(layer, state)
    return 0
