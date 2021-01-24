# TKINTER - sudo apt-get install python3-tk

# NUMPY - pip3 install numpy

# PILLOW - pip3 install pillow

# Running - python3 main.py

from tkinter import *
from PIL import Image, ImageTk
import numpy as np
from random import randrange

class Entity:
    def __init__(self, name, color, markedBoxColor):
        self.name = name
        self.color = color
        self.markedBoxColor = markedBoxColor
        self.score = 0

class Player(Entity):
    pass

class Agent(Entity):
    def playMove(self, stateOfBoxes, markedBoxes, stateOfRows, stateOfColumns, stateOfBoxesLines):
        canMarkBox = False
        boxes = np.argwhere(stateOfBoxes == 3)
        for index, box in boxes:
            b = list([index, box])
            if b not in markedBoxes and b != []:
                firstPossibleRow = b[0]
                secondPossibleRow = b[0] + 1
                firstPossibleColumn = b[1]
                secondPossibleColumn = b[1] + 1
                if stateOfBoxesLines[index][box] == 1:
                    firstPossibleCol = stateOfColumns[firstPossibleRow][firstPossibleColumn]
                    if firstPossibleCol == 0:
                        return [firstPossibleColumn, firstPossibleRow], 'column'
                    else:
                        return [secondPossibleColumn, firstPossibleRow], 'column'
                elif stateOfBoxesLines[index][box] == -1:
                    firstPossibleR = stateOfRows[firstPossibleRow][firstPossibleColumn]
                    if firstPossibleR == 0:
                        return [firstPossibleColumn, firstPossibleRow], 'row'
                    else:
                        return [firstPossibleColumn, secondPossibleRow], 'row'

        if not canMarkBox:
            random = randrange(2)
            if random == 0:
                first = stateOfRows
            else:
                first = stateOfColumns
            index, key = self.getRowOrColumn(first)
            if index == -1 and key == -1:
                search = stateOfRows if random == 1 else stateOfColumns
                index, key = self.getRowOrColumn(search)
                if index == -1 and key == -1:
                    return -1, -1
                else:
                    return [key, index], 'row' if random == 1 else 'column'
            else:
                return [key, index], 'row' if random == 0 else 'column'

    def getRowOrColumn(self, rowsOrColumns):
        possibleLines = []
        for index in range(len(rowsOrColumns)):
            for i in range(len(rowsOrColumns[index])):
                if rowsOrColumns[index][i] < 1:
                    possibleLines.append([index, i])
        if len(possibleLines):
            random = randrange(len(possibleLines))
            return possibleLines[random]
        else:
            return -1, -1

class Setup:
    boardSize = 600
    dotColor = '#CCCCCC'
    lineColor = '#6A889C'
    backgroundColor = '#1C3443'

    def setup(self, numberOfDots):
        self.numberOfDots = numberOfDots
        self.dotWidth = 0.15 * self.boardSize / numberOfDots
        self.markedLineWidth = 0.1 * self.boardSize / numberOfDots
        self.distanceBetweenDots = self.boardSize / numberOfDots

class Game:
    def __init__(self):
        self.window = Tk()
        self.window.configure(bg = Setup.backgroundColor)
        self.window.title('Dots and Boxes')
        self.canvas = Canvas(self.window, width = Setup.boardSize, height = Setup.boardSize, highlightthickness = 0)
        self.canvas.pack()
        self.canvas.configure(bg = Setup.backgroundColor)
        self.window.bind('<Button-1>', self.click)
        self.playerStarts = True
        self.initialize()

    # Inicijalizira igru
    def initialize(self):
        agent.score, player.score = 0, 0
        self.refreshScreen(True)
        self.stateOfBoxes = np.zeros(shape = (Setup.numberOfDots - 1, Setup.numberOfDots - 1))
        self.stateOfBoxesLines = np.zeros(shape = (Setup.numberOfDots - 1, Setup.numberOfDots - 1))
        self.stateOfRows = np.zeros(shape = (Setup.numberOfDots, Setup.numberOfDots - 1))
        self.stateOfColumns = np.zeros(shape = (Setup.numberOfDots - 1, Setup.numberOfDots))
        self.playerStarts = not self.playerStarts
        self.playerTurn = not self.playerStarts
        self.gameRestart = False
        self.score = []
        self.markedBoxes = []
        self.showGameState()
        self.canvas.create_text(Setup.boardSize - 20, 10, font = 'Helvetica 10 bold', text = 'v1.0.0', fill = 'white')
        self.welcome = self.canvas.create_text(10, 15, font = 'Helvetica 12 bold', text = '', anchor = NW)
        
        text = 'Good luck!'
        delay = 0
        for i in range(len(text) + 1):
            newText = lambda s = text[:i]: self.canvas.itemconfigure(self.welcome, text = s, fill = 'white')
            self.canvas.after(delay, newText)
            delay += 100

        image = Image.open('images/Restart.png')
        image = ImageTk.PhotoImage(image)
        label = Label(image = image, highlightthickness = 0, borderwidth = 0)
        label.image = image
        label.place(x = 0, y = Setup.boardSize - 40)
        label.bind('<Button-1>', self.restartGame)

        if not self.playerTurn:
            self.playAgentMove()

    def start(self):
        self.window.mainloop()

    def restartGame(self, event = None):
        self.canvas.delete('all')
        self.initialize()

    def findLinePosition(self, clickPosition):
        clickPosition = np.array(clickPosition)
        position = (clickPosition - Setup.distanceBetweenDots / 4) // (Setup.distanceBetweenDots / 2)

        typ = False
        linePosition = []

        if self.hasValueLessThan(position, 0):
            if position[1] % 2 == 0 and (position[0] - 1) % 2 == 0:
                column = int((position[0] - 1) // 2)
                row = int(position[1] // 2)
                linePosition = [column, row]
                typ = 'row'
            elif position[0] % 2 == 0 and (position[1] - 1) % 2 == 0:
                column = int(position[0] // 2)
                row = int((position[1] - 1) // 2)
                linePosition = [column, row]
                typ = 'column'

        return linePosition, typ

    def hasValueLessThan(self, position, value):
        for i in position:
            if i < value:
                return False
        return True

    def lineAlreadyDrawn(self, linePosition, typ):
        row = linePosition[0]
        column = linePosition[1]
        drawn = True
        try:
            if typ == 'row' and self.stateOfRows[column][row] == 0:
                drawn = False
            if typ == 'column' and self.stateOfColumns[column][row] == 0:
                drawn = False
        except:
            return drawn
        return drawn

    def updateStates(self, typ, linePosition):
        column = linePosition[0]
        row = linePosition[1]

        if row < (Setup.numberOfDots - 1) and column < (Setup.numberOfDots - 1):
            self.stateOfBoxes[row][column] += 1
            if typ == 'row':
                self.stateOfBoxesLines[row][column] += 1
            else:
                self.stateOfBoxesLines[row][column] -= 1

        if typ == 'row':
            self.stateOfRows[row][column] = 1
            if row >= 1:
                self.stateOfBoxes[row - 1][column] += 1
                self.stateOfBoxesLines[row - 1][column] += 1
        elif typ == 'column':
            self.stateOfColumns[row][column] = 1
            if column >= 1:
                self.stateOfBoxes[row][column - 1] += 1
                self.stateOfBoxesLines[row][column - 1] -= 1

    def markLine(self, typ, linePosition):
        if typ == 'row':
            xCoordStart = Setup.distanceBetweenDots / 2 + linePosition[0] * Setup.distanceBetweenDots
            xCoordEnd = xCoordStart + Setup.distanceBetweenDots
            yCoordStart = Setup.distanceBetweenDots / 2 + linePosition[1] * Setup.distanceBetweenDots
            yCoordEnd = yCoordStart
        elif typ == 'column':
            yCoordStart = Setup.distanceBetweenDots / 2 + linePosition[1] * Setup.distanceBetweenDots
            yCoordEnd = yCoordStart + Setup.distanceBetweenDots
            xCoordStart = Setup.distanceBetweenDots / 2 + linePosition[0] * Setup.distanceBetweenDots
            xCoordEnd = xCoordStart

        if self.playerTurn:
            color = player.color
        else:
            color = agent.color

        self.canvas.create_line(xCoordStart, yCoordStart, xCoordEnd, yCoordEnd, fill = color, width = Setup.markedLineWidth)

    def checkBox(self):
        boxes = np.argwhere(self.stateOfBoxes == 4)
        changePlayer = True
        if self.playerTurn:
            entity = player
        else:
            entity = agent
        
        for box in boxes:
            if list(box) not in self.markedBoxes and list(box) != []:
                self.markedBoxes.append(list(box))
                self.fillBox(box, entity.markedBoxColor)
                entity.score += 1
                changePlayer = False
        
        if changePlayer:
            self.playerTurn = not self.playerTurn

    def fillBox(self, box, color):
        xCoordStart = Setup.distanceBetweenDots / 2 + box[1] * Setup.distanceBetweenDots + Setup.markedLineWidth / 2
        yCoordStart = Setup.distanceBetweenDots / 2 + box[0] * Setup.distanceBetweenDots + Setup.markedLineWidth / 2
        xCoordEnd = xCoordStart + Setup.distanceBetweenDots - Setup.markedLineWidth
        yCoordEnd = yCoordStart + Setup.distanceBetweenDots - Setup.markedLineWidth
        self.canvas.create_rectangle(xCoordStart, yCoordStart, xCoordEnd, yCoordEnd, fill = color, outline = '')

    def refreshScreen(self, gameStart):
        if gameStart:
            for i in range(Setup.numberOfDots):
                x = i * Setup.distanceBetweenDots + Setup.distanceBetweenDots / 2
                self.canvas.create_line(x, Setup.distanceBetweenDots / 2, x, Setup.boardSize - Setup.distanceBetweenDots / 2, fill = Setup.lineColor, width = Setup.markedLineWidth)
                self.canvas.create_line(Setup.distanceBetweenDots / 2, x, Setup.boardSize - Setup.distanceBetweenDots / 2, x, fill = Setup.lineColor, width = Setup.markedLineWidth)
        for i in range(Setup.numberOfDots):
            for j in range(Setup.numberOfDots):
                xCoordStart = i * Setup.distanceBetweenDots + Setup.distanceBetweenDots / 2
                xCoordEnd = j * Setup.distanceBetweenDots + Setup.distanceBetweenDots / 2
                self.canvas.create_oval(xCoordStart - Setup.dotWidth / 2, xCoordEnd - Setup.dotWidth / 2, xCoordStart + Setup.dotWidth / 2, xCoordEnd + Setup.dotWidth / 2, fill = Setup.dotColor, outline = Setup.dotColor)
    
    def showGameState(self):
        if len(self.score):
            self.canvas.delete(self.score[0])
            self.canvas.delete(self.score[1])
            self.score = []
        self.score.append(self.canvas.create_text(Setup.boardSize / 2 - 100, 20, font = 'Helvetica 15 bold', text = player.name + ': ' + str(player.score), fill = player.markedBoxColor))
        self.score.append(self.canvas.create_text(100 + Setup.boardSize / 2, 20, font = 'Helvetica 15 bold', text = agent.name + ': ' + str(agent.score), fill = agent.color))

    def showScore(self):
        victory = True
        winner = None
        if player.score > agent.score:
            winner = player
            text = 'You beat ' + agent.name + '!'
        elif agent.score > player.score:
            winner = agent
            text = agent.name + ' won.'
        else:
            victory = False
        if not victory:
            text = 'It\'s a tie. Click anywhere for a new game.'
        else:
            text += ' Click anywhere to start a new game.'
        self.canvas.create_text(Setup.boardSize / 2, Setup.boardSize - Setup.distanceBetweenDots / 8, font = 'Helvetica 12 bold', text = text, fill = 'white')
        self.gameRestart = True

    def click(self, event):
        if not self.gameRestart:
            clickPosition = [event.x, event.y]
            linePosition, typ = self.findLinePosition(clickPosition)
            if typ and not self.lineAlreadyDrawn(linePosition, typ):
                self.playMove(typ, linePosition)
                if self.gameOver():
                    self.showScore()
                else:
                    if not self.playerTurn:
                        self.playAgentMove()
        else:
            self.canvas.delete('all')
            self.initialize()
            self.gameRestart = False

    def playMove(self, typ, linePosition):
        self.updateStates(typ, linePosition)
        self.markLine(typ, linePosition)
        self.checkBox()
        self.refreshScreen(False)
        self.showGameState()
        if not self.playerTurn:
            self.playAgentMove()

    def playAgentMove(self):
        linePosition, typ = agent.playMove(self.stateOfBoxes, self.markedBoxes, self.stateOfRows, self.stateOfColumns, self.stateOfBoxesLines)
        if linePosition != -1 and typ != -1:
            self.playMove(typ, linePosition)

    def gameOver(self):
        return (self.stateOfRows == 1).all() and (self.stateOfColumns == 1).all()

if __name__ == '__main__':
    while True:
        name = input('Enter username up to 10 characters: ')
        if not name or len(name) > 10:
            continue   
        else:
            break 

    while True:
        try:
            size = int(input('Enter game size from 3 to 6: '))    
            if size < 3 or size > 6:
                continue   
        except ValueError:
            print('Game size must be between 3 and 6.')
            continue
        else:
            break 

    Setup.setup(Setup, size)

    player = Player(name, color = '#0B5696', markedBoxColor = '#3D76A8')
    agent = Agent('Agent', color = '#BD1A00', markedBoxColor = '#C72C0E')

    game = Game()
    game.start()