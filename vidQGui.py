#!/usr/bin/env python3
import os
import PySimpleGUI as sg
import vidq
import subprocess
import ffmpeg
import datetime
import tempfile
from pathlib import Path
from pprint import pprint

#Generate a tmp dir for intermediary work on vids
tmpDir = tempfile.TemporaryDirectory()


#Function defs
def genVidRow(vid):
    #Takes a vid object
    return [[sg.Frame(title = vid.inputPath, layout = [[sg.Input(vid.title, k=f'-{vid.UUID}title-')],[sg.Input(vid.artist, k=f'-{vid.UUID}artist-')],[sg.T(f'Volume: {vid.volume}')],[sg.T(f'Resolution: {vid.xres}x{vid.yres}')],[sg.T(f'PixelFormat: {vid.pixelFormat}')],[sg.T(f'Framerate: {vid.avgFramerate}')]])]]


#def resizeVid(vid):
#    (ffmpeg .input

#def applyOverlay(vid):
#    (ffmpeg
#            .input(vid.path)
#            .

# Apply Title and Artist overlay
# ffmpeg -i $vidfile -vf "drawtext=tex,tfile=metadata.txt:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:fontsize=50:y=h-line_h-200:x=50:font=sans" $outputvid



# Define the window's contents
layout = [
        [sg.T('BETA SOFTWARE - This software incomplete and only suitible for basic testing at this time.', text_color='red',background_color='black')],
        [sg.Input(visible=False, enable_events=True, key='-IN-'), sg.FilesBrowse('Queue Videos')],
        [sg.Frame('Queued Videos', layout = [], k='-VIDFRAME-')],
        [sg.B('Export', k='-EXPORT-')],
        [sg.T(f'Exporting to:  {vidq.getOutputPath()}')],
        [sg.Button('Quit')]
]

# Create the window
window = sg.Window('Window Title', layout)

# Display and interact with the Window using an Event Loop
vidQueue = []
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break
    # Output a message to the window
    if event == '-IN-':
        for file in values['-IN-'].split(';'):
            newVid = vidq.vidMeta(inputPath=file, tmpDirPath=tmpDir.name)
            vidQueue.append(newVid)
            window.extend_layout(window['-VIDFRAME-'], genVidRow(newVid))
    if event == '-EXPORT-':
        #Sort and set upNext attr
        vidQueue.sort(key=lambda vid: vid.volume, reverse=False)
        for vid in vidQueue:
           vid.title = values[f'-{vid.UUID}title-']
           vid.artist = values[f'-{vid.UUID}artist-']
        for vid in vidQueue:
            nextKey = vidQueue.index(vid)+1
            if vid == vidQueue[-1]:
                vid.UpNext = None
            else:
                vid.upNext = vidQueue[nextKey].title + " by " + vidQueue[nextKey].artist
        for vid in vidQueue:
            vidq.prepVid(vid)

        vidq.concatVids(vidQueue)
        #window.extend_layout(window['-VIDFRAME-'], [[sg.Input(result)]])
            #vidq.resize(vid)




# Finish up by removing from the screen
window.close()


#############################
# NOTES
#
# Determine volume
# ffmpeg -i $vidfile -filter:a volumedetect -f null /dev/null

# Capture Title and Artist metadata
# ffmpeg -i $vidfile -f ffmetadata - 2>/dev/null | grep "title\|artist"

# Apply Title and Artist overlay
# ffmpeg -i $vidfile -vf "drawtext=textfile=metadata.txt:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:fontsize=50:y=h-line_h-200:x=50:font=sans" $outputvid

# Resize to 1920x1080, then apply Title and Artist overlay
# ffmpeg -i $vidfile -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1, drawtext=textfile=metadata.txt:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:fontsize=50:y=h-line_h-200:x=50:font=sans" $outputvid

# Not sure why this needs vsync 2, but it creates millions upon millions of duplicate frames and crashes without it.
# This resizes the two videos to 1920x1080 and then concats them
# ffmpeg -i $vidfile1 -i $vidfile2 -vsync 2 -filter_complex "[0:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1[c0],[1:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1[c1],[c0][0:a:0][c1][1:a:0]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -s 1920x1080 $outputvid

#Path setup
#inputDirName = "vidQInput"
#outputDirName = "vidQOutput"
#homeDirPath = str(Path.home())
#outputPath = os.path.join(homeDirPath, outputDirName)
#inputPath = os.path.join(homeDirPath, inputDirName)
#if not os.path.exists(outputPath):
#    os.mkdir(outputPath)
#if not os.path.exists(inputPath):
#    os.mkdir(inputPath)
