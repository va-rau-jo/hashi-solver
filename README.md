# The Hashi Solver

I made a solver for the popular puzzle game [Hashi](https://en.wikipedia.org/wiki/Hashiwokakero). The website I used to generate the games is [Puzzle Bridges](https://www.puzzle-bridges.com/). You can play some games here to familiarize yourself with the game.

The board starts with no connections drawn and some nodes: ![Start of Hashi game](images/small1.PNG 'Start of game')

Clicking on the "next step" button will make a move on the board, and display the most recently made move.

![Middle of Hashi game](images/small2.PNG 'Middle of game')

Once the puzzle is solved, the bridges will be highlighted to show it is completed.

![Completed Hashi game](images/small3.PNG 'Completed game')

# Rules

## Goal

The goal of Hashi all of the nodes with either 1 or 2 bridges between each node.

## Rules

The bridges must:

- Begin and end at distinct nodes (no self loops)
- Not cross any other bridges or nodes
- Only run orthogonally (cannot run diagonally)

Additionally,

- 2 nodes can only be connected with a maximum of 2 bridges
- The number of bridges connected to each node must match the number displayed on that node
- The bridges must connect the islands into a single connected group.

# Development Summary

This was developed entirely in Python and Tkinter was used for the UI.

Functions were developed for all the rules. The solving algorithm repeatedly ran the basic rules on each node on the board until no change was made.

Then, a check was made to see if any new bridge would break the continuity guarantee of the puzzle (single connected group). There must be at least one valid move at this point, and once that change is made, the base rules are ran again until completion or until another continuity check is required.

# Most challenging puzzle

The most challenging puzzle on the Hashi website is a 50x40 monthly puzzle. This is still solved extremely quickly by this program.

Start:
![Start of Hashi game](images/big1.PNG 'Start of game')

Middle:
![Middle of Hashi game](images/big2.PNG 'Middle of game')

End:
![Completed Hashi game](images/big3.PNG 'Completed game')

# Run it yourself!

Run `python3 ./main.py` to run the program on a random easy 7x7 Hashi puzzle

Run `python3 ./test.py` to run the tests for the different algorithm methods and to test some sample boards

Run:

`python3 ./main.py --size {size} --difficulty {diff}`

or

`python3 ./main.py -s {size} -d {diff}`

to run a puzzle with the given size and difficulty. The possible values for these arguments are listed below. Running without any arguments will run a 7x7 easy by default.

- Sizes:
  - 7x7
  - 10x10
  - 15x15
  - 25x25
  - special (the daily, weekly, and monthly puzzles)
- Difficulties:
  - easy (special easy is the daily)
  - medium (special medium is the weekly)
  - hard (special hard is the monthly)
