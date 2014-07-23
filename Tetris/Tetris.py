
### teoTetris.py ###

####################
# python 2.7.3
# pyglet 1.2alpha1
####################

import pyglet
import random
import math

# window dimensions
WIDTH = 400
HEIGHT = 300

# Grid width and height in bricks
GRID_WIDTH = 16 # must be even
GRID_HEIGHT = 25
GRID_X = 10
GRID_Y = 10

BRICKSIZE = 10
LINES_PER_LEVEL = 3
 
class Game:
  def __init__(self):
    self.gameActive = False
    self.gameOver = False
    self.gamePaused = False

  def startNewGame(self):
    self.difficulty = 1
    self.dropRate = 0.52
    self.score = 0
    self.lines = 0
    self.nextBlock = Block()
    self.curBlock = self.nextBlock
    self.autoDrop = False #State modified by activateAutoDrop(), and reset by changeHanderl(), at set interval
    self.gameActive = True
    self.gameOver = False
    self.gamePaused = False
    pyglet.clock.schedule_interval(self.activateAutoDrop, self.dropRate)
    self.newBlock()
    self.curGrid = Grid()
    
  def setDifficulty(self, n):
    if 1 <= n <= 25:
      self.difficulty = n
      curInfo.levelText.text = "Level: " + str(self.difficulty)
      self.dropRate = 0.51 - 0.02 * self.difficulty # Fastest possible dropRate is .001 at difficulty 25
      pyglet.clock.unschedule(self.activateAutoDrop)
      pyglet.clock.schedule_interval(self.activateAutoDrop, self.dropRate)

  def newBlock(self):
    self.curBlock = self.nextBlock
    self.curBlock.updatePosition(GRID_WIDTH / 2, GRID_HEIGHT - 1)
    self.nextBlock = Block()

  def activateAutoDrop(self, dt):
    self.autoDrop = True

class Info:
  def __init__(self):
    self.score = 0
    self.lines = 0
    self.infoBatch = pyglet.graphics.Batch()
    self.nextText = pyglet.text.Label("Next block:",
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = (WIDTH * .66),
                      y = (HEIGHT * .75),
                      batch = self.infoBatch)
    self.scoreText = pyglet.text.Label("Score: 0",
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = (WIDTH * .66),
                      y = (HEIGHT * .75) - 20,
                      batch = self.infoBatch)
    self.levelText = pyglet.text.Label("Level: 0",
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = (WIDTH * .66),
                      y = (HEIGHT * .75) - 40,
                      batch = self.infoBatch)
    self.linesText = pyglet.text.Label("Lines: 0",
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = (WIDTH * .66),
                      y = (HEIGHT * .75) - 60,
                      batch = self.infoBatch)

    self.msgBatch = pyglet.graphics.Batch()
    self.msgText = pyglet.text.Label('',
                      font_name = 'Times New Roman',
                      font_size = 20,
                      color = (255, 255, 255, 255),
                      align = "center",
                      anchor_x = "center",
                      x = (GRID_WIDTH * BRICKSIZE - GRID_X) / 2 + GRID_X,
                      y = (GRID_HEIGHT * BRICKSIZE - GRID_Y) / 2 + GRID_Y,
                      batch = self.msgBatch)

  def updateGameInfo(self, linesRemoved, game):
    self.addToScore(math.factorial(linesRemoved) * game.difficulty)
    self.addToLines(linesRemoved, game)

  def addToScore(self, n):
    self.score += n
    self.scoreText.text = "Score: " + str(self.score)

  def addToLines(self, n, game):
    self.lines += n
    self.linesText.text = "Lines: " + str(self.lines)
    if self.lines >= LINES_PER_LEVEL * game.difficulty:
      game.setDifficulty(game.difficulty + 1)

class Input:
  def __init__(self):
    self.validMoves = dict(left = True, right = True, down = True)

  def keyPress(self, symbol, game):
    if game.gameActive:
      if game.gameOver:
        game.gameActive = False
      elif symbol == pyglet.window.key.SPACE:
        if curGame.gamePaused:
          curGame.gamePaused = False
        else:
          curGame.gamePaused = True
    else:
      game.startNewGame()

  def changeHandler(self, dt, game, info):
    window.push_handlers(userInput)

    if game.gameActive and game.gameOver == False and game.gamePaused == False:
      self.checkValidMoves(game)

      if userInput[pyglet.window.key.UP]:
        if self.checkValidRotation(game):
          game.curBlock.rotate()
          self.checkValidMoves(game)

      # In this series of if statements, down is checked for validity prior to left and right.
      # This allows autoDrop to take priority over valid left or right checks but also allows for last second
      # left or right adjustments by the user even when the block is directly above a brick in the grid.

      if self.validMoves['down']:
        if userInput[pyglet.window.key.DOWN] or game.autoDrop:
          game.curBlock.updatePosition(game.curBlock.refX, game.curBlock.refY - 1)
          game.autoDrop = False
          self.checkValidMoves(game)

      if self.validMoves['left']:
        if userInput[pyglet.window.key.LEFT]:
          game.curBlock.updatePosition(game.curBlock.refX - 1, game.curBlock.refY)
          self.checkValidMoves(game)
          
      if self.validMoves['right']:
        if userInput[pyglet.window.key.RIGHT]:
          game.curBlock.updatePosition(game.curBlock.refX + 1, game.curBlock.refY)
          self.checkValidMoves(game)

      # check 'down' again now that the above changes have been handled
      if self.validMoves['down'] == False: # block is on top of brick in the grid or is at the bottom of the grid
        if game.curGrid.populate(game.curBlock):
          linesRemoved = game.curGrid.handleFullLines()
          if linesRemoved:
            info.updateGameInfo(linesRemoved, game)
          game.newBlock()
        else:
          game.gameOver = True
 
  @staticmethod
  def checkValidRotation(game):
    testOrientation = game.curBlock.blockOrientation
    
    if testOrientation + 1 < len(game.curBlock.brickLayout):
      testOrientation += 1
    else:
      testOrientation = 0
    
    validRotation = game.curGrid.checkForOverlap(testOrientation, game.curBlock)
    
    return validRotation
       
       
  def checkValidMoves(self, game):
    '''detect if the block borders the grid bourndaries or any bricks in the grid'''
    self.validMoves.update(left = True, right = True, down = True)
    for brick in game.curBlock.bricks:
      curX = brick.x
      curY = brick.y

      #Restrict movment if the block is on the grid border
      if curX == GRID_X:
        self.validMoves['left'] = False
      elif curX == GRID_WIDTH * BRICKSIZE:
        self.validMoves['right'] = False
      if curY == GRID_Y:
        self.validMoves['down'] = False

      #Now check for neighbouring bricks already on the grid
      for direction in self.validMoves.iterkeys():
        if self.validMoves[direction]:
          self.validMoves[direction] = game.curGrid.checkNeighbour(game.curBlock, direction)

class Block:
  def __init__ (self):
    self.brickLayout = self.randomShape()
    self.blockColor = self.randomColor()
    self.blockOrientation = 0

    self.refX = GRID_WIDTH + 4  #in bricks
    self.refY = GRID_HEIGHT - 1 #in bricks

    self.blockBatch = pyglet.graphics.Batch()
    self.brick = pyglet.image.create(BRICKSIZE, BRICKSIZE, pattern=pyglet.image.SolidColorImagePattern(color=(self.blockColor)))

    self.bricks = [pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch)]

    self.setCoordinates()

  def setCoordinates(self):
    """set the screen coords for each brick in the block, based on the block's current reference coords and orientation"""
    for i in range(4):
      self.bricks[i].x = ((self.refX + self.brickLayout[self.blockOrientation][i][0]) * BRICKSIZE) + GRID_X
      self.bricks[i].y = ((self.refY + self.brickLayout[self.blockOrientation][i][1]) * BRICKSIZE) + GRID_Y

  def rotate(self):
    """rotate the block clockwise"""
    if self.blockOrientation + 1 < len(self.brickLayout):
      self.blockOrientation += 1
    else:
      self.blockOrientation = 0

    self.setCoordinates()

  def updatePosition(self, x, y):
    """update the block's reference coords and then have the screen coords for each brick updated"""
    self.refX = x
    self.refY = y
    self.setCoordinates()

  @staticmethod
  def randomColor():
    colors = []
    colors.append( (200, 0, 0, 255) ) # red
    colors.append( (0, 150, 0, 255) )# green
    colors.append( (0, 0, 200, 255) )# blue
    colors.append( (238, 238, 0, 255) )# yellow
    colors.append( (104, 34, 139, 255) )# purple
    colors.append( (255, 127, 36, 255) )# orange
    colors.append( (112, 219, 219, 255) )# tourqouise

    return random.choice(colors)
  
  @staticmethod
  def randomShape():
    """ Return a random 3 dimension array defining the bricklayout of a block
        dimension 1 represents each block orientation (up to four), progressing clock-wise
        dimension 2 is specific bricks in the block
        dimension 3 is a tuple of x, y adjustment coordinates for the parent brick."""
    shapes = []
    
    # T shape
    shapes.append( [ 
                     [ (0,0), (-1,0), (1,0), (0,-1) ],
                     [ (0,0), (-1,0), (0,-1), (0,1) ],
                     [ (0,0), (-1,0), (1,0), (0,1) ],
                     [ (0,0), (0,1), (1,0), (0,-1) ]
                   ] )
    # L shape
    shapes.append( [ 
                     [ (0,0), (-1,0), (1,0), (-1,-1) ],
                     [ (0,0), (0,-1), (0,1), (-1,1) ],
                     [ (0,0), (-1,0), (1,0), (1,1) ],
                     [ (0,0), (0,-1), (0,1), (1,-1) ]
                   ] )
    # Reverse L shape
    shapes.append( [ 
                     [ (0,0), (-1,0), (1,0), (1,-1) ],
                     [ (0,0), (0,-1), (0,1), (-1,-1) ],
                     [ (0,0), (-1,0), (1,0), (-1,1) ],
                     [ (0,0), (0,-1), (0,1), (1,1) ]
                   ] )
    # Square
    shapes.append( [ [ (0,0), (-1,0), (-1,-1), (0,-1) ] ] )
    # Line
    shapes.append( [ 
                     [ (0,0), (-1,0), (1,0), (2,0) ],
                     [ (0,0), (0,1), (0,-1), (0,-2) ]
                   ] )
    # S shape
    shapes.append( [
                     [ (0,0), (1,0), (-1,-1), (0,-1) ],
                     [ (0,0), (0,1), (1,0), (1,-1) ] 
                    ] )
    # Z shape
    shapes.append( [
                     [ (0,0), (-1,0), (0,-1), (1,-1) ],
                     [ (0,0), (1,0), (1,1), (0,-1) ]
                   ] )
    
    return random.choice(shapes)

class Grid:
  def __init__ (self):
    self.bgImage = pyglet.image.create(GRID_WIDTH * BRICKSIZE, GRID_HEIGHT * BRICKSIZE, pattern=pyglet.image.SolidColorImagePattern(color=(30, 30, 30, 255)))
    self.gridBackground = pyglet.sprite.Sprite(self.bgImage, x = GRID_X, y = GRID_Y)
    
    self.gridBatch = pyglet.graphics.Batch()
    
    # gridpMap[] is a 2D array that tracks rows on the grid that have at least one occupied cell
    # When a falling block collides with the bottom of the grid or an occupied cell,
    #   gridMap is updated with information about which cells should be populated.
    # dimension 1 corresponds to rows (bottom to top)
    # dimension 2 corresponds to columns (left to right)
    # If a row on the grid has no occupied cells, there should not be an element for it.
    # When a new row is needed, working from the bottom of the grid up, a new row element should be appended
    #    so that the element with the largest index number represents the highest row in the grid with an occupied cell.
    self.gridMap = []
    self.addRow()

  def addRow(self):
    #add a row to the gridMap containting a new array for each cell in the grid's width
    self.gridMap.append(list( '0' * GRID_WIDTH))

  @staticmethod
  def calcRowCol(curLoc, boundary):
    
    if (curLoc - boundary) != 0:
      return (curLoc - boundary) / BRICKSIZE
    else:
      return 0

  def checkForOverlap(self, orientation, block):
    for i in range(len(block.bricks)):
      curBrickX = ( (block.refX + block.brickLayout[orientation][i][0]) * BRICKSIZE) + GRID_X
      curBrickY = ( (block.refY + block.brickLayout[orientation][i][1]) * BRICKSIZE) + GRID_Y
      
      colNum = self.calcRowCol(curBrickX , GRID_X)
      rowNum = self.calcRowCol(curBrickY , GRID_Y)

      if 0 > colNum or colNum >= GRID_WIDTH:
        return False
      elif rowNum < len(self.gridMap):
        if self.gridMap[rowNum][colNum] != '0':
          return False

    return True

  def checkNeighbour(self, block, direction):
    ''' direction should be 0 for left, 1 for right, and 2 for down '''
    #if 3 > direction >= 0: #only proceed if direction is valid
    noNeighbours = True

    while noNeighbours:
      for brick in block.bricks:
        colNum = self.calcRowCol(brick.x, GRID_X)
        rowNum = self.calcRowCol(brick.y, GRID_Y)
        
        if rowNum < len(self.gridMap):
          if direction == 'left':
            if self.gridMap[rowNum][colNum - 1] != '0':
              noNeighbours = False
          elif direction == 'right' and colNum + 1 < len(self.gridMap[rowNum]):
            if self.gridMap[rowNum][colNum + 1] != '0':
              noNeighbours = False
        if rowNum <= len(self.gridMap) and direction == 'down':
          if rowNum == 0:
            noNeighbours = False
          elif self.gridMap[rowNum - 1][colNum] != '0':
            noNeighbours = False
      return noNeighbours

  def populate(self, block):
    continueGame = True #assume that the block is going to occupy empty cells
    
    for brick in block.bricks:
      colNum = self.calcRowCol(brick.x, GRID_X)
      rowNum = self.calcRowCol(brick.y, GRID_Y)
      
      #add rows equal to the number of new rows required for each brick in the current orientation
      while rowNum >= len(self.gridMap):
        self.addRow()
      if self.gridMap[rowNum][colNum] == '0':
        self.brick = pyglet.image.create(BRICKSIZE, BRICKSIZE, pattern=pyglet.image.SolidColorImagePattern(color=(block.blockColor)))
        self.gridMap[rowNum][colNum] = pyglet.sprite.Sprite(self.brick, x=brick.x, y=brick.y, batch=self.gridBatch)
      else: # The target cell was already full, the game is over.
        continueGame = False

    return continueGame

  def refresh(self):
    """ Called by self.clearFullLines during the self.handleFullLines routine.
        Correct the y coordinate for each cell in the grid based on the cell's current row/index in the grid
        These coordinates become skewed when one or more lines is filled and popped from the grid self.clearFullLines"""
    for i in range(len(self.gridMap)):
      correctY = GRID_Y + i * BRICKSIZE
      for j in range(len(self.gridMap[i])):
        curCell = self.gridMap[i][j]
        if curCell != '0':
          if curCell.y != correctY:
            curCell.y = correctY

  def handleFullLines(self):
    removeList = self.checkFullLines()
    if removeList:
      self.flashFullLines(removeList)
      pyglet.clock.schedule_once(self.clearFullLines, .1 ,removeList)
      return len(removeList)

  def checkFullLines(self):
    removeList = False
    fullCells = 0
    
    for i in range(len(self.gridMap)):
      fullCells = 0
      for j in range(len(self.gridMap[i])):
        if self.gridMap[i][j] != '0':
          fullCells += 1
        if fullCells == len(self.gridMap[i]):
          if removeList == False:
            removeList = []
          removeList.append(i)

    return removeList

  def flashFullLines(self, removeList):
    for i in range(len(removeList)):
      for j in range(len(self.gridMap[ removeList[i] ])):
        self.gridMap[ removeList[i] ][j].opacity = 128

  def clearFullLines(self, dt, removeList):
    for i in range(len(removeList)):
      self.gridMap.pop(removeList[i] - i) #subtract i from the value at removeList[i] to account for previously removed lines
    self.refresh()

class Menu:
  def __init__(self):
    self.menuBatch = pyglet.graphics.Batch()
    
  def showMenuItems(self, win):
    self.title = pyglet.text.Label("TETRIS",
                      font_name = 'Arial',
                      font_size = 40,
                      color = (255, 255, 255, 255),
                      align = "center",
                      anchor_x = "center",
                      x = win.width / 2,
                      y = win.height / 2,
                      batch = self.menuBatch)
    self.play = pyglet.text.Label("Press Any Key Start",
                      font_name = 'Arial',
                      font_size = 20,
                      color = (255, 255, 255, 255),
                      align = "center",
                      anchor_x = "center",
                      x = win.width / 2,
                      y = win.height / 4,
                      batch = self.menuBatch)

""" Main window and related event handlers """
window = pyglet.window.Window(WIDTH, HEIGHT)
window.set_vsync(False)

@window.event
def on_key_press(symbol, mods):  #handles key presses that aren't processed if the key is held down
  curInput.keyPress(symbol, curGame)

@window.event
def on_draw():
  if curGame.gameActive:
    window.clear()
    curGame.curGrid.gridBackground.draw()
    curGame.curGrid.gridBatch.draw()
    curInfo.infoBatch.draw()
    curGame.nextBlock.blockBatch.draw()
    curGame.curBlock.blockBatch.draw()
    if curGame.gamePaused:
      curInfo.msgText.text = "Game Paused"
      curInfo.msgBatch.draw()
    if curGame.gameOver:
      curInfo.msgText.text = "GAME OVER"
      curInfo.msgBatch.draw()
  else:
    window.clear()
    curMenu.menuBatch.draw()

# Track the state of keys pressed and/or held down,
# could have used window.event.on_text_motion but the
# repeat delay causes clunky movement behaviour for this game
userInput = pyglet.window.key.KeyStateHandler()

curMenu = Menu()
curMenu.showMenuItems(window)

curInfo = Info()
curInput = Input()
curGame = Game()

pyglet.clock.schedule_interval(curInput.changeHandler, .1, curGame, curInfo)
pyglet.app.run()