"""
This module convert an action line to an interpretable job for the Theatre
evalutation. Basically, a job is a function which return the number of frames
it take to be done. Some job returns 0 (eg: variable set, scene changed) but
for instance if a job play an animations, it has to return the animation
length. This duration is needed to inform the theatre that the RUN_MODE can be
set back to RUN_MODE.NORMAL. As long as a job is running, the RUN_MODE is set
to RUN_MODE.SCRIPT which block the gameplay evaluation.
"""

from functools import partial
from corax.scene import find_player, find_animated_set
from corax.crackle.parser import (
    object_attribute, string_to_int_list, object_type, object_name)
from corax.crackle.action import (
    has_subject, filter_action, split_with_subject, extract_reach_arguments,
    is_nolock_action)


SEEKERS = {
    "player": find_player,
    "props": find_animated_set
}


def create_job(line, theatre):
    nolock = is_nolock_action(line)
    if nolock:
        line = " ".join(line.split(" ")[1:])
    if not has_subject(line):
        function = filter_action(line)
        if function == "run":
            result = partial(job_run_script, theatre, line.split(" ")[-1])
        elif function == "force":
            result = partial(job_force_script, theatre, line.split(" ")[-1])
        elif function == "wait":
            result = lambda: int(line.split(" ")[-1])
        elif function == "freeze":
            result = partial(job_freeze_theatre, theatre, int(int(line.split(" ")[-1])))
    else:
        subject, function, arguments = split_with_subject(line)
        result = create_job_with_subject(subject, function, arguments, theatre)
    if not nolock:
        return result
    return partial(nolock_job, result)


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
        if function == "play":
            anim = arguments
            return partial(
                job_play_animation,
                theatre,
                subject_name,
                anim,
                type_=subject_type)
        if function == "move":
            position = string_to_int_list(arguments)
            return partial(job_move_player, theatre, subject_name, position)
        elif function == "reach":
            pos, animations = extract_reach_arguments(arguments)
            return partial(job_reach, theatre, subject_name, pos, animations)
        if function == "set":
            return partial(job_set_movesheet, theatre, subject_name, arguments)
    elif subject_type == "props":
        if function == "play":
            anim = arguments
            return partial(
                job_play_animation,
                theatre,
                subject_name,
                anim,
                type_=subject_type)


def nolock_job(job):
    job()
    return 0


def job_freeze_theatre(theatre, value):
    theatre.freeze += value
    return 1


def job_set_movesheet(theatre, player_name, spritesheet_filename):
    player = find_player(theatre.scene, player_name)
    player.movement_manager.set_spritesheet(spritesheet_filename)
    return 0


def job_force_script(theatre, script_name):
    script = [
        script for script in theatre.scripts
        if script.name == script_name][0]
    theatre.run_script(script)
    return 50


def job_run_script(theatre, script_name):
    #todo
    return 0


def job_set_scene(theatre, scene_name):
    theatre.set_scene(scene_name)
    return 0


def job_set_global(theatre, key, value):
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    theatre.globals[key] = value
    return 0


def job_play_animation(
        theatre, animable_object_name, animation_name, type_="player"):
    animable = SEEKERS[type_](theatre.scene, animable_object_name)
    animable.movement_manager.set_move(animation_name)
    return animable.movement_manager.animation.length


def job_move_player(theatre, player_name, block_position):
    player = find_player(theatre.scene, player_name)
    player.coordinates.block_position = block_position
    return 0


def job_move_camera(theatre, pixel_position):
    theatre.scene.camera.set_center(pixel_position)
    return 0


def job_reach(theatre, player_name, block_position, animations):
    pass #TODO

