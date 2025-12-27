import tkinter as tk
from tkinter import messagebox
import random

class Checkers:
    def __init__(self, root):
        self.root = root
        self.root.title("Checkers Game - Your turn (Red)")
        self.board_size = 8
        self.cell_size = 60
        self.canvas = tk.Canvas(root, width=self.board_size*self.cell_size,
                                height=self.board_size*self.cell_size)
        self.canvas.pack()
        
        self.selected_piece = None
        self.turn = 'red'  # red (human) starts
        self.pieces = {}  # (row, col): {'color': 'red'/'black', 'king': bool}
        
        self.draw_board()
        self.init_pieces()
        self.draw_pieces()
        
        self.canvas.bind("<Button-1>", self.click)

    def draw_board(self):
        self.canvas.delete("square")
        color1 = "#DDB88C"
        color2 = "#A66D4F"
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = color1 if (row + col) % 2 == 0 else color2
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")

    def init_pieces(self):
        for row in range(3):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {'color': 'black', 'king': False}
        for row in range(5, 8):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    self.pieces[(row, col)] = {'color': 'red', 'king': False}

    def draw_pieces(self):
        self.canvas.delete("piece")
        for (row, col), piece in self.pieces.items():
            x = col * self.cell_size + self.cell_size // 2
            y = row * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 2 - 5
            fill_color = piece['color']
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill=fill_color, tags="piece")
            if piece['king']:
                self.canvas.create_text(x, y, text="K", fill="white", font=("Arial", 24, "bold"), tags="piece")

    def click(self, event):
        if self.turn != 'red':
            return  # Ignore clicks when it's AI's turn

        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if (row, col) not in self.pieces and self.selected_piece is None:
            return
        if self.selected_piece is None:
            if (row, col) in self.pieces and self.pieces[(row, col)]['color'] == self.turn:
                self.selected_piece = (row, col)
                self.highlight_moves()
        else:
            if (row, col) == self.selected_piece:
                self.selected_piece = None
                self.draw_board()
                self.draw_pieces()
                return
            if self.is_valid_move(self.selected_piece, (row, col)):
                self.make_move(self.selected_piece, (row, col))
                self.selected_piece = None
                self.draw_board()
                self.draw_pieces()
                if self.check_winner():
                    return
                self.switch_turn()
                self.root.after(500, self.ai_move)  # AI moves after 0.5 sec
            else:
                self.selected_piece = None
                self.draw_board()
                self.draw_pieces()

    def highlight_moves(self):
        self.draw_board()
        self.draw_pieces()
        moves = self.get_valid_moves(self.selected_piece)
        for move in moves:
            row, col = move
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3, tags="highlight")

    def get_valid_moves(self, pos):
        row, col = pos
        piece = self.pieces[pos]
        directions = []
        if piece['color'] == 'red' or piece['king']:
            directions.append((-1, -1))
            directions.append((-1, 1))
        if piece['color'] == 'black' or piece['king']:
            directions.append((1, -1))
            directions.append((1, 1))

        valid_moves = []
        # Normal moves
        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < self.board_size and 0 <= c < self.board_size:
                if (r, c) not in self.pieces:
                    valid_moves.append((r, c))

        # Capture moves
        for dr, dc in directions:
            r1, c1 = row + dr, col + dc
            r2, c2 = row + 2*dr, col + 2*dc
            if 0 <= r2 < self.board_size and 0 <= c2 < self.board_size:
                if (r1, c1) in self.pieces and self.pieces[(r1, c1)]['color'] != piece['color']:
                    if (r2, c2) not in self.pieces:
                        valid_moves.append((r2, c2))

        return valid_moves

    def is_valid_move(self, start, end):
        valid_moves = self.get_valid_moves(start)
        return end in valid_moves

    def make_move(self, start, end):
        piece = self.pieces[start]
        del self.pieces[start]
        self.pieces[end] = piece

        r1, c1 = start
        r2, c2 = end
        if abs(r2 - r1) == 2:
            captured = ((r1 + r2)//2, (c1 + c2)//2)
            if captured in self.pieces:
                del self.pieces[captured]

        # King promotion
        if piece['color'] == 'red' and r2 == 0:
            piece['king'] = True
        elif piece['color'] == 'black' and r2 == self.board_size - 1:
            piece['king'] = True

    def switch_turn(self):
        self.turn = 'black' if self.turn == 'red' else 'red'
        self.root.title(f"Checkers Game - {self.turn.capitalize()}'s Turn")

    def check_winner(self):
        red_pieces = [p for p in self.pieces.values() if p['color'] == 'red']
        black_pieces = [p for p in self.pieces.values() if p['color'] == 'black']
        if not red_pieces:
            messagebox.showinfo("Game Over", "Black (AI) wins!")
            self.root.destroy()
            return True
        elif not black_pieces:
            messagebox.showinfo("Game Over", "Red (You) wins!")
            self.root.destroy()
            return True
        return False

    def ai_move(self):
        if self.turn != 'black':
            return

        all_moves = self.get_all_moves('black')
        if not all_moves:
            messagebox.showinfo("Game Over", "Red (You) wins! AI has no moves.")
            self.root.destroy()
            return

        # Prefer capture moves
        capture_moves = [m for m in all_moves if abs(m[0][0] - m[1][0]) == 2]
        if capture_moves:
            move = random.choice(capture_moves)
        else:
            move = random.choice(all_moves)

        start, end = move
        self.make_move(start, end)
        self.draw_board()
        self.draw_pieces()
        if self.check_winner():
            return
        self.switch_turn()

    def get_all_moves(self, color):
        moves = []
        for pos, piece in self.pieces.items():
            if piece['color'] == color:
                valid_moves = self.get_valid_moves(pos)
                for move in valid_moves:
                    moves.append((pos, move))
        return moves

if __name__ == "__main__":
    root = tk.Tk()
    game = Checkers(root)
    root.mainloop()