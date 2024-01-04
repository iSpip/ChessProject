import ChessEngine
import ChessBot
import time

gs = ChessEngine.GameState()
gs.fenToBoard("5k2/8/8/8/8/2R5/2K5/8 w - - 0 1")

validMoves = gs.getValidMoves()


# timeStart = time.time()
# print("V2 : ", ChessBot.findBestMoveV2(gs, validMoves, 3))
# timeEnd = time.time()
# print(timeEnd-timeStart)

# timeStart = time.time()
# print("V3 : ", ChessBot.findBestMoveV3(gs, validMoves, 4))
# timeEnd = time.time()
# print(timeEnd-timeStart)

# timeStart = time.time()
# print("V4 : ", ChessBot.findBestMoveV4(gs, validMoves))
# timeEnd = time.time()
# print(timeEnd-timeStart)

# timeStart = time.time()
# print("V5 : ", ChessBot.findBestMoveV5(gs, validMoves, 4))
# timeEnd = time.time()
# print(timeEnd-timeStart)

# timeStart = time.time()
# print("V6 : ", ChessBot.findBestMoveV6(gs, validMoves, 4))
# timeEnd = time.time()
# print(timeEnd-timeStart)

# timeStart = time.time()
# print("V7 : ", ChessBot.findBestMoveV7(gs, validMoves, 7))
# timeEnd = time.time()
# print(timeEnd-timeStart)

timeStart = time.time()
print("V8 : ", ChessBot.findBestMoveV8(gs, validMoves, 8))
timeEnd = time.time()
print(timeEnd-timeStart)


