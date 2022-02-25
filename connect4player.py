"""
This Connect Four player just picks a random spot to play. It's pretty dumb.
"""
__author__ = "Jack Ruder"  # replace my name with yours
__license__ = "MIT"
__date__ = "February 2022"
from typing import List, Tuple
import random
import time
import numpy as np


class ComputerPlayer:
    def __init__(self, id, difficulty_level):
        """
        Constructor, takes a difficulty level (likely the # of plies to look
        ahead), and a player ID that's either 1 or 2 that tells the player what
        its number is.
        """
        self.ply = difficulty_level
        self.id = id
        if id == 1:
            self.opp = 2  # get opponent id
        else:
            self.opp = 1

    def pick_move_at_random(self, rack):
        """
        Pick the move to make. It will be passed a rack with the current board
        layout, column-major. A 0 indicates no token is there, and 1 or 2
        indicate discs from the two players. Column 0 is on the left, and row 0
        is on the bottom. It must return an int indicating in which column to
        drop a disc. The player current just pauses for half a second (for
        effect), and then chooses a random valid move.
        """
        time.sleep(0.5)  # pause purely for effect--real AIs shouldn't do this
        while True:
            play = random.randrange(0, len(rack))
            if rack[play][-1] == 0:
                return play

    def pick_move_n(self, rack, n):
        """
        Pick the move to make, for a game of connect-n.
        It will be passed a rack with the current board layout, column-major.
        A 0 indicates no token is there, and 1 or 2 indicate discs from the
        two players. Column 0 is on the left, and row 0 is on the bottom.
        It must return an int indicating in which column to drop a disc.
        Uses alpha beta Negamax with _evaluate to pick the best move, limited
        to a depth of self.ply
        """

        pass

    def negamax(self, current_rack, color, depth, n):
        # if we are a leaf node, return our heuristic and percolate up
        if depth == self.ply:
            if color == self.id:
                return self.__evaluate(current_rack, n)  # evaluate is + for self
            else:
                return -self.__evaluate(current_rack, n)
        else:  # then maximize the value of our children
            best = -np.inf
        return 0

    def __get_children(self, rack: Tuple[Tuple[int]], color):
        """
        gets an array of all possible moves that
        can be made in a position, with a color
        """
        children = []

        # go col by col
        for i, col in enumerate(rack):
            newcol = self.__drop_disc(col, color)
            if newcol is None:
                continue  # column full, no child here
            child = []
            for j in range(len(rack)):
                if j == i:  # if we are at this index
                    child.append(newcol)
                else:  # copy in the old columns
                    child.append(rack[j])
            children.append(Tuple(child))

        return children

    def __drop_disc(self, col, color):
        """
        given a column tuple and a color,
        drop a new disc of that color in
        the column
        """
        zero_index = -1
        j = 0
        # iterate until we find a zero or run out of room
        while zero_index < 0 and j < len(col):
            if col[j] == 0:
                zero_index = j
            else:
                j += 1

        if zero_index == -1:  # column is full
            return None  # can't make any moves in this column
        copy = []
        for k in range(len(col)):  # copy elements over in list from old
            if k == zero_index:  # unless we are at the first zero, drop
                copy.append(color)
            else:
                copy.append(col[k])

        return Tuple(col)

    def __evaluate(self, rack, n):
        """
        Evaluation function, ranged from -inf to +inf, + favors self, - favors opponent
        Inspects every possible quartet in the board, and adds to a total sum the following:
        4 of self: +inf
        3 of self + 1 blank: +100
        2 of self + 2 blank: +10
        1 of self + 3 blank: +1
        negate scores for opponent
        """
        total = 0
        rows = [] * len(rack[0])  # transpose
        for i in range(len(rack[0])):
            rows.append([0] * len(rack))
        for i, col in enumerate(rack):  # sum all columns first
            ret = self._count_in_line(col, n)
            if ret == np.inf or ret == -np.inf:
                return ret
            else:
                total += ret

            for j, elem in enumerate(col):  # might as well compute transpose as well
                rows[j][i] = elem

        for row in rows:  # sum the rows
            ret = self.__count_in_line(row, n)
            if ret == np.inf or ret == -np.inf:
                return ret
            else:
                total += ret

        # add all diagonals to the array
        diagonals = []

        # do up and right diagonals first, start from bottom
        for i in range(len(rack)):
            d = []
            k = i  # this column
            j = 0
            while k < len(rack) and j < len(rack[0]):  # while we are within bounds
                d.append(rack[k][j])
                k += 1
                j += 1
            if len(d) >= n:
                diagonals.append(d)

        # start at 1 as to not double count the main diagonal
        for j in range(1, len(rack[0])):
            d = []
            i = 0  # start on the left
            k = j  # this row
            while i < len(rack) and k < len(rack[0]):  # while we are within bounds
                d.append(rack[i][k])
                i += 1
                k += 1

            if len(d) >= n:
                diagonals.append(d)

        # do up and left diagonals, start from bottom
        for i in reversed(range(len(rack))):
            d = []
            k = i  # this column
            j = 0
            while k >= 0 and j < len(rack[0]):  # while we are within bounds
                d.append(rack[k][j])
                k -= 1
                j += 1
            if len(d) >= n:
                diagonals.append(d)

        # start from right at 1 as to not double count the main diagonal
        for j in range(1, len(rack[0])):
            d = []
            i = len(rack) - 1  # start on the right
            k = j  # this row
            while i >= 0 and k < len(rack[0]):  # while we are within bounds
                d.append(rack[i][k])
                i -= 1
                k += 1

            if len(d) >= n:
                diagonals.append(d)

        for d in diagonals:
            ret = self.__count_in_line(d, n)
            if ret == np.inf or ret == -np.inf:
                return ret
            else:
                total += ret

        return total

    def __count_in_line(self, line, n):
        """
        given an input line (col or row or diag)
        returns the summed score within a column using DP in O(n)
        """
        total = 0

        if len(line) < n:  # cant make an ntet
            return 0

        count = {self.id: [], self.opp: []}
        for i in range(len(line) - n + 1):
            count[self.id].append([0] * n)
            count[self.opp].append([0] * n)

        for i, disc in enumerate(line):
            if disc == 0:  # if the space is empty

                # while we still have quartets to start
                if i < len(line) - n + 1:
                    for j in range(1, n):
                        if j <= i:  # check index
                            # this spot is free, so same potential as before, just copy
                            count[self.id][i - j][j] = count[self.id][i - j][j - 1]
                            count[self.opp][i - j][j] = count[self.opp][i - j][j - 1]

                            if j == (n - 1):  # if we have filled a n-tet calc scores
                                # get the number of filled spots, negative if blocked
                                id_score = count[self.id][i - n + 1][n - 1]
                                opp_score = count[self.opp][i - n + 1][n - 1]
                                if id_score == n:  # game over!!!
                                    return np.inf
                                if opp_score == n:
                                    return -np.inf

                                # else, add/sub from sum. casting 10^(-x) to an int is 0
                                total += int(10**id_score)
                                total -= int(10**opp_score)

                # last n-1 quartets, just shift the allowed indices to avoid out of range errors
                else:
                    for k in range(
                        i - (n - 1), len(line) - (n - 1)
                    ):  # loop through remaining unfilled columns
                        if k < 0:
                            continue
                        j = i - k  # index at each spot
                        count[self.id][k][j] = count[self.id][k][
                            j - 1
                        ]  # fill, same logi
                        count[self.opp][k][j] = count[self.opp][k][j - 1]  # fill
                        if j == (n - 1):
                            # get the number of filled spots, negative if blocked
                            id_score = count[self.id][k][n - 1]
                            opp_score = count[self.opp][k][n - 1]
                            if id_score == n:  # game over!!!
                                return np.inf
                            if opp_score == n:
                                return -np.inf

                            # else, add/sub from sum. casting 10^(-x) to an int is 0
                            total += int(10**id_score)
                            total -= int(10**opp_score)

            if disc == self.id:
                if i < len(line) - n + 1:
                    for j in range(n):
                        if j == 0:  # base cases

                            # this is us, start with 1
                            count[self.id][i][0] = 1
                            # enemy is blocked, set to impossibly negative
                            count[self.opp][i][0] = -2 * n

                        elif j <= i:
                            count[self.id][i - j][j] = count[self.id][i - j][j - 1] + 1
                            count[self.opp][i - j][j] = -2 * n

                            if j == (n - 1):
                                id_score = count[self.id][i - n + 1][n - 1]
                                if id_score == n:  # game over!!!
                                    return np.inf
                                # else, add/sub from sum. casting 10^(-x) to an int is 0
                                total += int(10**id_score)
                # last n-1 quartets, just shift the allowed indices to avoid out of range errors
                else:
                    for k in range(
                        i - (n - 1), len(line) - (n - 1)
                    ):  # loop through remaining unfilled lineumns
                        if k < 0:
                            continue
                        j = i - k  # index at each spot
                        count[self.id][k][j] = count[self.id][k][j - 1] + 1  # fill
                        count[self.opp][k][j] = -2 * n
                        if j == (n - 1):  # ntet filled
                            id_score = count[self.id][k][n - 1]
                            if id_score == n:  # game over!!!
                                return np.inf
                            # else, add/sub from sum. casting 10^(-x) to an int is 0
                            total += int(10**id_score)

            ## same logic as above, just replace self.opp with self.id, and negate
            if disc == self.opp:
                if i < len(line) - n + 1:
                    for j in range(n):
                        if j == 0:
                            count[self.opp][i][0] = 1  # base case, start with 1
                            count[self.id][i][0] = -2 * n
                        elif j <= i:
                            count[self.opp][i - j][j] = (
                                count[self.opp][i - j][j - 1] + 1
                            )
                            count[self.id][i - j][j] = -2 * n
                            if j == (n - 1):

                                opp_score = count[self.opp][i - n + 1][n - 1]
                                if opp_score == n:  # game over!!!
                                    return -np.inf
                                # else, add/sub from sum. casting 10^(-x) to an int is 0
                                total -= int(10**opp_score)
                # last n-1 quartets, just shift the allowed indices to avoid out of range errors
                else:
                    for k in range(
                        i - (n - 1), len(line) - (n - 1)
                    ):  # loop through remaining unfilled lineumns
                        if k < 0:
                            continue
                        j = i - k  # index at each spot
                        count[self.opp][k][j] = count[self.opp][k][j - 1] + 1  # fill
                        count[self.id][k][j] = -2 * n
                        if j == (n - 1):
                            opp_score = count[self.id][k][n - 1]
                            if opp_score == n:  # game over!!!
                                return -np.inf
                            # else, add/sub from sum. casting 10^(-x) to an int is 0
                            total -= int(10**opp_score)
        return total


if __name__ == "__main__":
    c = ComputerPlayer(1, 1)
    print(((0, 0, 1, 0, 2), (0, 1, 1, 0, 2), (0, 1, 2, 2, 2), (0, 1, 1, 0, 1)))
    print(
        c.__evaluate(
            ((0, 0, 1, 0, 2), (0, 1, 1, 0, 2), (0, 1, 2, 2, 2), (0, 1, 1, 0, 1)), 4
        )
    )
