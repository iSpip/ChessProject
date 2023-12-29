import random

pieceValue = {0: 0, 1: 1, 2: 3, 3: 3.5, 4: 5, 5: 9, 6: 0, 9: -1, 10: -3, 11: -3.5, 12: -5, 13: -9, 14: 0}
CHECKMATE = 1000
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves, allyColor):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestMove = None
    random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        opponentMoves = gs.getValidMoves()
        opponentMaxScore = - CHECKMATE
        for opponentMove in opponentMoves:
            gs.makeMove(opponentMove)
            if gs.checkmate:
                # bestMove = move
                score = - turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = - turnMultiplier * scoreMaterial(gs.board, allyColor)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestMove = move
        gs.undoMove()
    return bestMove


def scoreMaterial(board, allyColor):
    score = 0
    for row in board:
        for square in row:
            score += pieceValue[square]
    # score = score if allyColor == 0 else -score
    return score

