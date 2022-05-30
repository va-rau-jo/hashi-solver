from msilib.schema import RemoveIniFile
import tkinter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

HASHI_EASY_URL = "https://www.puzzle-bridges.com/"

# The game board, used everywhere
BOARD = []
# Helper list to iterate over all of a node's neighbors
DIRECTIONS = ["left", "top", "right", "bottom"]
# Pixel distance between each node on the Hashi website
NODE_DISTANCE = 18

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
    x = int(int(style.split("top: ")[1].split("px;")[0]) / NODE_DISTANCE)
    y = int(int(style.split("left: ")[1].split("px;")[0]) / NODE_DISTANCE)

    left = getLeftNeighbor(x, y)
    top = getTopNeighbor(x, y)
    newNode = Node(value, x, y, left, top)
    BOARD[y][x] = newNode
    if left:
      left.right = newNode
    if top:
      top.bottom = newNode
  printBoard()
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
  for i in range(len(BOARD)):
    for j in range(len(BOARD[i])):
      finish4Node(BOARD[i][j])

def finish4Node(node):
  if not node or node.value != 4: return

  print(f"RUNNING ON {node}")

  # print(node.neighbors["left"])
  # print(node.neighbors["top"])
  # print(node.neighbors["right"])
  # print(node.neighbors["bottom"])
  bridgesToBuild = {}
  bridgeCount = 0

  for dir in DIRECTIONS:
    if node.neighbors[dir] and node.neighbors[dir].value > 0 and node.bridges[dir] < 2:
      addition = 1 if node.bridges[dir] == 1 else min(node.neighbors[dir].value, 2)
      bridgesToBuild[dir] = [node.neighbors[dir], addition]
      bridgeCount += addition

  if bridgeCount == 4:
    # print("CAN SOLVE")
    # print(node)
    print(bridgesToBuild)
    # for tuple in bridgesToBuild:
      # node.
    return True
  return False

def printBoard():
  print("")
  for i in range(len(BOARD)):
    line = ""
    for j in range(len(BOARD[i])):
      if BOARD[i][j]:
        line += f" {str(BOARD[i][j].value)} "
      else:
        line += " _ "
    print(line)
  print("")

def getInverseDirection(dir):
  if dir == "left": return "right"
  elif dir == "top": return "bottom"
  elif dir == "right": return "left"
  elif dir == "bottom": return "top"

class Node:
  def __init__(self, value, x, y, left=None, top=None, right=None, bottom=None):
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
    self.bridges[dir1] = count # set this node's bridge
    self.value -= count # decrease this node's count
    self.neighbors[dir1].bridges[dir2] = count # set neighbor's bridge
    self.neighbors[dir1].value -= count # set neighbor's value

  def connectLeft(self, count):
    self.connect("left", "right", count)

  def connectTop(self, count):
    self.connect("top", "bottom", count)

  def connectRight(self, count):
    self.connect("right", "left", count)

  def connectBottom(self, count):
    self.connect("bottom", "top", count)

  def __repr__(self) -> str:
    return f"{self.value} ({self.x}, {self.y})"

if __name__ == "__main__":
  getBoardHTML(HASHI_EASY_URL, 7, 7)

  solve()
