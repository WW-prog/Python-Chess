# --------------------------------------------------
# HANDLE GAMEPLAY, DISPLAY FUNCTIONALITY HERE
# --------------------------------------------------
# imports
from src.const import *
import pygame
import os
from tkinter import *
import tkinter.messagebox
# --------------------------------------------------
# board class handles entire board of squares
class Board:
    # --------------------------------------------------
    def __init__(self):
        # create blank board based on the columns and rows, holds the current board state
        self.squares = [[0 for col in range(cols)] for row in range(rows)]
        self.bCreate()
        self.bAddPiece("white")
        self.bAddPiece("black")
        self.lastMove = None
        self.epRow = None # info for en passant
        self.epCol = None
    # --------------------------------------------------
    # private methods to alter the board
    # set starting board
    def bCreate(self):
        # set board to hold squares instead of blank spaces
        for row in range(rows):
            for col in range(cols):
                self.squares[row][col] = Square(row,col)
    # --------------------------------------------------
    # add initial pieces to board
    def bAddPiece(self, color):
        # black pieces in first two rows
        # white pieces in last two rows
        row_pawn, row_other = (6,7) if color =="white" else (1,0)
        # add all pawns
        for col in range(cols):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        # add bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))
        # add knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))
        # add rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))
        # add queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))
        # add king
        self.squares[row_other][4] = Square(row_other, 4, King(color))
    # --------------------------------------------------
    # find possible moves
    def findMoves(self, piece, row, col):
        # --------------------------------------------------
        # methods to hold movement info for pieces, separated to clean up code
        # store possible moves as an array
        # --------------------------------------------------
        def pawnMove():
            # (y+1)
            # (y+2) -- if pawn has not moved
            # (x+1,y+1), (x-1,y+1) -- if taking piece
            # check if pawn has moved
            steps = 1
            if not piece.moved:
                steps = 2
            # --------------------------------------------------
            # blank space
            init = row + piece.direction
            target = row + (piece.direction*(1+steps))
            for movement in range(init,target,piece.direction):
                if Square.inRange(movement):
                    if (not self.squares[movement][col].hasPiece()):
                        # add move
                        piece.add_moves(MovePiece(Square(row,col), Square(movement,col)))
                        # update moved status
                        piece.moved = True
                    # blocked
                    else:
                        break
                # not in range
                else:
                    break
            # --------------------------------------------------
            # capture piece
            captureRow = row + piece.direction
            captureCol = [col-1,col+1]
            for possibleCaptureCol in captureCol:
                # check if diagonal is in bounds
                if Square.inRange(captureRow,possibleCaptureCol):
                    # check if it has opponent piece
                    if self.squares[captureRow][possibleCaptureCol].hasOpponentPiece(piece.color):
                        # add move
                        piece.add_moves(MovePiece(Square(row,col),Square(captureRow,possibleCaptureCol)))
                        # update moved status
                        piece.moved = True
            # --------------------------------------------------
            # en passant
            if self.epRow and self.epCol:
                # to the right
                if row == self.epRow and (col == self.epCol + 1 or col == self.epCol - 1):
                    # en passant possible
                    piece.add_moves(MovePiece(Square(row,col),Square(row+piece.direction,self.epCol)))
            # --------------------------------------------------
        # --------------------------------------------------
        def knightMove():
            # (x+2,y+1), (x+2,y-1), (x+1,y+2), (x+1,y-2)
            # (x-2, y+1), (x-2, y-1), (x-1,y+2), (x-1,y-2)
            possibleMoves = [
                (row+2,col+1),
                (row+2,col-1),
                (row+1,col+2),
                (row+1,col-2),
                (row-2,col+1),
                (row-2,col-1),
                (row-1,col+2),
                (row-1,col+2),
            ]
            # loop through array of possible moves and remove any that are not possible
            for pMove in possibleMoves:
                pMoveRow, pMoveCol = pMove
                if Square.inRange(pMoveRow, pMoveCol):
                    # move is not outside the board
                    if self.squares[pMoveRow][pMoveCol].isEmptyOrOpponent(piece.color):
                        # move lands on an empty space or opponent piece
                        # create a new move
                        init = Square(row,col)
                        target = Square(pMoveRow,pMoveCol)
                        movePiece = MovePiece(init,target)
                        # append valid move
                        piece.add_moves(movePiece)
        # --------------------------------------------------
        # since bishop, rook, and queen are so similar, use straightMoves to do the logic for all 3 at once
        def straightMoves(increment):
            for inc in increment:
                rowInc, colInc = inc
                possibleRow = row + rowInc
                possibleCol = col + colInc
                while True:
                    # check if in bounds
                    if Square.inRange(possibleRow,possibleCol):
                        # fill empty space until piece blocks or end of board
                        if (not self.squares[possibleRow][possibleCol].hasPiece()):
                            piece.add_moves(MovePiece(Square(row,col),Square(possibleRow,possibleCol)))
                        # if opponent piece is blocking, then that space is valid
                        if self.squares[possibleRow][possibleCol].hasOpponentPiece(piece.color):
                            piece.add_moves(MovePiece(Square(row,col),Square(possibleRow,possibleCol)))
                            # break loop for direction
                            break
                        # if own piece is blocking, then that space is not valid
                        if (not self.squares[possibleRow][possibleCol].hasOpponentPiece(piece.color)) and self.squares[possibleRow][possibleCol].hasPiece():
                            break
                        # update position
                        possibleRow = possibleRow + rowInc
                        possibleCol = possibleCol + colInc
                    else:
                        break
        # --------------------------------------------------
        def bishopMove():
            straightMoves([
                (1,1),
                (1,-1),
                (-1,1),
                (-1,-1)
            ])
        # --------------------------------------------------
        def rookMove():
            straightMoves([
                (0,-1),
                (0,1),
                (-1,0),
                (1,0)
            ])
        # --------------------------------------------------
        def queenMove():
            straightMoves([
                (1,1),
                (1,-1),
                (-1,1),
                (-1,-1),
                (0,-1),
                (0,1),
                (-1,0),
                (1,0)
            ])
        # --------------------------------------------------
        def kingMove():
            # --------------------------------------------------
            # move 1 in all directions
            movement = [
                (row,col+1),
                (row,col-1),
                (row+1,col),
                (row+1,col+1),
                (row+1,col-1),
                (row-1,col),
                (row-1,col+1),
                (row-1,col-1)
            ]
            # --------------------------------------------------
            # normal move
            for possibleMove in movement:
                possibleRow, possibleCol = possibleMove
                # check if in range
                if Square.inRange(possibleRow,possibleCol):
                    # if opponent or empty
                    if self.squares[possibleRow][possibleCol].isEmptyOrOpponent(piece.color):
                        piece.add_moves(MovePiece(Square(row,col),Square(possibleRow,possibleCol)))
            # --------------------------------------------------
            # castling
            # if king hasn't moved
            if not piece.moved:
                # --------------------------------------------------
                # king side
                # if rook hasn't moved
                currRow = row
                rightRook = self.squares[currRow][7]
                leftRook = self.squares[currRow][0]
                if not rightRook.piece.moved:
                    # if no piece in between
                    for space in range(5,7):
                        if self.squares[currRow][space].hasPiece():
                            # piece in between
                            break
                        if space == 6:
                            # add castling as potential move
                            # king side: rook (0,7) to (0,5), king (0,4) to (0,6)
                            piece.add_moves(MovePiece(Square(row,col),Square(row,6)))
                # --------------------------------------------------
                # queen side
                # if rook hasn't moved
                if not leftRook.piece.moved:
                    # if no piece in between
                    for space in range(1,4):
                        if self.squares[currRow][space].hasPiece():
                            # piece in between
                            break
                        if space == 3:
                            # add castling as potential move
                            # queen side: rook (0,0) to (0,3), king (0,4) to (0,2)
                            piece.add_moves(MovePiece(Square(row,col),Square(row,2)))
                # --------------------------------------------------
            # --------------------------------------------------
        # --------------------------------------------------
        # first check piece
        if isinstance(piece, Pawn): pawnMove()
        elif isinstance(piece, Knight): knightMove()
        elif isinstance(piece, Bishop): bishopMove()
        elif isinstance(piece, Rook): rookMove()
        elif isinstance(piece, Queen): queenMove()
        elif isinstance(piece, King): kingMove()
        # --------------------------------------------------
    # --------------------------------------------------
    # updating the board to reflect move
    def move_piece(self,piece,move):
        init = move.init
        target = move.target
        # --------------------------------------------------
        # change board location values
        # change start point to empty space
        self.squares[int(init.row)][int(init.col)].piece = None
        # change target space to piece
        self.squares[target.row][target.col].piece = piece
        # --------------------------------------------------
        # pawn promotion
        if isinstance(piece, Pawn):
            # don't need to check color since pawn cannot move backwards
            if target.row == 0 or target.row == 7:
                # make the chosen piece global so that it can be updated
                global chosenPiece
                # default value: if window is closed, then queen is the chosen piece
                chosenPiece = Queen(piece.color)
                # chosenPiece = None
                # --------------------------------------------------
                # alert to ask user what piece to promote to
                # create root
                root = tkinter.Tk()
                # set visual info
                root.title("Promotion")
                root.geometry(f'{popupWidth}x{popupHeight}')
                # message box info
                def promoteKnight():
                    global chosenPiece
                    chosenPiece = Knight(piece.color)
                    root.destroy()
                def promoteBishop():
                    global chosenPiece
                    chosenPiece = Bishop(piece.color)
                    root.destroy()
                def promoteRook():
                    global chosenPiece
                    chosenPiece = Rook(piece.color)
                    root.destroy()
                def promoteQueen():
                    global chosenPiece
                    chosenPiece = Queen(piece.color)
                    root.destroy()
                # create buttons
                buttonKnight = Button(root, text="Knight", command=promoteKnight, height=5,width=10)
                buttonBishop = Button(root, text="Bishop", command=promoteBishop, height=5,width=10)
                buttonRook = Button(root, text="Rook", command=promoteRook, height=5,width=10)
                buttonQueen = Button(root, text="Queen", command=promoteQueen, height=5,width=10)
                # position buttons
                buttonKnight.pack(side="left")
                buttonBishop.pack(side="right")
                buttonRook.pack(side="bottom")
                buttonQueen.pack(side="top")
                # run window
                root.mainloop()
                # --------------------------------------------------
                # set piece
                self.squares[target.row][target.col].piece = chosenPiece
        # --------------------------------------------------
        # update piece moved status
        piece.moved = True
        # clear valid moves
        piece.clear_moves()
        # update last move
        self.lastMove = move
    # --------------------------------------------------
    # gives the move in the piece
    def valid_move_piece(self,piece,move):
        return move in piece.moves
    # --------------------------------------------------
# --------------------------------------------------
# square class, handles individual squares
class Square:
    # --------------------------------------------------
    # get square's current row, column position and what piece(if any) is on that square
    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
    # --------------------------------------------------
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    # --------------------------------------------------
    # check if current space holds a piece
    def hasPiece(self):
        return self.piece != None
    # --------------------------------------------------
    # check if given move is outside the board
    @staticmethod # make the method static so that it doesn't require an instance of the Square class
    def inRange(*args): # inRange takes many parameters
        # loop through arguments, return false if it breaks a rule
        for arg in args:
            # outside the board
            if arg < 0 or arg > 7:
                return False
        # if no rules are broken, then return true
        return True
    # --------------------------------------------------
    # check if the space has the opponent's piece
    def hasOpponentPiece(self, color):
        # must both have a piece and the piece is of a different color
        return (self.hasPiece() and self.piece.color != color)
    # --------------------------------------------------
    # check if the move lands on an empty space or an opponent's space
    def isEmptyOrOpponent(self, color):
        return ((not self.hasPiece()) or self.hasOpponentPiece(color))
    # --------------------------------------------------
    # check if the space has own piece
    def hasOwnPiece(self, color):
        # must both have a piece and the piece is of the same color
        return (self.hasPiece() and self.piece.color == color)
    # --------------------------------------------------
# --------------------------------------------------
# piece class, handles pieces on squares 
class Piece: 
    # --------------------------------------------------
    # individual piece traits (value is used for AI using conventional weights)
    # pawn = 1
    # bishop, knight = 3
    # rook = 5
    # queen = 8
    # king = inf
    def __init__(self, name, color, value, icon=None, icon_rect=None):
        self.name = name
        self.color = color
        # get correct direction for board side
        value_sign = 1 if color == "white" else -1
        self.value = value*value_sign
        self.icon = icon
        self.set_icon() # set the image here
        self.icon_rect = icon_rect
        self.moves = [] # holds all of the moves (in order)
        self.moved = False # holds move status
    # --------------------------------------------------
    # set the square's icon
    def set_icon(self):
        # search for src/assets, get the png file with the correct name
        fileName = self.color[0] + self.name
        self.icon = os.path.join(
            f'src/assets/{fileName}.png')
    # --------------------------------------------------
    # add move to board
    def add_moves(self, move):
        self.moves.append(move)
    # --------------------------------------------------
    # clear moves once move is done
    def clear_moves(self):
        self.moves = []
    # --------------------------------------------------
# pawn
class Pawn(Piece):
    def __init__(self, color):
        # pawns are color specific for direction
        self.direction = -1 if color == "white" else 1
        super().__init__("Pawn", color, 1.0)
# knight
class Knight(Piece):
    def __init__(self, color):
        super().__init__("Knight", color, 3.0)
# bishop
class Bishop(Piece):
    def __init__(self, color):
        super().__init__("Bishop", color, 3.0)
# rook
class Rook(Piece):
    def __init__(self, color):
        super().__init__("Rook", color, 5.0)
# queen
class Queen(Piece):
    def __init__(self, color):
        super().__init__("Queen", color, 8.0)
# king (value is set to the sum of all other pieces)
class King(Piece):
    def __init__(self, color):
        super().__init__("King", color, 38.0)
# --------------------------------------------------
# render class, handles rendering pieces and board
class Render:
    # --------------------------------------------------
    def __init__(self):
        self.board = Board()
        # create move instance
        self.move = Move()
        # handle move order, start with white
        self.nextPlayer = "white"
    # --------------------------------------------------
    # draw board here
    def showBackground(self, display):
        for row in range(rows):
            for col in range (cols):
                # --------------------------------------------------
                # for even tiles, make it white
                if (row+col)%2==0:
                    tileColor = whiteCol
                # otherwise, make it black
                else:
                    tileColor = blackCol
                # --------------------------------------------------
                # draw board, (offsetX,offsetY,width,height)
                board = (col * squareSize, row * squareSize, squareSize, squareSize)
                pygame.draw.rect(display, tileColor, board)
                # --------------------------------------------------
    # --------------------------------------------------
    # show pieces
    def showPieces(self, display):
        for row in range(rows):
            for col in range(cols):
                # check piece
                if self.board.squares[row][col].hasPiece():
                    piece = self.board.squares[row][col].piece
                    # make exception for moved piece so it disappears when being moved
                    if piece is not self.move.piece: 
                        img = pygame.image.load(piece.icon)
                        img_center = col*squareSize+squareSize//2,  row*squareSize+squareSize//2
                        piece.icon_rect = img.get_rect(center=img_center)
                        display.blit(img, piece.icon_rect)
    # --------------------------------------------------
    # show move with color over square
    def showMoves(self, display):
        if self.move.moving:
            piece = self.move.piece
            # loop through all valid moves
            for move in piece.moves:
                color = moveCol
                rect = (move.target.col * squareSize, move.target.row * squareSize, squareSize, squareSize)
                pygame.draw.rect(display, color, rect)
    # --------------------------------------------------
    # switch to next turn
    def nextTurn(self):
        self.nextPlayer = "white" if self.nextPlayer == "black" else "black"
    # --------------------------------------------------
    def showLastMove(self, display):
        # check if a move was made before
        if self.board.lastMove:
            init = self.board.lastMove.init
            target = self.board.lastMove.target
            for pos in [init,target]:
                # show previous move
                color = prevCol
                rect = (pos.col * squareSize, pos.row * squareSize, squareSize, squareSize)
                pygame.draw.rect(display, color, rect)
    # --------------------------------------------------
# --------------------------------------------------
# move class, handles moving pieces visually
class Move:
    # --------------------------------------------------
    def __init__(self):
        # pointX, pointY hold mouse position
        self.pointX = 0
        self.pointY = 0
        # saved initial values
        self.initRow = 0
        self.initCol = 0
        self.piece = None
        # check whether piece is being moved or not
        self.moving = False
    # --------------------------------------------------
    # update the mouse position with input position
    def updatePoint(self, position):
        self.pointX, self.pointY = position
    # --------------------------------------------------
    def initialPos(self, position):
        # save initial point
        self.initCol, self.initRow = position[0] // squareSize, position[1] // squareSize
    # --------------------------------------------------
    def movePiece(self, piece):
        # save initial piece, change state to moving piece
        self.piece = piece
        self.moving = True
    # --------------------------------------------------
    def unmovePiece(self):
        # change state to no longer moving
        self.piece = None
        self.moving = False
    # --------------------------------------------------
    def updateBlit(self, screen):
        img = pygame.image.load(self.piece.icon)
        # normalize point to be within the square
        normalizedPointX, normalizedPointY = int(self.pointX // squareSize) * squareSize + squareSize // 2, int(self.pointY // squareSize) * squareSize + squareSize // 2
        img_center = (normalizedPointX, normalizedPointY)
        self.piece.icon_rect = img.get_rect(center=img_center)
        screen.blit(img, self.piece.icon_rect)
# --------------------------------------------------
# move piece class, handles moving pieces on board
class MovePiece:
    # --------------------------------------------------
    def __init__(self, init, target):
        self.init = init
        self.target = target
    # --------------------------------------------------
    def __str__(self):
        s = ''
        s += f'({self.init.col}, {self.init.row})'
        s += f' -> ({self.target.col}, {self.target.row})'
        return s
    # --------------------------------------------------
    def __eq__(self, other):
        return self.init == other.init and self.target == other.target
    # --------------------------------------------------
# --------------------------------------------------