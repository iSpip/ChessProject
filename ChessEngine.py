import copy
import ChessBot
import Zobrist
import numpy as np


class GameState:

    zobrist_hash = Zobrist.ChessHash()

    def __init__(self):

        # 0 = empty, 1 = pawn, 2 = knight, 3 = bishop, 4 = rook, 5 = queen, 6 = king, same for black + 8
        self.board = [
            [12, 10, 11, 13, 14, 11, 10, 12],
            [9, 9, 9, 9, 9, 9, 9, 9],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ]

        # State of the game
        self.whiteToMove = True
        self.inCheck = False
        self.checkmate = False
        self.stalemate = False

        # Keeping track of king location saves a lot of time
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # Special cases : pins, checks, en passant, castle rights
        self.pins = []               # Row of pinned piece, col of pinned piece, direction [0], direction [1]
        self.checks = []             # Row of attacking piece, col of attacking piece, direction [0], direction [1]
        self.enPassantPossible = ()  # Coordinates of the square where en passant is possible
        self.currentCastleRights = CastleRights(True, True, True, True)     # wks, wqs, bks, bqs

        # Logs to undo moves. Better idea would be to create a list of Game States.
        self.moveLog = []
        self.castleRightsLog = [copy.deepcopy(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs,
                                                           self.currentCastleRights.bks, self.currentCastleRights.bqs))]
        self.enPassantLog = [()]

        # Move function to make it easier to call the different methods
        self.moveFunctions = {1: self.getPawnMoves, 2: self.getKnightMoves, 3: self.getBishopMoves,
                              4: self.getRookMoves, 5: self.getQueenMoves, 6: self.getKingMoves}

        # Zobrist hash to see whether the position has already been analyzed
        self.zobristHash = self.zobrist_hash.calculate_hash(self.board, self.currentCastleRights, self.enPassantPossible, self.whiteToMove)

        # Keeping track of the squares attacked by pawns to help the move ordering
        self.whitePawnAttackingSquares = [(5, 1), (5, 0), (5, 2), (5, 1), (5, 3), (5, 2), (5, 4),
                                          (5, 3), (5, 5), (5, 4), (5, 6), (5, 5), (5, 7), (5, 6)]
        self.blackPawnAttackingSquares = [(2, 1), (2, 0), (2, 2), (2, 1), (2, 3), (2, 2), (2, 4),
                                          (2, 3), (2, 5), (2, 4), (2, 6), (2, 5), (2, 7), (2, 6)]
        self.whitePawnAttackingSquaresLog = [[(5, 1), (5, 0), (5, 2), (5, 1), (5, 3), (5, 2), (5, 4),
                                              (5, 3), (5, 5), (5, 4), (5, 6), (5, 5), (5, 7), (5, 6)]]
        self.blackPawnAttackingSquaresLog = [[(2, 1), (2, 0), (2, 2), (2, 1), (2, 3), (2, 2), (2, 4),
                                              (2, 3), (2, 5), (2, 4), (2, 6), (2, 5), (2, 7), (2, 6)]]

        # Keeping track of the material on the board to know if we reached "late game"
        self.whiteMaterial = 4000
        self.blackMaterial = 4000
        self.lateGameWeight = 8000

    def __repr__(self):
        return f'{self.board}'

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        # Update pawn attacking squares
        self.updatePawnAttackingSquares(move)
        self.whitePawnAttackingSquaresLog.append(copy.deepcopy(self.whitePawnAttackingSquares))
        self.blackPawnAttackingSquaresLog.append(copy.deepcopy(self.blackPawnAttackingSquares))

        # Pawn promotion
        if move.isPawnPromotion:
            if self.whiteToMove:
                self.board[move.endRow][move.endCol] = move.promotedPieceType

            else:
                self.board[move.endRow][move.endCol] = move.promotedPieceType + 8

        # En passant
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = 0

        if move.pieceMoved % 8 == 1 and (abs(move.startRow - move.endRow) == 2):
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()

        self.enPassantLog.append(copy.deepcopy(self.enPassantPossible))

        # Castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = 0
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = 0

        # Update castle rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            copy.deepcopy(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs,
                                       self.currentCastleRights.bks, self.currentCastleRights.bqs)))

        if move.pieceMoved == 6:
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == 14:
            self.blackKingLocation = (move.endRow, move.endCol)

        self.zobristHash = self.zobrist_hash.calculate_hash(self.board, self.currentCastleRights, self.enPassantPossible, self.whiteToMove)
        # print(self.zobristHash)

        self.whiteToMove = not self.whiteToMove

    def updateLateGameWeight(self):
        whiteMat = 0
        blackMat = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece > 8 and piece != 14:
                    blackMat += ChessBot.pieceValue[piece % 8]
                elif 0 < piece < 8 and piece != 6:
                    whiteMat += ChessBot.pieceValue[piece]

        self.whiteMaterial = whiteMat
        self.blackMaterial = blackMat
        self.lateGameWeight = whiteMat + blackMat

    def undoMove(self):
        # print("Avant undo", self.castleRightsLog)
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            if move.pieceMoved == 6:
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 14:
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = 0
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                # self.enPassantPossible = (move.endRow, move.endCol)

            # if move.pieceMoved % 8 == 1 and abs(move.startRow - move.endRow) == 2:
            #     self.enPassantPossible = ()

            self.whitePawnAttackingSquaresLog.pop()
            self.whitePawnAttackingSquares = self.whitePawnAttackingSquaresLog[-1]
            self.blackPawnAttackingSquaresLog.pop()
            self.blackPawnAttackingSquares = self.blackPawnAttackingSquaresLog[-1]


            self.enPassantLog.pop()
            self.enPassantPossible = self.enPassantLog[-1]

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = 0
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = 0

            # undo castling rights
            self.castleRightsLog.pop()
            self.currentCastleRights = copy.deepcopy(self.castleRightsLog[-1])
            self.whiteToMove = not self.whiteToMove

            self.zobristHash = self.zobrist_hash.calculate_hash(self.board, self.currentCastleRights,
                                                                self.enPassantPossible, self.whiteToMove)
            # print(self.zobristHash)
            self.checkmate = False
            self.stalemate = False

    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs,
                                        self.currentCastleRights.bks, self.currentCastleRights.bqs)
        moves = []

        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:  # only one check, we can block it
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []

                # if Knight, must capture the piece
                if pieceChecking % 8 == 2:
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved % 8 != 6:
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

            else:  # double check
                self.getKingMoves(kingRow, kingCol, moves)

        else:  # not in check
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:    # change to check if castle rights are ok
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastleRights = tempCastleRights

        return moves

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                turn = int(piece > 8)
                if piece == 0:
                    pass
                elif (turn == 0 and self.whiteToMove) or (turn == 1 and not self.whiteToMove):
                    self.moveFunctions[piece % 8](r, c, moves)  # better than several if in a row

        return moves

    def getPawnMoves(self, r, c, moves):
        # We check first if the piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # self.pins.remove(self.pins[i])      # Does not seem necessary
                break

        if self.whiteToMove:
            if r >= 1:
                if self.board[r - 1][c] == 0:   # in front
                    if not piecePinned or pinDirection == (-1, 0):
                        if r == 1:
                            self.addPawnPromotionMoves(moves, r, c, r - 1, c)
                        else:
                            moves.append(Move((r, c), (r - 1, c), self.board))
                        if r == 6 and self.board[r - 2][c] == 0:
                            moves.append(Move((r, c), (r - 2, c), self.board))
                if c - 1 >= 0:
                    if self.board[r - 1][c - 1] > 8:    # enemy piece left front
                        if not piecePinned or pinDirection == (-1, -1):
                            if r == 1:
                                self.addPawnPromotionMoves(moves, r, c, r - 1, c - 1)
                            else:
                                moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
                if c + 1 <= 7:
                    if self.board[r - 1][c + 1] > 8:    # enemy piece right front
                        if not piecePinned or pinDirection == (-1, 1):
                            if r == 1:
                                self.addPawnPromotionMoves(moves, r, c, r - 1, c + 1)
                            else:
                                moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (-1, -1):
                            moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))
        else:
            if r <= 6:
                if self.board[r + 1][c] == 0:   # in front
                    if not piecePinned or pinDirection == (1, 0):
                        if r == 6:
                            self.addPawnPromotionMoves(moves, r, c, r + 1, c)
                        else:
                            moves.append(Move((r, c), (r + 1, c), self.board))
                        if r == 1 and self.board[r + 2][c] == 0:
                            moves.append(Move((r, c), (r + 2, c), self.board))
                if c - 1 >= 0:
                    if 0 < self.board[r + 1][c - 1] < 8:    # enemy piece left front
                        if not piecePinned or pinDirection == (1, -1):
                            if r == 6:
                                self.addPawnPromotionMoves(moves, r, c, r + 1, c - 1)
                            else:
                                moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
                if c + 1 <= 7:
                    if 0 < self.board[r + 1][c + 1] < 8:    # enemy piece right front
                        if not piecePinned or pinDirection == (1, 1):
                            if r == 6:
                                self.addPawnPromotionMoves(moves, r, c, r + 1, c)
                            else:
                                moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def addPawnPromotionMoves(self, moves, startRow, startCol, endRow, endCol):
        moves.append(Move((startRow, startCol), (endRow, endCol), self.board, isPawnPromotion=True, promotedPieceType=5))
        moves.append(Move((startRow, startCol), (endRow, endCol), self.board, isPawnPromotion=True, promotedPieceType=4))
        moves.append(Move((startRow, startCol), (endRow, endCol), self.board, isPawnPromotion=True, promotedPieceType=3))
        moves.append(Move((startRow, startCol), (endRow, endCol), self.board, isPawnPromotion=True, promotedPieceType=2))

    def getKnightMoves(self, r, c, moves):
        # We check first if the piece is pinned
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                # self.pins.remove(self.pins[i])
                break

        if not piecePinned:
            knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2))
            allyColor = 0 if self.whiteToMove else 1
            for knightMove in knightMoves:
                endRow = r + knightMove[0]
                endCol = c + knightMove[1]
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if not isAlliedPiece(endPiece, allyColor):
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        self.getSlidingPieceMoves(r, c, moves, directions)

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, 1), (0, -1))
        self.getSlidingPieceMoves(r, c, moves, directions)
        # # We check first if the piece is pinned
        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pins) - 1, -1, -1):
        #     if self.pins[i][0] == r and self.pins[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pins[i][2], self.pins[i][3])
        #         if self.board[r][c] % 8 != 5:
        #             self.pins.remove(self.pins[i])
        #         break
        #
        # directions = ((-1, 0), (1, 0), (0, 1), (0, -1))
        # allyColor = 0 if self.whiteToMove else 1
        # for d in directions:
        #     for i in range(1, 8):
        #         endRow = r + d[0] * i
        #         endCol = c + d[1] * i
        #         if 0 <= endRow <= 7 and 0 <= endCol <= 7:
        #             if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
        #                 endPiece = self.board[endRow][endCol]
        #                 if endPiece == 0:
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                 elif (endPiece // 8) + allyColor == 1:  # enemy piece
        #                     moves.append(Move((r, c), (endRow, endCol), self.board))
        #                     break
        #                 else:
        #                     break
        #         else:  # off the board
        #             break

    def getSlidingPieceMoves(self, r, c, moves, directions):
        # We check first if the piece is pinned
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                break

        allyColor = 0 if self.whiteToMove else 1
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == 0:  # No piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif isEnemyPiece(endPiece, allyColor):  # Enemy piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # Allied piece
                            break
                else:  # Off the board
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1))
        allyColor = 0 if self.whiteToMove else 1
        for kingMove in kingMoves:
            endRow = r + kingMove[0]
            endCol = c + kingMove[1]
            if self.validKingSquare(r, c, endRow, endCol, allyColor):   # Check if the square is safe : not in check
                moves.append(Move((r, c), (endRow, endCol), self.board))

    def validKingSquare(self, startRow, startCol, endRow, endCol, allyColor):
        validKingSquareBool = False

        if 0 <= endRow <= 7 and 0 <= endCol <= 7:
            endPiece = self.board[endRow][endCol]
            if not isAlliedPiece(endPiece, allyColor):
                if allyColor == 0:
                    self.whiteKingLocation = (endRow, endCol)
                    enemyKingLocation = self.blackKingLocation
                else:
                    self.blackKingLocation = (endRow, endCol)
                    enemyKingLocation = self.whiteKingLocation
                inCheck, pins, checks = self.checkForPinsAndChecks()

                if not inCheck:
                    if (abs(enemyKingLocation[0] - endRow) > 1) or (abs(enemyKingLocation[1] - endCol) > 1):
                        validKingSquareBool = True  # We make sure kings cannot "touch" each other

                # Place back the king at its original destination
                if allyColor == 0:
                    self.whiteKingLocation = (startRow, startCol)
                else:
                    self.blackKingLocation = (startRow, startCol)

        return validKingSquareBool

    def getCastleMoves(self, r, c, moves):
        if (self.whiteToMove and self.currentCastleRights.wks) or (
                not self.whiteToMove and self.currentCastleRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (
                not self.whiteToMove and self.currentCastleRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):  # A changer pour ne pas utiliser Square under attack
        allyColor = 0 if self.whiteToMove else 1
        if self.board[r][c + 1] == 0 and self.board[r][c + 2] == 0:
            if self.validKingSquare(r, c, r, c + 1, allyColor) and self.validKingSquare(r, c, r, c + 2, allyColor):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        allyColor = 0 if self.whiteToMove else 1
        if self.board[r][c - 1] == 0 and self.board[r][c - 2] == 0 and self.board[r][c - 3] == 0:
            if self.validKingSquare(r, c, r, c - 1, allyColor) and self.validKingSquare(r, c, r, c - 2, allyColor):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            allyColor = 0
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            allyColor = 1
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1), (0, 1), (0, -1), (1, 0), (-1, 0))

        for i in range(len(directions)):
            d = directions[i]
            possiblePin = ()
            for j in range(1, 8):
                endRow = startRow + d[0] * j
                endCol = startCol + d[1] * j
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    pieceType = endPiece % 8

                    if isAlliedPiece(endPiece, allyColor):
                        if endPiece % 8 != 6:
                            if possiblePin == ():
                                possiblePin = (endRow, endCol, d[0], d[1])
                            else:
                                break
                    elif isEnemyPiece(endPiece, allyColor):  # Enemy piece
                        # Now we need to make sure the enemy piece checks our king
                        if (pieceType == 1 and j == 1 and ((allyColor == 0 and 0 <= i <= 1) or
                                                           (allyColor == 1 and 2 <= i <= 3))) or \
                                (pieceType == 3 and 0 <= i <= 3) or \
                                (pieceType == 4 and 4 <= i <= 7) or \
                                (pieceType == 5):
                            if possiblePin == ():   # No protecting piece was on the way
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:   # It is a pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:
                    break  # off the board

        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2))
        for knightMove in knightMoves:
            endRow = startRow + knightMove[0]
            endCol = startCol + knightMove[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece % 8 == 2 and isEnemyPiece(endPiece, allyColor):
                    inCheck = True
                    checks.append((endRow, endCol, knightMove[0], knightMove[1]))

        return inCheck, pins, checks

    def updateCastleRights(self, move):
        # King has moved ?
        if move.pieceMoved == 6:
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False

        elif move.pieceMoved == 14:
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False

        # Rook has moved ?
        elif move.pieceMoved == 4 and move.startRow == 7:
            if move.startCol == 7:
                self.currentCastleRights.wks = False
            elif move.startCol == 0:
                self.currentCastleRights.wqs = False

        elif move.pieceMoved == 12 and move.startRow == 0:
            if move.startCol == 7:
                self.currentCastleRights.bks = False
            elif move.startCol == 0:
                self.currentCastleRights.bqs = False

        # Rook captured ?
        if move.pieceCaptured == 4:
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastleRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastleRights.wks = False

        elif move.pieceCaptured == 12:
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastleRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastleRights.bks = False

    def numberOfMovesWithDepth(self, depth):
        if depth == 0:
            return 1

        validMoves = self.getValidMoves()
        numPositions = 0

        for move in validMoves:
            self.makeMove(move)
            numPositions += self.numberOfMovesWithDepth(depth - 1)
            self.undoMove()

        return numPositions

    def fenToBoard(self, fen):
        piece_map = {
            'p': 9, 'n': 10, 'b': 11, 'r': 12, 'q': 13, 'k': 14,
            'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6
        }
        fenSplit = fen.split(' ')
        newBoard = fenSplit[0]
        turn = fenSplit[1]
        castleRights = fenSplit[2]
        enPassantSquare = fenSplit[3]

        # Make new board
        rows = newBoard.split('/')
        for i in range(len(rows)):
            row = rows[i]
            col = 0
            for j in range(len(row)):
                char = row[j]
                if char.isdigit():
                    for k in range(int(char)):
                        self.board[i][col] = 0
                        col += 1
                else:
                    self.board[i][col] = piece_map[char]
                    col += 1

        # Whose turn it is ?
        self.whiteToMove = True if turn == "w" else False

        # Castle rights
        if castleRights == "-":
            self.currentCastleRights = CastleRights(False, False, False, False)
            self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs,
                                                 self.currentCastleRights.bks, self.currentCastleRights.bqs)]
        else:
            (wks, wqs, bks, bqs) = (False, False, False, False)
            for i in range(len(castleRights)):
                if castleRights[i] == "K":
                    wks = True
                elif castleRights[i] == "Q":
                    wqs = True
                elif castleRights[i] == "k":
                    bks = True
                elif castleRights[i] == "q":
                    bqs = True
            self.currentCastleRights = CastleRights(wks, wqs, bks, bqs)
            self.castleRightsLog = [
                copy.deepcopy(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.wqs,
                                           self.currentCastleRights.bks, self.currentCastleRights.bqs))]

        # En Passant ?
        if enPassantSquare == "-":
            self.enPassantPossible = ()
        else:
            self.enPassantPossible = (Move.ranks_to_rows[enPassantSquare[1]], Move.files_to_cols[enPassantSquare[0]])

        self.checkForPinsAndChecks()

    def updatePawnAttackingSquares(self, move):
        # If a pawn moves
        if move.pieceMoved == 1:
            # Remove squares not attacked anymore
            if (move.startRow - 1, move.startCol - 1) in self.whitePawnAttackingSquares:
                self.whitePawnAttackingSquares.remove((move.startRow - 1, move.startCol - 1))
            if (move.startRow - 1, move.startCol + 1) in self.whitePawnAttackingSquares:
                self.whitePawnAttackingSquares.remove((move.startRow - 1, move.startCol + 1))

            # Add new attacking squares
            if not move.isPawnPromotion:
                if move.endCol >= 1:
                    self.whitePawnAttackingSquares.append((move.endRow - 1, move.endCol - 1))
                if move.endCol <= 6:
                    self.whitePawnAttackingSquares.append((move.endRow - 1, move.endCol + 1))

        elif move.pieceMoved == 9:
            # Remove squares not attacked anymore
            if (move.startRow + 1, move.startCol - 1) in self.blackPawnAttackingSquares:
                self.blackPawnAttackingSquares.remove((move.startRow + 1, move.startCol - 1))
            if (move.startRow + 1, move.startCol + 1) in self.blackPawnAttackingSquares:
                self.blackPawnAttackingSquares.remove((move.startRow + 1, move.startCol + 1))

            # Add new attacking squares
            if not move.isPawnPromotion:
                if move.endCol >= 1:
                    self.blackPawnAttackingSquares.append((move.endRow + 1, move.endCol - 1))
                if move.endCol <= 6:
                    self.blackPawnAttackingSquares.append((move.endRow + 1, move.endCol + 1))

        # If a pawn is captured
        pieceCaptured = move.pieceCaptured
        (pieceCapturedRow, pieceCapturedCol) = (move.endRow, move.endCol)
        if move.isEnPassantMove:
            (pieceCapturedRow, pieceCapturedCol) = (move.startRow, move.endCol)
            if move.pieceMoved == 1:
                pieceCaptured = 9
            else:
                pieceCaptured = 1

        if pieceCaptured == 1:
            # Remove squares not attacked anymore
            if (pieceCapturedRow - 1, pieceCapturedCol - 1) in self.whitePawnAttackingSquares:
                self.whitePawnAttackingSquares.remove((pieceCapturedRow - 1, pieceCapturedCol - 1))
            if (pieceCapturedRow - 1, pieceCapturedCol + 1) in self.whitePawnAttackingSquares:
                self.whitePawnAttackingSquares.remove((pieceCapturedRow - 1, pieceCapturedCol + 1))

        elif pieceCaptured == 9:
            # Remove squares not attacked anymore
            if (pieceCapturedRow + 1, pieceCapturedCol - 1) in self.blackPawnAttackingSquares:
                self.blackPawnAttackingSquares.remove((pieceCapturedRow + 1, pieceCapturedCol - 1))
            if (pieceCapturedRow + 1, pieceCapturedCol + 1) in self.blackPawnAttackingSquares:
                self.blackPawnAttackingSquares.remove((pieceCapturedRow + 1, pieceCapturedCol + 1))


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, startSquare, endSquare, board, isEnPassantMove=False, isCastleMove=False, isPawnPromotion=False, promotedPieceType=0):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isPawnPromotion = isPawnPromotion
        self.promotedPieceType = promotedPieceType
        # if (self.pieceMoved == 1 and self.endRow == 0) or (self.pieceMoved == 9 and self.endRow == 7):
        #     self.isPawnPromotion = True
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = 9 if self.pieceMoved == 1 else 1

        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __repr__(self):
        return f'{self.cols_to_files[self.startCol]}{self.rows_to_ranks[self.startRow]}' \
               f'{self.cols_to_files[self.endCol]}{self.rows_to_ranks[self.endRow]}'

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


class CastleRights:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs

        self.castleRightID = wks * 1000 + wqs * 100 + bks * 10 + bqs

    def __repr__(self):
        return f'WKS : {self.wks}, WQS : {self.wqs}, BKS : {self.bks}, BQS : {self.bqs}, '

    def __eq__(self, other):
        if isinstance(other, CastleRights):
            return self.castleRightID == other.castleRightID
        return False


def isAlliedPiece(piece, allyColor):
    if piece != 0 and piece // 8 - allyColor == 0:
        return True
    else:
        return False


def isEnemyPiece(piece, allyColor):
    if piece != 0 and piece // 8 + allyColor == 1:
        return True
    else:
        return False


