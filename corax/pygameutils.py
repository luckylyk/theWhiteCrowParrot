
"""
This module is the bridge to PyGame. It is supposed to be one the rare import
of it. It wrap the pygame functions to make them as much generic as possible
to make a futur engine change easy. It's mainly helper to get and load pygame
object from files.
"""
import pygame
from pygame.locals import QUIT


def escape_in_events(events):
    return any(
        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or
        event.type == QUIT
        for event in events)


def space_in_events(events):
    return any(
        event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
        for event in events)


def tab_in_events(events):
    return any(
        event.type == pygame.KEYDOWN and event.key == pygame.K_TAB
        for event in events)
