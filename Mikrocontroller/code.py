import board
import time
import displayio
import framebufferio
import rgbmatrix
import terminalio
from adafruit_display_text import label
import requests

displayio.release_displays()

# RGB-Matrix initialisieren
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

# Display-Buffer und Farbpalette
SCALE = 1
data = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 2) # [w, h]

palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0x0000FF

# TileGrid für die Anzeige
tg1 = displayio.TileGrid(data, pixel_shader=palette)
g1 = displayio.Group(scale=SCALE)
g1.append(tg1)
display.root_group = g1

# logic variables


leftbar_index_top = 5
rightbar_index_top = 5

class Ball:
    def __init__(self,xpos,ypos,moveright,upordown):
        self.xpos = xpos
        self.ypos = ypos
        self.moveright = moveright
        self.upordown = upordown # 0: ball going in a straight line, 1: ball going up, -1 ball going down

ball = Ball(xpos=1,ypos=1,moveright=True,upordown=1)

def initdata():    
    data[0, 14] = 1
    data[0, 15] = 1
    data[0, 16] = 1
    data[0, 17] = 1
    data[0, 18] = 1
    data[63, 14] = 1
    data[63, 15] = 1
    data[63, 16] = 1
    data[63, 17] = 1
    data[63, 18] = 1


def updatematrix():
    display.refresh()

previousx = 0
previousy = 0

def moveball():
    previousx = ball.xpos
    previousy = ball.ypos
    if ball.upordown == 1:
        ball.ypos -= 1
    elif ball.upordown == -1:
        ball.ypos += 1

    if ball.moveright:
        ball.xpos += 1
    else:
        ball.xpos -= 1
    data[previousx, previousy] = 0
    data[ball.xpos, ball.ypos] = 1
    display.refresh
righscore = 0
leftscore = 0
def checkballstate():
    if (ball.ypos == 0 and ball.upordown == 1) or (ball.ypos == 31 and ball.upordown == -1): # Falls Ball oben oder unten am Rand ankommt, wird die Richtung gedreht
        ball.upordown *= -1
    haswon = False
    if((ball.xpos == 1 and ball.moveright == False) or (ball.xpos == 62 and ball.moveright == True)):
        haswon = checkcollision()
    if haswon:
        if ball.xpos == 1:
            rightscore += 1
            exit(2)
        elif ball.xpos == 31:
            leftscore += 1
            exit(1)

def checkcollision():
    # Richtung bestimmen
    if ball.moveright:
        xposmodifier = 1
        bar_index_top = rightbar_index_top
    else:
        xposmodifier = -1
        bar_index_top = leftbar_index_top

    next_ypos = ball.ypos + (ball.upordown * -1)
    
    # Kollision prüfen
    if data[ball.xpos + xposmodifier, next_ypos] == 1:
        diff = bar_index_top - next_ypos  # Abstand zur Bar berechnen
        
        if diff == 0 or diff == -1:
            ball.upordown = 1
        elif diff == -2:
            ball.upordown = 0
        elif diff == -3 or diff == -4:
            ball.upordown = -1

        ball.moveright = not ball.moveright  # Richtung umkehren
        return False  # Kollision erkannt
    return True  # Keine Kollision
leftup = False
leftdown = False
rightup = False
rightdown = False
def getResponse():
    response = requests.get("https://ping.unser.dns64.de/")
    
    if response.status_code == 200:
        data = response.json()
        leftup = data["leftup"]
        leftdown = data["leftdown"]
        rightup = data["rightup"]
        rightdown = data["rightdown"]
        print("Received Data:", data)
    else:
        print("Error:", response.status_code, response.text)
def movebar():
    global leftbar_index_top, rightbar_index_top

    if leftup and leftbar_index_top != 0:
        leftbar_index_top -= 1
        data[0, leftbar_index_top+5] = 0
        data[0, leftbar_index_top] = 1
    elif leftdown and leftbar_index_top != 27:
        leftbar_index_top += 1
        data[0, leftbar_index_top+4] = 1
        data[0, leftbar_index_top-1] = 0

    if rightup and rightbar_index_top != 0:
        rightbar_index_top -= 1
        data[63, rightbar_index_top+5] = 0
        data[63, rightbar_index_top] = 1
    elif rightdown and rightbar_index_top != 27:
        rightbar_index_top += 1
        data[63, rightbar_index_top+4] = 1
        data[63, rightbar_index_top-1] = 0


initdata()
updatematrix()
#matrix.pixel(ball.xpos,ball.ypos,1)
#matrix.show()
display.refresh()
time.sleep(1)
while True:
    updatematrix()
    checkballstate()
    moveball()
    getResponse()
    movebar()

    #time.sleep(0.2)
    display.refresh()