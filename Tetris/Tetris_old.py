# python 2.7.3
# pyglet 1.2alpha1

import pyglet
import random
import math


""" Define bounds of play area and starting position for new blocks"""
""" These dimensions should all be evenly divisible by BRICKSIZE   """
# window start size
START_WIDTH = 400
START_HEIGHT = 300
# boundaries of the play grid
MIN_Y = 10
MAX_Y = 260
MIN_X = 50
MAX_X = 210
#  coordinates for where the current block starts dropping
START_X = 130
START_Y = 260
#  coordinatess for where the upcoming block is displayed
PREVIEW_X = 300
PREVIEW_Y = 260
#  length of single brick side (bricks are the squares that compose blocks)
BRICKSIZE = 10

LINES_PER_LEVEL = 5

class Game:
  def __init__(self):
    self.gameState = False
    self.difficulty = 1
    self.dropRate = 0.52
    self.score = 0
    self.lines = 0
    self.block1 = Block()
    self.block2 = Block()
    self.nextBlock = self.block1
    self.curBlock = self.block2
    self.validMoves = [True, True, True]
    self.autoDrop = False #State modified by activateAutoDrop(), and reset by checkMoveRequest(), at set interval

    self.infoBatch = pyglet.graphics.Batch()
    self.nextText = pyglet.text.Label("Next block:",
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = PREVIEW_X - 25,
                      y = PREVIEW_Y + 20,
                      batch = self.infoBatch)
    self.scoreText = pyglet.text.Label("Score: " + str(self.score),
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = PREVIEW_X - 25,
                      y = PREVIEW_Y - 50,
                      batch = self.infoBatch)
    self.levelText = pyglet.text.Label("Level: " + str(self.difficulty),
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = PREVIEW_X - 25,
                      y = PREVIEW_Y - 70,
                      batch = self.infoBatch)
    self.linesText = pyglet.text.Label("Lines: " + str(self.lines),
                      font_name = 'Arial',
                      font_size = 12,
                      color = (255, 255, 255, 255),
                      align = "left",
                      x = PREVIEW_X - 25,
                      y = PREVIEW_Y - 90,
                      batch = self.infoBatch)

  def refresh(self):
    self.gameState = False
    self.difficulty = 1
    self.dropRate = 0.52
    self.score = 0
    self.lines = 0

  def setDifficulty(self, x):
    if x >= 1 and x <= 25:
      self.difficulty = x
      self.levelText.text = "Level: " + str(self.difficulty)
      self.dropRate = 0.51 - 0.02 * self.difficulty # Fastest possible dropRate is .001 at difficulty 25
 
  def addToScore(self, x):
    self.score += x
    self.scoreText.text = "Score: " + str(self.score)
    
  def addToLines(self, x):
    self.lines += x
    self.linesText.text = "Lines: " + str(self.lines)
    if self.lines >= LINES_PER_LEVEL * self.difficulty:
      self.setDifficulty(self.difficulty + 1)
     
  def newBlock(self, grid):
    if self.nextBlock == self.block1:
      self.curBlock = self.block1
      self.curBlock.updatePosition(START_X, START_Y)
      self.block2 = Block()
      self.nextBlock = self.block2    
    else:
      self.curBlock = self.block2
      self.curBlock.updatePosition(START_X, START_Y)
      self.block1 = Block()
      self.nextBlock = self.block1
    
    pyglet.clock.unschedule(self.activateAutoDrop)
    pyglet.clock.schedule_interval(self.activateAutoDrop, self.dropRate)
    pyglet.clock.unschedule(self.changeHandler)
    pyglet.clock.schedule_interval(self.changeHandler, .1, self.curBlock, grid)
    
  def changeHandler(self, dt, block, grid):
    #dt is a dummy parameter to handle timeshift arg passed by pyglet.clock.schedule_interval()
    self.checkMoveRequests(block, grid)
    if self.validMoves[2] == False: #the block is on top of brick in the grid or is at the bottom of the grid
      if grid.populate(block):
        linesRemoved = grid.handleFullLines()
        if linesRemoved:
          self.updateGameInfo(linesRemoved)
        self.newBlock(grid)
      else:
        self.gameOver()
  
  def gameOver(self):
    pyglet.clock.unschedule(self.activateAutoDrop)
    pyglet.clock.unschedule(self.changeHandler)
    self.gameState = "over"
    self.overTxt = pyglet.text.Label('GAME OVER',
                      font_name = 'Times New Roman',
                      font_size = 24,
                      color = (255, 255, 255, 255),
                      align = "center",
                      anchor_x = "center",
                      x = (MAX_X - MIN_X) / 2 + MIN_X,
                      y = MAX_Y - (BRICKSIZE * 4),
                      batch = self.infoBatch)
    
  def updateGameInfo(self, linesRemoved):
    self.addToScore(math.factorial(linesRemoved) * self.difficulty)
    self.addToLines(linesRemoved)

  def checkValidMoves(self, block, grid):
    '''detect if the block borders any bricks in the grid, or with the boundaries of the grid'''
    self.validMoves = [True, True, True]
    for i in range(4):
      curX = block.bricks[i].x
      curY = block.bricks[i].y

      #Restrict movment if the block is on the grid border
      if curX == MIN_X:
        self.validMoves[0] = False #left movement restricted
      elif curX == MAX_X - BRICKSIZE: #MAX_X adujsted by BRICKSIZE to account for curX referncing the bottom left of the brick
        self.validMoves[1] = False #right movement restricted
      if curY == MIN_Y:
        self.validMoves[2] = False #down movement restricted

      for j in range(3):
        #don't let the block trespass on existing bricks
        if self.validMoves[j]: #start with neighbours to the left, if we aren't at the border
          self.validMoves[j] = grid.checkNeighbour(block, j)

  def checkMoveRequests(self, block, grid):
    win.push_handlers(userInput)
    #determine valid moves
    self.checkValidMoves(block, grid)

    #check DOWN Requests first so that they take priority
    #this behavior feels closer to the original tetris
    if self.validMoves[2]:
      if userInput[pyglet.window.key.DOWN] or self.autoDrop:
        block.updatePosition(block.refX, block.refY - BRICKSIZE)
        #Deactivate autoDrop
        self.autoDrop = False
        #update valid moves based on the updated position
        self.checkValidMoves(block, grid) 
    if self.validMoves[0]:
      if userInput[pyglet.window.key.LEFT]:
        block.updatePosition(block.refX - BRICKSIZE, block.refY)
        #update valid moves based on the updated position
        self.checkValidMoves(block, grid)
    if self.validMoves[1]:
      if userInput[pyglet.window.key.RIGHT]:
        block.updatePosition(block.refX + BRICKSIZE, block.refY)

  def activateAutoDrop(self, dt):
    self.autoDrop = True

class Block:
  def __init__ (self):
    self.brickLayout = self.randomShape()
    self.blockOrientation = 0
    self.blockColor = self.randomColor()

    self.refX = PREVIEW_X
    self.refY = PREVIEW_Y

    self.blockBatch = pyglet.graphics.Batch()
    self.brick = pyglet.image.create(BRICKSIZE, BRICKSIZE, pattern=pyglet.image.SolidColorImagePattern(color=(self.blockColor)))

    self.bricks = [pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch),
                   pyglet.sprite.Sprite(self.brick, batch=self.blockBatch)]

    self.setCoordinates()

  def setCoordinates(self): 
    for i in range(4):
      self.bricks[i].x = self.refX + self.brickLayout[self.blockOrientation][i][0]
      self.bricks[i].y = self.refY + self.brickLayout[self.blockOrientation][i][1]

  def rotate(self):
    #update layoutPosition to the next possible position depending on the number of possibles in the current brickLoyout
    if self.blockOrientation + 1 < len(self.brickLayout):
      self.blockOrientation += 1
    else:
      self.blockOrientation = 0

    self.setCoordinates()

  def updatePosition(self, x, y):
    self.refX = x
    self.refY = y
    self.setCoordinates()

  def randomColor(self):
    r = random.randint(1,7)

    if r == 1:
      # red
      color = (200, 0, 0, 255)
    elif r == 2:
      # green
      color = (0, 150, 0, 255)
    elif r == 3:
      # blue
      color = (0, 0, 200, 255)
    elif r == 4:
      # yellow
      color = (238, 238, 0, 255)
    elif r == 5:
      # purple
      color = (104, 34, 139, 255)
    elif r == 6:
      # orange
      color = (255, 127, 36, 255)
    elif r == 7:
      # tourqouise
      color = (112, 219, 219, 255)
    
    return color
 
  def randomShape(self):
    """ Return a random 3 dimension array of brick cooridantes
      element 1 = one of four possible orientations, progressing clock-wise
      element 2 = specific brick in the shape
      element 3 = x, y adjustment coordinates of the brick."""
    r = random.randint(1,7)
  
    if r == 1:
      # shape- T
      shape = [ [ [0,0], [-10,0], [10,0], [0,-10] ],
                [ [0,0], [-10,0], [0,-10], [0,10] ],
                [ [0,0], [-10,0], [10,0], [0,10] ],
                [ [0,0], [0,10], [10,0], [0,-10] ] ]
    elif r == 2:
      # shape- L
      shape = [ [ [0,0], [-10,0], [10,0], [-10,-10] ],
                [ [0,0], [0,-10], [0,10], [-10,10] ],
                [ [0,0], [-10,0], [10,0], [10,10] ],
                [ [0,0], [0,-10], [0,10], [10,-10] ] ]
    elif r == 3:
      # shape-  reverse L
      shape = [ [ [0,0], [-10,0], [10,0], [10,-10] ],
                [ [0,0], [0,-10], [0,10], [-10,-10] ],
                [ [0,0], [-10,0], [10,0], [-10,10] ],
                [ [0,0], [0,-10], [0,10], [10,10] ] ]
    elif r == 4:
      # shape- square
      shape = [ [ [0,0], [-10,0], [-10,-10], [0,-10] ] ]
    elif r == 5:
      # shape- line
      shape = [ [ [0,0], [-10,0], [10,0], [20,0] ],
                [ [0,0], [0,10], [0,-10], [0,-20] ] ]
    elif r == 6:
      # shape- S
      shape = [ [ [0,0], [10,0], [-10,-10], [0,-10] ],
                [ [0,0], [0,10], [10,0], [10,-10] ] ]
    else:
      # shape- Z
      shape = [ [ [0,0], [-10,0], [0,-10], [10,-10] ],
                [ [0,0], [10,0], [10,10], [0,-10] ] ]
    return shape

class Grid:
  def __init__ (self):
    self.gridBatch = pyglet.graphics.Batch()

    #determine how many cells wide and tall the play grid is
    self.gridWidth = (MAX_X - MIN_X) / BRICKSIZE
    self.gridHeight = (MAX_Y - MIN_Y) / BRICKSIZE

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
    self.gridMap.append(list( '0' * self.gridWidth))
    
  def calcRowCol(self, curLoc, boundary):
      if (curLoc - boundary) != 0:
        return (curLoc - boundary) / BRICKSIZE
      else:
        return 0

  def checkNeighbour(self, block, direction):
    ''' direction should be 0 for left, 1 for right, and 2 for down '''
    if 3 > direction >= 0: #only proceed if direction is valid
      noNeighbours = True

      while noNeighbours:
        for i in range(4):
          colNum = self.calcRowCol(block.bricks[i].x, MIN_X)
          rowNum = self.calcRowCol(block.bricks[i].y, MIN_Y)
        
          if rowNum < len(self.gridMap):
            if direction == 0:
              if self.gridMap[rowNum][colNum - 1] != '0':
                noNeighbours = False
            elif direction == 1 and colNum + 1 < len(self.gridMap[rowNum]):
              if self.gridMap[rowNum][colNum + 1] != '0':
                noNeighbours = False
          if rowNum <= len(self.gridMap) and direction == 2:
            if rowNum == 0:
              noNeighbours = False
            elif self.gridMap[rowNum - 1][colNum] != '0':
              noNeighbours = False
        return noNeighbours

  def populate(self, block):
    continueGame = True #assume that the block is going to occupy empty cells
    
    for i in range(4):
      colNum = self.calcRowCol(block.bricks[i].x, MIN_X)
      rowNum = self.calcRowCol(block.bricks[i].y, MIN_Y)
      
      #add rows equal to the number of new rows required for each brick in the current orientation
      while rowNum >= len(self.gridMap):
        self.addRow()
      if self.gridMap[rowNum][colNum] == '0':
        self.brick = pyglet.image.create(BRICKSIZE, BRICKSIZE, pattern=pyglet.image.SolidColorImagePattern(color=(block.blockColor)))
        self.gridMap[rowNum][colNum] = pyglet.sprite.Sprite(self.brick, x=block.bricks[i].x, y=block.bricks[i].y, batch=self.gridBatch)
      else: # The target cell was already full, the game is over.
        continueGame = False

    return continueGame

  def refresh(self):
    """ Called by self.clearFullLines during the self.handleFullLines routine.
        Correct the y coordinate for each cell in the grid based on the cell's current row/index in the grid
        These coordinates become skewed when one or more lines is filled and popped from the grid self.clearFullLines"""
    for i in range(len(self.gridMap)):
      correctY = MIN_Y + i * BRICKSIZE
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
win = pyglet.window.Window(START_WIDTH, START_HEIGHT)
userInput = pyglet.window.key.KeyStateHandler() #used to track the state of keys that are held down

@win.event
def on_key_press(symbol, mods):  #handles key presses that aren't processed if the key is held down
  if curGame.gameState == True:
    if symbol == pyglet.window.key.UP:
      curGame.curBlock.rotate()
  elif curGame.gameState == "over":
    curGame.gameState = False
  else:
    curGame.refresh()
    curGame.gameState = True
    curGame.newBlock(curGrid)
    
@win.event
def on_draw():
  if curGame.gameState == True:
    win.clear()
    curGrid.gridBatch.draw()
    curGame.infoBatch.draw()
    curGame.nextBlock.blockBatch.draw()
    curGame.curBlock.blockBatch.draw()
  elif curGame.gameState == "over":
    win.clear()
    curGrid.gridBatch.draw()
    curGame.infoBatch.draw()
  else:
    win.clear()
    curMenu.menuBatch.draw()

curGrid = Grid()
curMenu = Menu()
curMenu.showMenuItems(win)
curGame = Game()

pyglet.app.run()
