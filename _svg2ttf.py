#!/usr/bin/fontforge -script

r'''
python file from https://github.com/pteromys/svgs2ttf
Revise by MaoHuPi

terminal command:
"C:\Program Files (x86)\FontForgeBuilds\run_fontforge.exe" "./_svg2ttf.py"
'''

import sys
import os.path
import json
import fontforge
import psMat
import math

path = '.' if os.path.isfile('./'+os.path.basename(__file__)) else os.path.dirname(os.path.abspath(__file__))
IMPORT_OPTIONS = ('removeoverlap', 'correctdir')

try:
    unicode
except NameError:
    unicode = str

def readJson(filename='font.json'):
    f = open(filename, 'r', encoding='utf-8')
    c = f.read()
    f.close()
    o = json.loads(c)
    return(o)

def setProperties(font, config):
    props = config['props']
    lang = props.pop('lang', 'English (US)')
    family = props.pop('family', None)
    style = props.pop('style', 'Regular')
    props['encoding'] = props.get('encoding', 'UnicodeFull')
    if family is not None:
        font.familyname = family
        font.fontname = family + '-' + style
        font.fullname = family + ' ' + style
    for k, v in config['props'].items():
        if hasattr(font, k):
            if isinstance(v, list):
                v = tuple(v)
            setattr(font, k, v)
        else:
            font.appendSFNTName(lang, k, v)
    for t in config.get('sfnt_names', []):
        font.appendSFNTName(str(t[0]), str(t[1]), unicode(t[2]))

def addGlyphs(font, config):
    matrixs = []
    if config.get('transform', False) != False:
        matrixs = [getattr(psMat, k)(*v) for k, v in config['transform'].items()]
    for k, v in config['glyphs'].items():
        g = font.createMappedChar(int(k, 0))
        font.removeGlyph(g)
        g = font.createChar(int(k, 0))
        # Get outlines
        src = '%s.svg' % k
        if not isinstance(v, dict):
            v = {'src': v or src}
        src = f'{path}/{config.get("input", ".")}/{v.pop("src", src)}'
        config['glyphsDone'].append(src)
        try:
            g.importOutlines(src, IMPORT_OPTIONS)
            g.removeOverlap()
            for matrix in matrixs:
                g.transform(matrix)
        except:
            print('Error (overlap)')
            return
        # Copy attributes
        for k2, v2 in v.items():
            if hasattr(g, k2):
                if isinstance(v2, list):
                    v2 = tuple(v2)
                setattr(g, k2, v2)

def main(config):
    if '*' in config['glyphs']:
        svgDir = config["input"]
        if os.path.isdir(svgDir):
            svgs = dict([(hex(ord(name[-5]) if len(name[0:-4]) == 1 else int(name[0:-4].lower().replace('u', ''))), '{name}'.format(dir = svgDir, name = name)) for name in os.listdir(svgDir) if os.path.isfile('{dir}/{name}'.format(dir = svgDir, name = name)) and (name.find('.svg') == len(name) - len('.svg'))])
            svgsSettings = config['glyphs'].pop('*')
            if type(svgsSettings) == dict:
                svgs = dict([(k, {**svgsSettings, 'src': src}) for k, src in svgs.items()])
            config['glyphs'].update(svgs)

    font = False
    sfdPath = config.get("sfd", "font.sfd")
    if config.get('sfd', False) != False and os.path.isfile(sfdPath):
        font = fontforge.open(sfdPath)
    else:
        font = fontforge.font()
    if font == False:
        return
    setProperties(font, config)
    config['glyphsDone'] = []
    addGlyphs(font, config)
    sys.stderr.write('writting')

    font.save(sfdPath)
    print(font, sfdPath)
    for outfile in config['output']:
        sys.stderr.write('writting')
        sys.stderr.write('Generating %s...\n' % outfile)
        font.generate(outfile)
    
    for src in config['glyphsDone']:
        os.unlink(src)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        os.chdir(os.path.abspath(sys.argv[1]))
        config = readJson('settings.json')['font']
    else:
        config = readJson(path + '/font.json')
    main(config)
    print('done')