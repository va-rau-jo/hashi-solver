from msilib.schema import RemoveIniFile
import requests
import tkinter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

HASHI_EASY_URL = "https://www.puzzle-bridges.com/"

BOARD = []
NODE_DISTANCE = 18 # Pixel distance between each node on the Hashi website


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

  # print(node.left)
  # print(node.top)
  # print(node.right)
  # print(node.bottom)
  neighbors = {}
  bridgeCount = 0

  if node.left and node.left.value > 0 and node.left_bridge < 2:
    addition = 1 if node.left_bridge == 1 else min(node.left.value, 2)
    neighbors["left"] = [node.left, addition]
    bridgeCount += addition

  if node.top and node.top.value > 0 and node.top_bridge < 2:
    addition = 1 if node.top_bridge == 1 else min(node.top.value, 2)
    neighbors["top"] = [node.top, addition]
    bridgeCount += addition

  if node.right and node.right.value > 0 and node.right_bridge < 2:
    addition = 1 if node.right_bridge == 1 else min(node.right.value, 2)
    neighbors["right"] = [node.right, addition]
    bridgeCount += addition

  if node.bottom and node.bottom.value > 0 and node.bottom_bridge < 2:
    addition = 1 if node.bottom_bridge == 1 else min(node.bottom.value, 2)
    neighbors["bottom"] = [node.bottom, addition]
    bridgeCount += addition

  if bridgeCount == 4:
    print("CAN SOLVE")
    print(node)
    return True

  # if len(remainingNodes) == 2:
  #   if remainingNodes.count("left") > 0:
  #     node.connectLeft()
  #   if remainingNodes.count("top") > 0:
  #     node.connectTop()
  #   if remainingNodes.count("right") > 0:
  #     node.connectRight()
  #   if remainingNodes.count("bottom") > 0:
  #     node.connectBottom()

def repeatForSides(node, function):
  function(*node.left)
  function(*node.top)
  function(*node.right)
  function(*node.bottom)

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

class Node:
  def __init__(self, value, x, y, left=None, top=None, right=None, bottom=None):
    self.value = value
    self.x = x
    self.y = y

    self.left = left
    self.top = top
    self.right = right
    self.bottom = bottom

    self.left_bridge = 0
    self.top_bridge = 0
    self.right_bridge = 0
    self.bottom_bridge = 0

  def connectLeft(self, count):
    self.left_bridge = count
    self.value -= count
    self.left.right_bridge = count
    self.left.value -= count

  def connectTop(self, count):
    self.top_bridge = count
    self.value -= count
    self.top.bottom_bridge = count
    self.top.value -= count

  def connectRight(self, count):
    self.right_bridge = count
    self.value -= count
    self.right.left_bridge = count
    self.right.value -= count

  def connectBottom(self, count):
    self.bottom_bridge = count
    self.value -= count
    self.bottom.top_bridge = count
    self.bottom.value -= count

  def __repr__(self) -> str:
    return f"{self.value} ({self.x}, {self.y})"

if __name__ == "__main__":
  getBoardHTML(HASHI_EASY_URL, 7, 7)

  solve()
