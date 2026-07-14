import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty

from core import GomokuGame
from AI import AdvancedAI

BOARD_SIZE = 15

class GameWidget(Widget):
    board_size = BOARD_SIZE
    grid_size = NumericProperty(0)
    margin = NumericProperty(0)
    piece_radius = NumericProperty(0)

    game = ObjectProperty(None)
    ai = ObjectProperty(None)
    vs_ai_mode = BooleanProperty(False)
    player_color = NumericProperty(1)

    status_text = StringProperty('Turn: Black')
    move_count_text = StringProperty('Moves: 0')

    _hover_row = NumericProperty(-1)
    _hover_col = NumericProperty(-1)
    _thinking = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = GomokuGame()
        self.ai = AdvancedAI()
        self.bind(size=self._update_layout, pos=self._update_layout)
        Clock.schedule_once(self._first_draw, 0.1)

    def _first_draw(self, dt):
        self._update_layout()
        self.draw_board()
        self._update_labels()

    def _update_layout(self, *args):
        if self.width <= 0 or self.height <= 0:
            return
        side = min(self.width, self.height)
        self.offset_x = (self.width - side) / 2
        self.offset_y = (self.height - side) / 2
        # 减小内边距，扩大棋盘有效面积
        self.margin = side * 0.032
        inner_side = side - 2 * self.margin
        self.grid_size = inner_side / (BOARD_SIZE - 1)
        # 增大棋子半径
        self.piece_radius = self.grid_size * 0.456
        self.draw_board()

    def draw_board(self):
        ox = self.x + self.offset_x
        oy = self.y + self.offset_y
        side = min(self.width, self.height)

        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.957, 0.886, 0.706, 1)
            Rectangle(pos=(ox, oy), size=(side, side))

        self.canvas.after.clear()
        with self.canvas.after:
            Color(0.184, 0.180, 0.176, 1)
            for i in range(BOARD_SIZE):
                x = ox + self.margin + i * self.grid_size
                y = oy + self.margin + i * self.grid_size
                Line(points=[ox + self.margin, y,
                             ox + self.margin + (BOARD_SIZE-1)*self.grid_size, y],
                     width=1.2)
                Line(points=[x, oy + self.margin,
                             x, oy + self.margin + (BOARD_SIZE-1)*self.grid_size],
                     width=1.2)

            star_points = [(3,3), (3,11), (7,7), (11,3), (11,11)]
            for r, c in star_points:
                cx = ox + self.margin + c * self.grid_size
                cy = oy + self.margin + r * self.grid_size
                Color(0, 0, 0, 1)
                Ellipse(pos=(cx-3.5, cy-3.5), size=(7,7))

            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    piece = self.game.board[r][c]
                    if piece != 0:
                        self._draw_piece(r, c, piece, ox, oy)

            # 高亮最后一步（红色圆环，不遮挡棋子）
            if self.game.last_move:
                r, c, _ = self.game.last_move
                cx = ox + self.margin + c * self.grid_size
                cy = oy + self.margin + r * self.grid_size
                Color(1, 0, 0, 1)  # 纯红
                Line(circle=(cx, cy, self.piece_radius + 2), width=2)

            if 0 <= self._hover_row < BOARD_SIZE and \
               0 <= self._hover_col < BOARD_SIZE and \
               self.game.board[self._hover_row][self._hover_col] == 0:
                cx = ox + self.margin + self._hover_col * self.grid_size
                cy = oy + self.margin + self._hover_row * self.grid_size
                if self.game.current_player == 1:
                    Color(0.576, 0.557, 0.518, 0.38)
                else:
                    Color(0.912, 0.896, 0.876, 0.38)
                Ellipse(pos=(cx - self.piece_radius + 5,
                             cy - self.piece_radius + 5),
                        size=(2*(self.piece_radius-5), 2*(self.piece_radius-5)))

    def _draw_piece(self, row, col, player, ox, oy):
        cx = ox + self.margin + col * self.grid_size
        cy = oy + self.margin + row * self.grid_size
        if player == 1:
            Color(0, 0, 0, 1)
        else:
            Color(1, 1, 1, 1)
        Ellipse(pos=(cx - self.piece_radius, cy - self.piece_radius),
                size=(2*self.piece_radius, 2*self.piece_radius))
        if player == 2:
            Color(0.565, 0.553, 0.586, 1)
            Line(circle=(cx, cy, self.piece_radius), width=1.2)

    def on_touch_down(self, touch):
        if self._thinking:
            return True
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if self.game.game_over:
            return True
        if self.vs_ai_mode and self.game.current_player != self.player_color:
            return True

        ox = self.x + self.offset_x
        oy = self.y + self.offset_y
        col = round((touch.x - ox - self.margin) / self.grid_size)
        row = round((touch.y - oy - self.margin) / self.grid_size)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            if self.game.make_move(row, col):
                self.draw_board()
                self._update_labels()
                if self.game.game_over:
                    self._show_gameover_popup()
                if self.vs_ai_mode and not self.game.game_over and \
                   self.game.current_player != self.player_color:
                    Clock.schedule_once(lambda dt: self.make_ai_move(), 0.3)
        return True

    def on_touch_move(self, touch):
        if self._thinking:
            return True
        if not self.collide_point(*touch.pos):
            return
        ox = self.x + self.offset_x
        oy = self.y + self.offset_y
        col = round((touch.x - ox - self.margin) / self.grid_size)
        row = round((touch.y - oy - self.margin) / self.grid_size)
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            self._hover_row = row
            self._hover_col = col
            self.draw_board()
        else:
            if self._hover_row != -1:
                self._hover_row = -1
                self._hover_col = -1
                self.draw_board()

    def _update_labels(self):
        if self.game.game_over:
            if self.game.winner == 0:
                self.status_text = 'Draw!'
            else:
                winner = 'Black' if self.game.winner == 1 else 'White'
                self.status_text = f'{winner} wins!'
        else:
            turn = 'Black' if self.game.current_player == 1 else 'White'
            self.status_text = f'Turn: {turn}'
        self.move_count_text = f'Moves: {len(self.game.move_history)}'

    def toggle_mode(self, button_instance):
        if self.vs_ai_mode:
            self.vs_ai_mode = False
            button_instance.text = 'vs AI'
            self.restart_game()
        else:
            self.vs_ai_mode = True
            self.player_color = 1
            self.ai.player = 2
            button_instance.text = '2 Players'
            self.restart_game()

    def set_two_player_mode(self):
        if self.vs_ai_mode:
            self.vs_ai_mode = False
            self.restart_game()

    def set_vs_ai_mode(self):
        if not self.vs_ai_mode:
            self.player_color = 1
            self.ai.player = 2
            self.vs_ai_mode = True
            self.restart_game()

    def make_ai_move(self):
        if self.game.game_over or not self.vs_ai_mode or \
           self.game.current_player == self.player_color:
            return
        self._thinking = True
        move = self.ai.get_move(self.game)
        if move:
            row, col = move
            if self.game.make_move(row, col):
                self.draw_board()
                self._update_labels()
                if self.game.game_over:
                    self._show_gameover_popup()
        self._thinking = False

    def restart_game(self):
        if self._thinking:
            return
        self.game.reset()
        if self.vs_ai_mode and self.player_color == 2:
            self.game.current_player = 3 - self.player_color
        self.draw_board()
        self._update_labels()
        if self.vs_ai_mode and self.game.current_player != self.player_color:
            Clock.schedule_once(lambda dt: self.make_ai_move(), 0.3)

    def undo_move(self):
        if self._thinking:
            return
        if self.game.game_over or not self.game.move_history:
            return
        if not self.vs_ai_mode:
            if self.game.undo(1):
                self.draw_board()
                self._update_labels()
        else:
            move_count = len(self.game.move_history)
            steps = 2 if self.game.current_player == self.player_color else 1
            if move_count < steps:
                return
            if self.game.undo(steps):
                self.draw_board()
                self._update_labels()

    def quit_game(self):
        App.get_running_app().stop()

    def _show_gameover_popup(self):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button as PopupButton
        from kivy.uix.label import Label as PopupLabel

        msg = 'Draw!' if self.game.winner == 0 else f'{["Black","White"][self.game.winner-1]} wins!'

        content = BoxLayout(orientation='vertical', spacing=20, padding=20)

        # 胜利文字：亮金色，与浅米色背景形成高对比度
        label = PopupLabel(text=msg, font_size='30sp', color=(1, 0.843, 0, 1),  # 亮金色
                           halign='center', valign='middle')
        content.add_widget(label)

        close_btn = PopupButton(text='OK', size_hint=(1, 0.4), font_size='20sp',
                                background_normal='',
                                background_color=(0.3, 0.6, 0.9, 1),
                                color=(1, 1, 1, 1))
        content.add_widget(close_btn)

        popup = Popup(title='Game Over',
                      content=content,
                      size_hint=(0.6, 0.4),
                      background_color=(0.936, 0.907, 0.857, 1),
                      separator_height=0,
                      auto_dismiss=False)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()


class GomokuApp(App):
    def build(self):
        # ----- 强制竖屏 -----
        w, h = Window.size
        if w > h:
            Window.size = (h, w)
        Window.minimum_width = 340
        Window.minimum_height = 520
        # -------------------

        Window.clearcolor = (0.921, 0.909, 0.879, 1)
        self.title = 'Gomoku'
        root = BoxLayout(orientation='vertical')

        # 顶部栏高度降低，给棋盘更多空间
        top_bar = BoxLayout(orientation='horizontal',
                            size_hint=(1, None),
                            height='40dp',
                            padding=[8, 2],
                            spacing=8)
        status_label = Label(text='Turn: Black',
                             font_size='17sp',
                             color=(0.1,0.1,0.1,1))
        move_label = Label(text='Moves: 0',
                           font_size='15sp',
                           color=(0.3,0.3,0.3,1))
        top_bar.add_widget(status_label)
        top_bar.add_widget(move_label)

        mode_btn = Button(text='vs AI', size_hint=(0.175,1),
                          background_normal='',
                          background_color=(0.293,0.591,0.903,1),
                          color=(1,1,1,1))
        top_bar.add_widget(mode_btn)

        board = GameWidget(size_hint=(1, 1))

        # 底部栏高度降低
        bottom_bar = BoxLayout(orientation='horizontal',
                               size_hint=(1, None),
                               height='42dp',
                               padding=[8,4],
                               spacing=8)
        buttons = [
            ('Restart', lambda x: board.restart_game()),
            ('Undo', lambda x: board.undo_move()),
            ('Quit', lambda x: board.quit_game())
        ]
        for text, callback in buttons:
            btn = Button(text=text, font_size='15sp',
                         background_normal='',
                         background_color=(0.969,0.723,0.020,1),
                         color=(0,0,0,1))
            btn.bind(on_release=callback)
            bottom_bar.add_widget(btn)

        status_label.text = board.status_text
        move_label.text = board.move_count_text
        board.bind(status_text=status_label.setter('text'))
        board.bind(move_count_text=move_label.setter('text'))

        mode_btn.bind(on_release=lambda x: board.toggle_mode(x))

        root.add_widget(top_bar)
        root.add_widget(board)
        root.add_widget(bottom_bar)
        return root


if __name__ == '__main__':
    GomokuApp().run()
