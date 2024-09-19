from random import choice
from math import inf
from functools import reduce

PLAYER_X = 1
PLAYER_O = -1
DEPTH = 10


class Game:
    def __init__(self, width=3, height=3, goal=3):
        self.board_x = 0
        self.board_o = 0
        self.width = width
        self.height = height
        self.goal = goal
        self.minimax_data = {}

    def get_board(self, state=None):
        board = [[0] * self.width for _ in range(self.height)]
        if state is None:
            board_x, board_o = self.board_x, self.board_o
        else:
            board_x, board_o = state

        for i in range(self.width * self.height):
            if board_x % 2:
                board[i // self.width][i % self.width] = 1
            board_x >>= 1

        for i in range(self.width * self.height):
            if board_o % 2:
                board[i // self.width][i % self.width] = -1
            board_o >>= 1

        return board

    def restart(self):
        self.board_x = 0
        self.board_o = 0

    def get_state(self):
        return self.board_x, self.board_o

    def game_over(self, state=None):
        if state is None:
            state = self.get_state()
        board_x, board_o = state
        return board_x | board_o == 2 ** (self.width * self.height) - 1 or self.value(state) != 0

    def value(self, state=None):
        """
        returns 0 if no one won
        returns inf if X won
        return -inf if O won
        """
        if state is None:
            state = self.get_state()

        def vertical(board):
            rows = []
            for i in range(self.height):
                row = board % 2 ** self.width
                rows.append(row)
                board >>= self.width
            return any(reduce(lambda x, y: x & y, rows[i:i + self.goal]) > 0
                       for i in range(self.height - self.goal + 1))

        def horizontal(board):
            lines = []
            for i in range(self.height):
                row = board % 2 ** self.width
                for j in range(self.width - self.goal + 1):
                    line = row % 2 ** self.goal
                    row >>= 1
                    lines.append(line)
                board >>= self.width
            return 2 ** self.goal - 1 in lines

        def diagonal(board):
            rows = []
            for i in range(self.height):
                row = board % 2 ** self.width
                rows.append(row)
                board >>= self.width
            return any(reduce(lambda x, y: x & y, (row >> j for j, row in enumerate(rows[i:i + self.goal]))) > 0 or
                       reduce(lambda x, y: x & y, (row >> j for j, row in enumerate(rows[i:i + self.goal][::-1]))) > 0
                       for i in range(self.height - self.goal + 1))

        board_x, board_o = state
        x_won = vertical(board_x) or horizontal(board_x) or diagonal(board_x)
        o_won = vertical(board_o) or horizontal(board_o) or diagonal(board_o)
        if x_won:
            return inf
        if o_won:
            return -inf
        return 0

    def player(self, state=None):
        """
        returns 1 if X turn
        returns -1 if O turn
        """
        if state is None:
            state = self.get_state()

        board_x, board_o = state
        player = 1
        board = board_x | board_o
        while board:
            player *= -1 if board % 2 else 1
            board >>= 1
        return player

    def moves(self, state=None):
        if state is None:
            state = self.get_state()

        board_x, board_o = state
        board = board_x | board_o
        moves = []
        move = 1
        for _ in range(self.width * self.height):
            if board % 2 == 0:
                moves.append(move)
            move <<= 1
            board >>= 1
        return moves

    def result(self, state, move):
        board_x, board_o = state
        player = self.player(state)
        if player == PLAYER_X:
            board_x |= move
        elif player == PLAYER_O:
            board_o |= move
        return board_x, board_o

    def make_move(self, move):
        if move is None:
            return

        self.board_x, self.board_o = self.result(self.get_state(), move)

    def flip_vertically(self, state):
        board_x, board_o = state
        new_board_x, new_board_o = 0, 0
        for i in range(self.height):
            new_board_x <<= self.width
            new_board_o <<= self.width
            new_board_x += board_x % 2 ** self.width
            new_board_o += board_o % 2 ** self.width
            board_x <<= self.width
            board_o <<= self.width
        new_state = new_board_x, new_board_o
        return new_state

    def evaluation(self, state):
        winning_positions = (2 ** self.goal - 1 - 2 ** i for i in range(self.goal))

        def horizontal(board_player, board_all):
            value = 0
            for i in range(self.height - 1):
                for j in range(self.width - self.goal):
                    line_player = board_player % 2 ** self.goal
                    line_all = board_all % 2 ** self.goal
                    if line_player == line_all and line_player in winning_positions:
                        value += 1
                    board_player <<= 1
                    board_all <<= 1
                board_player <<= self.goal - 1
                board_all <<= self.goal - 1

            return value

        def vertical(board_player, board_all):
            value = 0
            for i in range(self.width):
                line_player = 0
                line_all = 0
                for j in range(self.goal):
                    line_player <<= 1
                    line_all <<= 1
                    line_player += (board_player << (i + j * self.width)) % 2
                    line_all += (board_all << (i + j * self.width)) % 2
                    if line_player == line_all and line_player in winning_positions:
                        value += 1
                for j in range(self.goal, self.height):
                    line_player <<= 1
                    line_all <<= 1
                    line_player += (board_player << (i + j * self.width)) % 2
                    line_all += (board_all << (i + j * self.width)) % 2
                    line_player %= 2 ** self.goal
                    line_all %= 2 ** self.goal
                    if line_player == line_all and line_player in winning_positions:
                        value += 1

            return value

        board_x, board_o = state
        player = self.player(state)
        board = board_x | board_o

        value_x = horizontal(board_x, board) + vertical(board_x, board)
        value_o = horizontal(board_o, board) + vertical(board_o, board)

        if value_x and player == PLAYER_X:
            return inf
        if value_o and player == PLAYER_O:
            return -inf
        if value_x > 1:
            return inf
        if value_o > 1:
            return -inf

        return 0

    def cache_data(self, state, value):
        self.minimax_data[state] = value

    def minimax(self, state, depth=DEPTH, alpha=-inf, beta=inf):
        if state in self.minimax_data:
            return self.minimax_data.get(state)

        if self.game_over(state):
            value = self.value(state)
            self.cache_data(state, value)
            return value

        evaluation = self.evaluation(state)
        if depth == 0 or evaluation != 0:
            self.cache_data(state, evaluation)
            return evaluation

        player = self.player(state)
        func = max if player == PLAYER_X else min
        value = -inf if player == PLAYER_X else inf
        for move in self.moves(state):
            value = func(value, self.minimax(self.result(state, move), depth - 1))
            alpha = func(alpha, value)
            if alpha > beta:
                break
        self.cache_data(state, value)
        flip1 = self.flip_vertically(state)
        self.cache_data(flip1, value)
        return value

    def clear_data(self):
        self.minimax_data = {}

    def best_move(self, state=None):
        if state is None:
            state = self.get_state()

        if self.game_over(state):
            return

        moves = self.moves()
        value_moves = {}
        for move in moves:
            value = self.minimax(self.result(state, move))
            value_moves[value] = value_moves.get(value, []) + [move]

        func = max if self.player(state) == PLAYER_X else min

        return choice(value_moves.get(func(value_moves.keys())))


if __name__ == '__main__':
    # tests
    game = Game()
    print(
        'horizontal X',
        game.value((0b111000000, 0b000101000)),
        'horizontal O',
        game.value((0b000101100, 0b111000000)),
        'vertical X',
        game.value((0b100100100, 0b000001011)),
        'vertical O',
        game.value((0b000001011, 0b100100100)),
        'diagonal1 X',
        game.value((0b100010001, 0b010000110)),
        'diagonal1 O',
        game.value((0b010000110, 0b100010001)),
        'diagonal2 X',
        game.value((0b001010100, 0b010000011)),
        'diagonal2 O',
        game.value((0b010000011, 0b001010100)),
        sep='\n'
    )

    from datetime import datetime as dt

    game = Game(3, 3, 3)
    t1 = dt.now()
    print(game.minimax(game.get_state()))
    t2 = dt.now()
    print(t2 - t1)
