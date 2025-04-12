# Crackle Script Language.


## Presentation:
This is the Corax Engine event script language.
Don't be scared, it's extremely easy to use. The language rely on indent of
four spaces. It is composed of scripts which are evaluated by the Zones
where it is attached. For instance, a zone named "chest_interaction" has is
defined as "affected by whitecrow", the script will be evaluated when the
zone contains the center of "whitecrow".
The syntax is pretty simple, zero indent is the script declaration level.
Firt indent level is the condition to execute the followings jobs and the
second indent level is the job queue.


## Crackle words:
- **declaration**:
    script, event
- **comparation operator**:
    has, in, is, by, overlaps
- **conditional and time related adverbs/function**:
    always, freeze, nolock, wait
- **functions**:
    aim, checkpoint, clear, fadein, fadeout, flush, force, freeze,
    hide, join, move, pin, play, reach, restart, restore, run, show, set,
    shift, wait, add, remove, raise, offset
- **corax known objects**:
    animation, flip, gamepad, globals, hitmap, key,
    name, player, pressed, scene, sheet, theatre, zone,
    camera, target
- **built-in values**:
    false, true


## Declaration:
This is the header of each script. This define the context, the
namespace and the usage of the script.
- **script**:
A script is composed of tree part: declaration, conditions and jobs.
A script is usually linked to a zone. The zone is checking the
condition if any element center specified in the zone.affect
attribute is inside the zone. If all conditions are true, set the
theatre evaluation as Script (note that this is locking the
gameplay evaluation)
and the script is executed.
    - declaration: `script name`
    - condition: `object operator value`
    - example usage:


```script catch_chain
    gamepad.keys.pressed has X
    player.whitecrow.flip is true
    player.whitecrow.animation is idle
        player.whitecrow reach (19, 6) by (return, step)
        player.whitecrow aim LEFT by return
        player.whitecrow play catch_chain
```

- **concurrent**:
Similar to script, it does not lock the gameplay and several concurrent can be executed at the same time.
- **event**:
The event is quite similare to script but composed by only two
parts: declaration and jobs.
Usually events can be linked to multiple things, it can be
triggered by a collision in a relationship system or by an
event_zone.
    - declaration: `event name`
    - example usage:

```
event asphyxia
    pin player.whitecrow
    flush player.whitecrow
    player.whitecrow.sheet set underwater
    player.whitecrow play asphyxia
    wait 20
    fadeout 30
    wait 2
    restore
```


## Comparator and operators:
- **by**:
    This word split actions arguments for some jobs.
    Actions using the workd `by`: reach, join, aim, place, init
    - Syntax:
        `<subject> <function> <argument1> by <argument2>`
    - Usages:
        `player.whitecrow reach (53, -3) by (return, walk_a, footsie)`
        `player.whitecrow aim LEFT by return`
        `player.whitecrow place prop.ladder by (8, -10)`
        `theatre.timer.asphixia_countdown init underwater.asphyxia by 1000`
- **has**: (script condition only)
    Use to check if array has an element.
    - Syntax:
        `<array> has <element>`
    - Usages:
        - Check key pressed
            `gamepad.keys.pressed has UP`
- **in**: (script condition only)
    Use to check if element is in array.
    - Syntax:
        `<element> in <array>`
    - Usages:
        - A charactor or prop currently playing animation name is in a list of string.
            `prop.blackknight.animation in (idle, hidden, entry, hidden_startup)`
            `npc.jos.animation in (idle, shaking)`
            `player.whitecrow.animation in (crouch_down, crouched_over)`
- **is**: (script condition only)
    This is the equal operator.
    - Syntax:
        `<element> is <value>`
    - Usages:
        - Check Npc, Player, Character or prop coordinate direction.
            `player.whitecrow.flip is false`
        - Check Npc, Player, character or prop current sheet name.
            `player.whitecrow.sheet is exploration`
        - Check Npc, Player, character or prop current animation name.
            `player.whitecrow.animation is idle`
        - Check global variable value.
            `theatre.globals.chest_locked is false`
- **overlaps**: (script condition only)
    This word is used to check if two hitmaps are overlapping.
    - Syntax:
        `<hitmap1> overlaps <hitmap2>`
    - Usages:
        `prop.ladder.hitmap.ground_zone overlaps player.whitecrow.hitmap.leggs`


## Time related words:

- **always**: (script condition only)
    This is used to define that a Script has no condition.
    example:
```
script push_cart
    always
        prop.cart_bg play descent
```
- **freeze**: (action only)
    Function to freeze the game evaluation for a given number of frames.
    - Syntax: `freeze <number>`
- **nolock**: (action only)
    Can be add before each action line to indicate the next action can
    start directly. This is working on every action.
    - Syntax: `noclock <action>`
- **wait**: (action only)
    This is a function to wait a certain number frames before execute next
    action. This is different thant freeze. Freeze is totaly freezing the
    game evaluation. Wait let the game continue around the script.
    - Syntax: `wait <number>`

