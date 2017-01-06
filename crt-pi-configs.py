# creates cfg files for crt-pi
# params are:
# * core (currently, mame2003 or fbalpha)
# * screen width (eg 1920)
# * screen height (eg 1080)
# example usage:
# python crt-pi-configs.py mame2003 1920 1080

import sys
import os
import shutil

if "mame2003" in sys.argv[1]:
    fileName = "resolution_db/mame2003.txt"
    coreName = "MAME 2003"
elif "fbalpha" in sys.argv[1]:
    fileName = "resolution_db/fbalpha.txt"
    coreName = "FB Alpha"

screenWidth = int(sys.argv[2])
screenHeight = int(sys.argv[3])

screenAspectRatio = screenWidth/screenHeight

# Create directory for cfgs, if it doesn't already exist
if not os.path.exists(coreName):
    os.makedirs(coreName)

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
    aspectRatio = int(gameInfo[9])/int(gameInfo[10])
    gameType = gameInfo[4]
    integerWidth = int(gameInfo[7])
    integerHeight = int(gameInfo[8])

    cfgFileName = coreName + '/' + gameName + '.cfg'

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
            newCfgFile.write("# Auto-generated crt-pi-vertical.glslp .cfg\n")
            newCfgFile.write("# Place in /opt/retropie/configs/all/retroarch/config/{}/\n".format(coreName))
            newCfgFile.write("video_shader_enable = \"true\"\n")
            newCfgFile.write("video_shader = \"/opt/retropie/configs/all/retroarch/shaders/crt-pi-vertical.glslp\"\n")

        elif "H" in gameOrientation:
            newCfgFile.write("# Auto-generated crt-pi.glslp .cfg\n")
            newCfgFile.write("# Place in /opt/retropie/configs/all/retroarch/config/{}/\n".format(coreName))
            newCfgFile.write("video_shader_enable = \"true\"\n")
            newCfgFile.write("video_shader = \"/opt/retropie/configs/all/retroarch/shaders/crt-pi.glslp\"\n")

        # if not perfectly integer scaled, we will get scaling artefacts, so let's fix that
        aspectRatios = [];
        if screenAspectRatio > aspectRatio:
            # games with an aspect ratio smaller than your screen should be scaled to fit vertically
            newCfgFile.write("# To avoid horizontal rainbow artefacts, use integer scaling for the width\n")
            
            # build list of potential aspect ratios with different integer scales
            for scaleX in range(1, 10):
                aspectRatios.append((scaleX * gameWidth) / screenHeight)

            # find closest integer scale to desired ratio
            scaleX = aspectRatios.index(min(aspectRatios, key=lambda x:abs(x-aspectRatio))) + 1

            viewportWidth = int(gameWidth * scaleX)
            viewportHeight = screenHeight
            
            # centralise the image
            viewportX = int((screenWidth - viewportWidth) / 2)
            viewportY = 0

        else:
            # games with an aspect ratio larger than your screen should be scaled to fit horizontally
            newCfgFile.write("# To avoid horizontal rainbow artefacts, use integer scaling for the height\n")
            
            # build list of potential aspect ratios with different integer scales
            for scaleX in range(1, 15):
                aspectRatios.append(screenWidth / (scaleX * gameHeight))

            # find closest integer scale to desired ratio
            scaleY = aspectRatios.index(min(aspectRatios, key=lambda x:abs(x-aspectRatio))) + 1

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
outputFileName = "crt-pi_" + coreName + "_configs_" + str(screenWidth) + "x" + str(screenHeight)
outputFileName = outputFileName.replace(" ", "")
outputFileName = outputFileName.lower()
print('Creating zipfile {}.zip'.format(outputFileName))
shutil.make_archive(outputFileName, 'zip', coreName)