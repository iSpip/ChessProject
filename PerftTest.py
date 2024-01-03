import ChessEngine
import time

gs = ChessEngine.GameState()
gs.fenToBoard("2r1k2r/pppq1Npp/2bppb2/1N6/1n4n1/2BPPB2/PPPQ1PPP/R4K1R w k - 1 14")

# gs.makeMove(ChessEngine.Move((1, 5), (0, 7), gs.board))


def perftTest(depth):   # Get the number of position possible from a start position at a certain depth. Allows to compare with Stockfish- if our engine is correct.
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


perftTest(4)

