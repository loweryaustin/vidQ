from dataclasses import dataclass, field
import ffmpeg
import os
import uuid
import re
import subprocess
import tempfile
from pathlib import Path


def getOutputPath():
    homeDirPath = str(Path.home())
    outputPath = os.path.join(homeDirPath, 'vidQOut.mp4')
    return outputPath

def getVolume(vidPath):
    process = subprocess.Popen(
            (
                ffmpeg
                .input(vidPath)
                .filter('volumedetect')
                .output('-', format='null')
                .compile()
                )
            , stderr = subprocess.PIPE
            , encoding = 'utf8'
            )
    cmd_output = process.stderr.readlines()
    for line in cmd_output:
        pattern = re.compile(r'mean_volume: (-?\d+?.\d+?) dB')
        matches = pattern.finditer(line)
        for match in matches:
            return match.group(1)


def prepVid(vidObject):
    textOverlay = f'{vidObject.title}\r\nBy {vidObject.artist}'
    if vidObject.upNext is not None:
        textOverlay = f'{textOverlay}\r\nNext: {vidObject.upNext}'

    tempText = tempfile.NamedTemporaryFile(delete=False)
    tempText.write(bytes(textOverlay, 'utf-8'))
    tempText.close()
#    inStream = ffmpeg.input(vidObject.inputPath)
#    vidAudio = inStream.audio
#    vidVideo = inStream.video
#    vidVideo = vidVideo.filter('scale', size='hd1080', force_original_aspect_ratio='decrease')
#    vidVideo = vidVideo.drawtext(text=textOverlay,x='50',y='h-line_h-200',font='sans',fontcolor='white',box='1',boxcolor='black@0.6',boxborderw='20',fontsize='50')
#    out = ffmpeg.output(vidAudio, vidVideo, vidObject.tmpPath)
#    out = ffmpeg.overwrite_output(out)
#    ffmpeg.run(out)
    cmd = f'ffmpeg -y -i "{vidObject.inputPath}" -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1, drawtext=textfile={tempText.name}:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:fontsize=50:y=h-line_h-100:x=50:font=sans" "{vidObject.tmpPath}"'
    #os.system(cmd)
    os.system(cmd)
    os.unlink(tempText.name)


def concatVids(vidMetaList):
    fileList = ""
    scale = ""
    audio = ""
    for k, vid in enumerate(vidMetaList):
        fileList = f'{fileList} -i {vid.tmpPath}'
        scale = f'{scale}[{k}:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1[c{k}],'
        audio = f'{audio}[c{k}][{k}:a:0]'


    vidCount = len(vidMetaList)
    concat = f'concat=n={vidCount}:'
    vidOut = f'v=1:a=1[v][a]'
    maps = f'-map "[v]" -map "[a]"'
    cmd = f'ffmpeg -y {fileList} -vsync 2 -filter_complex "{scale}{audio}{concat}{vidOut}" {maps} "/home/user1/out.mp4"'

#    joined = ffmpeg.concat(*inputs, v=1, a=1)
#    ffmpeg.output(joined[0], joined[1], "/home/user1/output.mp4").run()
#    cmd = "ffmpeg -f concat -safe 0 -i " + processList + " -c copy "+ dir + "output.mp4"
    #return cmd
    #return f'ffmpeg -i "{concatString}" -c copy "/home/user1/outputtesting.mp4"'
    #subprocess.Popen(cmd)
    os.system(cmd)
    #temp.close()
#def sortVids(vidQueue):
#    return vidQueue.sort(key=lambda vid: vid.volume, reverse=False)


# Not sure why this needs vsync 2, but it creates millions upon millions of duplicate frames and crashes without it.
# This resizes the two videos to 1920x1080 and then concats them
# ffmpeg -i $vidfile1 -i $vidfile2 -vsync 2 -filter_complex "[0:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1[c0],[1:v:0]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1[c1],[c0][0:a:0][c1][1:a:0]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -s 1920x1080 $outputvid

# Resize to 1920x1080, then apply Title and Artist overlay
# ffmpeg -i $vidfile -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,setsar=1, drawtext=textfile=metadata.txt:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=20:fontsize=50:y=h-line_h-200:x=50:font=sans" $outputvid

@dataclass
class vidMeta:
    inputPath:           str
    UUID:               str = field(init=False)
    tmpDirPath:           str
    tmpPath:               str = field(init=False)
    upNext:               str = None
    #[d]isplay [a]spect [r]atio
    dar:            str = field(init=False)
    #[s]ample [a]spect [r]atio
    sar:            str = field(init=False)
    xres:           int = field(init=False)
    yres:           int = field(init=False)
    title:          str = field(init=False)
    artist:         str = field(init=False)
    containerBitrate:         str = field(init=False)
    volume:         float = field(init=False)
    fileSize:       str = field(init=False)
    avgFramerate:      int = field(init=False)
    audioCodecName:     str = field(init=False)
    audioCodecNameLong:     str = field(init=False)
    videoCodecName:     str = field(init=False)
    videoCodecNameLong:     str = field(init=False)
    videoBitrate:     str = field(init=False)
    audioBitrate:     str = field(init=False)
    pixelFormat:     str = field(init=False)
    formatName:     str = field(init=False)
    formatNameLong:     str = field(init=False)
    rawMetaJSON:     dict = field(init=False)

    def __post_init__(self) -> None:
        # the path attribute will be changed during the course of working with the file, but we still want to keep track of the original file

        self.UUID = uuid.uuid4().hex
        self.tmpPath = os.path.join( self.tmpDirPath, uuid.uuid4().hex) + '.mp4'
        self.rawMetaJSON = ffmpeg.probe(self.inputPath)
        self.formatName = self.rawMetaJSON.get('format').get('format_name')
        self.formatNameLong = self.rawMetaJSON.get('format').get('format_long_name')
        self.dar = self.rawMetaJSON.get('streams')[0].get('display_aspect_ratio')
        self.sar = self.rawMetaJSON.get('streams')[0].get('sample_aspect_ratio')
        self.xres = self.rawMetaJSON.get('streams')[0].get('coded_width')
        self.yres = self.rawMetaJSON.get('streams')[0].get('coded_height')
        self.title = self.rawMetaJSON.get('format').get('tags').get('title') or "EMPTY"
        self.artist = self.rawMetaJSON.get('format').get('tags').get('artist') or "EMPTY"
        self.containerBitrate = self.rawMetaJSON.get('streams')[0].get('bit_rate')
        self.volume = getVolume(self.inputPath)
        self.fileSize = self.rawMetaJSON.get('format').get('size')
        self.avgFramerate = self.rawMetaJSON.get('streams')[0].get('avg_frame_rate')
        self.audioCodecName = self.rawMetaJSON.get('streams')[1].get('codec_name')
        self.audioCodecNameLong = self.rawMetaJSON.get('streams')[1].get('codec_long_name')
        self.videoCodecName = self.rawMetaJSON.get('streams')[0].get('codec_name')
        self.videoCodecNameLong = self.rawMetaJSON.get('streams')[0].get('codec_long_name')
        self.videoBitrate = self.rawMetaJSON.get('streams')[0].get('bit_rate')
        self.videoBitrate = self.rawMetaJSON.get('streams')[0].get('bit_rate')
        self.audioBitrate = self.rawMetaJSON.get('streams')[1].get('bit_rate')
        self.pixelFormat = self.rawMetaJSON.get('streams')[0].get('pix_fmt')
