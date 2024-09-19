import tkinter as tk
from game import *

A = 170
ROWS, COLS, GOAL = 3, 3, 3
W, H = ROWS * A, COLS * A


def click(event):
    global first_move
    if game.game_over():
        first_move = not first_move
        game.restart()
        if not first_move:
            pass
            game.make_move(game.best_move())
        redraw()
        return
    x, y = event.x, event.y
    col, row = x // A, y // A
    move = 2 ** (col + row * game.width)
    if move in game.moves():
        game.make_move(move)
        game.make_move(game.best_move())
        redraw()


def redraw():
    canvas.delete('all')

    for i in range(1, game.width):
        canvas.create_line(i * A, 0, i * A, H, width=5)

    for i in range(1, game.height):
        canvas.create_line(0, i * A, W, i * A, width=5)

    board = game.get_board()

    for j, row in enumerate(board):
        for i, col in enumerate(row):
            x, y = i * A, j * A
            if col == PLAYER_X:
                canvas.create_line(x, y, x + A, y + A, fill='red', width=5)
                canvas.create_line(x + A, y, x, y + A, fill='red', width=5)
            elif col == PLAYER_O:
                canvas.create_oval(x, y, x + A, y + A, outline='blue', width=5)

    canvas.create_text(0, 0, text=game.minimax(game.get_state()), font='Verdana 14', anchor=tk.NW)
    game.clear_data()


game = Game(ROWS, COLS, GOAL)
first_move = True

root = tk.Tk()

canvas = tk.Canvas(root, width=W, height=H, bg='white')
canvas.pack()

redraw()
root.bind('<Button-1>', click)

root.mainloop()
