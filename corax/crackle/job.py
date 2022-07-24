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
from corax.iterators import fade
from corax.seeker import (
    find_animated_set, find_element, find_zone, find_character)

from corax.crackle.action import (
    has_subject, filter_action, split_with_subject, extract_reach_arguments,
    is_nolock_action)
from corax.crackle.collector import value_collector
from corax.crackle.parser import (
    object_attribute, string_to_int_list, object_type, object_name)


def create_job(line, theatre):
    nolock = is_nolock_action(line)
    if nolock:
        line = " ".join(line.split(" ")[1:])
    if not has_subject(line):
        result = create_job_without_subject(line, theatre)
    else:
        subject, function, arguments = split_with_subject(line)
        result = create_job_with_subject(subject, function, arguments, theatre)
    if result is None:
        raise ValueError(f'Impossible to build job from: {line}')
    if not nolock:
        return result
    return partial(nolock_job, result)


def create_job_without_subject(line, theatre):
    function = filter_action(line)
    match function:
        case "checkpoint":
            return partial(job_checkpoint, theatre)
        case "clear":
            return partial(job_clear, theatre)
        case "disable":
            obj = line.split(" ")[-1]
            return create_enable_disable_job(theatre, obj, False)
        case "enable":
            obj = line.split(" ")[-1]
            return create_enable_disable_job(theatre, obj, True)
        case "fadein":
            duration = int(line.split(" ")[-1])
            return partial(job_fade, theatre, function == "fadein", duration)
        case "fadeout":
            duration = int(line.split(" ")[-1])
            return partial(job_fade, theatre, function == "fadein", duration)
        case "force":
            return partial(job_force_script, theatre, line.split(" ")[-1])
        case "freeze":
            return partial(
                job_freeze_theatre, theatre, int(int(line.split(" ")[-1])))
        case "flush":
            player_name = object_name(line.split(" ")[-1])
            return partial(job_flush_animation, theatre, player_name)
        case "hide":
            element = object_name(line.split(" ")[-1])
            return partial(
                job_switch_visibility, theatre, element, function == "show")
        case "pin":
            player_name = object_name(line.split(" ")[-1])
            return partial(job_pin, theatre, player_name)
        case "restart":
            return partial(job_restart, theatre)
        case "restore":
            return partial(job_restore, theatre)
        case "run":
            return partial(job_run_script, theatre, line.split(" ")[-1])
        case "show":
            element = object_name(line.split(" ")[-1])
            return partial(
                job_switch_visibility, theatre, element, function == "show")
        case "wait":
            return value_collector(int(line.split(" ")[-1]))


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

    elif subject_type == "camera":
        if subject_name == "target":
            return partial(job_camera_target, theatre, function, arguments)

    elif subject_type in ("player", "npc"):
        return create_character_job(theatre, subject_name, function, arguments)

    elif subject_type == "prop":
        match function:
            case "play":
                animation = arguments
                prop = find_animated_set(theatre.scene, subject_name)
                return partial(job_play_animation, prop, animation)
            case "move":
                prop = find_animated_set(theatre.scene, subject_name)
                return partial(job_move, prop, string_to_int_list(arguments))
            case "offset":
                prop = find_animated_set(theatre.scene, subject_name)
                size = prop.animation_controller.size
                offset = string_to_int_list(arguments)
                center = prop.animation_controller.animation.pixel_center
                return partial(
                    job_offset, prop.coordinate, offset, center, size)

    elif subject_type == "zone":
        zone = find_zone(theatre.scene, subject_name)
        rect = string_to_int_list(arguments)
        return partial(job_shift_zone, zone, rect)


def create_character_job(theatre, character_name, function, arguments):
    character = find_character(theatre, character_name)
    match function:
        case "aim":
            direction, move = arguments.split(" by ")
            return partial(job_aim, character, move, direction)
        case "hide":
            layer = arguments
            return partial(job_switch_layer, character, False, layer)
        case "move":
            position = string_to_int_list(arguments)
            return partial(job_move, character, position)
        case "offset":
            offset = string_to_int_list(arguments)
            return partial(job_offset, character, offset)
        case "play":
            anim = arguments
            return partial(job_play_animation, character, anim)
        case "reach":
            pos, animations = extract_reach_arguments(arguments)
            return partial(job_reach, character, pos, animations)
        case "set":
            return partial(job_set_sheet, character, arguments)
        case "show":
            layer = arguments
            return partial(job_switch_layer, character, True, layer)


def create_enable_disable_job(theatre, obj, state):
    type_ = object_type(obj)
    name = object_name(obj)
    if type_ == "zone":
        return partial(job_enable_disable_zone, theatre, name, state)
    elif type_ == "camera":
        return partial(job_camera_boundaries, theatre, state)


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


def job_camera_boundaries(theatre, state):
    theatre.scene.scrolling.use_soft_boundaries = state
    return 0


def job_camera_target(theatre, function, target):
    target = find_character(theatre, target)
    match function:
        case "add":
            theatre.scene.scrolling.targets.append(target)
        case "remove":
            theatre.scene.scrolling.targets.remove(target)
    return 0


def job_clear(theatre):
    theatre.loaded_scenes.clear()
    return 0


def job_checkpoint(theatre):
    theatre.checkpoint_requested = True
    return 0


def job_enable_disable_zone(theatre, zone, state):
    zone = find_zone(theatre.scene, zone)
    zone.enable = state
    return 0


def job_fade(theatre, reverse=True, duration=10):
    theatre.transition = fade(duration, maximum=255, reverse=reverse)
    return duration - 1


def job_freeze_theatre(theatre, value):
    theatre.freeze += value
    return 1


def job_force_script(theatre, script_name):
    script = [
        script for script in theatre.scripts
        if script.name == script_name][0]
    theatre.run_script(script)
    return 50


def job_flush_animation(theatre, character_name):
    character = find_character(theatre, character_name)
    character.animation_controller.flush()
    return 0


def job_move_camera(theatre, pixel_position):
    theatre.scene.camera.set_center(pixel_position)
    return 0


def job_move(evaluable, block_position):
    evaluable.coordinate.block_position = block_position
    return 0


def job_offset(character, offset):
    character.animation_controller.offset(block_offset=offset)
    return 0


def job_pin(theatre, character_name):
    try:
        character = find_character(theatre, character_name)
        character.pin()
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise Exception from e
    return 0


def job_play_animation(animable, animation_name):
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


def job_restore(theatre):
    theatre.run_mode = RUN_MODES.RESTORE
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


def job_switch_visibility(theatre, name, visible):
    element = find_element(theatre.scene, name)
    element.visible = visible
    return 0
