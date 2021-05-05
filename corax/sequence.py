import copy
import logging
from corax.core import EVENTS
from corax.animation import build_centers_list
from corax.coordinate import flip_position, to_pixel_position, to_block_position, aim_target
from corax.euclide import distance2d
from corax.gamepad import reverse_buttons
from corax.mathutils import sum_num_arrays


def filter_moves_by_inputs(data, input_buffer, flip=False):
    """
    Filter existing moves in spritesheet data comparing the inputs they
    requires to the given input buffer statues.
    """
    moves = []
    for move in data["evaluation_order"]:
        inputs = data["moves"][move]["inputs"]
        inputs = reverse_buttons(inputs) if flip else inputs
        conditions = (
            any(i in input_buffer.pressed_delta() for i in inputs) and
            all(i in input_buffer.inputs() for i in inputs))
        if conditions:
            moves.append(move)
    return moves


def filter_unholdable_moves(data, input_buffer, flip=False):
    """
    Filter existing moves in spritesheet data comparing the inputs they and
    holdable and check if the input required to unhold them fit with the input
    buffer status.
    """
    moves = []
    for move in data["evaluation_order"]:
        if data["moves"][move]["hold"] is False:
            continue
        inputs = data["moves"][move]["inputs"]
        inputs = reverse_buttons(inputs) if flip else inputs
        if any(i in input_buffer.released_delta() for i in inputs):
            moves.append(move)
    return moves


def filter_moves_with_event(moves, data, event):
    return [
        move for move in moves
        if data["moves"][move]["pre_events"].get(event) or
        data["moves"][move]["post_events"].get(event)]


def is_layers_authorized(move, data, layers):
    """
    Verify if current layers match with moves conditions proposed
    """
    sheet_data = data["moves"][move]
    conditions = sheet_data["conditions"]
    if not conditions or not conditions.get("has_layers"):
        return True
    return all(layer in layers for layer in conditions.get("has_layers"))


def is_moves_sequence_valid(move, data, animation):
    """
    Check if the move given is authorized look the move conditions.
    """
    sheet_data = data["moves"][move]
    conditions = sheet_data["conditions"]
    if not conditions:
        return True
    return (
        animation.name in conditions.get("animation_in", []) and
        animation.name not in conditions.get("animation_not_in", []))


def is_move_cross_zone(
        data, move, block_position, flip, zones, image_size):
    """
    Check if the block positions centers are passing across a zone give.
    Its also checking the next animations if the given one is in the middle of
    a sequence.
    """
    sheet_data = data["moves"][move]
    block_positions = []
    while True:
        pre_offset = sheet_data["pre_events"].get(EVENTS.BLOCK_OFFSET)
        post_offset = sheet_data["post_events"].get(EVENTS.BLOCK_OFFSET)
        flip_event = sheet_data["post_events"].get(EVENTS.FLIP)
        flip_event = flip_event or sheet_data["pre_events"].get(EVENTS.FLIP)
        if (not pre_offset and not post_offset) or flip_event:
            # We assume if the first move contains a FLIP event, it will not
            # move in space (even if an offset to compensate the flip is set).
            # By the way, a case where this need to evaluate could happend in
            # the futur but this is a tricky case. The that will not be
            # implemented as far as it is not necessary.
            break
        centers = build_centers_list(sheet_data, image_size, flip)
        block_positions.extend(predict_block_positions(
            centers=centers,
            image_size=image_size,
            block_position=block_position,
            flip=flip,
            pre_offset=pre_offset,
            post_offset=post_offset))

        if pre_offset:
            pre_offset = flip_position(pre_offset) if flip else pre_offset
            block_position = sum_num_arrays(block_position, pre_offset)
        if post_offset:
            post_offset = flip_position(post_offset) if flip else post_offset
            block_position = sum_num_arrays(block_position, post_offset)

        sheet_data = data["moves"][sheet_data["next_move"]]
    return any(z.contains(pos) for z in zones for pos in block_positions)


def predict_block_positions(
        centers,
        image_size,
        block_position,
        flip,
        pre_offset=None,
        post_offset=None):

    if pre_offset:
        pre_offset = flip_position(pre_offset) if flip else pre_offset
        block_position = sum_num_arrays(pre_offset, block_position)

    block_positions = []
    pixel_position = to_pixel_position(block_position)

    for center in centers or []:
        center = sum_num_arrays(center, pixel_position)
        if center == pixel_position:
            continue
        block_positions.append(to_block_position(center))

    if post_offset is not None:
        pixel_offset = to_pixel_position(post_offset)
        pixel_offset = flip_position(pixel_offset) if flip else pixel_offset
        center = sum_num_arrays(pixel_offset, centers[0], pixel_position)
        block_position = to_block_position(center)
        block_positions.append(block_position)

    return block_positions


def build_sequence_to_destination(moves, data, coordinate, dst):
    """
    Produce a movement iterator to reach a block position destination using
    the moves given.
    """
    flippers = filter_moves_with_event(moves, data, EVENTS.FLIP)
    flippers_sanity_check(flippers, moves)
    if coordinate.flip:
        dst = sum_num_arrays(dst, move_offset(flippers[0], data, flip=True))
    if not distance2d(dst, coordinate.block_position):
        return []

    sequence = []
    # Work on a coordinate copy to mock the path will be done.
    coord = copy.deepcopy(coordinate)
    moves = [move for move in moves if move not in flippers]

    # Check if the coordinate are aiming the destination and if not, start the
    # equence with an animation to return the character.
    if not aim_target(coord.block_position, coord.flip, dst):
        coord.flip = not coord.flip
        offset = move_offset(moves[0], data, coord.flip)
        dst = sum_num_arrays(dst, offset)
        coord.block_position = sum_num_arrays(coord.block_position, offset)
        sequence.append(flippers[0])

    for move in moves:
        while True:
            offset = move_offset(move, data, coord.flip)
            block_position = sum_num_arrays(coord.block_position, offset)
            if distance2d(block_position, dst) == 0.0:
                sequence.append(move)
                return sequence
            if not aim_target(block_position, coord.flip, dst):
                break
            sequence.append(move)
            coord.block_position = block_position
            loop_on = data["moves"][move]["loop_on"]
            move = loop_on or move

    logging.debug(
        "Reach: Not able to reach the destination {} "
        "from {}".format(dst, coord.block_position))
    return sequence


def flippers_sanity_check(flippers, moves):
    if not flippers:
        moves = ", ".join(moves)
        message = (
            f"Reach: moves providen ({moves}) has to contain at least "
            "one flip event.")
        raise ValueError(message)
    elif len(flippers) > 1:
        message = (
            f"More than one flipper move found in the list. "
            f"Only the first found {flippers[0]} will be used.")
        logging.debug(message)


def move_offset(move, data, flip=False):
    """
    Compute total offset of a move in a sheet. Adding pre and post block
    offsets.
    """
    pre = data["moves"][move]["pre_events"].get(EVENTS.BLOCK_OFFSET)
    post = data["moves"][move]["post_events"].get(EVENTS.BLOCK_OFFSET)
    offset = sum_num_arrays(pre or [0, 0], post or [0, 0])
    return offset if not flip else flip_position(offset)