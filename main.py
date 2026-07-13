"""
Kivy 五子棋游戏入口
保持与原版相同的接口：GomokuGame, AdvancedAI
"""

import kivy
kivy.require('2.2.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty, ObjectProperty, BooleanProperty, StringProperty
)

# 原版游戏逻辑接口 —— 完全不动
from core import GomokuGame
from AI import AdvancedAI


class GameWidget(Widget):
    """
    游戏主控件，包含棋盘绘制、触摸交互、状态管理
    所有与原版 gui.py 中 GomokuGUI 的功能一一对应
    """
    board_size = 15
    grid_size = NumericProperty(35)
    margin = NumericProperty(50)
    piece_radius = NumericProperty(15)

    # 颜色常量（与原版一致）
    board_color = (240/255, 217/255, 168/255, 1)   # #F0D9A8
    line_color = (0, 0, 0, 1)                      # #000000
    black_color = (0, 0, 0, 1)
    white_color = (1, 1, 1, 1)
    highlight_color = (1, 0, 0, 1)                 # #FF0000

    # 游戏逻辑对象（与原版相同）
    game = ObjectProperty(None)
    ai = ObjectProperty(None)

    # 模式标志
    vs_ai_mode = BooleanProperty(False)
    player_color = NumericProperty(1)   # 1=黑(先手), 2=白(后手)

    # 用于悬停效果的临时变量
    _hover_row = NumericProperty(-1)
    _hover_col = NumericProperty(-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game = GomokuGame()
        self.ai = AdvancedAI()

        # 绑定窗口大小变化，动态调整棋盘尺寸
        Window.bind(size=self._update_layout)

        # 初始绘制
        Clock.schedule_once(self._first_draw, 0.1)

    def _first_draw(self, dt):
        self.draw_board()
        self.update_status()

    def _update_layout(self, instance, value):
        """根据窗口大小重新计算棋盘格子大小和边距"""
        win_w, win_h = value
        usable_w = win_w * 0.65
        usable_h = win_h * 0.85
        max_grid_w = (usable_w - 2 * self.margin) / (self.board_size - 1)
        max_grid_h = (usable_h - 2 * self.margin) / (self.board_size - 1)
        new_grid = min(max_grid_w, max_grid_h, 55)
        if new_grid > 18:
            self.grid_size = int(new_grid)
            self.piece_radius = int(new_grid * 0.40)
            self.margin = int(new_grid * 1.37)
        self.draw_board()

    # ---------- 棋盘绘制 ----------
    def draw_board(self):
        """重绘整个棋盘（包括棋子、高亮、星位）"""
        self.canvas.before.clear()
        with self.canvas.before:
            # 背景色
            Color(*self.board_color)
            Rectangle(pos=self.pos, size=self.size)

        self.canvas.after.clear()
        with self.canvas.after:
            # 棋盘线条
            Color(*self.line_color)
            for i in range(self.board_size):
                y = self.margin + i * self.grid_size
                Line(points=[self.margin, y,
                              self.margin + (self.board_size-1)*self.grid_size, y],
                     width=1.5)
                x = self.margin + i * self.grid_size
                Line(points=[x, self.margin,
                              x, self.margin + (self.board_size-1)*self.grid_size],
                     width=1.5)

            # 星位（天元 + 四角星）
            star_positions = [(3,3), (3,11), (7,7), (11,3), (11,11)]
            for row, col in star_positions:
                cx = self.margin + col * self.grid_size
                cy = self.margin + row * self.grid_size
                Color(*self.line_color)
                Ellipse(pos=(cx-4, cy-4), size=(8,8))

            # 棋子
            for row in range(self.board_size):
                for col in range(self.board_size):
                    piece = self.game.board[row][col]
                    if piece != 0:
                        self._draw_piece(row, col, piece)

            # 高亮最后一步
            if self.game.last_move:
                row, col, player = self.game.last_move
                cx = self.margin + col * self.grid_size
                cy = self.margin + row * self.grid_size
                Color(*self.highlight_color)
                Ellipse(pos=(cx - self.piece_radius - 2,
                             cy - self.piece_radius - 2),
                        size=(2*(self.piece_radius+2), 2*(self.piece_radius+2)))

            # 悬停预览（如果有）
            if 0 <= self._hover_row < self.board_size and \
               0 <= self._hover_col < self.board_size and \
               self.game.board[self._hover_row][self._hover_col] == 0:
                cx = self.margin + self._hover_col * self.grid_size
                cy = self.margin + self._hover_row * self.grid_size
                if self.game.current_player == 1:
                    Color(136/255, 136/255, 136/255, 0.5)
                else:
                    Color(204/255, 204/255, 204/255, 0.5)
                Ellipse(pos=(cx - self.piece_radius + 5,
                             cy - self.piece_radius + 5),
                        size=(2*(self.piece_radius-5), 2*(self.piece_radius-5)))

    def _draw_piece(self, row, col, player):
        """绘制单个棋子"""
        cx = self.margin + col * self.grid_size
        cy = self.margin + row * self.grid_size
        if player == 1:
            Color(*self.black_color)
        else:
            Color(*self.white_color)
        Ellipse(pos=(cx - self.piece_radius, cy - self.piece_radius),
                size=(2*self.piece_radius, 2*self.piece_radius))
        # 白棋加边框
        if player == 2:
            Color(102/255, 102/255, 102/255, 1)
            Line(circle=(cx, cy, self.piece_radius), width=1)

    # ---------- 触摸事件 ----------
    def on_touch_down(self, touch):
        """点击落子"""
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        if self.game.game_over:
            return True
        if self.vs_ai_mode and self.game.current_player != self.player_color:
            return True

        # 计算棋盘坐标
        col = round((touch.x - self.margin) / self.grid_size)
        row = round((touch.y - self.margin) / self.grid_size)
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.game.make_move(row, col):
                self.draw_board()
                self.update_status()
                if self.game.game_over:
                    self._show_gameover_popup()
                # 如果是人机模式且轮到AI，调度AI
                if self.vs_ai_mode and not self.game.game_over and \
                   self.game.current_player != self.player_color:
                    Clock.schedule_once(lambda dt: self.make_ai_move(), 0.3)
        return True

    def on_touch_move(self, touch):
        """悬停预览"""
        if not self.collide_point(*touch.pos):
            return
        col = round((touch.x - self.margin) / self.grid_size)
        row = round((touch.y - self.margin) / self.grid_size)
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            self._hover_row = row
            self._hover_col = col
            self.draw_board()
        else:
            if self._hover_row != -1:
                self._hover_row = -1
                self._hover_col = -1
                self.draw_board()

    # ---------- 状态更新（通过 ids 更新 kv 中的标签）----------
    def update_status(self):
        """更新顶部标签"""
        # 当前玩家
        player_text = "当前: 黑棋" if self.game.current_player == 1 else "当前: 白棋"
        self.ids.current_player_label.text = player_text
        # 步数
        move_count = len(self.game.move_history)
        self.ids.move_count_label.text = f"步数: {move_count}"
        # 状态
        if self.game.game_over:
            if self.game.winner == 0:
                status_text = "游戏结束: 平局"
                status_color = (255/255, 152/255, 0, 1)  # 橙色
            else:
                winner_text = "黑棋" if self.game.winner == 1 else "白棋"
                status_text = f"游戏结束: {winner_text}获胜!"
                status_color = (244/255, 67/255, 54/255, 1)  # 红色
        else:
            status_text = "游戏中..."
            status_color = (76/255, 175/255, 80/255, 1)  # 绿色
        self.ids.status_label.text = status_text
        self.ids.status_label.color = status_color
        # 模式
        mode_text = "双人对战" if not self.vs_ai_mode else "人机对战"
        self.ids.mode_label.text = f"模式: {mode_text}"

    # ---------- 公共方法（供按钮和内部调用）----------
    def set_two_player_mode(self):
        """切换到双人模式"""
        if self.vs_ai_mode:
            self.vs_ai_mode = False
            self.restart_game()

    def set_vs_ai_mode(self):
        """切换到人机模式（弹出选择先手/后手）"""
        if not self.vs_ai_mode:
            # 弹出选择对话框
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            popup = Popup(title='选择先手',
                          content=content,
                          size_hint=(0.6, 0.4),
                          auto_dismiss=False)
            msg = Label(text='请选择您的棋子颜色：')
            btn_box = BoxLayout(spacing=10, size_hint_y=0.4)
            btn_black = Button(text='黑棋 (先手)')
            btn_white = Button(text='白棋 (后手)')
            btn_box.add_widget(btn_black)
            btn_box.add_widget(btn_white)
            content.add_widget(msg)
            content.add_widget(btn_box)

            def on_black(instance):
                self.player_color = 1
                self.ai.player = 2
                self.vs_ai_mode = True
                popup.dismiss()
                self.restart_game()

            def on_white(instance):
                self.player_color = 2
                self.ai.player = 1
                self.vs_ai_mode = True
                popup.dismiss()
                self.restart_game()

            btn_black.bind(on_release=on_black)
            btn_white.bind(on_release=on_white)
            popup.open()

    def make_ai_move(self):
        """AI 下棋（与原版逻辑一致）"""
        if (self.game.game_over or not self.vs_ai_mode or
            self.game.current_player == self.player_color):
            return
        move = self.ai.get_move(self.game)
        if move:
            row, col = move
            if self.game.make_move(row, col):
                self.draw_board()
                self.update_status()
                if self.game.game_over:
                    self._show_gameover_popup()

    def restart_game(self):
        """重新开始游戏"""
        self.game.reset()
        if self.vs_ai_mode and self.player_color == 2:
            self.game.current_player = 3 - self.player_color  # AI先手
        self.draw_board()
        self.update_status()
        if self.vs_ai_mode and self.game.current_player != self.player_color:
            Clock.schedule_once(lambda dt: self.make_ai_move(), 0.3)

    def undo_move(self):
        """悔棋（与原版逻辑完全一致）"""
        if self.game.game_over or not self.game.move_history:
            return
        if not self.vs_ai_mode:
            if self.game.undo(1):
                self.draw_board()
                self.update_status()
        else:
            move_count = len(self.game.move_history)
            if self.game.current_player == self.player_color:
                steps_to_undo = 2
            else:
                steps_to_undo = 1
            if move_count < steps_to_undo:
                popup = Popup(title='提示',
                              content=Label(text='步数不足，无法悔棋'),
                              size_hint=(0.5, 0.3))
                popup.open()
                return
            if self.game.undo(steps_to_undo):
                self.draw_board()
                self.update_status()

    def quit_game(self):
        """退出游戏"""
        App.get_running_app().stop()

    def _show_gameover_popup(self):
        """显示游戏结束弹窗"""
        if self.game.winner == 0:
            msg = '平局！'
        else:
            winner = '黑棋' if self.game.winner == 1 else '白棋'
            msg = f'{winner}获胜！'
        popup = Popup(title='游戏结束',
                      content=Label(text=msg),
                      size_hint=(0.5, 0.3))
        popup.open()


class GomokuApp(App):
    """Kivy 应用类"""
    def build(self):
        self.title = '业闲 - 五子棋'
        # 手动加载 game.kv（因为 kv 文件名与 App 类名不匹配）
        Builder.load_file('game.kv')
        return GameWidget()


if __name__ == '__main__':
    GomokuApp().run()