# creates cfg files for crt-pi
# params are:
# * core (currently, mame2003 or fbalpha)
# * screen width (eg 1920) OR curvature
# * screen height (eg 1080)
# example usage:
# python crt-pi-configs.py mame2003 1920 1080
# python crt-pi-configs.py mame2003 1366 768
# python crt-pi-configs.py mame2003 1280 720
# python crt-pi-configs.py mame2003 1280 1024
# python crt-pi-configs.py mame2003 curvature
# python crt-pi-configs.py fbalpha 1920 1080
# python crt-pi-configs.py fbalpha 1366 768
# python crt-pi-configs.py fbalpha 1280 720
# python crt-pi-configs.py fbalpha 1280 1024
# python crt-pi-configs.py fbalpha curvature
# python crt-pi-configs.py consoles 1920 1080
# python crt-pi-configs.py consoles 1366 768
# python crt-pi-configs.py consoles 1280 720
# python crt-pi-configs.py consoles 1280 1024

import sys
import os
import shutil

console = False
if "mame2003" in sys.argv[1]:
    fileName = "resolution_db/mame2003.txt"
    coreName = "MAME 2003"
    pathName = coreName
elif "fbalpha" in sys.argv[1]:
    fileName = "resolution_db/fbalpha.txt"
    coreName = "FB Alpha"
    pathName = coreName
elif "consoles" in sys.argv[1]:
    fileName = "resolution_db/consoles.txt"
    pathName = "consoles"
    console = True

if "curvature" in sys.argv[2]:
    curvature = True
else:
    curvature = False
    screenWidth = int(sys.argv[2])
    screenHeight = int(sys.argv[3])
    screenAspectRatio = screenWidth/screenHeight
    tolerance = 25

resultionDbFile = open(fileName, "r" )
print('opened file {}'.format(fileName))

for gameInfo in resultionDbFile:
	# strip line breaks
    gameInfo = gameInfo.rstrip()
    
    # parse info
    gameInfo = gameInfo.split(",")
    gameName = gameInfo[0]
    gameOrientation = gameInfo[3]
    gameWidth = int(gameInfo[1])
    gameHeight = int(gameInfo[2])
    aspectRatio = int(gameInfo[9]) / int(gameInfo[10])
    gameType = gameInfo[4]
    #integerWidth = int(gameInfo[7])
    #integerHeight = int(gameInfo[8])

    if console:
        coreName = gameName

    cfgFileName = pathName + '/' + gameName + '.cfg'

    # Create directory for cfgs, if it doesn't already exist
    if not os.path.exists(pathName):
        os.makedirs(pathName)

    # create cfg file
    print('creating {}'.format(cfgFileName))
    newCfgFile = open(cfgFileName, 'w')

    if "V" in gameType:
        # Vector games shouldn't use shaders, so clear it out
        newCfgFile.write("# Auto-generated vector .cfg\n")
        newCfgFile.write("# Place in /opt/retropie/configs/all/retroarch/config/{}/\n".format(coreName))
        newCfgFile.write("video_shader_enable = \"false\"\n")

    else:
        if "V" in gameOrientation:
            if curvature:
                shader = "crt-pi-curvature-vertical.glslp"
            else:
                shader = "crt-pi-vertical.glslp"
            # flip vertical games
            gameWidth = int(gameInfo[2])
            gameHeight = int(gameInfo[1])

        elif "H" in gameOrientation:
            if curvature:
                shader = "crt-pi-curvature.glslp"
            else:
                shader = "crt-pi.glslp"

        newCfgFile.write("# Auto-generated {} .cfg\n".format(shader))
        newCfgFile.write("# Place in /opt/retropie/configs/all/retroarch/config/{}/\n".format(coreName))
        newCfgFile.write("video_shader_enable = \"true\"\n")
        newCfgFile.write("video_shader = \"/opt/retropie/configs/all/retroarch/shaders/{}\"\n".format(shader))

        if not curvature:
            # if not perfectly integer scaled, we will get scaling artefacts, so let's fix that
            if screenAspectRatio > aspectRatio:
                # games with an aspect ratio smaller than your screen should be scaled to fit vertically
                newCfgFile.write("# To avoid horizontal rainbow artefacts, use integer scaling for the width\n")

                # build list of potential aspect ratios with different integer scales
                aspectRatios = []
                for scaleX in range(1, 99):
                    aspectRatios.append((scaleX * gameWidth) / screenHeight)

                # find closest integer scale to desired ratio
                aspectRatios.reverse()
                scaleX = 98-aspectRatios.index(min(aspectRatios, key=lambda x:abs(x-aspectRatio)))

                viewportWidth = int(gameWidth * scaleX)
                if console:
                    # consoles have overscan, so adjust viewportHeight to "Title Safe Area"
                    if "Nestopia" in coreName:
                        overscanV = 8
                    else:
                        overscanV = 0

                    # build list of potential aspect ratios with different integer scales
                    aspectRatios = []
                    for scaleY in range(1, 99):
                        aspectRatios.append(viewportWidth / (scaleY * gameHeight))

                    # find closest integer scale to desired ratio
                    aspectRatios.reverse()
                    scaleY = 98-aspectRatios.index(min(aspectRatios, key=lambda x:abs(x-aspectRatio)))

                    viewportHeight = screenHeight + (overscanV * scaleY)
                else:
                    viewportHeight = screenHeight

                # we prefer it to be wider than narrower, so do that, according to tolerance
                newAspect = viewportWidth / viewportHeight
                if newAspect < aspectRatio:
                    widerAspect = (gameWidth * (scaleX + 1)) / screenHeight
                    if ((widerAspect - aspectRatio)/aspectRatio * 100) <= tolerance:
                        viewportWidth = int(gameWidth * (scaleX + 1))

                # centralise the image
                viewportX = int((screenWidth - viewportWidth) / 2)
                viewportY = int((screenHeight - viewportHeight) / 2)

            else:
                # games with an aspect ratio larger than your screen should be scaled to fit horizontally
                newCfgFile.write("# To avoid horizontal rainbow artefacts, use integer scaling for the height\n")
                
                # build list of potential aspect ratios with different integer scales
                aspectRatios = []
                for scaleX in range(1, 99):
                    aspectRatios.append(screenWidth / (scaleX * gameHeight))

                # find closest integer scale to desired ratio
                aspectRatios.reverse()
                scaleY = 98-aspectRatios.index(min(aspectRatios, key=lambda x:abs(x-aspectRatio)))

                viewportWidth = screenWidth
                viewportHeight = int(gameHeight * scaleY)
                
                # centralise the image
                viewportX = 0
                viewportY = int((screenHeight - viewportHeight) / 2)

            newCfgFile.write("aspect_ratio_index = \"22\"\n")
            newCfgFile.write("custom_viewport_width = \"{}\"\n".format(viewportWidth))
            newCfgFile.write("custom_viewport_height = \"{}\"\n".format(viewportHeight))
            newCfgFile.write("custom_viewport_x = \"{}\"\n".format(viewportX))
            newCfgFile.write("custom_viewport_y = \"{}\"\n".format(viewportY))

    newCfgFile.close()

resultionDbFile.close()

# make zip of configs
if curvature:
    outputFileName = "crt-pi-curvature_" + pathName + "_configs"
else:
    outputFileName = "crt-pi_" + pathName + "_configs_" + str(screenWidth) + "x" + str(screenHeight)
outputFileName = outputFileName.replace(" ", "")
outputFileName = outputFileName.lower()
print('Creating zipfile {}.zip'.format(outputFileName))
shutil.make_archive(outputFileName, 'zip', pathName)