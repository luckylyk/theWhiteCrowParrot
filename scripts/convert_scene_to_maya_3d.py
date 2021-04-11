
import os
import json
from maya import cmds
import mtoa.utils as mutils
from PySide2 import QtGui
import corax.context as cctx


WORLDSCALE = 0.1


def create_maya_set(scenefilename, gamepath):
    cmds.file(new=True, force=True)
    cctx.initialize(["", gamepath])
    scenepath = os.path.join(cctx.SCENE_FOLDER, scenefilename)

    with open(scenepath, "r") as f:
        data = json.load(f)

    x_offset = (data["boundary"][2] / 2.0)
    for element in data["elements"]:
        if element["type"] != "set_static":
            continue

        imagepath = os.path.join(cctx.SET_FOLDER, element["file"])
        size = QtGui.QImage(imagepath).size()
        width, height = size.width(), size.height()
        x, y = element["position"]
        plane = cmds.polyPlane(
            subdivisionsX=1,
            subdivisionsY=1,
            width=width,
            height=height)
        cmds.move(
            (x - x_offset),
            (element["deph"] * 50),
            y,
            plane)

        create_texture_shader(imagepath, plane[0])
        cmds.rename(plane[0], element["name"].replace("/", "_"))
    camera = cmds.createNode("camera")
    cmds.move(0, 0, 390, cmds.listRelatives(camera, parent=True))
    cmds.setAttr(camera + ".nearClipPlane", 300)
    cmds.setAttr(camera + ".farClipPlane", 500)
    cmds.setAttr(camera + ".focalLength", 100)
    cmds.setAttr(camera + ".displayCameraFrustum", 1)
    cmds.setAttr(camera + ".displayCameraFarClip", 1)
    cmds.setAttr(camera + ".displayCameraNearClip", 1)
    mutils.createLocator("aiSkyDomeLight", asLight=True)


def create_texture_shader(path, node):
    shadernode = cmds.shadingNode("lambert", asShader=True, name="shader")
    filenode = cmds.shadingNode("file", asTexture=True, name="texture")
    remapnode = cmds.shadingNode("remapColor", asTexture=True, name="remap")
    cmds.setAttr(filenode + ".fileTextureName", path, type="string")
    cmds.setAttr(filenode + ".filterType", 0)
    cmds.connectAttr(filenode + ".outColor", shadernode + ".color")
    cmds.connectAttr(filenode + ".outColor", remapnode + ".color")
    cmds.connectAttr(remapnode + ".outColor", shadernode + ".transparency")
    cmds.setAttr(remapnode + ".red[2].red_FloatValue", 0.0)
    cmds.setAttr(remapnode + ".red[2].red_Position", 0.999)
    cmds.setAttr(remapnode + ".red[2].red_Interp", 1)
    cmds.setAttr(remapnode + ".green[2].green_FloatValue", 0.0)
    cmds.setAttr(remapnode + ".green[2].green_Position", 0.999)
    cmds.setAttr(remapnode + ".green[2].green_Interp", 1)
    cmds.setAttr(remapnode + ".blue[2].blue_FloatValue", 0.0)
    cmds.setAttr(remapnode + ".blue[2].blue_Position", 0.999)
    cmds.setAttr(remapnode + ".blue[2].blue_Interp", 1)
    cmds.select(node)
    cmds.hyperShade(assign=shadernode)

