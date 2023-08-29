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
from corax.iterators import fade, timer
from corax.mathutils import sum_num_arrays
from corax.scene import layover
from corax.screen import map_to_render_area
from corax.seeker import (
    find_animated_set, find_element, find_zone, find_character)

from corax.crackle.action import (
    has_subject, filter_action, split_with_subject, parse_join_arguments,
    parse_reach_arguments, is_nolock_action)
from corax.crackle.collector import value_collector
from corax.crackle.parser import (
    object_attribute, string_to_int_list, object_type, object_name)
from corax.crackle.condition import create_subject_value_collector


def create_job(line, theatre, script):
    nolock = is_nolock_action(line)
    if nolock:
        line = " ".join(line.split(" ")[1:])
    if not has_subject(line):
        result = create_job_without_subject(line, theatre)
    else:
        subject, function, arguments = split_with_subject(line)
        result = create_job_with_subject(
            subject, function, arguments, theatre, script)
    if result is None:
        raise ValueError(f'Impossible to build job from: {line}')
    return partial(nolock_job, result) if nolock else result


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
            frames = int(int(line.split(" ")[-1]))
            return partial(job_freeze_theatre, theatre, frames)
        case "flush":
            player_name = object_name(line.split(" ")[-1])
            return partial(job_flush_animation, theatre, player_name)
        case "hide":
            element = object_name(line.split(" ")[-1])
            show = function == "show"
            return partial(job_switch_visibility, theatre, element, show)
        case "pin":
            player_name = object_name(line.split(" ")[-1])
            return partial(job_pin, theatre, player_name)
        case "restart":
            return partial(job_restart, theatre)
        case "restore":
            return partial(job_restore, theatre)
        case "run":
            return partial(job_run_script, theatre, line.split(" ")[-1])
        case "start":
            timername = object_attribute(line.split(" ")[-1])
            return partial(job_start_timer, theatre, timername)
        case "stop":
            timername = object_attribute(line.split(" ")[-1])
            return partial(job_stop_timer, theatre, timername)
        case "show":
            element = object_name(line.split(" ")[-1])
            show = function == "show"
            return partial(job_switch_visibility, theatre, element, show)
        case "wait":
            return value_collector(int(line.split(" ")[-1]))
    message = f'function "{function}" for implemented for line without subject'
    raise NotImplementedError(message)


def create_job_with_subject(subject, function, arguments, theatre, script):
    subject_type = object_type(subject)
    subject_name = object_name(subject)
    match subject_type:
        case 'locals':
            return create_local_variable_job(
                script, subject_name, function, theatre, arguments)
        case "theatre":
            return create_theatre_job(subject, function, theatre, arguments)
        case "camera":
            if subject_name == "target":
                return partial(job_camera_target, theatre, function, arguments)
        case "player":
            name = subject_name
            return create_character_job(theatre, script, name, function, arguments)
        case "npc":
            name = subject_name
            return create_character_job(theatre, script, name, function, arguments)
        case "prop":
            return create_prop_job(subject_name, function, arguments, theatre)
        case "static":
            return create_static_object_job(
                subject_name, function, arguments, theatre)
        case "zone":
            zone = find_zone(theatre.scene, subject_name)
            rect = string_to_int_list(arguments)
            return partial(job_shift_zone, zone, rect)
    message = f'function "{function}" for implemented for {subject_type}'
    raise NotImplementedError(message)


def create_local_variable_job(
        script, variable_name, function, theatre, arguments):
    match function:
        case "set":
            collector = create_subject_value_collector(arguments, theatre)
            return partial(
                job_set_local_variable, script, variable_name, collector)



def create_theatre_job(subject, function, theatre, arguments):
    subject_name = object_name(subject)
    match function:
        case "set":
            if subject_name == "scene":
                return partial(job_set_scene, theatre, arguments)
            elif subject_name == "globals":
                key = object_attribute(subject)
                return partial(job_set_global, theatre, key, arguments)
        case "move":
            if subject_name == "camera":
                position = string_to_int_list(arguments)
                return partial(job_move_camera, theatre, position)
        case "init":
            subject_attribute = object_attribute(subject)
            event, duration = arguments.split(" by ")
            duration = int(duration)
            name = subject_attribute
            return partial(job_init_timer, theatre, name, event, duration)
    message = f'function "{function}" for implemented for theatre'
    raise NotImplementedError(message)


def create_static_object_job(name, function, arguments, theatre):
    static_object = find_element(theatre.scene, name)
    return create_element_job(static_object, function, arguments, theatre)


def create_prop_job(name, function, arguments, theatre):
    prop = find_animated_set(theatre.scene, name)
    return create_element_job(prop, function, arguments, theatre)


def create_element_job(element, function, arguments, theatre):
    match function:
        case "layover":
            target = object_name(arguments)
            return partial(job_layover, theatre, element.name, target)
        case "play":
            animation = arguments
            return partial(job_play_animation, element, animation)
        case "move":
            return partial(job_move, element, string_to_int_list(arguments))
        case "offset":
            size = element.animation_controller.size
            offset = string_to_int_list(arguments)
            center = element.animation_controller.animation.pixel_center
            return partial(
                job_offset, element.coordinate, offset, center, size)
    message = f'function "{function}" for implemented for prop'
    raise NotImplementedError(message)


def create_character_job(theatre, script, character_name, function, arguments):
    character = find_character(theatre, character_name)
    match function:
        case "aim":
            direction, move = arguments.split(" by ")
            return partial(job_aim, character, move, direction)
        case "hide":
            layer = arguments
            return partial(job_switch_layer, character, False, layer)
        case "join":
            pos, elt, animations = parse_join_arguments(arguments)
            elt = object_name(elt)
            return partial(job_join, theatre, character, elt, pos, animations)
        case "layover":
            target = object_name(arguments)
            return partial(job_layover, theatre, character_name, target)
        case "move":
            position = string_to_int_list(arguments)
            return partial(job_move, character, position)
        case "offset":
            offset = string_to_int_list(arguments)
            return partial(job_offset, character, offset)
        case "play":
            anim = arguments
            return partial(job_play_animation, character, anim)
        case "place":
            prop, offset = arguments.split(" by ")
            prop_name = object_name(prop)
            offset = string_to_int_list(offset)
            return partial(job_place, theatre, character, prop_name, offset)
        case "reach":
            pos, animations = parse_reach_arguments(arguments)
            return partial(job_reach, character, pos, animations)
        case "set":
            return partial(job_set_sheet, script, character, arguments)
        case "show":
            layer = arguments
            return partial(job_switch_layer, character, True, layer)
    message = f'function "{function}" for implemented for character'
    raise NotImplementedError(message)


def create_enable_disable_job(theatre, obj, state):
    type_ = object_type(obj)
    name = object_name(obj)
    match type_:
        case "zone":
            return partial(job_enable_disable_zone, theatre, name, state)
        case "camera":
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
    # Ensure if loopon attribute is set is holdable move, the animation will
    # not loop automatically after aim is played !
    player.animation_controller.unhold([move])
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


def job_join(theatre, character, element_name, block_position, animations):
    element = find_element(theatre.scene, element_name)
    element_block_position = element.coordinate.block_position
    block_position = sum_num_arrays(element_block_position, block_position)
    return job_reach(character, block_position, animations)


def job_init_timer(theatre, name, event, duration):
    theatre.timers[name] = timer(name, event, duration)
    return 0


def job_set_local_variable(script, variable_name, collector):
    print(variable_name, collector())
    print(script.locals)
    script.locals[variable_name] = collector()
    return 0


def job_move_camera(theatre, pixel_position):
    mapped_pixel_position = map_to_render_area(*pixel_position)
    theatre.scene.camera.set_center(mapped_pixel_position)
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


def job_place(theatre, placer, name, offset):
    element = find_element(theatre.scene, name)
    placer.animation_controller.place(element, offset)
    return 0


def job_play_animation(animable, animation_name):
    animable.animation_controller.set_move(animation_name)
    return animable.animation_controller.animation.length


def job_reach(character, block_position, animations):
    sequence = character.reach(block_position, animations)
    data = character.animation_controller.data
    key = "frames_per_image"
    character.animation_controller.animation.hold = False
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


def job_set_sheet(script, player, arguments):
    if arguments.startswith('locals'):
        sheet_name = script.locals[arguments.split('.')[-1]]
    else:
        sheet_name = arguments
    player.set_sheet(sheet_name)
    return 0


def job_shift_zone(zone, rect):
    zone.set_rect(rect)
    return 0


def job_start_timer(theatre, timername):
    theatre.timers[timername].start()
    return 0


def job_stop_timer(theatre, timername):
    del theatre.timers[timername]
    return 0


def job_switch_layer(character, state, layer):
    character.set_layer_visible(layer, state)
    return 0


def job_switch_visibility(theatre, name, visible):
    element = find_element(theatre.scene, name)
    element.visible = visible
    return 0


def job_layover(theatre, element_name, target_name):
    element = find_element(theatre.scene, element_name)
    target = find_element(theatre.scene, target_name)
    layover(theatre.scene.layers, element, target)
    return 0
