import sys
import time
import pygame
import pygame.gfxdraw
from pygame.locals import *


MAX = sys.maxsize
MIN = -MAX
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)

def matrixToString(m):  # convert game board to string for printing
    s = ""
    colRow = " "
    for i in range(len(m[0])):
        colRow = colRow + str(i)
    s = s + colRow + "\n"
    linIndex = 0
    for line in m:
        s = s + str(linIndex)
        linIndex += 1
        for elem in line:
            s = s + str(elem)
        s = s + '\n'

    return s

def fHash(m, depth):  # function to hash contents of game board
    s = ""
    for line in m:
        for elem in line:
            s = s + str(elem)
    s = s + str(depth)
    x = hash(s)
    return x

class Move:
    def __init__(self, lin=-1, col=-1):
        self.lin = lin
        self.col = col


class Game:
    def __init__(self):
        data = input("Introduceti numarul de linii:")  # citim nr linii
        while (not data.isnumeric()) or data == "0":
            print("Input invalid!")
            data = input("Introduceti numarul de linii:")
        self.nrLin = int(data)

        data = input("Introduceti numarul de coloane:")  # citim nr coloane
        while (not data.isnumeric()) or data == "0":
            print("Input invalid!")
            data = input("Introduceti numarul de coloane:")
        self.nrCol = int(data)

        data = input("Introduceti simbolul de joc(X/O):")  # citim simbolul de joc
        while (not data.upper() == "X") and (not data.upper() == "O"):
            print("Input invalid!")
            data = input("Introduceti simbolul de joc(X/O):")
        if data.upper() == "X":
            self.jmin = "X"
            self.jmax = "O"
        else:
            self.jmin = "O"
            self.jmax = "X"

        data = input("Introduceti dificultatea(1/2/3):")  # citim dificultatea
        while data != "1" and data != "2" and data != "3":
            print("Input invalid!")
            data = input("Introduceti dificultatea(1/2/3):")
        if data == "1":
            self.maxDepth = 2
        elif data == "2":
            self.maxDepth = 3
        else:
            self.maxDepth = 5

        self.jminScore = 0  # scor jucator
        self.jmaxScore = 0  # scor PC
        self.endScore = self.nrLin * self.nrCol / 2  # scor la care a castigat o parte

        data = input("Introduceti algoritmul de joc(0=minMax/1=alphaBeta):")  # citim algoritmul de joc
        while data != "0" and data != "1":
            print("Input invalid!")
            data = input("Introduceti algoritmul de joc(0=minMax/1=alphaBeta):")
        self.isAlphaBeta = bool(int(data))

        self.nrLinReal = 2 * self.nrLin + 1  # calculam dimensiunile reale ale matricii
        self.nrColReal = 2 * self.nrCol + 1

        self.pozMap = {}  # map de poziitii deja calculate

        self.board = []  # initializam board-ul de joc
        for i in range(self.nrLinReal):
            line = []
            if i % 2 == 0:
                for j in range(self.nrColReal):
                    if j % 2 == 0:
                        line.append("·")
                    else:
                        line.append(" ")
            else:
                for j in range(self.nrColReal):
                    line.append(" ")
            self.board.append(line)

    def __str__(self):
        return f"Nr linii={self.nrLin}, Nr coloane={self.nrCol},\n " \
               f"Simbol jucator:{self.jmin}, Simbol calculator:{self.jmax}\n" \
               f"Adancime max:{self.maxDepth}, Se aplica AlphaBeta:{self.isAlphaBeta}\n" \
               f"Board:\n{matrixToString(self.board)}"

    def showBoardConfig(self):
        print(f"Scor:{self.jminScore}, ScorBot:{self.jmaxScore},\n"
              f"Board:\n{matrixToString(self.board)}\n")

    def isEndGame(self):  # verificarea conditiei de final
        jminScore = self.jminScore
        jmaxScore = self.jmaxScore
        endScore = self.endScore
        nrLin = self.nrLin
        nrCol = self.nrCol
        if jminScore > endScore or \
                jmaxScore > endScore or \
                jmaxScore + jminScore == nrLin * nrCol:  # winmin/winmax/remiza
            return True
        return False

    def evaluate(self):  # evaluare configuratiei actuale

        jminScore = self.jminScore
        jmaxScore = self.jmaxScore
        nrLin = self.nrLin
        nrCol = self.nrCol
        if self.isEndGame():
            if jmaxScore > jminScore:
                return MAX # win jmax
            elif jmaxScore < jminScore:
                return MIN # win jmin
            else:
                return 0  # remiza
        return jmaxScore - jminScore

    def minimax(self, depth, isJmax):
        hsh = fHash(self.board, depth)  # verificam daca nu a fost deja calculata configuratia
        if hsh in self.pozMap:
            score = self.pozMap[hsh]
            if score >= 0:
                return score + 1/(depth + 1)
            else:
                return score - 1 / (depth + 1)

        score = self.evaluate()


        if self.isEndGame():  # final de joc
            self.pozMap[hsh] = score
            if score >= 0:
                return score + 1 / (depth + 1)
            else:
                return score - 1 / (depth + 1)

        if depth == self.maxDepth - 1:  # se atinge adancimea max
            self.pozMap[hsh] = score
            if score >= 0:
                return score + 1 / (depth + 1)
            else:
                return score - 1 / (depth + 1)

        if isJmax:  # max turn
            best = MIN  # init minint
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line[(lineIdx + 1) % 2::2]):
                    if elem == " ":
                        if lineIdx % 2 == 0:  # if line with '-'
                            i = lineIdx
                            j = colIdx * 2 + 1
                            self.board[i][j] = "-"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima linie verificam daca se formeaza patrat deasupra
                            if self.checkBoxAbove(i, j):
                                self.board[i - 1][j] = self.jmax
                                self.jmaxScore += 1
                                ch1 = True
                            # daca nu e ultima linie verificam daca se formeaza patrat sub
                            if self.checkBoxBelow(i, j):
                                self.board[i + 1][j] = self.jmax
                                self.jmaxScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = max(best, self.minimax(depth + 1, isJmax))
                            else:  # altfel se considera mutarea celuilalt
                                best = max(best, self.minimax(depth + 1, not isJmax))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i - 1][j] = " "
                                self.jmaxScore -= 1
                            if ch2:
                                self.board[i + 1][j] = " "
                                self.jmaxScore -= 1

                        else:  # if line with '|'
                            i = lineIdx
                            j = colIdx * 2
                            self.board[i][j] = "|"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima coloana verificam daca se formeaza patrat in stanga
                            if self.checkBoxLeft(i, j):
                                self.board[i][j - 1] = self.jmax
                                self.jmaxScore += 1
                                ch1 = True
                            # daca nu e ultima coloana verificam daca se formeaza patrat in dreapta
                            if self.checkBoxRight(i, j):
                                self.board[i][j + 1] = self.jmax
                                self.jmaxScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = max(best, self.minimax(depth + 1, isJmax))
                            else:  # altfel se considera mutarea celuilalt
                                best = max(best, self.minimax(depth + 1, not isJmax))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i][j - 1] = " "
                                self.jmaxScore -= 1
                            if ch2:
                                self.board[i][j + 1] = " "
                                self.jmaxScore -= 1
            self.pozMap[hsh] = best  # salvam scorul calculat

            if best >= 0:
                return best + 1 / (depth + 1)
            else:
                return best - 1 / (depth + 1)
        else:  # min turn
            best = MAX  # init maxint
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line[(lineIdx + 1) % 2::2]):
                    if elem == " ":
                        if lineIdx % 2 == 0:  # if line with '-'
                            i = lineIdx
                            j = colIdx * 2 + 1
                            self.board[i][j] = "-"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima linie verificam daca se formeaza patrat deasupra
                            if self.checkBoxAbove(i, j):
                                self.board[i - 1][j] = self.jmin
                                self.jminScore += 1
                                ch1 = True
                            # daca nu e ultima linie verificam daca se formeaza patrat sub
                            if self.checkBoxBelow(i, j):
                                self.board[i + 1][j] = self.jmin
                                self.jminScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = min(best, self.minimax(depth + 1, isJmax))
                            else:  # altfel se considera mutarea celuilalt
                                best = min(best, self.minimax(depth + 1, not isJmax))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i - 1][j] = " "
                                self.jminScore -= 1
                            if ch2:
                                self.board[i + 1][j] = " "
                                self.jminScore -= 1

                        else:  # if line with '|'
                            i = lineIdx
                            j = colIdx * 2
                            self.board[i][j] = "|"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima coloana verificam daca se formeaza patrat in stanga
                            if self.checkBoxLeft(i, j):
                                self.board[i][j - 1] = self.jmin
                                self.jminScore += 1
                                ch1 = True
                            # daca nu e ultima coloana verificam daca se formeaza patrat in dreapta
                            if self.checkBoxRight(i, j):
                                self.board[i][j + 1] = self.jmin
                                self.jminScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = min(best, self.minimax(depth + 1, isJmax))
                            else:  # altfel se considera mutarea celuilalt
                                best = min(best, self.minimax(depth + 1, not isJmax))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i][j - 1] = " "
                                self.jminScore -= 1
                            if ch2:
                                self.board[i][j + 1] = " "
                                self.jminScore -= 1
            self.pozMap[hsh] = best
            if best >= 0:
                return best + 1 / (depth + 1)
            else:
                return best - 1 / (depth + 1)

    def alphaBeta(self, depth, isJmax, alpha, beta):
        hsh = fHash(self.board, depth)  # poz deja descoperita
        if hsh in self.pozMap:
            score = self.pozMap[hsh]
            if score >= 0:
                return score + 1 / (depth + 1)
            else:
                return score - 1 / (depth + 1)

        score = self.evaluate()

        if self.isEndGame():  # final de joc
            self.pozMap[hsh] = score
            if score >= 0:
                return score + 1 / (depth + 1)
            else:
                return score - 1 / (depth + 1)

        if depth == self.maxDepth - 1:  # se atinge adancimea max
            self.pozMap[hsh] = score
            if score >= 0:
                return score + 1 / (depth + 1)
            else:
                return score - 1 / (depth + 1)

        if isJmax:  # max turn
            best = MIN  # init minint
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line[(lineIdx + 1) % 2::2]):
                    if elem == " ":
                        if lineIdx % 2 == 0:  # if line with '-'
                            i = lineIdx
                            j = colIdx * 2 + 1
                            self.board[i][j] = "-"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima linie verificam daca se formeaza patrat deasupra
                            if self.checkBoxAbove(i, j):
                                self.board[i - 1][j] = self.jmax
                                self.jmaxScore += 1
                                ch1 = True
                            # daca nu e ultima linie verificam daca se formeaza patrat sub
                            if self.checkBoxBelow(i, j):
                                self.board[i + 1][j] = self.jmax
                                self.jmaxScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = max(best, self.alphaBeta(depth + 1, isJmax, alpha, beta))
                            else:  # altfel se considera mutarea celuilalt
                                best = max(best, self.alphaBeta(depth + 1, not isJmax, alpha, beta))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i - 1][j] = " "
                                self.jmaxScore -= 1
                            if ch2:
                                self.board[i + 1][j] = " "
                                self.jmaxScore -= 1

                            alpha = max(alpha, best)
                            if beta <= alpha:
                                self.pozMap[hsh] = best
                                if best >= 0:
                                    return best + 1 / (depth + 1)
                                else:
                                    return best - 1 / (depth + 1)

                        else:  # if line with '|'
                            i = lineIdx
                            j = colIdx * 2
                            self.board[i][j] = "|"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima coloana verificam daca se formeaza patrat in stanga
                            if self.checkBoxLeft(i, j):
                                self.board[i][j - 1] = self.jmax
                                self.jmaxScore += 1
                                ch1 = True
                            # daca nu e ultima coloana verificam daca se formeaza patrat in dreapta
                            if self.checkBoxRight(i, j):
                                self.board[i][j + 1] = self.jmax
                                self.jmaxScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = max(best, self.alphaBeta(depth + 1, isJmax, alpha, beta))
                            else:  # altfel se considera mutarea celuilalt
                                best = max(best, self.alphaBeta(depth + 1, not isJmax, alpha, beta))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i][j - 1] = " "
                                self.jmaxScore -= 1
                            if ch2:
                                self.board[i][j + 1] = " "
                                self.jmaxScore -= 1

                            alpha = max(alpha, best)
                            if beta <= alpha:
                                self.pozMap[hsh] = best
                                if best >= 0:
                                    return best + 1 / (depth + 1)
                                else:
                                    return best - 1 / (depth + 1)
            self.pozMap[hsh] = best
            if best >= 0:
                return best + 1 / (depth + 1)
            else:
                return best - 1 / (depth + 1)
        else:  # min turn
            best = MAX  # init maxint
            for lineIdx, line in enumerate(self.board):
                for colIdx, elem in enumerate(line[(lineIdx + 1) % 2::2]):
                    if elem == " ":
                        if lineIdx % 2 == 0:  # if line with '-'
                            i = lineIdx
                            j = colIdx * 2 + 1
                            self.board[i][j] = "-"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima linie verificam daca se formeaza patrat deasupra
                            if self.checkBoxAbove(i, j):
                                self.board[i - 1][j] = self.jmin
                                self.jminScore += 1
                                ch1 = True
                            # daca nu e ultima linie verificam daca se formeaza patrat sub
                            if self.checkBoxBelow(i, j):
                                self.board[i + 1][j] = self.jmin
                                self.jminScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = min(best, self.alphaBeta(depth + 1, isJmax, alpha, beta))
                            else:  # altfel se considera mutarea celuilalt
                                best = min(best, self.alphaBeta(depth + 1, not isJmax, alpha, beta))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i - 1][j] = " "
                                self.jminScore -= 1
                            if ch2:
                                self.board[i + 1][j] = " "
                                self.jminScore -= 1

                            beta = min(beta, best)
                            if beta <= alpha:
                                self.pozMap[hsh] = best
                                if best >= 0:
                                    return best + 1 / (depth + 1)
                                else:
                                    return best - 1 / (depth + 1)

                        else:  # if line with '|'
                            i = lineIdx
                            j = colIdx * 2
                            self.board[i][j] = "|"  # move

                            ch1 = False
                            ch2 = False
                            # daca nu e prima coloana verificam daca se formeaza patrat in stanga
                            if self.checkBoxLeft(i, j):
                                self.board[i][j - 1] = self.jmin
                                self.jminScore += 1
                                ch1 = True
                            # daca nu e ultima coloana verificam daca se formeaza patrat in dreapta
                            if self.checkBoxRight(i, j):
                                self.board[i][j + 1] = self.jmin
                                self.jminScore += 1
                                ch2 = True
                            if ch1 or ch2:  # se mai primeste o mutare daca s-a completat un patrat
                                best = min(best, self.minimax(depth + 1, isJmax))
                            else:  # altfel se considera mutarea celuilalt
                                best = min(best, self.minimax(depth + 1, not isJmax))

                            self.board[i][j] = " "  # undo move
                            if ch1:
                                self.board[i][j - 1] = " "
                                self.jminScore -= 1
                            if ch2:
                                self.board[i][j + 1] = " "
                                self.jminScore -= 1

                            beta = min(beta, best)
                            if beta <= alpha:
                                self.pozMap[hsh] = best
                                if best >= 0:
                                    return best + 1 / (depth + 1)
                                else:
                                    return best - 1 / (depth + 1)

            self.pozMap[hsh] = best
            if best >= 0:
                return best + 1 / (depth + 1)
            else:
                return best - 1 / (depth + 1)

    def findMove(self):
        bestVal = MIN
        bestMove = Move()
        for lineIdx, line in enumerate(self.board):  # evalueaza toate mutarile posibile si o alege pe cea mai buna
            for colIdx, elem in enumerate(line[(lineIdx + 1) % 2::2]):
                if elem == " ":
                    i = lineIdx

                    ch1 = False
                    ch2 = False
                    if lineIdx % 2 == 0:  # if line with '-'
                        j = colIdx * 2 + 1
                        self.board[i][j] = "-"

                        if self.checkBoxAbove(i, j):
                            self.board[i - 1][j] = self.jmax
                            self.jmaxScore += 1
                            ch1 = True

                        if self.checkBoxBelow(i, j):
                            self.board[i + 1][j] = self.jmax
                            self.jmaxScore += 1
                            ch2 = True

                        if ch1 or ch2:
                            if not self.isAlphaBeta:
                                moveVal = self.minimax(0, True)
                            else:
                                moveVal = self.alphaBeta(0, True, MIN, MAX)
                        else:
                            if not self.isAlphaBeta:
                                moveVal = self.minimax(0, False)
                            else:
                                moveVal = self.alphaBeta(0, False, MIN, MAX)

                        self.board[i][j] = " "
                        if ch1:
                            self.board[i - 1][j] = " "
                            self.jmaxScore -= 1
                        if ch2:
                            self.board[i + 1][j] = " "
                            self.jmaxScore -= 1
                    else:  # if line with '|'
                        j = colIdx * 2
                        self.board[i][j] = "|"

                        if self.checkBoxLeft(i, j):
                            self.board[i][j - 1] = self.jmax
                            self.jmaxScore += 1
                            ch1 = True

                        if self.checkBoxRight(i, j):
                            self.board[i][j + 1] = self.jmax
                            self.jmaxScore += 1
                            ch2 = True

                        if ch1 or ch2:
                            if not self.isAlphaBeta:
                                moveVal = self.minimax(0, True)
                            else:
                                moveVal = self.alphaBeta(0, True, MIN, MAX)
                        else:
                            if not self.isAlphaBeta:
                                moveVal = self.minimax(0, False)
                            else:
                                moveVal = self.alphaBeta(0, False, MIN, MAX)

                        self.board[i][j] = " "
                        if ch1:
                            self.board[i][j - 1] = " "
                            self.jmaxScore -= 1
                        if ch2:
                            self.board[i][j + 1] = " "
                            self.jmaxScore -= 1
                    if moveVal > bestVal or bestVal == MIN:
                        bestMove.lin = i
                        bestMove.col = j
                        bestVal = moveVal
        return bestMove

    def checkBoxAbove(self, i, j):  # verifica daca se formeaza patrat deasupra
        if i != 0:
            if self.board[i - 1][j - 1] == "|" and \
                    self.board[i - 1][j + 1] == "|" and \
                    self.board[i - 2][j] == "-":
                return True
        return False

    def checkBoxBelow(self, i, j):  # verifica daca se formeaza patrat sub
        if i != self.nrLinReal - 1:
            if self.board[i + 1][j - 1] == "|" and \
                    self.board[i + 1][j + 1] == "|" and \
                    self.board[i + 2][j] == "-":
                return True
        return False

    def checkBoxLeft(self, i, j):  # verifica daca se formeaza patrat in stanga
        if j != 0:
            if self.board[i - 1][j - 1] == "-" and \
                    self.board[i + 1][j - 1] == "-" and \
                    self.board[i][j - 2] == "|":
                return True
        return False

    def checkBoxRight(self, i, j):  # verifica daca se formeaza patrat in dreapta
        if j != self.nrColReal - 1:
            if self.board[i - 1][j + 1] == "-" and \
                    self.board[i + 1][j + 1] == "-" and \
                    self.board[i][j + 2] == "|":
                return True
        return False

    def playConsole(self):
        print("Indexarea liniilor si coloanelor se face de la 0!")
        print("Introduceti comanda exit pentru a termina jocul!")
        print(newGame)
        startTime = time.time()
        player = True
        computerMoves = 0
        playerMoves = 0
        while not self.isEndGame():
            if player:  # daca este randul computerului
                computerMoves += 1
                moveTime = time.time()
                move = self.findMove()
                print(f"Timp gandire:{time.time() - moveTime}")
                goAgain = False
                print(f"Calculatorul a adaugat o linie pe linia:{move.lin}, coloana:{move.col}")

                if move.lin % 2 == 0:
                    self.board[move.lin][move.col] = "-"
                    if self.checkBoxAbove(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin - 1][move.col] = self.jmax
                        self.jmaxScore += 1
                    if self.checkBoxBelow(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin + 1][move.col] = self.jmax
                        self.jmaxScore += 1
                else:
                    self.board[move.lin][move.col] = "|"
                    if self.checkBoxLeft(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin][move.col - 1] = self.jmax
                        self.jmaxScore += 1
                    if self.checkBoxRight(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin][move.col + 1] = self.jmax
                        self.jmaxScore += 1
                if not goAgain:
                    player = not player
                self.showBoardConfig()
                # print(fHash(self.board))
            else:  # daca este randul jucatorului

                data = input("Introduceti linia:")
                while (not data.isnumeric()) or int(data) < 0 or int(data) >= self.nrLinReal:
                    if data != "exit":
                        print("Input invalid!")
                        data = input("Introduceti linia:")
                    else:
                        scor = self.evaluate()
                        print(f"Ati incheiat jocul!\nScor:{self.jminScore}\nScor calculator:{self.jmaxScore}")
                        print(f"Timp de joc:{time.time() - startTime}")
                        print(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}")

                        sys.exit(0)
                playerMoves += 1
                lin = int(data)

                data = input("Introduceti coloana:")
                while (not data.isnumeric()) or int(data) < 0 or int(data) >= self.nrColReal:
                    if data != "exit":
                        print("Input invalid!")
                        data = input("Introduceti linia:")
                    else:
                        scor = self.evaluate()
                        print(f"Ati incheiat jocul!\nScor:{self.jminScore}\nScor calculator:{self.jmaxScore}")
                        print(f"Timp de joc:{time.time() - startTime}")
                        print(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}")

                        sys.exit(0)
                col = int(data)

                goAgain = False

                if (lin % 2 == 0 and col % 2 == 1) or (lin % 2 == 1 and col % 2 == 0):
                    if self.board[lin][col] == " ":

                        if lin % 2 == 0:
                            self.board[lin][col] = "-"
                            if self.checkBoxAbove(lin, col):
                                goAgain = True
                                self.board[lin - 1][col] = self.jmin
                                self.jminScore += 1
                            if self.checkBoxBelow(lin, col):
                                goAgain = True
                                self.board[lin + 1][col] = self.jmin
                                self.jminScore += 1
                        else:
                            self.board[lin][col] = "|"
                            if self.checkBoxLeft(lin, col):
                                goAgain = True
                                self.board[lin][col - 1] = self.jmin
                                self.jminScore += 1
                            if self.checkBoxRight(lin, col):
                                goAgain = True
                                self.board[lin][col + 1] = self.jmin
                                self.jminScore += 1
                        self.showBoardConfig()
                        # print(fHash(self.board))
                    else:
                        goAgain = True
                        print("Pozitia este deja ocupata!")
                else:
                    goAgain = True
                    print("Input invalid!")
                if not goAgain:
                    player = not player
        else:
            scor = self.evaluate()
            print(f"Timp de joc:{time.time() - startTime}")
            print(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}")
            if scor == 0:
                print("Remiza")
            elif scor > 0:
                print(f"Ati pierdut!\nScor:{self.jminScore}\nScor calculator:{self.jmaxScore}")
            else:
                print(f"Ati castigat!\nScor:{self.jminScore}\nScor calculator:{self.jmaxScore}")

    def playGUI(self):
        startTime = time.time()
        player = True
        computerMoves = 0
        playerMoves = 0

        modifier = 100
        pygame.init()
        mwidth = self.nrColReal * modifier
        mheight = self.nrLinReal * modifier
        winwidth = mwidth + 2 * modifier
        maxPoz = self.nrLinReal * 2
        crtPoz = 0
        screen = pygame.display.set_mode((winwidth, mheight))
        pygame.display.set_caption('DotsAndBoxes')

        for i in range(self.nrLin + 1):  # print starting game board
            for j in range(self.nrCol + 1):
                rect = Rect(j*2*modifier,i*2*modifier,modifier,modifier)
                pygame.draw.rect(screen, WHITE, rect)
        for i in range(self.nrLin):
            for j in range(self.nrCol):
                rect = Rect(j*2*modifier + modifier,i*2*modifier + modifier,modifier,modifier)
                pygame.draw.rect(screen, BLUE, rect)


        font = pygame.font.SysFont('arial', 20)  # setup font

        while not self.isEndGame():
            if player:  # daca este randul computerului
                pygame.event.pump()
                computerMoves += 1
                moveTime = time.time()
                move = self.findMove()

                msg = f"Timp gandire:"
                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                msg = f"{'{:.4f}'.format(time.time() - moveTime)}"
                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)
                msg = f"Lin:{move.lin}, Col:{move.col}"
                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, RED)

                poz = convertToGUI(move.lin, move.col, modifier)
                rect = Rect(poz[0], poz[1], modifier, modifier)
                pygame.draw.rect(screen, WHITE, rect)
                pygame.display.update()

                goAgain = False


                if move.lin % 2 == 0:
                    self.board[move.lin][move.col] = "-"
                    if self.checkBoxAbove(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin - 1][move.col] = self.jmax
                        poz = convertToGUI(move.lin - 1, move.col, modifier)
                        showSymbol(poz[0],poz[1],screen, self.jmax, modifier)
                        self.jmaxScore += 1
                    if self.checkBoxBelow(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin + 1][move.col] = self.jmax
                        poz = convertToGUI(move.lin + 1, move.col, modifier)
                        showSymbol(poz[0], poz[1], screen, self.jmax, modifier)
                        self.jmaxScore += 1
                else:
                    self.board[move.lin][move.col] = "|"
                    if self.checkBoxLeft(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin][move.col - 1] = self.jmax
                        poz = convertToGUI(move.lin, move.col - 1, modifier)
                        showSymbol(poz[0], poz[1], screen, self.jmax, modifier)
                        self.jmaxScore += 1
                    if self.checkBoxRight(move.lin, move.col):
                        goAgain = True
                        self.board[move.lin][move.col + 1] = self.jmax
                        poz = convertToGUI(move.lin, move.col + 1, modifier)
                        showSymbol(poz[0], poz[1], screen, self.jmax, modifier)
                        self.jmaxScore += 1
                if not goAgain:
                    player = not player

            else:  # daca este randul jucatorului
                msg = "Alegeti o mutare!"
                crtPoz = showMessage(screen, mwidth, modifier, font, msg, crtPoz, maxPoz, GREEN)
                pygame.display.update()
                while True:
                    ok = True
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            scor = self.evaluate()
                            print(f"Ati incheiat jocul!\nScor:{self.jminScore}\nScor calculator:{self.jmaxScore}")
                            print(f"Timp de joc:{time.time() - startTime}")
                            print(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}")
                            sys.exit()
                        if event.type == MOUSEBUTTONDOWN:
                            poz = pygame.mouse.get_pos()
                            poz = convertFromGUI(poz[0],poz[1],modifier)
                            if poz[1] < self.nrColReal:
                                ok = False
                                break
                    if not ok:
                        break

                lin = poz[0]
                col = poz[1]
                goAgain = False

                if (lin % 2 == 0 and col % 2 == 1) or (lin % 2 == 1 and col % 2 == 0):
                    if self.board[lin][col] == " ":

                        playerMoves += 1

                        poz = convertToGUI(poz[0], poz[1], modifier)
                        rect = Rect(poz[0], poz[1], modifier, modifier)
                        pygame.draw.rect(screen, WHITE, rect)
                        pygame.display.update()

                        if lin % 2 == 0:
                            self.board[lin][col] = "-"
                            if self.checkBoxAbove(lin, col):
                                goAgain = True
                                self.board[lin - 1][col] = self.jmin
                                poz = convertToGUI(lin - 1, col, modifier)
                                showSymbol(poz[0], poz[1], screen, self.jmin, modifier)
                                self.jminScore += 1
                            if self.checkBoxBelow(lin, col):
                                goAgain = True
                                self.board[lin + 1][col] = self.jmin
                                poz = convertToGUI(lin + 1, col, modifier)
                                showSymbol(poz[0], poz[1], screen, self.jmin, modifier)
                                self.jminScore += 1
                        else:
                            self.board[lin][col] = "|"
                            if self.checkBoxLeft(lin, col):
                                goAgain = True
                                self.board[lin][col - 1] = self.jmin
                                poz = convertToGUI(lin, col - 1, modifier)
                                showSymbol(poz[0], poz[1], screen, self.jmin, modifier)
                                self.jminScore += 1
                            if self.checkBoxRight(lin, col):
                                goAgain = True
                                self.board[lin][col + 1] = self.jmin
                                poz = convertToGUI(lin, col + 1, modifier)
                                showSymbol(poz[0], poz[1], screen, self.jmin, modifier)
                                self.jminScore += 1
                        # self.showBoardConfig()
                        # print(fHash(self.board))
                    else:
                        goAgain = True
                else:
                    goAgain = True

                if not goAgain:
                    player = not player
        else:
            scor = self.evaluate()
            showMessage(screen, mwidth, modifier, font, "GAME OVER!", 0, maxPoz)
            showMessage(screen, mwidth, modifier, font, "CLICK PT A CONTINUA!", 1, maxPoz)
            ok = True
            while ok:
                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN:
                        ok = False
                        break

            screen.fill(BLACK)
            midx = winwidth // 2
            midy = mheight // 2

            font = pygame.font.SysFont('arial', 30)
            text = font.render(f"Timp de joc:{time.time() - startTime}", True, WHITE)
            textRect = text.get_rect()
            textRect.center = (midx, midy + 2 * modifier)
            screen.blit(text, textRect)

            text = font.render(f"Nr mutari jucator:{playerMoves}   Nr mutari PC:{computerMoves}", True, WHITE)
            textRect = text.get_rect()
            textRect.center = (midx, midy + modifier)
            screen.blit(text, textRect)

            if scor == 0:
                text = font.render("Remiza!", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx , midy)
                screen.blit(text, textRect)
                text = font.render(f"Scor:{self.jminScore}  Scor calculator:{self.jmaxScore}", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx, midy - modifier)
                screen.blit(text, textRect)
            elif scor > 0:
                text = font.render("Ati pierdut!", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx, midy)
                screen.blit(text, textRect)
                text = font.render(f"Scor:{self.jminScore}  Scor calculator:{self.jmaxScore}", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx, midy - modifier)
                screen.blit(text, textRect)
            else:
                text = font.render("Ati castigat!", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx, midy)
                screen.blit(text, textRect)
                text = font.render(f"Scor:{self.jminScore}  Scor calculator:{self.jmaxScore}", True, WHITE)
                textRect = text.get_rect()
                textRect.center = (midx , midy - modifier)
                screen.blit(text, textRect)

            pygame.display.update()
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()

    def start(self):
        gameMode = input("Alegeti modul de joc(0 = consola/ 1 = GUI):")
        while gameMode != "0" and gameMode != "1":
            print("Input invalid!")
            gameMode = input("Alegeti modul de joc(0 = consola/ 1 = GUI):")
        if gameMode == "0":
            self.playConsole()
        else:
            self.playGUI()


def convertFromGUI(x, y, modifier):  # functie utilitara pt a converti pozitie din gui in matrice
    return ((y//modifier, x//modifier))  # (nrcol, nrlin)

def convertToGUI(lin, col, modifier):  # functie utilitara pt a converti pozitie din matrice in gui
    return ((col * modifier, lin * modifier))

def showMessage(screen, mwidth, modifier, font, msg, position, maxPoz, color = None):
    # functie pt afisare log message in GUI
    if position == 0:  # clear log
        rect = Rect(mwidth , 0, 2 * modifier, maxPoz * 2 * modifier)
        screen.fill(BLACK, rect)

    text = font.render(msg, True, WHITE)

    textRect = text.get_rect()
    # textRect = rect.fit(textRect)

    textRect.center = (mwidth + modifier, modifier // 4 + position * (modifier//2))

    if color != None:
        textRect.width = modifier * 2
        textRect.height = modifier // 2
        textRect.left = mwidth
        textRect.top = position * (modifier // 2)
        pygame.draw.rect(screen, color, textRect)

    screen.blit(text, textRect)

    pygame.display.update()
    position += 1

    if position == maxPoz:
        return 0
    else:
        return position

def showSymbol(x, y, screen, symbol, modifier):  # functie pt a marca simbolul unui jucator pe gui
    font = pygame.font.SysFont('arial', 50)
    text = font.render(symbol, True, WHITE)
    textRect = text.get_rect()
    textRect.center = (x + modifier//2, y + modifier//2)
    screen.blit(text, textRect)
    pygame.display.update()

if __name__ == "__main__":
    newGame = Game()
    newGame.start()