from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import CoreLabel
import random
from viking_game import Board
from structs import Entity
import math as m

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._keyboard = Window.request_keyboard(
            self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)
        self._keyboard.bind(on_key_up=self._on_key_up)
        self.last_clicked = None

        self.register_event_type("on_frame")
        self.keysPressed = set()
        self._entities = set()

        Clock.schedule_interval(self._on_frame, 0)

        self.board = None


    def find_square(self, x, y): #does not work properly yet
        min_ = float("inf")
        loc_x, loc_y = -1, -1
        for row in self.board.board:
            for square in row:


                a = (square.pos[0]+square.size[0]//2 - x)**2 + (square.pos[1]+square.size[1]//2 - y)**2
                distance = m.sqrt(a)
                if  distance < min_:
                    min_ = distance
                    loc_x, loc_y = square.x, square.y
        return (loc_x, loc_y)

    def on_touch_down(self, touch):

        (x, y) = self.find_square(*touch.pos)
        if self.last_clicked is None:
            self.last_clicked = (x, y)

            pos_moves = self.board.give_pos_moves(x, y)
            for (x_pos, y_pos) in pos_moves:
                if self.board.board[x_pos][y_pos].color != "special":
                    self.board.board[x_pos][y_pos].color = "green"
            self.board.set_images()

            return
        self.board.remove_green()

        if (x, y) in self.board.give_pos_moves(*self.last_clicked):
            self.board.move(*self.last_clicked, *(x, y))
        self.last_clicked = None
        self.board.set_images()


    def make_board(self):
        board_size = 11
        self.board = Board(board_size, board_size)
        squares = self.board.board
        for row in squares:
            for square in row:
                square.pos = (Window.width/board_size*square.pos[0], Window.height/board_size*square.pos[1])
                square.size = (50, 50)
                square.set_image()
                #square.pos = (500, 100)
                self.add_entity(square)

    def _on_frame(self, dt):
        self.dispatch("on_frame", dt)

    def on_frame(self, dt):
        pass

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self._score_label.text = "Score: " + str(value)
        self._score_label.refresh()
        self._score_instruction.texture = self._score_label.texture
        self._score_instruction.size = self._score_label.texture.size

    def add_entity(self, entity):
        self._entities.add(entity)
        self.canvas.add(entity._instruction)

    def remove_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)
            self.canvas.remove(entity._instruction)

    def collides(self, e1, e2):
        r1x = e1.pos[0]
        r1y = e1.pos[1]
        r2x = e2.pos[0]
        r2y = e2.pos[1]
        r1w = e1.size[0]
        r1h = e1.size[1]
        r2w = e2.size[0]
        r2h = e2.size[1]

        if (r1x < r2x + r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y):
            return True
        else:
            return False

    def colliding_entities(self, entity):
        result = set()
        for e in self._entities:
            if self.collides(e, entity) and e != entity:
                result.add(e)
        return result

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self.keysPressed.add(keycode[1])

    def _on_key_up(self, keyboard, keycode):
        text = keycode[1]
        if text in self.keysPressed:
            self.keysPressed.remove(text)


game = GameWidget()

game.make_board()

class MyApp(App):
    def build(self):
        return game


if __name__ == "__main__":
    app = MyApp()
    app.run()
