from functools import partial
from corax.scene import find_player
from corax.crackle.parser import object_attribute, string_to_int_list, object_type, object_name
from corax.crackle.action import (
    has_subject, filter_action, split_with_subject, extract_reach_arguments)



def create_job(line, theatre):
    if not has_subject(line):
        function = filter_action(line)
        if function == "run":
            return partial(theatre.run, line.split(" ")[-1])
    subject, function, arguments = split_with_subject(line)
    return create_job_with_subject(subject, function, arguments, theatre)


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
            return partial(job_play_animation, theatre, subject_name, anim)
        if function == "move":
            position = string_to_int_list(arguments)
            return partial(job_move_player, theatre, subject_name, position)
        elif function == "reach":
            pos, animations = extract_reach_arguments(arguments)
            return partial(job_reach, theatre, subject_name, pos, animations)


def iter_on_jobs(jobs):
    for job in jobs:
        frame_count = job()
        while frame_count > 0:
            yield
            frame_count -= 1


def job_set_scene(theatre, scene_name):
    theatre.set_scene(scene_name)
    return 0


def job_set_global(theatre, key, value):
    theatre.globals[key] = value
    return 0


def job_play_animation(theatre, player_name, animation_name):
    player = find_player(theatre.scene, player_name)
    player.movement_manager.set_move(animation_name)
    return player.movement_manager.animation.length


def job_move_player(theatre, player_name, block_position):
    player = find_player(theatre.scene, player_name)
    player.cordinates.block_position = block_position
    return 0


def job_move_camera(theatre, pixel_position):
    theatre.scene.camera.set_center(pixel_position)
    return 0


def job_reach(theatre, player_name, block_position, animations):
    pass

