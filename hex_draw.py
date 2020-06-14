import math
import tkinter as tk


class Polygon:
    def __init__(self, points=None):
        if points:
            self.points = points
        else:
            self.points = []

    def paint(self, canvas, position, color='', active_color='', outline='black', width=4, tag=None):
        center_x, center_y = position
        points = []
        for x, y, in self.points:
            points.append(x + center_x)
            points.append(y + center_y)
        if tag:
            canvas.create_polygon(*points, fill=color, outline=outline, activefill=active_color, width=width, tag=tag)
        else:
            canvas.create_polygon(*points, fill=color, outline=outline, activefill=active_color, width=width)


class RegularPolygon(Polygon):
    def __init__(self, side_count, radius=1, rotate=False):
        points = []
        if not rotate:
            base_radians = math.pi * (side_count - 4) * 0.5 / side_count
        else:
            base_radians = 0
        for i in range(0, side_count):
            radians = base_radians + i * 2 * math.pi / side_count
            x = math.cos(radians) * radius
            y = math.sin(radians) * radius
            points.append((x, y))
        super().__init__(points)


class Pad:
    def __init__(self, canvas, side_length, spacing):
        self.hexagon = RegularPolygon(6, side_length)
        self.canvas = canvas
        self.side_length = side_length
        self.h_to_a = 2 * math.sqrt(3) + 2 * spacing
        self.v_to_a = 3 + math.sqrt(3) * spacing
        # self.m_to_a = (3 + math.sqrt(3) * spacing) / 165
        self.m_to_a = math.sqrt((3 * self.h_to_a) ** 2 + (6 * self.v_to_a) ** 2) / 1130
        self.colored_lattices = []
        for c in range(0, 7):
            for r in range(0, 8):
                x = c * self.h_to_a * self.side_length * 0.5
                if r % 2 == 1:
                    x -= 0.5 * self.h_to_a * self.side_length * 0.5
                x = self.pad_x_to_canvas_x(x)
                y = self.pad_y_to_canvas_y(r * self.v_to_a * self.side_length * 0.5)
                if r > 3:
                    self.hexagon.paint(canvas, (x, y), color='blue', tag=f'{c}-{r}')
                else:
                    self.hexagon.paint(canvas, (x, y), color='skyblue', tag=f'{c}-{r}')

    def reset_color(self):
        for c, r in self.colored_lattices:
            if r > 3:
                self.canvas.itemconfigure(f'{c}-{r}', fill='blue')
            else:
                self.canvas.itemconfigure(f'{c}-{r}', fill='skyblue')
        self.colored_lattices = []

    def change_color(self, c, r, color):
        self.canvas.itemconfigure(f'{c}-{r}', fill=color)
        self.colored_lattices.append((c, r))

    def get_distance(self, position_1, position_2):
        c1, r1 = position_1
        c2, r2 = position_2
        v1 = r1
        if v1 % 2 == 0:
            h1 = c1
        else:
            h1 = c1 - 0.5
        v2 = r2
        if v2 % 2 == 0:
            h2 = c2
        else:
            h2 = c2 - 0.5
        x1 = h1 * self.h_to_a
        y1 = v1 * self.v_to_a
        x2 = h2 * self.h_to_a
        y2 = v2 * self.v_to_a
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def pad_x_to_canvas_x(self, x):
        return x + self.side_length * 2

    def pad_y_to_canvas_y(self, y):
        return 700 - y - self.side_length * 2

    def canvas_x_to_pad_x(self, x):
        return x - self.side_length * 2

    def canvas_y_to_pad_y(self, y):
        return 700 - y - self.side_length * 2

    def find_lattice_by_xy(self, x, y):
        x = self.canvas_x_to_pad_x(x)
        y = self.canvas_y_to_pad_y(y)
        r = int(y * 2 / (self.v_to_a * self.side_length) + 0.5)
        if r < 0 or r > 7:
            return None
        if r % 2 == 1:
            x += 0.25 * self.h_to_a * self.side_length
        c = int(x * 2 / (self.h_to_a * self.side_length) + 0.5)
        if c < 0 or c > 6:
            return None
        return c, r

    def draw_range(self, c, r, max_distance):
        self.reset_color()
        if r > 3:
            row_start = 0
            row_end = r
            top_color = 'orange'
            bottom_color = 'red'
            self_color = 'green'
        else:
            row_start = r + 1
            row_end = 8
            top_color = 'red'
            bottom_color = 'orange'
            self_color = 'lime'
        for c1 in range(0, 7):
            for r1 in range(row_start, row_end):
                if self.get_distance((c, r), (c1, r1)) < max_distance * self.m_to_a:
                    if r1 > 3:
                        self.change_color(c1, r1, top_color)
                    else:
                        self.change_color(c1, r1, bottom_color)
        self.change_color(c, r, self_color)


previous_c = -1
previous_r = -1
previous_range_index = 2
range_list = [180, 420, 660, 890, 1130]
range_index = 2
pad: Pad


def draw_range(event):
    global previous_c, previous_r, previous_range_index, pad, range_index
    lattice = pad.find_lattice_by_xy(event.x, event.y)
    if not lattice:
        previous_c = -1
        previous_r = -1
        return
    base_c, base_r = lattice
    if base_c == previous_c and base_r == previous_r and range_index == previous_range_index:
        return
    previous_c = base_c
    previous_r = base_r
    previous_range_index = range_index
    pad.draw_range(base_c, base_r, range_list[range_index])


def change_range(event):
    global range_index
    if event.delta > 0:
        if range_index < 4:
            range_index += 1
    elif event.delta < 0:
        if range_index > 0:
            range_index -= 1
    draw_range(event)


def main():
    global pad
    root = tk.Tk()
    root.geometry('700x700')
    canvas = tk.Canvas()
    canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
    pad = Pad(canvas, side_length=48.0, spacing=0.0)
    canvas.bind('<Motion>', draw_range)
    canvas.bind('<MouseWheel>', change_range)
    tk.mainloop()


if __name__ == '__main__':
    main()
