import ChessEngine
import time

gs = ChessEngine.GameState()
# gs.fenToBoard("2r1k2r/pppq1Npp/2bppb2/1N6/1n4n1/2BPPB2/PPPQ1PPP/R4K1R w k - 1 14")
# best time so far with depth of 4 : 48.0
# gs.makeMove(ChessEngine.Move((1, 5), (0, 7), gs.board))


def stockfishComparison(depth):
    somme = 0
    timeStart = time.time()
    validMoves = gs.getValidMoves()
    for move in validMoves:
        gs.makeMove(move)
        numPositions = gs.numberOfMovesWithDepth(depth - 1)
        somme += numPositions
        print(f'{move}: {numPositions}')
        gs.undoMove()
    timeEnd = time.time()
    computeTime = timeEnd - timeStart
    print("somme : ", somme)
    print("temps : ", computeTime)


stockfishComparison(4)

#
# for i in range(2):
#     move = validMoves[i]
#     print(move)
#     gs.makeMove(move)
#     # print("Après move", gs.castleRightsLog)
#
#     gs.undoMove()
#     # print("Après undo", gs.castleRightsLog)

# print(somme)


