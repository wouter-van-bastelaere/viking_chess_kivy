from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
from structs import Entity


class Square(Entity):
    def __init__(self, color="no_color", piece=None, only_king=False, victory=False, pos=(50,50), x=0, y=0, **kwargs):
        super().__init__()
        self.pos  = pos
        self.test = 20
        self.piece, self.color = piece, color
        self.only_king = only_king
        self.victory=victory
        self.x = y
        self.y = x

    def free(self):
        return self.piece is None and not self.only_king
    def free_for_king(self):
        return self.piece is None
    def __bool__(self):
        print("depricated bool on", self.color, self.piece, self.only_king)
        return self.free()
    def __repr__(self):
        try:
            if self.piece is None: return "-"
            return str(self.piece)
        except:
            return "failed to print Square"

    def set_image(self):

        if self.piece is None:
            if self.color == "special":
                self.source = "assets/special.png"
            elif self.color == "green":
                self.source = "assets/green.png"  
            else:
                self.source = "assets/white.png"
            return


        if self.color == "special":
            self.source = "assets/special.png"
    
        if self.piece.king:
            self.source = "assets/koning.png"
            return
        
        try:
            self.source = "assets/" + self.piece.team + ".png"
        except:
            self.source = "assets/white.png"
            
    

class Piece:
    def __init__(self, team, king=False):
        self.team, self.king = team, king
    def __repr__(self):
        if self.king:
            return "k"
        return str(self.team)[0]

class Board:
    def __init__(self, width, leng):
        self.width, self.leng = width, leng
        self.board = None
        self.reset_board()

    def set_images(self):
        for row in self.board:
            for square in row:
                square.set_image()
    def remove_green(self):
        for row in self.board:
            for square in row:
                if square.color == "green":
                    square.color = "white"


    def reset_board(self):

        self.board = [[Square(color="zwart", pos=(i,j), x=i, y=j) for i in range(self.leng)] for j in range(self.width)]

        only_king_square = [(self.width//2, self.leng//2), (0, self.leng-1), (0, 0), (self.width-1, self.leng-1), (self.width-1, 0)]
        for x, y in only_king_square:
            self.board[x][y].only_king = True
            self.board[x][y].color = "special"
        
        victory = [ (0, self.leng-1), (0, 0), (self.width-1, self.leng-1), (self.width-1, 0)]
        for x, y in victory:
            self.board[x][y].victory = True

        king = [(self.width//2, self.leng//2)]
        for x, y in king:
            self.board[x][y].piece = Piece("yellow", True)

        if self.width == 11 and  self.leng == 11:
            attackers = [(0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (1, 5)] \
                    +   [(3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (5, 1)] \
                    +   [(10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (9, 5)] \
                    +   [(3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (5, 9)]

            for x, y in attackers:
                 self.board[x][y].piece = Piece("red")
                    
            defenders =   [                (5, 3)                ] \
                        + [        (4, 4), (5, 4), (6, 4)        ] \
                        + [(3, 5), (4, 5),         (6, 5), (7, 5)] \
                        + [        (4, 6), (5, 6), (6, 6)        ] \
                        + [                (5, 7)                ]
            for x, y in defenders:
                 self.board[x][y].piece = Piece("yellow")

        

    def __repr__(self):
        return str(self.board)

    def inside(self, x, y):
        if x < 0             : return False
        if y < 0             : return False
        if x >= self.width   : return False
        if y >= self.leng    : return False
        return True
    def allowed(self, x, y, is_king):
        def allowed_piece(x, y):
            if not self.inside(x, y)  : return False
            square = self.board[x][y]
            if square.free(): return True #the square is empty
            return False
        def allowed_king(x, y):
            if not self.inside(x, y)  : return False
            square = self.board[x][y]
            if square.free_for_king(): return True #the square is empty
            return False
        if is_king:
            return allowed_king(x, y)
        return allowed_piece(x, y)

    def give_pos_moves(self, x, y):
        if not self.inside(x, y): return []
        square = self.board[x][y]
        if square.piece is None: return []#if we did not select a piece, we can not move

        possible_moves = []
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]

        for i in directions:
            next_x, next_y = x + i[0], y + i[1]

            while(self.allowed(next_x, next_y, square.piece.king)):
                possible_moves.append((next_x, next_y))
                next_x += i[0]
                next_y += i[1]


        return possible_moves

    def move(self, x, y, x_new, y_new):
        if (x_new, y_new) not in self.give_pos_moves(x, y):
            print("ilegal move can not be made", x, y, " to", x_new, y_new)
            return False
        
        square_from = self.board[x][y]
        square_to   = self.board[x_new][y_new]
        if square_from.piece.king:
            if square_to.victory:
                print("defenders won the game!!!")
            square_to.piece = square_from.piece
            square_from.piece = None
            return True
        
        def try_take_piece(x1, y1, x2, y2, x3, y3):#one is the piece that just moved, is the piece that may or may not be removed, 3 is the extensions on whick we check.
            if not self.inside(x1, y1): return False
            if not self.inside(x2, y2): return False
            if not self.inside(x3, y3): return False

            piece1 = self.board[x1][y1].piece
            piece2 = self.board[x2][y2].piece
            piece3 = self.board[x3][y3].piece


            if piece1 is None or piece2 is None: return False
            if piece2.king:
                print("we don't take the king yet")
                return False

            if piece3 is None:
                if self.board[x3][y3].color == "special":
                    if piece1.team != piece2.team:
                        self.board[x2][y2].piece = None
                        return True
                return False
                
            if piece1.team != piece3.team or piece1.team == piece2.team: return False
            

            self.board[x2][y2].piece = None
            return True

        self.board[x_new][y_new].piece = self.board[x][y].piece
        self.board[x][y].piece = None

        try_take_piece(x_new, y_new, x_new+1, y_new  , x_new+2, y_new  )
        try_take_piece(x_new, y_new, x_new-1, y_new  , x_new-2, y_new  )
        try_take_piece(x_new, y_new, x_new  , y_new+1, x_new  , y_new+2)
        try_take_piece(x_new, y_new, x_new  , y_new-1, x_new  , y_new-2)



