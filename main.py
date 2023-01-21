'''
2023 © MaoHuPi
autoFontGenerator/main.py
'''

''' Import '''
import pygame
import cv2
import math
import json
import numpy as np
import os
from matplotlib import ft2font as ft2f
import re

''' Settings '''
from settings import *

''' Start '''
projectPath = PROJECT_PATH

def pygameToCv2(surface):
    image = pygame.surfarray.array3d(surface)
    image = image.transpose([1, 0, 2])
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return(image)
def readFile(path):
    file = open(path, 'r+', encoding = 'utf-8')
    content = file.read()
    file.close()
    return(content)
def writeFile(path, content):
    file = open(path, 'w+', encoding = 'utf-8')
    content = file.write(content)
    file.close()

# mathod from maohupi/vidionTest/main.py
def rad(deg): return deg/360*(math.pi*2)
def deg(rad): return rad/(math.pi*2)*360
lastFontSetting = ''
font = False
fontCharmap = False 
def textImage(text='', size = 30, bold = False, fgc = (0, 0, 0), bgc = False, fontName = 'arial', isSysFont = True, recordFont = True):
    if recordFont:
        global lastFontSetting, font, fontCharmap
    # render image
    text = str(text)
    fontSetting = json.dumps([fontName, size, bold])
    if recordFont:
        if lastFontSetting != fontSetting:
            lastFontSetting = fontSetting
            font = (pygame.font.SysFont if isSysFont else pygame.font.Font)(
                fontName, size, bold=bold)
            fontCharmap = ft2f.FT2Font(fontName).get_charmap()
    else: 
        font = (pygame.font.SysFont if isSysFont else pygame.font.Font)(
                fontName, size, bold=bold)
    if bgc:
        image = font.render(text, True, fgc, bgc)
    else:
        image = font.render(text, True, fgc)
    return(image)
def drawImage(surface, image, position, resize=False, rotation=False, origin='lt'):
    position = list(position)
    size = image.get_size()
    image = image.convert_alpha()
    if resize != False:
        resize = [int(n) for n in resize]
        image = pygame.transform.scale(image, resize)
        size = resize
    if rotation != False:
        image = pygame.transform.rotate(image, rotation)  # deg
        r = rad(rotation % 90)
        size = [
            math.sin(r)*size[1] + math.cos(r)*size[0],
            math.sin(r)*size[0] + math.cos(r)*size[1]
        ]
    origin = 'cc' if origin == 'c' else origin
    for i in range(2):
        if origin[i] in ['a', 'lt'[i]]:
            pass
        elif origin[i] in ['e', 'rb'[i]]:
            position[i] -= size[i]
        elif origin[i] in ['c', 'm']:
            position[i] -= size[i]/2
    surface.blit(image, position)

def getRect(image, x, y, w, h):
    return(image[y:y+h, x:x+w])
def setRect(image, x, y, w, h, image2):
    sw, sh = SCALE_OFFSET_FUNCTION()
    tx, ty = TRANSLATE_OFFSET_FUNCTION()
    x = int(x + w/2 + sw)
    y = int(y + h/2 + sw)
    w = int(w*sw)
    h = int(h*sh)
    x = int(x - w/2)
    y = int(y - h/2)
    oriRect = [x, y, x+w, y+h]
    newRect = [max(x, 0), max(y, 0), min(x+w, image.shape[1]-1), min(y+h, image.shape[0]-1)]
    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    image2 = cv2.resize(image2, (w, h), interpolation = cv2.INTER_AREA)
    mixImage = image[newRect[1]:newRect[3], newRect[0]:newRect[2]]
    mixPart = image2[newRect[1]-oriRect[1]:h+(newRect[3]-oriRect[3]), newRect[0]-oriRect[0]:w+(newRect[2] - oriRect[2])]
    if 0 in mixImage.shape:
        return
    image[newRect[1]:newRect[3], newRect[0]:newRect[2]] = PART_MIX_FUNCTION(mixImage, mixPart)
settings = readFile(projectPath + '/settings.json')
settings = json.loads(settings)
def getCorrespondPart(image):
    values = []
    ignoreNum = 10
    if not(len(settings['elements']) > 0 and np.sum(abs(image-255)) > ignoreNum):
        return(False)
    for element in settings['elements']:
        core = np.array(element['core'])
        part = element['path']
        # valueMax = np.sum(core)
        # valueMax = core.shape[0]*core.shape[1] - len(core[core == 0])
        valueMax = len(core[core == 1])
        resizedImage = cv2.resize(image, core.shape, interpolation = cv2.INTER_AREA)
        value = np.sum(resizedImage*core)/valueMax
        values.append({'value': value, 'part': part})
    correspondPart = sorted(values, key = lambda valuePartPair: -valuePartPair['value'])[0]['part']
    correspondPart = cv2.imread(f'{projectPath}/{correspondPart}')
    return(correspondPart)

pygame.init()

w, h = [300, 300]
win = pygame.display.set_mode((w, h))

background = pygame.Surface((w, h))
background.fill((255, 255, 255))
title = textImage('Auto Font Generator', size = 30, fgc = (64, 121, 144), bgc = False, bold = True, fontName = 'arial', isSysFont = True, recordFont = False)
drawImage(background, title, position = (w/2, 10), origin = 'ct')

sw, sh = [800, 800]
surface = pygame.Surface((sw, sh))

def generateChar(charCode):
    global lastFontSetting, font, fontCharmap
    surface.fill((255, 255, 255))
    text = textImage(chr(charCode), size = int(sw*SAMPLING_SCALE), fgc = (0, 0, 0), bgc = False, fontName = 'GenJyuuGothic-Normal.ttf', isSysFont = False)
    if not(charCode in fontCharmap):
        return(False)
    drawImage(surface, text, position = (sw/2, sh/2), origin = 'c')
    image = pygameToCv2(surface)
    # pygame.image.save(surface, 'word.jpg')

    win.blit(background, (0, 0))
    drawImage(win, surface, position = (w/2, h/2), resize = (w/2, h/2), origin = 'c')
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cv2.destroyAllWindows()
            generateFont()
            exit()

    # image = cv2.imread('word.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # image = cv2.medianBlur(image, 7)
    # image = cv2.Laplacian(image, -1, 1, 5)
    # image = cv2.Sobel(image, -1, 1, 1, 1, 7)
    # image = cv2.Canny(image, 36, 36)
    if DEBUG_MODE:
        cv2.imshow('image', cv2.resize(image, (500, 500), interpolation = cv2.INTER_AREA))
        cv2.waitKey(1)

    splitNum = PART_SPLIT_NUM
    splitResolution = PART_SPLIT_RESOLUTION
    image = cv2.resize(image, (splitResolution*splitNum, splitResolution*splitNum), interpolation = cv2.INTER_AREA)
    newImage = np.full_like(image, 255)
    for i in range(splitNum):
        for j in range(splitNum):
            part = getRect(image, splitResolution*i, splitResolution*j, 100, 100)
            correspondPart = getCorrespondPart(part)
            if not(type(correspondPart) == bool and correspondPart == False):
                setRect(newImage, splitResolution*i, splitResolution*j, 100, 100, correspondPart)
    if DEBUG_MODE:
        cv2.imshow('fontImage', cv2.resize(newImage, (500, 500), interpolation = cv2.INTER_AREA))
        cv2.waitKey(0)
    outputPath = f'{projectPath}/output/u{charCode}'
    outputPathPng = f'{outputPath}.png'
    outputPathSvg = f'{outputPath}.svg'
    image = cv2.resize(newImage, (1080, 1080), interpolation = cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
    image[image[:, :, 0] > 100, 3] = 0
    image = CUT_FUNCTION(image)
    if os.path.isfile(outputPathPng):
        os.unlink(outputPathPng)
    if os.path.isfile(outputPathSvg):
        os.unlink(outputPathSvg)
    cv2.imwrite(f'{outputPath}.png', image)
    os.system(f'bitmap2vector --input "{outputPath}.png" --blurdelta 2000 --numberofcolors 2 --viewbox true --scale {FONT_SCALE} > "{outputPath}.svg"')
    os.unlink(f'{outputPath}.png')

    content = readFile(outputPathSvg)
    regex = r'<path.[^>]*opacity="0".[^>]*/>'
    content = re.sub(regex, '', content)
    writeFile(outputPathSvg, content)
    return(True)

def generateFont():
    os.system(f'C:/"Program Files (x86)"/FontForgeBuilds/bin/ffpython.exe "./_svg2ttf.py" "{PROJECT_PATH}"')

def main():
    counter = 1
    try:
        for i in range(CHAR_START, CHAR_END+1):
            response = generateChar(i)
            if counter % GENERATE_PER_CHAR == 0:
                generateFont()
            counter += 1 if response else 0
    except Exception as e:
        print(e)
        pass
    generateFont()

main()
cv2.destroyAllWindows()