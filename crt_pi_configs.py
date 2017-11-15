# creates cfg files for crt-pi
# params are:
# * core (eg mame2003 or fbalpha)
# * screen width (eg 1920) OR curvature
# * screen height (eg 1080)
# example usage:
# python crt_pi_configs.py mame2003 1920 1080
# python crt_pi_configs.py fbalpha 1920 1080
# python crt_pi_configs.py consoles 1920 1080
# python -c "import crt_pi_configs; crt_pi_configs.createZip(False,1920,1080)"

from __future__ import division
import sys
import os
import shutil


def generateConfigs(arg1, arg2, arg3):
    console = False
    if "mame2003" in arg1:
        fileName = "resolution_db/mame2003.txt"
        coreName = "MAME 2003"
    elif "fbalpha" in arg1:
        fileName = "resolution_db/fbalpha.txt"
        coreName = "FB Alpha"
    elif "consoles" in arg1:
        fileName = "resolution_db/consoles.txt"
        # Initialise coreName for consoles to allow log file creation
        coreName = "Consoles"
        console = True

    if "curvature" in arg2:
        curvature = True
    else:
        curvature = False
        screenWidth = int(arg2)
        screenHeight = int(arg3)
        # Tolerance for "scale to fit" in either axis - the unit is the percentage of the game size in that direction.  Default is 25 (i.e. 25%)
        tolerance = 25
        resolution = str(screenWidth) + "x" + str(screenHeight)
        outputLogFile = open(coreName + "-" + resolution + ".csv", "w")
        outputLogFile.write("Tolerance : ,{}\n".format(tolerance))
        outputLogFile.write("ROM Name,X,Y,Orientation,Aspect1,Aspect2,ViewportWidth,ViewportHeight,HorizontalOffset,VerticalOffset,ScaleFactor\n")

    resolutionDbFile = open(fileName, "r" )
    print("Opened database file {}".format(fileName))
    if not curvature:
        print("created log file ./{}".format(outputLogFile.name))
    print("Creating system-specific config files.\n")
    sys.stdout.write('[')
    sys.stdout.flush()
    gameCount = 0

    for gameInfo in resolutionDbFile:
        gameCount = gameCount+1
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

        cfgFileName = gameName + ".cfg"

        # Create directory for cfgs, if it doesn"t already exist
        if curvature:
            path = "curvature" + "/" + coreName
        else:
            path = resolution + "/" + coreName
        if not os.path.isdir(path):
            os.makedirs (path)

        # create cfg file
        if (gameCount%100 == 0):
            sys.stdout.write('.')
            sys.stdout.flush()
        newCfgFile = open(path + "/" + cfgFileName, "w")

        if "V" in gameType:
            # Vector games shouldn"t use shaders, so clear it out
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
                # Calculate pixel 'squareness' and adjust gameHeight figure to keep the same aspect ratio, but with square pixels (keeping Width as-was to avoid scaling artifacts)
                pixelSquareness = ((gameWidth/gameHeight)/aspectRatio)
                gameHeight = int(gameHeight * pixelSquareness)

            elif "H" in gameOrientation:
                if curvature:
                    shader = "crt-pi-curvature.glslp"
                else:
                    shader = "crt-pi.glslp"
                # Calculate pixel 'squareness' and adjust gameWidth figure to keep the same aspect ratio, but with square pixels (keeping Height as-was)
                pixelSquareness = ((gameWidth/gameHeight)/aspectRatio)
                gameWidth = int(gameWidth / pixelSquareness)

            if not curvature:
                # Check scale factor in horizontal and vertical directions
                vScaling = screenHeight/gameHeight
                hScaling = screenWidth/gameWidth
            	
                # Keep whichever scaling factor is smaller. 
                if vScaling < hScaling:
                    scaleFactor = vScaling
                else:
                    scaleFactor = hScaling

                # For vertical format games, width multiplies by an integer scale factor, height can multiply by the actual scale factor.
                if "V" in gameOrientation:
                    # Pick whichever integer scale factor is nearest to the actual scale factor for the width without going outside the screen area
                    if (scaleFactor - int(scaleFactor) > 0.5 and gameWidth * int(scaleFactor + 1) < screenWidth):
                        viewportWidth = gameWidth * int(scaleFactor + 1)
                    else:
                        viewportWidth = gameWidth * int(scaleFactor)
                    viewportHeight = int(gameHeight * scaleFactor)
                    # If, somehow, the viewport height is less than the screen height, but it's within tolerance of the game height, scale to fill the screen vertically 
                    if screenHeight - viewportHeight < (gameHeight * (tolerance / 100)):
                        viewportHeight = screenHeight

                # For horizontal games, scale both axes by the scaling factor.  If the resulting viewport size is within our tolerance for the game height or width, expand it to fill in that direction
                else:
                    viewportWidth = int(gameWidth * scaleFactor)
                    if screenWidth - viewportWidth < (gameWidth * (tolerance / 100)):
                        viewportWidth = screenWidth
                    viewportHeight = int(gameHeight * scaleFactor)
                    if screenHeight - viewportHeight < (gameHeight * (tolerance / 100)):
                        viewportHeight = screenHeight
                    # Add 'overscan' area for Nestopia consoles, as per original script (more or less)
                    if ("console" and "Nestopia" in coreName):
                        viewportHeight = viewportHeight + 8 * int(scaleFactor)
                    
                # centralise the image
                viewportX = int((screenWidth - viewportWidth) / 2)
                viewportY = int((screenHeight - viewportHeight) / 2)
                
                #Write the output file
                newCfgFile.write("# Auto-generated {} .cfg\n".format(shader))
                newCfgFile.write("# Game Title : {} , Width : {}, Height : {}, Aspect : {}:{}, Scale Factor : {}\n".format(gameName, gameWidth, gameHeight, int(gameInfo[9]), int(gameInfo[10]),scaleFactor))
                if not curvature:
                    newCfgFile.write("# Screen Width : {}, Screen Height : {}\n".format(screenWidth, screenHeight))
                newCfgFile.write("# Place in /opt/retropie/configs/all/retroarch/config/{}/\n".format(coreName))

                # Disable shader if the scale is too small
                if scaleFactor >= 3:
                    newCfgFile.write("video_shader_enable = \"true\"\n")
                    newCfgFile.write("video_shader = \"/opt/retropie/configs/all/retroarch/shaders/{}\"\n".format(shader))
                    newCfgFile.write("aspect_ratio_index = \"22\"\n")
                    newCfgFile.write("custom_viewport_width = \"{}\"\n".format(viewportWidth))
                    newCfgFile.write("custom_viewport_height = \"{}\"\n".format(viewportHeight))
                    newCfgFile.write("custom_viewport_x = \"{}\"\n".format(viewportX))
                    newCfgFile.write("custom_viewport_y = \"{}\"\n".format(viewportY))
                else:
                    newCfgFile.write("# Insufficient resolution for good quality shader\n")
                    newCfgFile.write("video_shader_enable = \"false\"\n")
                
                outputLogFile.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(gameInfo[0],gameInfo[1],gameInfo[2],gameInfo[3],gameInfo[9],gameInfo[10],viewportWidth,viewportHeight,viewportX,viewportY,scaleFactor))

        newCfgFile.close()

    resolutionDbFile.close()
    print("]\n")
    print("Done!\n")
    if not curvature:
        outputLogFile.close()
        print("Log written to ./{}  <--Delete if not needed".format(outputLogFile.name))
    print("Files written to ./{}/\nPlease transfer files to /opt/retropie/configs/all/retroarch/config/{}/\n".format(path, coreName))


def createZip(curvature=False, screenWidth=0, screenHeight=0):
    if curvature:
        outputFileName = "crt-pi-curvature_configs"
        path = "curvature"
    else:
        resolution = str(screenWidth) + "x" + str(screenHeight)
        outputFileName = "crt-pi_configs_" + resolution
        path = resolution
    outputFileName = outputFileName.replace(" ", "")
    outputFileName = outputFileName.lower()

    print("Creating zipfile {}".format(outputFileName))
    shutil.make_archive(outputFileName, "zip", path)

    # now delete config dirs
    print("Deleting temp directory: {}".format(path))
    shutil.rmtree(path)


if __name__ == "__main__":
    generateConfigs(sys.argv[1], sys.argv[2], sys.argv[3])
