from main import Node, finish4Node

def test4NodeLogic():
  node = Node(4, 0, 0, None, None, Node(3, 0, 0), Node(3, 0, 0))

  assert finish4Node(node)

  node.neighbors["left"] = None
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(3, 0, 0)

  assert finish4Node(node)

  node.neighbors["left"] = Node(1, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert finish4Node(node)

  node.neighbors["left"] = Node(2, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert not finish4Node(node)

  node.neighbors["left"] = Node(2, 0, 0)
  node.neighbors["top"] = Node(1, 0, 0)
  node.neighbors["right"] = Node(1, 0, 0)
  node.neighbors["bottom"] = Node(1, 0, 0)

  assert not finish4Node(node)

if __name__ == "__main__":
  test4NodeLogic()
  print("\nTests passed!")