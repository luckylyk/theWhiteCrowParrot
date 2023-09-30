
import pygame

import corax.context as cctx
import corax.screen as sctx
from corax.core import COLORS, SHAPE_TYPES, MENU_MODES
from corax.coordinate import to_pixel_position, to_block_position
from corax.gamepad import CONNECT_GAMEPAD_WARNING
from corax.mathutils import sum_num_arrays
from corax.renderengine.io import get_image, NULL_SHADER
from corax.screen import map_to_render_area

from corax.character import CharacterSlot
from corax.graphicelement import SetAnimatedElement, SetStaticElement
from corax.plugin import list_registered_plugin_shape_classes
from corax.particles import ParticlesSystem
from corax.specialeffect import SpecialEffectsEmitter


def draw_image(id_, surface, position, alpha=255):
    image = get_image(id_)
    if alpha == 255:
        surface.blit(image, map_to_render_area(*position))
        return
    # work around to blit with transparency found on here:
    # https://nerdparadise.com/programming/pygameblitopacity
    # thanks dude !
    x, y = position
    w, h = image.get_size()
    temp = pygame.Surface((w, h), pygame.SRCALPHA)
    temp.blit(surface, (-x, -y))
    temp.blit(image, (0, 0))
    temp.set_alpha(alpha)
    surface.blit(temp, map_to_render_area(*position))


def draw_rect(
        surface, color, x, y, width, height, alpha=255, map_to_screen=False):
    if map_to_screen:
        x, y = map_to_render_area(x, y)
    temp = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(temp, color, [0, 0, width, height])
    temp.set_alpha(alpha)
    surface.blit(temp, (x, y))


def draw_background(surface, color=None, alpha=255):
    color = color or COLORS.BLACK
    draw_rect(
        surface=surface,
        color=color,
        x=0,
        y=0,
        width=sctx.SCREEN[0],
        height=sctx.SCREEN[1],
        alpha=alpha)


def draw_ellipse(surface, color, x, y, height, width, map_to_screen=False):
    if map_to_screen:
        x, y = map_to_render_area(x, y)
    pygame.draw.ellipse(surface, color, [x, y, height, width])


def draw_grid(surface, camera, color, alpha=255):
    temp = pygame.Surface(cctx.RESOLUTION, pygame.SRCALPHA)
    # Render grid
    l = map_to_render_area(-camera.pixel_position[0] % cctx.BLOCK_SIZE, 0)[0]
    while l < cctx.RESOLUTION[0]:
        pygame.draw.line(temp, color, (l, 0), (l, sctx.SCREEN[1]))
        l += cctx.BLOCK_SIZE
    t = map_to_render_area(0, 0)[1]
    while t < cctx.RESOLUTION[1]:
        pygame.draw.line(temp, color, (0, t), (sctx.SCREEN[0], t))
        t += cctx.BLOCK_SIZE
    temp.set_alpha(alpha)
    surface.blit(temp, (0, 0))


def draw_text(surface, color, x, y, text, size=15, bold=False):
    font = pygame.font.SysFont('Consolas', size)
    font.bold = bold
    textsurface = font.render(text, False, color)
    surface.blit(textsurface, (x, y))


def draw_centered_text(surface, text, color=None):
    color = color or COLORS.WHITE
    font = pygame.font.SysFont('Consolas', 15)
    text = font.render(text, True, color)
    x, y = sctx.SCREEN
    text_rect = text.get_rect(center=(x / 2, y / 2))
    surface.blit(text, text_rect)


def draw_letterbox(surface):
    if not sctx.USE_LETTERBOX:
        return
    if sctx.TOP_LETTERBOX:
        draw_rect(surface, COLORS.BLACK, *sctx.TOP_LETTERBOX)
    if sctx.BOTTOM_LETTERBOX:
        draw_rect(surface, COLORS.BLACK, *sctx.BOTTOM_LETTERBOX)
    if sctx.LEFT_LETTERBOX:
        draw_rect(surface, COLORS.BLACK, *sctx.LEFT_LETTERBOX)
    if sctx.RIGHT_LETTERBOX:
        draw_rect(surface, COLORS.BLACK, *sctx.RIGHT_LETTERBOX)


def render_menu(menu, surface):
    draw_background(
        surface,
        menu.data["background_color"],
        menu.data["background_alpha"])

    for i, item in enumerate(menu.items):
        key = "text_color" if i != menu.index else "current_text_color"
        draw_text(
            surface=surface,
            color=menu.data[key],
            x=item.position[0],
            y=item.position[1],
            text=item.text,
            bold=(i == menu.index),
            size=menu.data["size"])


def render_particle_system(system, surface, deph, camera):
    deph = deph + system.deph
    position = camera.relative_pixel_position(system.pixel_position, deph)
    if position != system.kept_position:
        system.kept_position = position
    color = system.shape_options["color"]
    for spot in system.spots:
        x = position[0] + spot.pixel_position[0] - system.pixel_position[0]
        y = position[1] + spot.pixel_position[1] - system.pixel_position[1]

        size = system.shape_options["size"]
        if system.shape_options["type"] == SHAPE_TYPES.SQUARE:
            draw_rect(surface, color, x, y, size, size, alpha=system.alpha)
        elif system.shape_options["type"] == SHAPE_TYPES.ELLIPSE:
            draw_ellipse(surface, color, x, y, size, size)


def render_special_effects_emitter(emitter, surface, deph, camera):
    deph = deph + emitter.deph
    alpha = emitter.alpha
    for special_effect in emitter.special_effects:
        position = camera.relative_pixel_position(
            special_effect.pixel_position, deph)
        for image in special_effect.animation.images:
            draw_image(image, surface, position, alpha)


def render_zone(zone, surface, camera):
    world_pos = to_pixel_position([zone.l, zone.t])
    x, y = camera.relative_pixel_position(world_pos)
    x, y = map_to_render_area(x, y)
    w, h = to_pixel_position([zone.width, zone.height])
    draw_rect(surface, (255, 255, 255), x, y, w, h, alpha=25)


def render_character_slot(character, surface, deph, camera):
    character = character.character
    deph = deph + character.deph
    position = camera.relative_pixel_position(character.pixel_position, deph)
    for image in character.animation_controller.images:
        draw_image(image, surface, position)


def render_animated_element(element, surface, deph, camera):
    deph = deph + element.deph
    position = camera.relative_pixel_position(element.pixel_position, deph)
    try:
        for image in element.animation_controller.images:
            draw_image(image, surface, position, element.alpha)
    except TypeError as e:
        print(
            f'Render element: "{element.name}". No image found. Animation '
            f'index is {element.animation_controller.animation.index}. '
            f'Animation is {element.animation_controller.animation.name}.')
        raise TypeError from e


def render_static_element(element, surface, deph, camera):
    deph = deph + element.deph
    position = camera.relative_pixel_position(element.pixel_position, deph)
    draw_image(element.image, surface, position)


def render_plugin_shapes(element, surface, deph, camera):
    totdeph = deph + element.deph
    position = camera.relative_pixel_position(element.pixel_position, totdeph)
    for image in element.images:
        draw_image(image, surface, position)
    if cctx.DEBUG:
        element.render_debug(surface, deph, camera)


def render_layer(layer, surface, camera):
    match = {
        CharacterSlot: render_character_slot,
        ParticlesSystem: render_particle_system,
        SetStaticElement: render_static_element,
        SpecialEffectsEmitter: render_special_effects_emitter,
        SetAnimatedElement: render_animated_element}

    match.update({
        cls: render_plugin_shapes
        for cls in list_registered_plugin_shape_classes()})

    for element in layer.elements:
        if not element.visible:
            continue
        renderer = match[type(element)]
        renderer(element, surface, layer.deph, camera)


def render_scene(scene):
    bg = pygame.Surface(sctx.SCREEN, pygame.SRCALPHA)
    bg.fill(scene.background_color)
    result = [(bg, None)]
    for layer in sorted(scene.layers, key=lambda layer: layer.deph):
        layer_surface = pygame.Surface(sctx.SCREEN, pygame.SRCALPHA)
        layer_surface.convert_alpha()
        render_layer(layer, layer_surface, scene.camera)
        result.append([layer_surface, layer.shader])
    return result


def render_scene_debug_overlay(scene, surface):
    for zone in scene.zones:
        render_zone(zone, surface, scene.camera)

    for slot in scene.player_slots + scene.npc_slots:
        if slot.character is None:
            continue
        render_player_debug(
            player=slot.character,
            deph=0,
            surface=surface,
            camera=scene.camera)


def render_player_debug(player, deph, surface, camera):
    # Render hitmaps

    for name, blocks in player.hitmaps.items():
        color = player.hitmap_colors.get(name)
        if not color:
            continue
        for block in blocks:
            block = sum_num_arrays(block, player.coordinate.block_position)
            position = to_pixel_position(block)
            x, y = camera.relative_pixel_position(position, deph)
            x, y = map_to_render_area(x, y)
            draw_rect(surface, color, x, y, cctx.BLOCK_SIZE, cctx.BLOCK_SIZE, 100)

    if player.name != 'whitecrow':
        return

    draw_grid(surface, camera, (125, 125, 125), alpha=50)
    size = player.animation_controller.size
    # Render coordinates infos on onverlay
    center = player.animation_controller.animation.pixel_center
    position = sum_num_arrays(center, player.pixel_position)
    x, y = camera.relative_pixel_position(position, deph)
    x, y = map_to_render_area(x, y)
    draw_rect(surface, (255, 255, 0), x - 1, y - 1, 2, 2, 255)
    position = to_block_position(position)
    position = to_pixel_position(position)
    x, y = camera.relative_pixel_position(position, deph)
    x, y = map_to_render_area(x, y)
    size = cctx.BLOCK_SIZE
    draw_rect(surface, (150, 150, 255), x, y, size, size, 50)
    pcenter = player.animation_controller.animation.pixel_center
    bcenter = to_block_position(pcenter)
    bcenter = sum_num_arrays(player.coordinate.block_position, bcenter)
    wpcenter = sum_num_arrays(player.coordinate.pixel_position, pcenter)
    text = f"{player.name}"
    x, y = map_to_render_area(5, 0)
    draw_text(surface, (155, 255, 0), x, y, text)
    text = f"    (position: {player.coordinate.block_position})"
    x, y = map_to_render_area(0, 15)
    draw_text(surface, (155, 255, 0), x, y, text)
    pxcenter = player.animation_controller.animation.pixel_center
    text = f"    (center pixel position: {pxcenter})"
    x, y = map_to_render_area(0, 30)
    draw_text(surface, (155, 255, 0), x, y, text)
    text = f"    (center block position: {bcenter})"
    x, y = map_to_render_area(0, 45)
    draw_text(surface, (155, 255, 0), x, y, text)
    text = f"    (global pixel center: {wpcenter})"
    x, y = map_to_render_area(0, 60)
    draw_text(surface, (155, 255, 0), x, y, text)
    text = f"    (sheet name: {player.sheet_name})"
    x, y = map_to_render_area(0, 75)
    draw_text(surface, (155, 255, 0), x, y, text)
    text = f"    (camera center position: {camera.pixel_center})"
    x, y = map_to_render_area(0, 90)
    draw_text(surface, (155, 255, 0), x, y, text)


def render(gameloop, window, events):
    if not gameloop.has_connected_joystick:
        screen = pygame.Surface(sctx.SCREEN, pygame.SRCALPHA)
        draw_centered_text(
            screen,
            CONNECT_GAMEPAD_WARNING,
            COLORS.WHITE)
        return [(screen, NULL_SHADER)]

    theatre = gameloop.theatre
    if not theatre.scene:
        raise RuntimeError("Can't render a theatre with no scene runnging")

    surfaces_and_shaders = render_scene(theatre.scene)
    overlay = pygame.Surface(sctx.SCREEN, flags=pygame.SRCALPHA)
    overlay.convert_alpha()
    if theatre.transition:
        try:
            theatre.alpha = next(theatre.transition)
        except StopIteration:
            theatre.transition = None

    if transition_alpha := 255 - theatre.alpha:
        draw_background(overlay, alpha=transition_alpha)

    if gameloop.menu.mode != MENU_MODES.INACTIVE:
        render_menu(gameloop.menu, overlay)

    draw_letterbox(overlay)
    if cctx.DEBUG:
        render_scene_debug_overlay(theatre.scene, overlay)
    surfaces_and_shaders.append((overlay, NULL_SHADER))
    window.render(surfaces_and_shaders, events)
