import sys
import tkinter as tk
import tkinter.font as tkfont

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

HASHI_EASY_URL_7x7 = "https://www.puzzle-bridges.com/"
HASHI_HARD_URL_7x7 = "https://www.puzzle-bridges.com/?size=2"
HASHI_EASY_URL_25x25 = "https://www.puzzle-bridges.com/?size=9"
HASHI_HARD_URL_25x25 = "https://www.puzzle-bridges.com/?size=11"
HASHI_MONTHLY_URL_50x40 = "https://www.puzzle-bridges.com/?size=14"

# The game board, used everywhere
BOARD = []
ORIGINAL_BOARD = []
# Updated if a move is made. Used to detect when the game is over
boardChanged = True
#
currentMoveIndex = 0

# Helper list to iterate over all of a node's neighbors
DIRECTIONS = ["left", "top", "right", "bottom"]
# Ordered list of moves made
MOVES = []
# Pixel distance between each node on the Hashi website
NODE_DISTANCE = 18

# UI Values
BORDER = 10
DEFAULT_BRIDGE_COLOR = "black"
RECENT_BRIDGE_COLOR = "green"
FINISHED_BRIDGE_COLOR = "orange"
HEIGHT = 800
INCREMENT_X = 0 #(HEIGHT - 2 * BORDER) / (len(BOARD[0]) + 1)
INCREMENT_Y = 0 #(HEIGHT - 2 * BORDER) / (len(BOARD) + 1)
NODE_RADIUS = 0 #radius = INCREMENT_X / 2
WIDTH = 1000

window = tk.Tk()
canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")

class Node:
  def __init__(self, value, x, y, left=None, top=None, right=None, bottom=None) -> None:
    self.originalValue = value
    self.value = value
    self.x = x
    self.y = y

    self.neighbors = {
      "left": left,
      "top": top,
      "right": right,
      "bottom": bottom
    }

    self.bridges = {
      "left": 0,
      "top": 0,
      "right": 0,
      "bottom": 0
    }

  def copy(self):
    # Neighbors will be reset since they will reference completely new nodes
    return Node(self.value, self.x, self.y)

  def connect(self, dir1, dir2, count):
    global boardChanged
    boardChanged = True

    self.bridges[dir1] += count # set this node's bridge
    self.value -= count # decrease this node's count
    self.neighbors[dir1].bridges[dir2] += count # set neighbor's bridge
    self.neighbors[dir1].value -= count # set neighbor's value

    # Draw the bridge between the two nodes
    if self.x != self.neighbors[dir1].x:
      startx = min(self.x, self.neighbors[dir1].x) + 1
      endx = max(self.x, self.neighbors[dir1].x)
      for i in range(startx, endx):
        BOARD[self.y][i] = "-" if self.bridges[dir1] == 1 else "--"
    else:
      starty = min(self.y, self.neighbors[dir1].y) + 1
      endy = max(self.y, self.neighbors[dir1].y)
      for i in range(starty, endy):
        BOARD[i][self.x] = "|" if self.bridges[dir1] == 1 else "H"

    MOVES.append(Move(self.x, self.y, self.neighbors[dir1].x, self.neighbors[dir1].y, count, self.bridges[dir1]))
    # print(MOVES[-1])
    # printBoard()

  # Method to check if a node has a neighbor / that neighbor is reachable.
  # If the neighbor is no longer reachable because of another bridge,
  # it is deleted from the current node's neighbor list.
  # Returns True if a valid neighbor is found, False otherwise.
  def hasNeighbor(self, dir):
    if not self.neighbors[dir]:
      return False

    # If there is a bridge that intercepts the path
    # between the neighbor, the node is considered to
    # not have a neighbor anymore
    if self.x != self.neighbors[dir].x:
      startx = min(self.x, self.neighbors[dir].x) + 1
      endx = max(self.x, self.neighbors[dir].x)
      for i in range(startx, endx):
        if BOARD[self.y][i] == "|" or BOARD[self.y][i] == "H":
          self.neighbors[dir] = None
          return False
    else:
      starty = min(self.y, self.neighbors[dir].y) + 1
      endy = max(self.y, self.neighbors[dir].y)
      for i in range(starty, endy):
        if BOARD[i][self.x] == "-" or BOARD[i][self.x] == "--":
          self.neighbors[dir] = None
          return False

    return True

  def removeLastConnection(self, dir1, dir2):
    removed = MOVES.pop()
    self.bridges[dir1] -= removed.value # set this node's bridge
    self.value += removed.value # decrease this node's count
    self.neighbors[dir1].bridges[dir2] -= removed.value # set neighbor's bridge
    self.neighbors[dir1].value += removed.value # set neighbor's value

    # Search between the two nodes and remove
    # any bridges that might have been created
    if self.x != self.neighbors[dir1].x:
      startx = min(self.x, self.neighbors[dir1].x) + 1
      endx = max(self.x, self.neighbors[dir1].x)
      for i in range(startx, endx):
        BOARD[self.y][i] = None
    else:
      starty = min(self.y, self.neighbors[dir1].y) + 1
      endy = max(self.y, self.neighbors[dir1].y)
      for i in range(starty, endy):
        BOARD[i][self.x] = None
    # printBoard()

  def __repr__(self) -> str:
    return f"{self.value} ({self.x}, {self.y})"

class Move:
  def __init__(self, x1, y1, x2, y2, value, total) -> None:
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.value = value
    self.total = total

  def __repr__(self) -> str:
    return f"({self.x1}, {self.y1}) ({self.x2}, {self.y2}) => {self.value}"

# Helper method to test specific boards since the Hashi website URL
# does not update with the game board ids.
# Should operate identically to getBoardHTML without using a ChromeDriver
def useSpecificBoard():
  global BOARD
  BOARD = [
    [Node(2, 0, 0), None, None, Node(1, 3, 0), None, None, Node(2, 6, 0)],
    [None, None, None, None, None, None, None],
    [Node(4, 0, 2), None, None, None, None, None, Node(4, 6, 2)],
    [None, Node(3, 1, 3), None, Node(6, 3, 3), None, Node(4, 5, 3), None],
    [None, None, None, None, None, None, None],
    [None, Node(1, 1, 5), None, None, None, Node(2, 5, 5), None],
    [Node(2, 0, 6), None, None, Node(5, 3, 6), None, None, Node(4, 6, 6)]
  ]

  global INCREMENT_X, INCREMENT_Y, NODE_RADIUS
  INCREMENT_X = (HEIGHT - 2 * BORDER) / (len(BOARD[0]) + 1)
  INCREMENT_Y = (HEIGHT - 2 * BORDER) / (len(BOARD) + 1)
  NODE_RADIUS = INCREMENT_X / 2

  # Calculate neighbors
  for i in range(len(BOARD)):
    for j in range(len(BOARD[i])):
      node = BOARD[i][j]
      if isinstance(node, Node):
        node.neighbors["left"] = getLeftNeighbor(BOARD, node.x - 1, node.y)
        node.neighbors["top"] = getTopNeighbor(BOARD, node.x, node.y - 1)
        # Add the current node to its neighbor's right neighbor field
        if node.neighbors["left"]:
          node.neighbors["left"].neighbors["right"] = node
        # Add the current node to its neighbor's bottom neighbor field
        if node.neighbors["top"]:
          node.neighbors["top"].neighbors["bottom"]  = node

# Given a Hashi URL and height and width, initialize the game board with all available nodes.
def getBoardHTML(url, height, width):
  global INCREMENT_X, INCREMENT_Y, NODE_RADIUS
  INCREMENT_X = (HEIGHT - 2 * BORDER) / (width + 1)
  INCREMENT_Y = (HEIGHT - 2 * BORDER) / (height + 1)
  NODE_RADIUS = INCREMENT_X / 2

  for i in range(height):
    BOARD.append([])
    for j in range(width):
      BOARD[i].append(None)

  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  driver.get(url)
  nodes = driver \
            .find_element(by=By.CLASS_NAME, value="board-tasks") \
            .find_elements(by=By.XPATH, value="*")

  for element in nodes:
    value = int(element.text)
    style = element.get_attribute("style")
    # guaranteed to be integer values divisible by 18 (node distance)
    y = int(int(style.split("top: ")[1].split("px;")[0]) / NODE_DISTANCE)
    x = int(int(style.split("left: ")[1].split("px;")[0]) / NODE_DISTANCE)

    left = getLeftNeighbor(BOARD, x, y)
    top = getTopNeighbor(BOARD, x, y)
    newNode = Node(value, x, y, left, top)
    BOARD[y][x] = newNode
    if left:
      left.neighbors["right"] = newNode
    if top:
      top.neighbors["bottom"]  = newNode
  driver.close()

# Starts at (x, y) and searches left to see
# if there is a node to the left of (x, y)
# Returns that node if it is found, None otherwise
def getLeftNeighbor(board, x, y):
  for i in range(x, -1, -1):
    if board[y][i]:
      return board[y][i]

# Starts at (x, y) and searches up to see
# if there is a node to above (x, y)
# Returns that node if it is found, None otherwise
def getTopNeighbor(board, x, y):
  for i in range(y, -1, -1):
    if board[i][x]:
      return board[i][x]

# Main solver for the Hashi board.
# Global BOARD and MOVE lists are updated with the solution
def solve():
  global boardChanged
  # printBoard()

  while boardChanged:
  # for i in range(1):
    while boardChanged:
      boardChanged = False
      for i in range(len(BOARD)):
        for j in range(len(BOARD[i])):
          node = BOARD[i][j]
          if isinstance(node, Node):
              # print(f"DOING {node}")
              finishNode(node)
              dontDirectConnect1Or2Nodes(node)
              addPartialBridgesToNode(node)
    # Continuity checks are ran after guaranteed checks
    # since they are much more uncommon than guaranteed checks
    bridgeMade = False
    # print("board stopped changing")
    for i in range(len(BOARD)):
      if bridgeMade: break # If a bridge is made, break out of larger for loop
      for j in range(len(BOARD[i])):
        node = BOARD[i][j]
        if checkForContinuity(node):
          bridgeMade = True
          break

  # printBoard()
  # print(MOVES)
  return BOARD

# Checks for continuity starting at "node" since every
# Hashi puzzle must have all nodes connected
# Returns True if a bridge is created, False otherwise
def checkForContinuity(node):
  if not isinstance(node, Node) or node.value != 1: return False
  possibleConnections = []
  # Accumulate the possible bridges we can make
  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.bridges[dir] == 0:
      possibleConnections.append(dir)

  for connectionDir in possibleConnections:
    # test adding this bridge and see if we have continuity across all nodes
    node.connect(connectionDir, getInverseDirection(connectionDir), 1)

    emptyNodeFound = False
    # Search graph until we find a non-complete node -> might preserve continuity
    # or until we run out of nodes -> since it's not the last bridge, we don't have continuity
    nodes = []
    visited = [node]
    for dir in DIRECTIONS:
      if node.hasNeighbor(dir) and node.neighbors[dir].value == 0:
        nodes.append(node.neighbors[dir])

    # iterate until we run out of full nodes
    while (not emptyNodeFound and len(nodes) != 0):
      curr = nodes.pop()
      visited.append(curr)
      if curr.value != 0: # Found a non-completed node, stop searching
        emptyNodeFound = True
        break
      for dir in DIRECTIONS:
        if curr.hasNeighbor(dir):
          if curr.neighbors[dir] not in visited and curr.bridges[dir] > 0:
            if curr.neighbors[dir].value == 0:
              nodes.append(curr.neighbors[dir])
            else:
              emptyNodeFound = True
              break

    # Undo bridge, if an empty node is found it might be added back later
    node.removeLastConnection(connectionDir, getInverseDirection(connectionDir))
    if not emptyNodeFound:
      possibleConnections.remove(connectionDir)

  if len(possibleConnections) == 1:
    node.connect(possibleConnections[0], getInverseDirection(possibleConnections[0]), 1)
    return True
  return False

# Uses original value of node instead of node.value
# If a 1 only has 1 non-one neighbor, connect it.
# Solo 1's cannot connect to each other
# Returns True if a bridge is created, False otherwise
def dontDirectConnect1Or2Nodes(node):
  if not isinstance(node, Node): return
  # Only valid for checking "pure" 1s or 2s (1s or 2s that have no active bridges)
  if (node.originalValue != 1 or node.value != 1) and \
     (node.originalValue != 2 or node.value != 2):
    return

  # Search for any possible neighbors that do not include a pure 1 or 2.
  # If this node is a pure 1, ignore other pure 1s.
  # If this node is a pure 2, ignore other pure 2s.
  otherNeighbors = []
  for dir in DIRECTIONS:
    if node.hasNeighbor(dir):
      if node.neighbors[dir].originalValue != node.originalValue or \
          node.neighbors[dir].value != node.originalValue:
        otherNeighbors.append(dir)

  # If there is only one neighbor in the list,
  # we must have at least 1 bridge connecting to them
  if len(otherNeighbors) == 1:
    # print(f"connecting 1 to only possible {node}")
    node.connect(otherNeighbors[0], getInverseDirection(otherNeighbors[0]), 1)
    return True
  return False

# If there are any guarantees for single bridges
# starting from this node, add them.
# Ex. A 5 with 3 neighbors must have at least 1 bridge
# conencting each of them, so this method should detect that.
# Similarly, a 4 with a 1 neighbor and 2 other neighbors must
# have at least 1 bridge to each of those 2 other neighbors.
# Returns True if a bridge is created, False otherwise
def addPartialBridgesToNode(node: Node):
  if not isinstance(node, Node) or node.value == 0: return
  bridgesToBuild = {}

  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      bridgesToBuild[dir] = min(min(2, node.neighbors[dir].value), 2 - node.bridges[dir])

  bridgeAdded = False
  for key in bridgesToBuild:
    totalBridges = 0
    for key2 in bridgesToBuild:
      if key != key2:
        totalBridges += bridgesToBuild[key2]
    if totalBridges < node.value:
      node.connect(key, getInverseDirection(key), 1)
      bridgeAdded = True
      bridgesToBuild[key] -= 1
  return bridgeAdded

# "Finishes" a nodes remaining bridges if all the possible bridges are guaranteed.
# Ex. A 4 with 2 neighbors can be finished with 2 double bridges.
# Returns True if a bridge is created, False otherwise
def finishNode(node: Node):
  if not isinstance(node, Node) or node.value == 0: return
  bridgesToBuild = {}
  bridgeCount = 0

  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      addition = 1 if node.bridges[dir] == 1 else min(node.value, min(node.neighbors[dir].value, 2))
      bridgesToBuild[dir] = addition
      bridgeCount += addition

  if bridgeCount == node.value:
    for dir in bridgesToBuild:
      node.connect(dir, getInverseDirection(dir), bridgesToBuild[dir])
    return True
  return False

def printBoard():
  for i in range(len(BOARD)):
    line = ""
    for j in range(len(BOARD[i])):
      node = BOARD[i][j]
      if isinstance(node, Node):
        line += f" {str(BOARD[i][j].value)} "
      elif node:
        if node == "-":
          line += "---"
        elif node == "--":
          line += "==="
        else:
          line += f" {node[0]} "
      else:
        line += " _ "
    print(line)
  print("")

# Helper method to get the inverse to whatever direction is passed in.
# Any operation on a node's neighbor should mutate the
# neighbor in exactly the opposite way. Adding a left bridge
# should add a right bridge to the neighbor, etc.
def getInverseDirection(dir):
  if dir == "left": return "right"
  elif dir == "top": return "bottom"
  elif dir == "right": return "left"
  elif dir == "bottom": return "top"

def copyBoard(board):
  copy = []
  for i in range(len(board)):
    copy.append([])
    for j in range(len(board[i])):
      copy[i].append(None)

  for i in range(len(board)):
    for j in range(len(board[i])):
      oldNode = BOARD[i][j]
      if isinstance(oldNode, Node):
        node = oldNode.copy()
        copy[i][j] = node
        node.neighbors["left"] = getLeftNeighbor(copy, node.x - 1, node.y)
        node.neighbors["top"] = getTopNeighbor(copy, node.x, node.y - 1)
        # Add the current node to its neighbor's right neighbor field
        if node.neighbors["left"]:
          node.neighbors["left"].neighbors["right"] = node
        # Add the current node to its neighbor's bottom neighbor field
        if node.neighbors["top"]:
          node.neighbors["top"].neighbors["bottom"]  = node
  return copy

def nextButtonOnClick():
  global currentMoveIndex

  gameOver = currentMoveIndex == len(MOVES)
  defaultColor = DEFAULT_BRIDGE_COLOR if not gameOver else FINISHED_BRIDGE_COLOR

  if currentMoveIndex < len(MOVES):
    drawNextMove(currentMoveIndex, defaultColor, RECENT_BRIDGE_COLOR)
    currentMoveIndex += 1
  elif currentMoveIndex == len(MOVES): # puzzle finished, all bridges are golden
    for i in range(currentMoveIndex):
      drawNextMove(i, defaultColor, FINISHED_BRIDGE_COLOR)
    currentMoveIndex += 1

def drawNextMove(i, defaultColor, recentColor):
  if i < len(MOVES):
    drawBridge(MOVES[i], recentColor)
    drawNode(MOVES[i].x1, MOVES[i].y1)
    drawNode(MOVES[i].x2, MOVES[i].y2)
  if i > 0 and i < len(MOVES):
    drawBridge(MOVES[i - 1], defaultColor)
    drawNode(MOVES[i - 1].x1, MOVES[i - 1].y1)
    drawNode(MOVES[i - 1].x2, MOVES[i - 1].y2)

def prevButtonOnClick():
  global currentMoveIndex
  defaultColor = DEFAULT_BRIDGE_COLOR
  recentColor = RECENT_BRIDGE_COLOR

  if currentMoveIndex > 0:
    currentMoveIndex -= 1

  if currentMoveIndex == len(MOVES): # Undo all golden lines
    for i in range(currentMoveIndex):
      drawBridge(MOVES[i], defaultColor)
    drawBridge(MOVES[i], recentColor)
  elif currentMoveIndex >= 0:
    move = MOVES[currentMoveIndex]
    drawBridge(move, "white") # Erase previous line
    if move.x1 != move.x2: # Draw horizontal gridlines
      xmin = min(move.x1, move.x2)
      xmax = max(move.x1, move.x2)
      x1 = BORDER + INCREMENT_X * (xmin + 1) + NODE_RADIUS
      x2 = BORDER + INCREMENT_X * (xmax + 1) - NODE_RADIUS
      y = BORDER + INCREMENT_Y * (move.y1 + 1)
      drawGridLine(x1, y, x2, y) # Redraw main gridline
      for i in range(xmin, xmax): # Redraw crossing gridlines
        x = BORDER + INCREMENT_X * (i + 1)
        drawGridLine(x, y - 10, x, y + 10)
    else: # Draw vertical gridlines
      miny = min(move.y1, move.y2)
      maxy = max(move.y1, move.y2)
      y1 = BORDER + INCREMENT_Y * (miny + 1) + NODE_RADIUS
      y2 = BORDER + INCREMENT_Y * (maxy + 1) - NODE_RADIUS
      x = BORDER + INCREMENT_X * (move.x1 + 1)
      drawGridLine(x, y1, x, y2) # Redraw main gridline
      for i in range(miny, maxy): # Redraw crossing gridlines
        y = BORDER + INCREMENT_Y * (i + 1)
        drawGridLine(x - 10, y, x + 10, y)
    # Redraw nodes
    drawNode(move.x1, move.y1)
    drawNode(move.x2, move.y2)

    # Draw most recent bridge
    if currentMoveIndex > 0:
      drawBridge(MOVES[currentMoveIndex - 1], recentColor)


def solveButtonOnClick():
  global currentMoveIndex
  currentMoveIndex = len(MOVES)
  nextButtonOnClick()

def clearButtonOnClick():
  global currentMoveIndex
  for i in range(currentMoveIndex):
    prevButtonOnClick()

def render():
  drawGrid()
  drawNodes()

  gameOver = currentMoveIndex == len(MOVES)
  defaultColor = DEFAULT_BRIDGE_COLOR if not gameOver else FINISHED_BRIDGE_COLOR
  recentColor = RECENT_BRIDGE_COLOR if not gameOver else FINISHED_BRIDGE_COLOR

  for i in range(currentMoveIndex - 1):
    if i < len(MOVES):
      drawBridge(MOVES[i], defaultColor)
  if currentMoveIndex > 0 and currentMoveIndex <= len(MOVES):
    drawBridge(MOVES[currentMoveIndex - 1], recentColor)

  drawButtons()

def drawBridge(move: Move, color):
  strokeWidth = max(int(NODE_RADIUS / 8), 3)
  doubleSpace = max(int(NODE_RADIUS / 8), 2) # Space between a double bridge's 2 bridges
  if move.x1 != move.x2: # Draw horizontal bridge
    x1 = min(move.x1, move.x2)
    x2 = max(move.x1, move.x2)
    x1 = BORDER + INCREMENT_X * (x1 + 1) + NODE_RADIUS
    x2 = BORDER + INCREMENT_X * (x2 + 1) - NODE_RADIUS
    y = BORDER + INCREMENT_Y * (move.y1 + 1)
    if move.total == 1:
      canvas.create_line(x1, y, x2, y, width=strokeWidth, fill=color)
    else:
      canvas.create_line(x1, y, x2, y, width=strokeWidth, fill="white")
      canvas.create_line(x1, y - doubleSpace, x2, y - doubleSpace, width=strokeWidth, fill=color)
      canvas.create_line(x1, y + doubleSpace, x2, y + doubleSpace, width=strokeWidth, fill=color)
  else: # Draw vertical bridge
    y1 = min(move.y1, move.y2)
    y2 = max(move.y1, move.y2)
    y1 = BORDER + INCREMENT_Y * (y1 + 1) + NODE_RADIUS
    y2 = BORDER + INCREMENT_Y * (y2 + 1) - NODE_RADIUS
    x = BORDER + INCREMENT_X * (move.x1 + 1)
    if move.total == 1:
      canvas.create_line(x, y1, x, y2, width=strokeWidth, fill=color)
    else:
      canvas.create_line(x, y1, x, y2, width=strokeWidth, fill="white")
      canvas.create_line(x - doubleSpace, y1, x - doubleSpace, y2, width=strokeWidth, fill=color)
      canvas.create_line(x + doubleSpace, y1, x + doubleSpace, y2, width=strokeWidth, fill=color)

def drawNode(x, y):
  node = ORIGINAL_BOARD[y][x]
  if isinstance(node, Node):
    x1 = BORDER + INCREMENT_X * (x + 1) - NODE_RADIUS
    y1 = BORDER + INCREMENT_Y * (y + 1) - NODE_RADIUS
    x2 = x1 + 2 * NODE_RADIUS
    y2 = y1 + 2 * NODE_RADIUS
    width = max(int(NODE_RADIUS / 15), 2)
    canvas.create_oval(x1, y1, x2, y2, fill="white", outline="black", width=width)
    font = tkfont.Font(family="Arial", size=max(int(NODE_RADIUS / 1.5), 10), weight="normal", slant="roman")
    canvas.create_text(x1 + NODE_RADIUS, y1 + NODE_RADIUS, font=font, text=node.value, justify=tk.CENTER)

def drawNodes():
  for y in range(-2, len(ORIGINAL_BOARD) + 2):
    for x in range(-2, len(ORIGINAL_BOARD[0]) + 2):
      if y >= 0 and x >= 0 and y < len(ORIGINAL_BOARD) and x < len(ORIGINAL_BOARD[y]):
        drawNode(x, y)

def drawGridLine(x1, y1, x2, y2):
  canvas.create_line(x1, y1, x2, y2, fill="gray")

def drawGrid():
  for i in range(-2, len(ORIGINAL_BOARD) + 2):
    drawGridLine(BORDER,
                 BORDER + INCREMENT_Y * i,
                 HEIGHT - BORDER,
                 BORDER + INCREMENT_Y * i)
    for j in range(-2, len(ORIGINAL_BOARD[0]) + 2):
      drawGridLine(BORDER + INCREMENT_X * j,
                   BORDER,
                   BORDER + INCREMENT_X * j,
                   HEIGHT - BORDER)

def drawButtons():
  buttonWidth = 10
  buttonHeight = 2

  font = tkfont.Font(family="Arial", size=10, weight="bold", slant="roman")

  prev_button = tk.Button(
    text="Prev Step",
    width=buttonWidth,
    height=buttonHeight,
    bg="lightblue",
    fg="black",
    font=font,
    command=prevButtonOnClick
  )
  prev_button.place(x=WIDTH - 200, y=((HEIGHT / 2) - 25))

  next_button = tk.Button(
    text="Next Step",
    width=buttonWidth,
    height=buttonHeight,
    bg="lightblue",
    fg="black",
    font=font,
    command=nextButtonOnClick
  )
  next_button.place(x=WIDTH - 100, y=((HEIGHT / 2) - 25))

  clear_button = tk.Button(
    text="Clear",
    width=buttonWidth,
    height=buttonHeight,
    bg="lightblue",
    fg="black",
    font=font,
    command=clearButtonOnClick
  )
  clear_button.place(x=WIDTH - 200, y=((HEIGHT / 2) + 25))

  solve_button = tk.Button(
    text="Solve",
    width=buttonWidth,
    height=buttonHeight,
    bg="lightblue",
    fg="black",
    font=font,
    command=solveButtonOnClick
  )
  solve_button.place(x=WIDTH - 100, y=int((HEIGHT / 2) + 25))

def getHashiSiteUrl(size, difficulty):
  baseUrl = "https://www.puzzle-bridges.com/"
  sizes = ["7x7", "10x10", "15x15", "25x25", "special"]
  # Dailies are special easy, weeklies are special medium, monthlies are special hard
  difficulties = ["easy", "medium", "hard"]

  # For some reason the site has these values flipped ???
  if size == "special" and difficulty == "easy":
    return f"{baseUrl}?size=13"
  if size == "special" and difficulty == "medium":
    return f"{baseUrl}?size=12"

  for i in range(len(sizes)):
    for j in range(len(difficulties)):
      if size == sizes[i] and difficulty == difficulties[j]:
        if i == 0 and j == 0:
          return baseUrl
        return f"{baseUrl}?size={(i * len(difficulties) + j)}"

if __name__ == "__main__":
  if "--test" in sys.argv:
    useSpecificBoard()
  else:
    size = "7x7"
    difficulty = "easy"
    if len(sys.argv) >= 3:
      try: # Try to get size argument
        sizeIdx = sys.argv.index("--size")
        size = sys.argv[sizeIdx + 1].lower()
      except:
        try:
          sizeIdx = sys.argv.index("-s")
          size = sys.argv[sizeIdx + 1].lower()
        except:
          pass # continue since size is by default 7x7 already
      try: # Try to get difficulty argument
        difficultyIdx = sys.argv.index("--difficulty")
        difficulty = sys.argv[difficultyIdx + 1].lower()
      except:
        try:
          difficultyIdx = sys.argv.index("-d")
          difficulty = sys.argv[difficultyIdx + 1].lower()
        except:
          pass # continue since size is by default 7x7 already

    url = getHashiSiteUrl(size, difficulty)
    if not url:
      print("\nERROR running program!\n")
      print("Available sizes are 7x7, 10x10, 15x15, 25x25, or special")
      print("Available difficulties are easy, medium, and hard")
      print("  Ex. \"python main.py --size 7x7 --difficulty hard\"")
      print("  or  \"python main.py -s special -d medium\"")
      print("  or (defaults to 7x7 easy) \"python main.py\"")
      sys.exit()

    if "x" in size:
      height = int(size.split("x")[0])
      width = int(size.split("x")[1])
    else: # Special
      if difficulty == "easy":
        height, width = 30, 30
      elif difficulty == "medium":
        height, width = 40, 30
      else:
        height, width = 50, 40
    getBoardHTML(url, height, width)

  ORIGINAL_BOARD = copyBoard(BOARD)
  canvas.pack()
  solve()
  render()

  tk.mainloop()