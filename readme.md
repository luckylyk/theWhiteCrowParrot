# the White Crow Parrot
###### author : Lionel Brouyère
Open Source action adventure point and click game (in development for a while)
![](https://i.ibb.co/WBpXBsJ/Capture.png)
![](https://i.ibb.co/sF8jD6z/Capture2.png)
![](https://i.ibb.co/fDDpXGj/Capture3.png)

### Corax engine
The Corax engine is a 2d adventure side scroller video game engine. It work with a strict cordinate system based on a grid. The sprites movements are locked on that grid. All the event systems, hitboxes system and animation data are following that grid. However the grid size can be set by project.
- Currently built around PyGame2 framework
- 2d Hand drawn animations gameplay
- Gameplay strictly locked on a grid (eg Prince of Persia)

### Crackle script
Game story scripting is using the engine langage: crackle.  Very basic langage which allow to script action under multiple condition:
```
script go_to_tente_with_sword // script definition
    key UP is pressed // first indent are the conditions
    scene is forest_01 // "and" operator is the one used implicitly
    player whitecrow: sheet is whitecrowparrot_sword.json
    player whitecrow: animation is idle
    player whitecrow: hitbox foot in zone tente
        player whitecrow: play tidy_up_sword // second indent are actions executed
        run go_to_tente // is all conditions are true
```

### SDK
Suite of tools to edit the game data
- kritas_script: some helpers to export animation and set from krita
- Pluck: UI to edit the game data such as levels, scripts and sprites frames data


### Scripts
This is a temporary folder where some scripts to fix data and help development are store. Actually this is litterally a trash bin folder. Just kept for history.
