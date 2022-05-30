from main import Node, finish4Node, repeatForSides

def t(val):
  print(val)

def testRepeatForSides():
  # def x(a,b):
  #   print "param 1 %s param 2 %s"%(a,b)
  # def y(z,t):
  #   z(*t)
  # y(x,("hello","manuel"))
  repeatForSides(Node(2, 0, 0), t)

def test4NodeLogic():
  node = Node(4, 0, 0)
  node.left = None
  node.top = None
  node.right = Node(3, 0, 0)
  node.bottom = Node(3, 0, 0)

  assert finish4Node(node)

  node.left = None
  node.top = Node(1, 0, 0)
  node.right = Node(1, 0, 0)
  node.bottom = Node(3, 0, 0)

  assert finish4Node(node)

  node.left = Node(1, 0, 0)
  node.top = Node(1, 0, 0)
  node.right = Node(1, 0, 0)
  node.bottom = Node(1, 0, 0)

  assert finish4Node(node)

  node.left = Node(2, 0, 0)
  node.top = Node(1, 0, 0)
  node.right = Node(1, 0, 0)
  node.bottom = Node(1, 0, 0)

  assert not finish4Node(node)

  node.left = Node(2, 0, 0)
  node.top = Node(1, 0, 0)
  node.right = Node(1, 0, 0)
  node.bottom = Node(1, 0, 0)

  assert not finish4Node(node)

if __name__ == "__main__":
  test4NodeLogic()