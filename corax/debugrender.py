
import corax.context as cctx
from corax.coordinate import to_block_position, to_pixel_position, map_pixel_position
from corax.mathutils import sum_num_arrays
from corax.pygameutils import render_rect, render_text, render_grid


def render_player_debug(player, deph, screen, camera):
    render_grid(screen, camera, (125, 125, 125), alpha=50)

    # Render coordinates infos on onverlay
    size = player.animation_controller.data["frame_size"]
    center = player.animation_controller.animation.pixel_center
    position = sum_num_arrays(center, player.pixel_position)
    x, y = camera.relative_pixel_position(position, deph)
    render_rect(screen, (255, 255, 0), x-1, y-1, 2, 2, 255)
    position = to_block_position(position)
    position = to_pixel_position(position)
    x, y = camera.relative_pixel_position(position, deph)
    size = cctx.BLOCK_SIZE
    render_rect(screen, (150, 150, 255), x, y, size, size, 50)
    pcenter = player.animation_controller.animation.pixel_center
    bcenter = to_block_position(pcenter)
    bcenter = sum_num_arrays(player.coordinate.block_position, bcenter)
    wpcenter = sum_num_arrays(player.coordinate.pixel_position, pcenter)
    text = f"{player.name}"
    render_text(screen, (155, 255, 0), 0, 0, text)
    text = f"    (position: {player.coordinate.block_position})"
    render_text(screen, (155, 255, 0), 0, 15, text)
    text = f"    (center pixel position: {player.animation_controller.animation.pixel_center})"
    render_text(screen, (155, 255, 0), 0, 30, text)
    text = f"    (center block position: {bcenter}"
    render_text(screen, (155, 255, 0), 0, 45, text)
    text = f"    (global pixel center: {wpcenter}"
    render_text(screen, (155, 255, 0), 0, 60, text)

    # Render hitboxes
    for name, blocks in player.hitboxes.items():
        color = player.hitbox_colors.get(name)
        if not color:
            continue
        for block in blocks:
            block = sum_num_arrays(block, player.coordinate.block_position)
            position = to_pixel_position(block)
            x, y = camera.relative_pixel_position(position, deph)
            render_rect(screen, color, x, y, size, size, 50)
