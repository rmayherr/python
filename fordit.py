#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# This program uses the Google text-to-speach engine.
## ----------- prerequisites -----------------------
# To install it run: sudo python3 -m pip install gtts
# --------------------------------------------------
# additionaly you can install on Debian on this way:
# sudo apt install python3-gtts* mpg321
#### this means: python3-gtts-token/stable,now 1.1.1-1
####             python3-gtts/stable,now 1.2.0-1
#### mpg321 is a lightweith mp3 player here runs in -q quiet mode
from gtts import gTTS
import os
from time import sleep
os.system('tput bold; tput setaf 7')
minta = '''
\tOlivier Nakache és Eric Toledano 2011-ben valamibe nagyon
\tbeletaláltak az Életrevalókkal: az a film egy lecsúszott,
\tkisstílű fekete munkakerülő és egy kőgazdag, sznob,
\tfehér arisztokrata egymásra utaltságából költött csodálatosan
\temberi és közben állati vicces mesét. Pedig igaz történet
\tvolt az alapja: a proli srác ápolóként szegődött a nyaktól
\tlefelé lebénult burzsuj mellé, és aztán persze mind a ketten
\tkihozták egymásból a legjobbat, csak épp finoman szólva sem
\tazokkal a módszerekkel, amik először eszünkbe jutnának.
\tA filmből hollywoodi remake is készült, világszerte
\t– Budapesten is – játsszák, és általában is
\ta francia film egyik legendájává vált.
'''
print('Write in, or paste from the cliboard  Ctrl+Shif+V  the text you whant to hear.')
text_in = input('\n\tÍrd be, vagy másold be a szöveget amit fel kell olvasni:\n\t\
Van egy szöveg-minta, ha nem adnál meg semmit, csak ENTERT ütnél.')
os.system('tput bold; tput setaf 2') # linux terminal green colored text
# the \ on the end of the line enshures a line-break between the code
print("\tÉrdemes kipróbálni hogyan olvasná fel\n\t\
egy másik nyelvű ember ezt a szöveget!!!\n")
nyelv = str(input('\n\tAdd meg a nyelvet amelyiken szólni fog.\n\t\
(pl.: hu-->(Magyar), fr-->(Francia, de-->(Német), en-->(English)\n\t \
tr-->(Török), hi-->(Hindi-Inidia), vagy hu-->(Magyar):\t\n'))
os.system('tput sgr0') # linux terminal end of green colored text
if len(text_in) <=1:
    text_in = minta
if len(nyelv) <=1 or nyelv == '':
    nyelv = 'hu'
os.system('tput sgr0')
print(text_in)
engine = gTTS(text = text_in, lang = nyelv)
engine.save('kimenet.mp3')
#os.system('mplayer -really-quiet kimenet.mp3')
os.system('mpg321 -q kimenet.mp3')
os.system('afplay kimenet.mp3')
def elegedett():
    os.system('tput bold; tput setaf 7')
    elegedett = int(input('\n\tEgy 1-től 10-ig tartó skálán értékeld az elégedettségedet:\n\t'))
    if elegedett <= 5:
        os.system('tput bold; tput setab 1')
        print('\n\t Sajnálom, ezt tudja a Google szövegbeolvasója :\n')
        os.system('tput sgr0')
    elif elegedett >= 6 and elegedett <=8:
        os.system('tput bold; tput setaf 5')
        print('\n\tNa! Akkor egész jónak ítéled,\n\tennél jobb nem lesz egy darabig.\n')
        os.system('tput sgr0')
    elif elegedett >= 9:
        os.system('tput bold; tput setaf 2')
        print('\n\tSzuper!\n\tIlyen értékelést, nem is vártam!\n\tKöszi!\n')
        os.system('tput sgr0')
elegedett()

