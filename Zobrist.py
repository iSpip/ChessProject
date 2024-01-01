import random
import ChessEngine

class ChessHash:
    def __init__(self):
        self.init_hash_values()

    def init_hash_values(self):
        self.piece_keys = {
            0: 0,  # Empty square
            1: random.getrandbits(64),  # Pawn
            2: random.getrandbits(64),  # Knight
            3: random.getrandbits(64),  # Bishop
            4: random.getrandbits(64),  # Rook
            5: random.getrandbits(64),  # Queen
            6: random.getrandbits(64),  # King
            # Repeat for black pieces (add 8 to piece value)
            9: random.getrandbits(64),
            10: random.getrandbits(64),
            11: random.getrandbits(64),
            12: random.getrandbits(64),
            13: random.getrandbits(64),
            14: random.getrandbits(64),
            # and for castling rights ...
            15: random.getrandbits(64),
            16: random.getrandbits(64),
            17: random.getrandbits(64),
            18: random.getrandbits(64),
            # en passant rights
            19: random.getrandbits(64)
        }
        self.table = {}

        self.pieces = [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]
        for i in range(64):
            self.table[i] = {}
            for piece in self.pieces:
                self.table[i][piece] = random.getrandbits(64)


    def calculate_hash(self, board, currentCastleRights, enPassantPossible):
        hash_value = 0
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != 0:
                    hash_value ^= self.table[8*i + j][piece]

        # Include castle rights in the hash
        if currentCastleRights.wks:
            hash_value ^= self.piece_keys[15]  # Adjust key index as needed
        if currentCastleRights.wqs:
            hash_value ^= self.piece_keys[16]
        if currentCastleRights.bks:
            hash_value ^= self.piece_keys[17]
        if currentCastleRights.bqs:
            hash_value ^= self.piece_keys[18]
        if enPassantPossible != ():
            hash_value ^= self.piece_keys[19]

        return hash_value


# Example usage:
# gs = ChessEngine.GameState()
#
# ch = ChessHash()
# hash_value = ch.calculate_hash(gs)
# print(hash_value)
