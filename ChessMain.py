import pygame as p
import ChessEngine

# Initialisation of Pygame
p.init()

# Constants
WIDTH = HEIGHT = 512
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
    #gs.makeMove(ChessEngine.Move((0, 0), (0, 2), gs.board))

    validMoves = gs.getValidMoves()
    moveMade = False    # flag variable for when a move is made
    loadImages()
    running = True
    squareSelected = ()     # no square selected at first
    playerClicks = []
    print(gs.currentCastleRights)
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
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            squareSelected = ()     # reset user click
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:

            validMoves = gs.getValidMoves()

            #print(gs.currentCastleRights)
            print(gs.castleRightsLog)

            moveMade = False
        drawGameState(screen, gs, squareSelected)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, squareSelected):
    drawBoard(screen, squareSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen, squareSelected):
    colors = [BLANC, NOIR]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    if len(squareSelected) == 2:
        p.draw.rect(screen, (30, 90, 30),
                    p.Rect(squareSelected[1] * SQ_SIZE, squareSelected[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != 0:
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
