import random

pieceValue = {0: 0, 1: 1, 2: 3, 3: 3.5, 4: 5, 5: 9, 6: 0, 9: -1, 10: -3, 11: -3.5, 12: -5, 13: -9, 14: 0}
CHECKMATE = 1000
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    bestScore = CHECKMATE
    bestMove = None
    for move in validMoves:
        gs.makeMove(move)
        score = scoreMaterial(gs.board)
        if score < bestScore:
            bestScore = score
            bestMove = move
        gs.undoMove()
    return bestMove


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            score += pieceValue[square]

    return score

