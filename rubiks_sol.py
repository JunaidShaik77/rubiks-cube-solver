# rubiks_cube_solver.py
import tkinter as tk
from tkinter import messagebox, font
import random
import kociemba

# --- Core Cube Logic ---
class Cube:
    COLORS = {
        "W": "#FFFFFF", "Y": "#FFD700", "G": "#009B48",
        "B": "#0046AD", "O": "#FF5900", "R": "#B71234"
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = {
            'U': ['W'] * 9, 'D': ['Y'] * 9, 'F': ['G'] * 9,
            'B': ['B'] * 9, 'L': ['O'] * 9, 'R': ['R'] * 9
        }

    def _rotate_face_clockwise(self, face):
        s = self.state[face]
        self.state[face] = [s[6], s[3], s[0], s[7], s[4], s[1], s[8], s[5], s[2]]

    def move(self, move_str):
        def triple(m): [self.move(m) for _ in range(3)]
        if move_str.endswith("'"): return triple(move_str[0])
        if move_str.endswith("2"): return [self.move(move_str[0]) for _ in range(2)]

        if move_str == 'U':
            self._rotate_face_clockwise('U')
            f, r, b, l = self.state['F'], self.state['R'], self.state['B'], self.state['L']
            f[:3], r[:3], b[:3], l[:3] = r[:3], b[:3], l[:3], f[:3]
        elif move_str == 'D':
            self._rotate_face_clockwise('D')
            f, r, b, l = self.state['F'], self.state['R'], self.state['B'], self.state['L']
            f[6:], l[6:], b[6:], r[6:] = l[6:], b[6:], r[6:], f[6:]
        elif move_str == 'R':
            self._rotate_face_clockwise('R')
            u, f, d, b = self.state['U'], self.state['F'], self.state['D'], self.state['B']
            u2, f2, d2, b2 = u[2::3], f[2::3], d[2::3], b[6::-3]
            u[2], u[5], u[8] = f2
            f[2], f[5], f[8] = d2
            d[2], d[5], d[8] = b2[::-1]
            b[0], b[3], b[6] = u2[::-1]
        elif move_str == 'L':
            self._rotate_face_clockwise('L')
            u, f, d, b = self.state['U'], self.state['F'], self.state['D'], self.state['B']
            u0, f0, d0, b0 = u[::3], f[::3], d[::3], b[8::-3]
            u[0], u[3], u[6] = b0[::-1]
            f[0], f[3], f[6] = u0
            d[0], d[3], d[6] = f0
            b[2], b[5], b[8] = d0[::-1]
        elif move_str == 'F':
            self._rotate_face_clockwise('F')
            u, l, d, r = self.state['U'], self.state['L'], self.state['D'], self.state['R']
            u6, u7, u8 = u[6:9]
            u[6], u[7], u[8] = l[8], l[5], l[2]
            l[2], l[5], l[8] = d[2], d[1], d[0]
            d[0], d[1], d[2] = r[6], r[3], r[0]
            r[0], r[3], r[6] = u6, u7, u8
        elif move_str == 'B':
            self._rotate_face_clockwise('B')
            u, r, d, l = self.state['U'], self.state['R'], self.state['D'], self.state['L']
            u0, u1, u2 = u[0], u[1], u[2]
            u[0], u[1], u[2] = r[2], r[5], r[8]
            r[2], r[5], r[8] = d[8], d[7], d[6]
            d[6], d[7], d[8] = l[0], l[3], l[6]
            l[0], l[3], l[6] = u2, u1, u0

    def scramble(self, scramble_str):
        for move in scramble_str.split():
            self.move(move)

    def to_kociemba_str(self):
        center = {self.state[f][4]: f for f in 'URFDLB'}
        return ''.join(center[c] for face in 'URFDLB' for c in self.state[face])

# --- GUI Application ---
class RubiksCubeGUI(tk.Tk):
    def __init__(self, cube):
        super().__init__()
        self.cube = cube
        self.title("Rubik's Cube Solver")
        self.geometry("800x600")
        self.configure(bg="#333333")
        self.facelet_size = 40
        self.canvases = {}
        self._create_widgets()
        self._draw_cube()

    def _create_widgets(self):
        main_frame = tk.Frame(self, bg="#333333")
        main_frame.pack(pady=20)

        cube_frame = tk.Frame(main_frame, bg="#333333")
        cube_frame.grid(row=0, column=0)

        positions = {'U': (1,0), 'L': (0,1), 'F': (1,1), 'R': (2,1), 'B': (3,1), 'D': (1,2)}
        for face, (x, y) in positions.items():
            face_canvas = tk.Canvas(cube_frame, width=120, height=120, bg="#333")
            face_canvas.grid(row=y, column=x)
            self.canvases[face] = [face_canvas.create_rectangle(j*40, i*40, j*40+40, i*40+40, outline='black') for i in range(3) for j in range(3)]

        control_frame = tk.Frame(main_frame, bg="#333333")
        control_frame.grid(row=0, column=1, padx=20)

        self.scramble_entry = tk.Entry(control_frame, width=40)
        self.scramble_entry.pack(pady=5)
        self.scramble_entry.insert(0, "R U R' U' F' L B2 D")

        tk.Button(control_frame, text="Scramble", command=self._apply_scramble).pack(fill="x")
        tk.Button(control_frame, text="Random", command=self._random_scramble).pack(fill="x")
        tk.Button(control_frame, text="Solve", command=self._solve_cube, bg='green', fg='white').pack(fill="x")
        tk.Button(control_frame, text="Reset", command=self._reset_cube, bg='red', fg='white').pack(fill="x")

        self.solution_label = tk.Label(control_frame, text="", fg="white", wraplength=200, bg="#333333")
        self.solution_label.pack(pady=10)

    def _draw_cube(self):
        for face, facelets in self.cube.state.items():
            canvas = self.canvases[face][0].master
            for i in range(9):
                canvas.itemconfig(self.canvases[face][i], fill=self.cube.COLORS[facelets[i]])

    def _apply_scramble(self):
        scramble = self.scramble_entry.get()
        self.cube.scramble(scramble)
        self._draw_cube()
        self.solution_label.config(text="")

    def _random_scramble(self):
        moves = [m + m2 for m in 'URFDLB' for m2 in ['', "'", '2']]
        scramble = ' '.join(random.choice(moves) for _ in range(20))
        self.scramble_entry.delete(0, tk.END)
        self.scramble_entry.insert(0, scramble)
        self._apply_scramble()

    def _reset_cube(self):
        self.cube.reset()
        self._draw_cube()
        self.solution_label.config(text="")

    def _solve_cube(self):
        try:
            sol = kociemba.solve(self.cube.to_kociemba_str())
            self.solution_label.config(text="Solution: " + sol)
            self._animate_solution(sol.split())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _animate_solution(self, moves):
        if not moves:
            messagebox.showinfo("Done", "Cube Solved!")
            return
        move = moves.pop(0)
        self.cube.move(move)
        self._draw_cube()
        self.after(300, self._animate_solution, moves)

if __name__ == "__main__":
    app = RubiksCubeGUI(Cube())
    app.mainloop()
