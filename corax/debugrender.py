
import corax.context as cctx
from corax.coordinate import to_block_position, to_pixel_position
from corax.mathutils import sum_num_arrays
from corax.pygameutils import render_rect, render_text, render_grid
from corax.screen import screen_relative_y


def render_player_debug(player, deph, screen, camera):
    render_grid(screen, camera, (125, 125, 125), alpha=50)
    # Render coordinates infos on onverlay
    size = player.animation_controller.size
    center = player.animation_controller.animation.pixel_center
    position = sum_num_arrays(center, player.pixel_position)
    x, y = camera.relative_pixel_position(position, deph)
    y = screen_relative_y(y)
    render_rect(screen, (255, 255, 0), x - 1, y - 1, 2, 2, 255)
    position = to_block_position(position)
    position = to_pixel_position(position)
    x, y = camera.relative_pixel_position(position, deph)
    y = screen_relative_y(y)
    size = cctx.BLOCK_SIZE
    render_rect(screen, (150, 150, 255), x, y, size, size, 50)
    pcenter = player.animation_controller.animation.pixel_center
    bcenter = to_block_position(pcenter)
    bcenter = sum_num_arrays(player.coordinate.block_position, bcenter)
    wpcenter = sum_num_arrays(player.coordinate.pixel_position, pcenter)
    text = f"{player.name}"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(0), text)
    text = f"    (position: {player.coordinate.block_position})"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(15), text)
    pxcenter = player.animation_controller.animation.pixel_center
    text = f"    (center pixel position: {pxcenter})"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(30), text)
    text = f"    (center block position: {bcenter})"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(45), text)
    text = f"    (global pixel center: {wpcenter})"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(60), text)
    text = f"    (sheet name: {player.sheet_name})"
    render_text(screen, (155, 255, 0), 0, screen_relative_y(75), text)

    # Render hitmaps
    for name, blocks in player.hitmaps.items():
        color = player.hitmap_colors.get(name)
        if not color:
            continue
        for block in blocks:
            block = sum_num_arrays(block, player.coordinate.block_position)
            position = to_pixel_position(block)
            x, y = camera.relative_pixel_position(position, deph)
            y = screen_relative_y(y)
            render_rect(screen, color, x, y, size, size, 50)
