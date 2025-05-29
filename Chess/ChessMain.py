import pygame as p
import ChessEngine 

width = height = 512 #400 ( Another option )
dimension = 8 #8x8 board
sq_size = height // dimension
max_fps = 15 #untuk animasi
images = {}

def loadImages(): 
    pieces = ['wp','wR','wN', 'wB', 'wK', 'wQ', 'bp','bR','bN','bB','bK','bQ']
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (sq_size,sq_size) )
        #images[wp] panggil pion putih
        
def main():
    p.init()
    screen = p.display.set_mode((width,height))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #Flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = () # no square is selected, keep track of teh last click of the user (tuple : (row, col))
    playerClicks = [] # keep track of palyers clicks (two tuples: [(6, 4), (4, 4)] )
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Mouuse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()#(x, y) location of mouse
                col = location[0]//sq_size
                row = location[1]//sq_size
                if sqSelected == (row, col): #the user clicked the same square twice 
                    sqSelected = () #deselect
                    playerClicks = [] #clear player clicks
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                if len(playerClicks) == 2: #after 2nd clicks
                    move =ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                      gs.makeMove(move)
                      moveMade = True
                      sqSelected = () #reset user clicks
                      playerClicks = []
                    else:
                        playerClicks = [sqSelected]
            #Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo when "z" is pressed 
                    gs.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
                        
        drawGameState(screen, gs)
        clock.tick(max_fps)
        p.display.flip()
        
def drawGameState(screen, gs):
    drawBoard(screen) #Mengambarkan square
    drawPieces(screen, gs.board) #Mengambarkan piece di atas square
    

#Mengambarkan square pada board

def drawBoard(screen):
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

#Mengambarkan piece di atas board menggunakan GameState.board

def drawPieces(screen,board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != '--': #Bukan empty square
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        
if __name__ == '__main__':
    main()