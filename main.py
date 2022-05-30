import tkinter
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
boardChanged = True
# Helper list to iterate over all of a node's neighbors
DIRECTIONS = ["left", "top", "right", "bottom"]
MOVES = []
# Pixel distance between each node on the Hashi website
NODE_DISTANCE = 18

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

  def connect(self, dir1, dir2, count):
    global boardChanged
    boardChanged = True

    self.bridges[dir1] += count # set this node's bridge
    self.value -= count # decrease this node's count
    self.neighbors[dir1].bridges[dir2] += count # set neighbor's bridge
    self.neighbors[dir1].value -= count # set neighbor's value

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

    MOVES.append(Move(self.x, self.y, self.neighbors[dir1].x, self.neighbors[dir1].y, count))
    debug(MOVES[-1])
    printBoard()

  def hasNeighbor(self, dir):
    if not self.neighbors[dir]:
      return False

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
    printBoard()

  def __repr__(self) -> str:
    return f"{self.value} ({self.x}, {self.y})"

class Move:
  def __init__(self, x1, y1, x2, y2, value) -> None:
    self.x1 = x1
    self.y1 = y1
    self.x2 = x2
    self.y2 = y2
    self.value = value

  def __repr__(self) -> str:
    return f"({self.x1}, {self.y1}) ({self.x2}, {self.y2}) => {self.value}"

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

  for i in range(len(BOARD)):
    for j in range(len(BOARD[i])):
      node = BOARD[i][j]
      if isinstance(node, Node):
        node.neighbors["left"] = getLeftNeighbor(node.x - 1, node.y)
        node.neighbors["top"] = getTopNeighbor(node.x, node.y - 1)
        if node.neighbors["left"]:
          node.neighbors["left"].neighbors["right"] = node
        if node.neighbors["top"]:
          node.neighbors["top"].neighbors["bottom"]  = node

def getBoardHTML(url, height, width):
  for i in range(height):
    BOARD.append([])
    for j in range(width):
      BOARD[i].append(None)

  chrome_options = Options()
  chrome_options.add_argument("--headless")

  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  driver.get(url)
  # bridges = driver.find_element(by=By.CLASS_NAME, value="board-bridges").find_elements(by=By.CSS_SELECTOR, value="*")
  nodes = driver.find_element(by=By.CLASS_NAME, value="board-tasks").find_elements(by=By.XPATH, value="*")

  for element in nodes:
    value = int(element.text)
    style = element.get_attribute("style")
    # guaranteed to be integer values divisible by 18 (node distance)
    y = int(int(style.split("top: ")[1].split("px;")[0]) / NODE_DISTANCE)
    x = int(int(style.split("left: ")[1].split("px;")[0]) / NODE_DISTANCE)
    print(x)
    print(y)

    left = getLeftNeighbor(x, y)
    top = getTopNeighbor(x, y)
    newNode = Node(value, x, y, left, top)
    BOARD[y][x] = newNode
    if left:
      left.neighbors["right"] = newNode
    if top:
      top.neighbors["bottom"]  = newNode
  driver.close()

def getLeftNeighbor(x, y):
  for i in range(x, -1, -1):
    if BOARD[y][i]:
      return BOARD[y][i]

def getTopNeighbor(x, y):
  for i in range(y, -1, -1):
    if BOARD[i][x]:
      return BOARD[i][x]

def solve():
  global boardChanged
  printBoard()

  while boardChanged:
  # for i in range(1):
    while boardChanged:
      boardChanged = False
      for i in range(len(BOARD)):
        for j in range(len(BOARD[i])):
          node = BOARD[i][j]
          if isinstance(node, Node):
              print(f"DOING {node}")
              finishNode(node)
              dontDirectConnect1Or2Nodes(node)
              addPartialBridgesToNode(node)
              # addPartialBridgesToOddNode(node)
    # Ran after guaranteed checks
    print("board stopped changing")
    pathFound = False
    for i in range(len(BOARD)):
      if pathFound: break
      for j in range(len(BOARD[i])):
        node = BOARD[i][j]
        if checkForContinuity(node):
          pathFound = True
          break

  printBoard()
  print(MOVES)
  return BOARD

def checkForContinuity(node):
  if not isinstance(node, Node) or node.value != 1: return False
  possibleConnections = []
  # iterate until we run out of full nodes
  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.bridges[dir] == 0:
      possibleConnections.append(dir)

  for connectionDir in possibleConnections:
    debug(f"testing continuity on {node}")
    node.connect(connectionDir, getInverseDirection(connectionDir), 1)

    emptyNodeFound = False
    nodes = []
    visited = [node]
    for dir in DIRECTIONS:
      if node.hasNeighbor(dir) and node.neighbors[dir].value == 0:
        nodes.append(node.neighbors[dir])

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

    node.removeLastConnection(connectionDir, getInverseDirection(connectionDir))
    if not emptyNodeFound:
      possibleConnections.remove(connectionDir)

  if len(possibleConnections) == 1:
    debug(f"adding for continuity: {node}")
    node.connect(possibleConnections[0], getInverseDirection(possibleConnections[0]), 1)
    return True
  return False

# Uses original value of node instead of node.value
# If a 1 only has 1 non-one neighbor, connect it.
# Solo 1's cannot connect to each other
def dontDirectConnect1Or2Nodes(node):
  if not isinstance(node, Node): return
  if (node.originalValue != 1 or node.value != 1) and (node.originalValue != 2 or node.value != 2): # pure 2
    return

  # print("HERE")
  # print(node)
  otherNeighbors = []
  for dir in DIRECTIONS:
    if node.hasNeighbor(dir):

      # print(node.neighbors[dir].originalValue)
      # print(node.neighbors[dir].value)
      if node.neighbors[dir].originalValue != node.originalValue or node.neighbors[dir].value != node.originalValue:
        otherNeighbors.append(dir)

  # print(otherNeighbors)

  if len(otherNeighbors) == 1:
    debug(f"connecting 1 to only possible {node}")
    node.connect(otherNeighbors[0], getInverseDirection(otherNeighbors[0]), 1)
    return True
  return False


# Should connect all these nodes with a 1 bridge, repeats
# similar logic for any other odd nodes since they behave the         3 _ 3
# same for different numbers of neighbors (7 has guaranteed 1         _
# nodes on all 4 sides)                                               3
def addPartialBridgesToOddNode(node: Node):
  if not isinstance(node, Node) or (node.value != 1 and node.value != 3 and node.value != 5 and node.value != 7):
    return
  bridgesToBuild = []

  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      bridgesToBuild.append(dir)

  if len(bridgesToBuild) == int(node.value / 2 + 1):
    for dir in bridgesToBuild:
      node.connect(dir, getInverseDirection(dir), 1)
    return True
  return False

def addPartialBridgesToNode(node: Node):
  if not isinstance(node, Node) or node.value == 0:
  #  or (node.originalValue != 1 and node.originalValue != 3 and node.originalValue != 5 and node.originalValue != 7):
    return
  bridgesToBuild = {}

  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      bridgesToBuild[dir] = min(min(2, node.neighbors[dir].value), 2 - node.bridges[dir])

  print(bridgesToBuild)
  # originalValue = node.value
  for key in bridgesToBuild:
    totalBridges = 0
    for key2 in bridgesToBuild:
      if key != key2:
        totalBridges += bridgesToBuild[key2]
    print(f"total without {key} = {totalBridges}")
    if totalBridges < node.value:
      print("CONNECTING " + key)
      node.connect(key, getInverseDirection(key), 1)
      bridgesToBuild[key] -= 1


  # print(bridgesToBuild)
  # if len(bridgesToBuild) == int(node.originalValue / 2 + 1):
  #   for dir in bridgesToBuild:
  #     node.connect(dir, getInverseDirection(dir), 1)
  #   return True

def finishNode(node: Node):
  # debug(f"FINISHNODE: RUNNING ON {node}")
  if not isinstance(node, Node) or node.value == 0: return
  bridgesToBuild = {}
  bridgeCount = 0

  for dir in DIRECTIONS:
    if node.hasNeighbor(dir) and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      addition = 1 if node.bridges[dir] == 1 else min(node.value, min(node.neighbors[dir].value, 2))
      bridgesToBuild[dir] = addition
      bridgeCount += addition

  print(bridgeCount)
  if bridgeCount == node.value:
    # debug(f"finishing {node}")
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

def debug(line):
  if False:
    print(line)

def getInverseDirection(dir):
  if dir == "left": return "right"
  elif dir == "top": return "bottom"
  elif dir == "right": return "left"
  elif dir == "bottom": return "top"

if __name__ == "__main__":
  import sys
  if len(sys.argv) == 1:
    getBoardHTML(HASHI_MONTHLY_URL_50x40, 50, 40)
  else:
    useSpecificBoard()
  solve()
