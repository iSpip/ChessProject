import random

class ChessHash:
    def __init__(self):
        self.init_hash_values()

    def init_hash_values(self):
        self.piece_keys = {
            # and for castling rights ...
            1: random.getrandbits(64),
            2: random.getrandbits(64),
            3: random.getrandbits(64),
            4: random.getrandbits(64),
            # en passant rights
            5: random.getrandbits(64)
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
            hash_value ^= self.piece_keys[1]
        if currentCastleRights.wqs:
            hash_value ^= self.piece_keys[2]
        if currentCastleRights.bks:
            hash_value ^= self.piece_keys[3]
        if currentCastleRights.bqs:
            hash_value ^= self.piece_keys[4]
        if enPassantPossible != ():     # Not sure that it works well, because it depends on the location ?
            hash_value ^= self.piece_keys[5]

        return hash_value


# Example usage:
# gs = ChessEngine.GameState()
#
# ch = ChessHash()
# hash_value = ch.calculate_hash(gs)
# print(hash_value)
