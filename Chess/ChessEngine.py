class GameState():
    def __init__(self):
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bp','bp','bp','bp','bp','bp','bp','bp'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['--','--','--','--','--','--','--','--'],
            ['wp','wp','wp','wp','wp','wp','wp','wp'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR'],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves, 'N': self.getKnightMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []

        
    
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        #update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation= (move.endRow, move.endCol)
    
    def undoMove(self):
        if len(self.moveLog) != 0: #Menyakinkan ada move untuk di undo 
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured 
            self.whiteToMove = not self.whiteToMove #Switch turns back 
            #updated the king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol) 
    
    #All moves considering checks
            
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #Only 1 check, block check, or move king
                moves = self.getAllPossibleMoves()
                #To block a check you must move a piece into one of the squares between the enemy pieces and king 
                check = self.checks[0] #Check information 
                checkRow = check[0] 
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] #Enemy piece causing the check
                validSquares = [] #Squares piece can move to
                #If knight, must capture knight or move king , other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow,checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2] and check[3] are check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                
                #Get rid of any moves that don't block check or move king 
                for i in range(len(moves) - 1, -1, -1): #Go through backwards when you are removing from a list as iterating 
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: #Double check king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: #Not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        return moves
        
    
    
        
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch turns back
        for move in oppMoves:
            if move.endRow  == r and move.endCol == c: #square is under attack
                return True
        return False
        
    #All moves not considering checks
    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #Number of rows
            for c in range(len(self.board[r])): #Number of cols is given to me
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #calls the appropriate move function based on piece type

        return moves 
        
    def getPawnMoves(self, r, c , moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: #White pawn moves
            if self.board[r-1][c] == '--': #1st square move
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r,c), (r-2,c), self.board))
                    
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1,-1):
                        moves.append(Move((r, c), (r-1, c-1), self.board)) 
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == 'b': #enemy piece to capture
                    if not piecePinned or pinDirection == (-1,1):
                        moves.append(Move((r, c), (r-1, c+1), self.board)) 
                    
        elif not self.whiteToMove: #black pawn moves
            if self.board[r+1][c] == "--":
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r,c), (r+2,c), self.board))
            #Captures
            if c - 1 >= 0: #Capture to left
                if self.board[r+1][c-1][0] == "w":
                    if not piecePinned or pinDirection == (1,-1):
                        moves.append(Move((r,c), (r+1,c-1), self.board ))
            if c + 1 <= 7: #Capture to right
                if self.board[r+1][c+1][0] == 'w':
                    if not piecePinned or pinDirection == (1,1):
                        moves.append(Move((r,c), (r+1, c+1), self.board))
    
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for i in range(len(self.pins) -1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #Can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0,-1), (1,0), (0,1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #Empty space valid 
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #Enemy piece valid 
                            moves.append(Move((r,c) , (endRow, endCol), self.board))
                            break
                        else: #Friendly piece invalid 
                            break
                else: #Off board
                    break 
    
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8): #Bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': #Empty space valid
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: #Enemy piece valid
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break
                        else:
                            break #Friendly piece invalid
                else:
                    break  #Off board invalid
    
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) -1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1) )
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #Not an ally piece (empty or enemy pieces)
                        moves.append(Move((r,c), (endRow,endCol), self.board))
        
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #Not an ally piece (empty or enemy pieces)
                    #Place king on end square and check for checks 
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    #Place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c, moves)
        self.getBishopMoves(r, c, moves)
    
    def checkForPinsAndChecks(self):
        pins = [] #Squares where the allied pinned is and direction pinned from
        checks = [] #Squares where enemy is applying a check
        endPiece = '--'
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #Check outward from king and checks, keep track of pins
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () #Rose possible pins 
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): #First ally piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #Second ally piece, so no pin or check possible in this direction 
                            break
                elif endPiece[0] == enemyColor:
                    type = endPiece[1]
                    #5 possibilities in this complex conditional
                    #1.) orthogonally away from king and piece is rook
                    #2.) diagonally away from king and piece is bishop
                    #3.) 1 square away diagonally from king and piece is pawn
                    #4.) any direction and piece is queen
                    #5.) any direction 1 square away and piece is king 
                    if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == "B") or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == "K"):
                        if possiblePin == ():
                            inCheck = True
                            checks.append((endRow, endCol, d[0], d[1]))
                            break
                        else: #Piece blocking so pin
                            pins.append(possiblePin)
                            break
                    else: #Enemy piece not applying check:
                        break
                else:
                    break #Off board
        #Check for knight checks
        knightMoves = ((-2, -1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1) )
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': #Enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
    
class Move():
    # maps keys to values
    # key = value
    ranksToRows= {'1':7, '2':6, '3': 5, '4': 4,'5': 3,'6': 2,'7': 1,'8': 0}
    rowsToRanks = {v : k for k, v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles= {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol 
        
    
    #Overriding the equals method 
    
    def __eq__(self,other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        #you can add to make this like real ches notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
        
    def getRankFile(self,r ,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]








        