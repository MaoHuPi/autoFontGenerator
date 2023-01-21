'''
2023 © MaoHuPi
autoFontGenerator/settings.py
'''

''' Debug Mode '''
'Off'
DEBUG_MODE = False
'On'
# DEBUG_MODE = True

''' Project Path '''
'Relative'
PROJECT_PATH = './HuPiMonsterFont'
'Absolute'
# PROJECT_PATH = 'C://Users/.../...'

''' Sampling Scale '''
'Normal'
# SAMPLING_SCALE = 1
'Overflow'
SAMPLING_SCALE = 0.6

''' Font Scale '''
'Default'
FONT_SCALE = 1/SAMPLING_SCALE
# FONT_SCALE = 1

''' Part Split '''
'Default'
# PART_SPLIT_NUM = 20
# PART_SPLIT_RESOLUTION = 100
'Fast'
PART_SPLIT_NUM = 5
PART_SPLIT_RESOLUTION = 10

''' Char Range '''
'basic'
CHAR_START = 1
CHAR_END = 659
'zh'
# CHAR_START = 11904
# CHAR_END = 40917

''' Part Mix '''
import numpy as np
'Default'
PART_MIX_FUNCTION = lambda image, part: part
# def PART_MIX_FUNCTION(image, part):
#     for item in [image, part]:
#         item[item[:, :] < 100] = True
#         item[item[:, :] >= 100] = False
#     image = np.logical_and(image, part)
#     image[image[:, :] == True] = 0
#     image[image[:, :] != True] = 255
#     return(image)
'Fill'
# PART_MIX_FUNCTION = lambda image, part: np.full_like(part, 0)
'Differentiation'
# def PART_MIX_FUNCTION(image, part):
#     for item in [image, part]:
#         item[item[:, :] < 100] = True
#         item[item[:, :] >= 100] = False
#     image[part[:, :] == True] = np.logical_not(image[part[:, :] == True])
#     image[image[:, :] == True] = 0
#     image[image[:, :] != True] = 255
#     return(image)

''' Part Offset '''
'Default'
TRANSLATE_OFFSET_FUNCTION = lambda: [0, 0]
SCALE_OFFSET_FUNCTION = lambda: [1, 1]
'Crash'
# import random
# TRANSLATE_OFFSET_FUNCTION = lambda: [random.randint(0, 10) - 5, random.randint(0, 10) - 5]
# SCALE_OFFSET_FUNCTION = lambda: [random.randint(0, 10)/10 + 0.5, random.randint(0, 10)/10 + 0.5]

''' Output Cut '''
'Normal'
CUT_HORIZONTAL = 0
CUT_VERTICAL = 0
'Thin'
# CUT_HORIZONTAL = 300
# CUT_VERTICAL = 0
'Cut Function (Do not strike out)'
CUT_FUNCTION = lambda x: x[CUT_VERTICAL:1080-CUT_VERTICAL, CUT_HORIZONTAL:1080-CUT_HORIZONTAL, :]

''' Generate Font '''
GENERATE_PER_CHAR = 20