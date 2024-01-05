import time

board = [
            [12, 10, 11, 13, 14, 11, 10, 12],
            [9, 9, 9, 9, 9, 9, 9, 9],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [4, 2, 3, 5, 6, 3, 2, 4]
        ]

board2 = [12, 10, 11, 13, 14, 11, 10, 12, 9, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 4, 2, 3, 5, 6, 3, 2, 4]

startTime = time.time()
c = 0
for i in range(10000):
    for j in range(8):
        for k in range(8):
            if board[j][k] == 1:
                c += 1
endTime = time.time()
print(endTime - startTime)


startTime = time.time()
c = 0
for i in range(10000):
    for j in range(64):
        if board2[j] == 1:
            c += 1
endTime = time.time()
print(endTime - startTime)
