import ChessEngine
import ChessBot
import time

gs = ChessEngine.GameState()
gs.fenToBoard("rnbqk2r/4bppp/p2ppn2/1p6/3NP3/2N1BP2/PPPQ2PP/R3KB1R w KQkq - 2 9")

validMoves = gs.getValidMoves()


# timeStart = time.time()
# print("V3 : ", ChessBot.findBestMoveV3(gs, validMoves))
# timeEnd = time.time()
# print(timeEnd-timeStart)

timeStart = time.time()
print("V4 : ", ChessBot.findBestMoveV4(gs, validMoves))
timeEnd = time.time()
print(timeEnd-timeStart)

# timeStart = time.time()
# print("V5 : ", ChessBot.findBestMoveV5(gs, validMoves))
# timeEnd = time.time()
# print(timeEnd-timeStart)
#
# timeStart = time.time()
# print("V6 : ", ChessBot.findBestMoveV6(gs, validMoves))
# timeEnd = time.time()
# print(timeEnd-timeStart)
