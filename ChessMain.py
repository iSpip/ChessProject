import pygame as p
import ChessEngine

# Initialisation of Pygame
p.init()
p.mixer.init()
moveSound = p.mixer.Sound('sounds/move.mp3')
captureSound = p.mixer.Sound('sounds/capture.mp3')

# Constants
WIDTH = HEIGHT = 750
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
BLANC = (240, 217, 181)
NOIR = (181, 136, 99)
IMAGES = {}


def loadImages():
    pieces = [1, 4, 2, 3, 6, 5, 9, 12, 10, 11, 14, 13]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + str(piece) + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    # gs.fenToBoard("r3k2r/pppq1ppp/2bppb2/1N4N1/1n4n1/2BPPB2/PPPQ1PPP/R4K1R b kq - 17 12")
    # gs.makeMove(ChessEngine.Move((0, 0), (0, 2), gs.board))

    validMoves = gs.getValidMoves()
    moveMade = False    # flag variable for when a move is made
    loadImages()
    running = True
    squareSelected = ()     # no square selected at first
    playerClicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()    # (x, y) location of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if squareSelected == (row, col):    # user clicked on the same square
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)

                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            isCapture = False
                            if gs.board[move.endRow][move.endCol] != 0 or validMoves[i].isEnPassantMove:
                                isCapture = True

                            gs.makeMove(validMoves[i])

                            if isCapture:
                                captureSound.play()
                            else:
                                moveSound.play()

                            moveMade = True
                            squareSelected = ()     # reset user click
                            playerClicks = []
                            break
                    if not moveMade:
                        playerClicks = [squareSelected]

            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    squareSelected = ()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, squareSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


def highlightPossibleSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        r, c = squareSelected
        allyColor = 0 if gs.whiteToMove else 1
        if ChessEngine.isAlliedPiece(gs.board[r][c], allyColor):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(130)    # transparency
            s.fill(p.Color(10, 80, 10))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            s2 = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s2.fill((0, 0, 0, 0))
            p.draw.circle(s2, p.Color(20, 120, 20, 130), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 7)
            # s.fill(p.Color(30, 150, 30))

            s3 = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
            s3.fill((20, 120, 20, 130))
            p.draw.circle(s3, p.Color(0, 0, 0, 0), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE / 1.8)

            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] == 0:
                        screen.blit(s2, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                    else:
                        screen.blit(s3, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def highlightLastMove(screen, gs):
    if gs.moveLog:
        lastMove = gs.moveLog[-1]
        rStart, cStart = lastMove.startRow, lastMove.startCol
        rEnd, cEnd = lastMove.endRow, lastMove.endCol
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(130)  # transparency
        s.fill(p.Color(225, 205, 0))    # 225, 205, 0 bien, lichess
        screen.blit(s, (cStart * SQ_SIZE, rStart * SQ_SIZE))
        screen.blit(s, (cEnd * SQ_SIZE, rEnd * SQ_SIZE))


def highlightCheck(screen, gs):
    if gs.inCheck:
        kingSquare = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
        r, c = kingSquare
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(130)  # transparency
        s.fill(p.Color(180, 0, 0))  # 225, 205, 0 bien, lichess
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))


def drawGameState(screen, gs, validMoves, squareSelected):
    drawBoard(screen, squareSelected)
    highlightCheck(screen, gs)
    highlightLastMove(screen, gs)
    highlightPossibleSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen, squareSelected):
    colors = [BLANC, NOIR]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    # if len(squareSelected) == 2:
    #     p.draw.rect(screen, (30, 90, 30),
    #                 p.Rect(squareSelected[1] * SQ_SIZE, squareSelected[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != 0:
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
