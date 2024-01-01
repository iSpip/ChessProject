import random
import MapBonuses as mb

pieceValue = {0: 0, 1: 1, 2: 3, 3: 3.2, 4: 5, 5: 9, 6: 0, 9: -1, 10: -3, 11: -3.5, 12: -5, 13: -9, 14: 0}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4


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
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = - CHECKMATE
        else:
            opponentMaxScore = - CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkmate:
                    # bestMove = move
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = - turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestMove = move
        gs.undoMove()
    return bestMove


def findBestMoveV2(gs, validMoves):
    global bestMove
    bestMove = None
    random.shuffle(validMoves)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    return bestMove


def findBestMoveV3(gs, validMoves):
    global bestMoveV3, counterV3
    bestMoveV3 = None
    counterV3 = 0
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counterV3)
    return bestMoveV3


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global bestMoveV3, counterV3
    counterV3 += 1
    if depth == 0:
        return turnMultiplier * evaluateBoard(gs)

    maxScore = - CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        possibleMoves = gs.getValidMoves()
        score = - findMoveNegaMaxAlphaBeta(gs, possibleMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMoveV3 = move
        gs.undoMove()
        if maxScore > alpha:    # pruning
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global bestMove
    if depth == 0:
        return turnMultiplier * evaluateBoard(gs)

    maxScore = - CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        possibleMoves = gs.getValidMoves()
        score = - findMoveNegaMax(gs, possibleMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMove = move
        gs.undoMove()
    return bestMove


def evaluateBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    materialEvaluation = scoreMaterial(gs.board)

    return materialEvaluation


def scoreMaterial(board):
    score = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != 0:
                if piece > 7:
                    score += pieceValue[piece] - mb.piece_position_scores[piece][row][col]
                else:
                    score += pieceValue[piece] + mb.piece_position_scores[piece][row][col]
    # score = score if allyColor == 0 else -score
    return score

