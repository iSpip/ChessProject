import random
import MapBonuses as mb

pieceValue = {0: 0,
              1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 20000,
              9: -100, 10: -320, 11: -330, 12: -500, 13: -900, 14: -20000}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 3


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
    global bestMoveV2, counterV2
    bestMoveV2 = None
    counterV2 = 0
    random.shuffle(validMoves)
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    print(counterV2)
    return bestMoveV2


def findBestMoveV3(gs, validMoves):
    global bestMoveV3, counterV3
    bestMoveV3 = None
    counterV3 = 0
    findMoveNegaMaxAlphaBetaV3(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counterV3)
    return bestMoveV3


def findMoveNegaMaxAlphaBetaV3(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global bestMoveV3, counterV3
    counterV3 += 1
    if depth == 0:
        return turnMultiplier * evaluateBoard(gs)

    maxScore = - CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        possibleMoves = gs.getValidMoves()
        score = - findMoveNegaMaxAlphaBetaV3(gs, possibleMoves, depth - 1, -beta, -alpha, -turnMultiplier)
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


def findBestMoveV4(gs, validMoves):
    global bestMoveV4, counterV4, hash_tableV4
    bestMoveV4 = None
    counterV4 = 0
    hash_tableV4 = {}
    findMoveNegaMaxAlphaBetaV4(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, gs.zobristHash)
    print(counterV4)
    return bestMoveV4


def findMoveNegaMaxAlphaBetaV4(gs, validMoves, depth, alpha, beta, turnMultiplier, hash_value):
    global bestMoveV4, counterV4, hash_tableV4
    counterV4 += 1

    if hash_value in hash_tableV4 and hash_tableV4[hash_value]['depth'] >= depth:
        return hash_tableV4[hash_value]['score']

    if depth == 0:
        score = turnMultiplier * evaluateBoard(gs)
        hash_tableV4[hash_value] = {'score': score, 'depth': depth}
        return score

    maxScore = - CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        possibleMoves = gs.getValidMoves()
        score = - findMoveNegaMaxAlphaBetaV4(gs, possibleMoves, depth - 1, -beta, -alpha, -turnMultiplier, gs.zobristHash)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMoveV4 = move
        gs.undoMove()
        if maxScore > alpha:    # pruning
            alpha = maxScore
        if alpha >= beta:
            break

    # Store the maxScore in hash_table
    hash_tableV4[hash_value] = {'score': maxScore, 'depth': depth}

    return maxScore


def findBestMoveV5(gs, validMoves):
    global bestMoveV5, counterV5, hash_tableV5
    bestMoveV5 = None
    counterV5 = 0
    hash_tableV5 = {}
    sortedMoves = orderMoves(gs, validMoves)
    findMoveNegaMaxAlphaBetaV5(gs, sortedMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1, gs.zobristHash)
    print(counterV5)
    return bestMoveV5


def findMoveNegaMaxAlphaBetaV5(gs, sortedMoves, depth, alpha, beta, turnMultiplier, hash_value):
    global bestMoveV5, counterV5, hash_tableV5
    counterV5 += 1

    if hash_value in hash_tableV5 and hash_tableV5[hash_value]['depth'] >= depth:
        return hash_tableV5[hash_value]['score']

    if depth == 0:
        score = turnMultiplier * evaluateBoard(gs)
        hash_tableV5[hash_value] = {'score': score, 'depth': depth}
        return score

    maxScore = - CHECKMATE

    for move in sortedMoves:
        gs.makeMove(move)
        hash_value = gs.zobristHash
        possibleMoves = gs.getValidMoves()
        sortedPossibleMoves = orderMoves(gs, possibleMoves)
        score = - findMoveNegaMaxAlphaBetaV5(gs, sortedPossibleMoves, depth - 1, -beta, -alpha, -turnMultiplier, gs.zobristHash)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMoveV5 = move
        gs.undoMove()
        if maxScore > alpha:    # pruning
            alpha = maxScore
        if alpha >= beta:
            break

    # Store the maxScore in hash_table
    hash_tableV5[hash_value] = {'score': maxScore, 'depth': depth}

    return maxScore


def findBestMoveV6(gs, validMoves, depth):
    global bestMoveV6, counterV6
    bestMoveV6 = None
    counterV6 = 0
    sortedMoves = orderMoves(gs, validMoves)
    findMoveNegaMaxAlphaBetaV6(gs, sortedMoves, depth, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counterV6)
    return bestMoveV6


def findMoveNegaMaxAlphaBetaV6(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global bestMoveV6, counterV6
    counterV6 += 1
    if depth == 0:
        return turnMultiplier * evaluateBoard(gs)

    maxScore = - CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        possibleMoves = gs.getValidMoves()
        sortedPossibleMoves = orderMoves(gs, possibleMoves)
        score = - findMoveNegaMaxAlphaBetaV6(gs, sortedPossibleMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                bestMoveV6 = move
        gs.undoMove()
        if maxScore > alpha:    # pruning
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def orderMoves(gs, validMoves):
    moves_with_score = []

    for move in validMoves:
        moveScoreGuess = 0
        movedPieceType = gs.board[move.startRow][move.startCol]
        capturedPieceType = gs.board[move.endRow][move.endCol]

        if capturedPieceType != 0:
            moveScoreGuess = pieceValue[capturedPieceType] - pieceValue[movedPieceType]

        if move.isPawnPromotion:
            moveScoreGuess += pieceValue[6]

        if gs.whiteToMove:
            if (move.endRow, move.endCol) in gs.blackPawnAttackingSquares:
                moveScoreGuess -= pieceValue[gs.board[move.startRow][move.startCol]]
        else:
            if (move.endRow, move.endCol) in gs.whitePawnAttackingSquares:
                moveScoreGuess -= pieceValue[gs.board[move.startRow][move.startCol]]



        moves_with_score.append((move, moveScoreGuess))

    moves_with_score.sort(key=lambda x: x[1], reverse=True)
    # if gs.whiteToMove:
    #     moves_with_score.sort(key=lambda x: x[1], reverse=True)
    # else:
    #     moves_with_score.sort(key=lambda x: x[1])
    sorted_moves = [move for move, _ in moves_with_score]

    return sorted_moves


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global bestMoveV2, counterV2
    counterV2 += 1
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
                bestMoveV2 = move
        gs.undoMove()
    return maxScore


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

