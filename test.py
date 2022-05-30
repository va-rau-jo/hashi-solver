from main import BOARD, Node, addPartialBridgesToOddNode, finishNode, getLeftNeighbor, getTopNeighbor, solve

def testPartialNodeLogic():
  node = Node(3, 0, 0, None, None, Node(3, 0, 0), Node(3, 0, 0))
  assert addPartialBridgesToOddNode(node)

  node = Node(3, 0, 0, None, Node(3, 0, 0), None, Node(3, 0, 0))
  assert addPartialBridgesToOddNode(node)

  node = Node(3, 0, 0, Node(7, 0, 0), Node(4, 0, 0), None, None)
  assert addPartialBridgesToOddNode(node)

  node = Node(3, 0, 0, Node(4, 0, 0), Node(4, 0, 0), Node(4, 0, 0), None)
  node.bridges["left"] = 1
  assert not addPartialBridgesToOddNode(node)

def testFinishNodeLogic():
  node = Node(4, 0, 0, None, None, Node(3, 0, 0), Node(3, 0, 0))

  assert finishNode(node)

  node = Node(4, 0, 0)
  node.neighbors["left"] = None
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(3, 0, 0)

  assert finishNode(node)

  node = Node(4, 0, 0)
  node.neighbors["left"] = Node(1, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert finishNode(node)

  node = Node(4, 0, 0)
  node.neighbors["left"] = Node(2, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert not finishNode(node)

  node = Node(4, 0, 0)
  node.neighbors["left"] = Node(2, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert not finishNode(node)

board1 = [
    [Node(4, 0, 0), None, Node(4, 2, 0), None, Node(4, 4, 0), None, Node(3, 6, 0)],
    [None, None, None, None, None, None, None],
    [Node(4, 0, 2), None, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None, None, Node(1, 2, 5), None, Node(1, 4, 5), None, None],
    [Node(4, 0, 6), None, None, None, None, None, Node(3, 6, 6)]
  ]

board2 = [
    [Node(1, 0, 0), None, Node(2, 2, 0), None, Node(1, 4, 0), None, Node(2, 6, 0)],
    [None, None, None, None, None, None, None],
    [Node(2, 0, 2), None, Node(5, 2, 2), None, None, None, Node(5, 6, 2)],
    [None, None, None, None, None, None, None],
    [Node(2, 0, 4), None, None, Node(2, 3, 4), None, Node(3, 5, 4), None],
    [None, None, None, None, None, None, Node(1, 6, 5)],
    [Node(3, 0, 6), None, Node(4, 2, 6), None, None, Node(3, 5, 6), None]
  ]

board3 = [
    [Node(2, 0, 0), None, None, None, None, None, None],
    [None, Node(1, 1, 1), None, None, Node(2, 4, 1), None, Node(2, 6, 1)],
    [None, None, None, None, None, None, None],
    [Node(6, 0, 3), None, Node(5, 2, 3), None, Node(4, 4, 3), None, Node(3, 6, 3)],
    [None, None, None, Node(1, 3, 4), None, None, None],
    [None, None, Node(2, 2, 5), None, Node(2, 4, 5), None, None],
    [Node(2, 0, 6), None, None, Node(3, 3, 6), None, None, Node(3, 6, 6)]
  ]

board4 = [
    [Node(2, 0, 0), None, Node(2, 2, 0), None, None, None, Node(2, 6, 0)],
    [None, None, None, None, None, None, None],
    [Node(4, 0, 2), None, None, None, Node(4, 4, 2), None, Node(2, 6, 2)],
    [None, None, None, Node(1, 3, 3), None, None, None],
    [None, None, None, None, None, None, None],
    [Node(3, 0, 5), None, None, Node(3, 3, 5), None, None, None],
    [None, None, Node(2, 2, 6), None, Node(6, 4, 6), None, Node(3, 6, 6)]
  ]

board5 = [
    [Node(2, 0, 0), None, Node(2, 2, 0), None, Node(5, 4, 0), None, Node(2, 6, 0)],
    [None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None],
    [None, None, None, None, None, None, Node(1, 6, 3)],
    [None, None, Node(2, 2, 4), None, None, None, None],
    [None, None, None, None, None, None, None],
    [Node(3, 0, 6), None, Node(4, 2, 6), None, Node(6, 4, 6), None, Node(3, 6, 6)]
  ]

board6 = [
    [Node(1, 0, 0), None, None, None, Node(2, 4, 0), None, None],
    [None, None, None, None, None, None, Node(1, 6, 1)],
    [Node(3, 0, 2), None, Node(2, 2, 2), None, None, None, None],
    [None, None, None, None, Node(5, 4, 3), None, Node(4, 6, 3)],
    [None, None, None, None, None, None, None],
    [Node(4, 0, 5), None, Node(4, 2, 5), None, Node(3, 4, 5), None, None],
    [None, Node(1, 1, 6), None, None, None, None, Node(2, 6, 6)]
  ]

board7 = [
    [None, None, None, None, Node(1, 4, 0), None, Node(2, 6, 0)],
    [Node(4, 0, 1), None, None, Node(6, 3, 1), None, Node(2, 5, 1), None],
    [None, None, None, None, None, None, None],
    [None, Node(1, 1, 3), None, Node(5, 3, 3), None, None, Node(3, 6, 3)],
    [None, None, None, None, None, Node(1, 5, 4), None],
    [None, Node(1, 1, 5), None, Node(2, 3, 5), None, None, Node(1, 6, 5)],
    [Node(3, 0, 6), None, None, None, None, Node(2, 5, 6), None]
  ]

board8 = [
    [Node(2, 0, 0), None, None, Node(1, 3, 0), None, None, Node(2, 6, 0)],
    [None, None, None, None, None, None, None],
    [Node(4, 0, 2), None, None, None, None, None, Node(4, 6, 2)],
    [None, Node(3, 1, 3), None, Node(6, 3, 3), None, Node(4, 5, 3), None],
    [None, None, None, None, None, None, None],
    [None, Node(1, 1, 5), None, None, None, Node(2, 5, 5), None],
    [Node(2, 0, 6), None, None, Node(5, 3, 6), None, None, Node(4, 6, 6)]
  ]

def testBoards():
  boards = [board1]

  for board in boards:
    BOARD = board
    for i in range(len(BOARD)):
      for j in range(len(BOARD[i])):
        node = board[i][j]
        if node:
          # print(node.neighbors)
          node.neighbors["left"] = getLeftNeighbor(node.x - 1, node.y)
          # print(node.neighbors)
          node.neighbors["top"] = getTopNeighbor(node.x, node.y - 1)
          if node.neighbors["left"]:
            node.neighbors["left"].neighbors["right"] = node
          if node.neighbors["top"]:
            node.neighbors["top"].neighbors["bottom"]  = node

    solved = solve()
    print(solved)

if __name__ == "__main__":
  testFinishNodeLogic()
  testPartialNodeLogic()
  testBoards()
  print("\nTests passed!")