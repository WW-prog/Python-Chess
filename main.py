# --------------------------------------------------
# MAIN PYTHON FILE TO RUN
# --------------------------------------------------
import pygame
import sys
# import external file stuff
from src.const import * # import all from const.py
from src.board import * # import classes from class.py
from tkinter import *
import tkinter.messagebox
# --------------------------------------------------
class Main:
    # --------------------------------------------------
    # things to do on start
    def __init__(self):
        pygame.init()
        # create screen as variable self.screen
        self.screen = pygame.display.set_mode((width, height)) 
        # set caption of display as "Chess"
        pygame.display.set_caption('Chess') 
        # create variable "displayRender" which renders the display
        self.displayRender = Render()
    # --------------------------------------------------
    # show screen methods, separated to clean up code
    def showScreen(self, displayRender, screen):
        displayRender.showBackground(screen)
        displayRender.showLastMove(screen)
        displayRender.showPieces(screen)
    def showMovesScreen(self, displayRender, screen):
        displayRender.showBackground(screen)
        displayRender.showMoves(screen)
        displayRender.showLastMove(screen)
        displayRender.showPieces(screen)
    # --------------------------------------------------
    # main recurring loop to run, done after init
    def mainLoop(self):
        # set initialized variables to local (not technically necessary, but cleans up code)
        screen = self.screen
        displayRender = self.displayRender
        board = self.displayRender.board
        move = self.displayRender.move
        # --------------------------------------------------
        # en passant
        epPawn = [None,None,None]
        # --------------------------------------------------
        # loop
        while True:
            # --------------------------------------------------
            # update screen with render method
            self.showMovesScreen(displayRender, screen)
            # prevent display refresh from erasing movement image
            if move.moving:
                move.updateBlit(screen)
            # --------------------------------------------------
            # check game state
            for event in pygame.event.get():
                # --------------------------------------------------
                # click to select piece
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # save initial position
                    move.updatePoint(event.pos)
                    # targeted row, corrected for square size
                    targetedRow = int(move.pointY // squareSize)
                    targetedCol = int(move.pointX // squareSize)
                    # check if the selected square has a piece
                    if board.squares[targetedRow][targetedCol].hasPiece:
                        # piece is there
                        # --------------------------------------------------
                        # save initial piece type
                        piece = board.squares[targetedRow][targetedCol].piece
                        # --------------------------------------------------
                        # make sure move is being made by the right player
                        if piece.color == displayRender.nextPlayer:
                            # --------------------------------------------------
                            # find possible moves
                            board.findMoves(piece, targetedRow, targetedCol)
                            # save initial position and piece
                            move.initialPos(event.pos)
                            move.movePiece(piece)
                            # show screen
                            self.showMovesScreen(displayRender, screen)
                            # --------------------------------------------------
                        # --------------------------------------------------
                # --------------------------------------------------
                # move mouse to desired location
                elif event.type == pygame.MOUSEMOTION:
                    # check if piece is being moved
                    if move.moving and piece.color == displayRender.nextPlayer:
                        move.updatePoint(event.pos)
                        # show screen
                        self.showMovesScreen(displayRender, screen)
                        move.updateBlit(screen)
                # --------------------------------------------------
                # click release to place piece
                elif event.type == pygame.MOUSEBUTTONUP:
                    if move.moving:
                        move.updatePoint(event.pos)
                        releaseRow = int(move.pointY // squareSize)
                        releaseCol = int(move.pointX // squareSize)
                        # create move
                        proposedMove = MovePiece(Square(move.initRow, move.initCol), Square(releaseRow, releaseCol))
                        # check if move is valid
                        if board.valid_move_piece(move.piece,proposedMove):
                            # execute move
                            board.move_piece(move.piece,proposedMove)
                            # check castling
                            # --------------------------------------------------
                            # if king is moved
                            if move.piece.name == "King":
                                # if king moved 2 spaces, then move rook to other side
                                # queen side
                                if move.initCol - releaseCol == 2:
                                    currRook = board.squares[int(move.initRow)][0].piece
                                    rookMove = MovePiece(Square(int(move.initRow), 0),Square(int(move.initRow),3))
                                    board.move_piece(currRook,rookMove)
                                # king side
                                elif move.initCol - releaseCol == -2:
                                    currRook = board.squares[int(move.initRow)][7].piece
                                    rookMove = MovePiece(Square(int(move.initRow), 7),Square(int(move.initRow), 5))
                                    board.move_piece(currRook,rookMove)
                            # --------------------------------------------------
                            # set en passant to possible
                            # if pawn is moved
                            if move.piece.name == "Pawn":
                                # --------------------------------------------------
                                # en passant check
                                # if pawn moved diagonal
                                if abs(releaseRow - move.initRow) == 1 and abs(releaseCol - move.initCol) == 1:
                                    # if pawn moved behind ep pawn
                                    dir = 1 if epPawn[2] == "white" else -1
                                    if releaseCol == epPawn[1] and releaseRow == epPawn[0]+dir:
                                        # remove ep pawn
                                        board.squares[epPawn[0]][epPawn[1]].piece = None
                                # --------------------------------------------------
                                # if pawn moved 2 squares, set epPawn to pawn's coordinate
                                if abs(releaseRow - move.initRow) == 2:
                                    epPawn = [releaseRow,releaseCol,move.piece.color]
                                else:
                                    epPawn = [None,None,None]
                                # --------------------------------------------------
                            # otherwise, set epPawn to None
                            else:
                                epPawn = [None,None,None]
                            # update board to know which pawn is vulnerable
                            board.epRow = epPawn[0]
                            board.epCol = epPawn[1]
                            # --------------------------------------------------
                            # go to next player turn
                            displayRender.nextTurn()
                            # show screen
                            self.showScreen(displayRender, screen)
                    # stop moving piece
                    move.unmovePiece()
                    # --------------------------------------------------
                    # check if king is taken
                    wKing = 0
                    bKing = 0
                    # loop through board
                    for cRow in range(0,8):
                        for cCol in range(0,8):
                            currPiece = board.squares[cRow][cCol].piece
                            if currPiece:
                                if currPiece.name == "King":
                                    if currPiece.color == "white":
                                        wKing = 1
                                    if currPiece.color == "black":
                                        bKing = 1
                    if bKing == 0:
                        # if black king not present, white wins
                        tkinter.messagebox.showinfo("","White Wins!")
                        pygame.quit()
                        sys.exit()
                    if wKing == 0:
                        # if white king not present, black wins
                        tkinter.messagebox.showinfo("","Black Wins!")
                        pygame.quit()
                        sys.exit()
                    # --------------------------------------------------
                # --------------------------------------------------
                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # --------------------------------------------------
            # --------------------------------------------------
            # update board state after move
            pygame.display.update()
            # --------------------------------------------------
        # --------------------------------------------------
# --------------------------------------------------
main = Main()
main.mainLoop()
# --------------------------------------------------