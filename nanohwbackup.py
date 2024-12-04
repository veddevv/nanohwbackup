import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, simpledialog, messagebox
from PIL import Image, ImageDraw, ImageTk
import psutil
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_SAVE_DIR = os.getenv('DEFAULT_SAVE_DIR', os.path.expanduser('~'))

class NanoHWApp(tk.Tk):
    VERSION = "0.2.2"

    def __init__(self):
        super().__init__()
        self.title("NanoHW")
        self.geometry("800x600")
        self.configure(bg="#ffffff")

        self.create_tabs()
        self.setup_system_info_tab()
        self.setup_nanopaint()
        self.setup_about_tab()

    def create_tabs(self):
        self.tab_control = ttk.Notebook(self)
        self.system_info_tab = ttk.Frame(self.tab_control)
        self.nanopaint_tab = ttk.Frame(self.tab_control)
        self.about_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.system_info_tab, text="System Info")
        self.tab_control.add(self.nanopaint_tab, text="NanoPaint")
        self.tab_control.add(self.about_tab, text="About")
        self.tab_control.pack(expand=1, fill="both")

    def setup_system_info_tab(self):
        self.create_system_info_label()
        self.create_system_info_chart()
        self.initialize_animation()

    def create_system_info_label(self):
        tk.Label(self.system_info_tab, text="System Information", font=("Arial", 16, "bold")).pack(pady=10)

    def create_system_info_chart(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()
        self.ax1.set_xlabel('Time')
        self.ax1.set_ylabel('CPU Usage (%)', color='tab:blue')
        self.ax2.set_ylabel('Memory Usage (%)', color='tab:orange')
        self.cpu_xdata, self.cpu_ydata = [], []
        self.memory_xdata, self.memory_ydata = [], []
        self.cpu_line, = self.ax1.plot([], [], 'b-', label='CPU Usage')
        self.memory_line, = self.ax2.plot([], [], 'r-', label='Memory Usage')
        self.ax1.legend(loc='upper left')
        self.ax2.legend(loc='upper right')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.system_info_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

    def initialize_animation(self):
        self.ani = animation.FuncAnimation(self.fig, self.update_chart, interval=1000, blit=False)

    def update_chart(self, frame):
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
        self.cpu_xdata.append(len(self.cpu_xdata))
        self.cpu_ydata.append(cpu_usage)
        self.memory_xdata.append(len(self.memory_xdata))
        self.memory_ydata.append(memory_usage)
        self.ax1.set_xlim(max(0, len(self.cpu_xdata) - 20), len(self.cpu_xdata))
        self.ax2.set_xlim(max(0, len(self.memory_xdata) - 20), len(self.memory_xdata))
        self.cpu_line.set_data(self.cpu_xdata, self.cpu_ydata)
        self.memory_line.set_data(self.memory_xdata, self.memory_ydata)
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        return self.cpu_line, self.memory_line

    def setup_nanopaint(self):
        self.drawing = False
        self.current_brush = "circle"
        self.brush_size = 5
        self.current_color = "#000000"
        self.history = []
        self.canvas = tk.Canvas(self.nanopaint_tab, bg="white", width=600, height=400)
        self.canvas.pack()
        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.canvas_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_on_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.toolbar = tk.Frame(self.nanopaint_tab)
        self.toolbar.pack()
        self.brush_var = tk.StringVar(value=self.current_brush)
        tk.Label(self.toolbar, text="Brush:").pack(side=tk.LEFT, padx=5)
        brushes = ["circle", "square", "line"]
        for brush in brushes:
            tk.Radiobutton(self.toolbar, text=brush.capitalize(), variable=self.brush_var, value=brush, command=self.set_brush).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Color", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Undo", command=self.undo).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Clear", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Save", command=self.save_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Load", command=self.load_image).pack(side=tk.LEFT, padx=5)
        tk.Button(self.toolbar, text="Text", command=self.add_text).pack(side=tk.LEFT, padx=5)

    def setup_about_tab(self):
        tk.Label(self.about_tab, text="NanoHW", font=("Arial", 16, "bold"), bg="#ffffff").pack(pady=10)
        tk.Label(self.about_tab, text=f"Version {self.VERSION}", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(self.about_tab, text="Made by Veddev", font=("Arial", 14), bg="#ffffff").pack(pady=5)
        tk.Label(self.about_tab, text="This program is free and open-source software", font=("Arial", 12), bg="#ffffff").pack(pady=5)
        tk.Label(self.about_tab, text="under the GNU General Public License (GPL) v3.0.", font=("Arial", 12), bg="#ffffff").pack(pady=5)

    def start_draw(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y
        self.history.append(self.image.copy())

    def draw_on_canvas(self, event):
        if self.drawing:
            x, y = event.x, event.y
            if self.current_brush == "circle":
                self.canvas.create_oval(self.last_x - self.brush_size, self.last_y - self.brush_size, self.last_x + self.brush_size, self.last_y + self.brush_size, fill=self.current_color, outline=self.current_color)
                self.draw.ellipse([self.last_x - self.brush_size, self.last_y - self.brush_size, self.last_x + self.brush_size, self.last_y + self.brush_size], fill=self.current_color)
            elif self.current_brush == "square":
                self.canvas.create_rectangle(self.last_x - self.brush_size, self.last_y - self.brush_size, self.last_x + self.brush_size, self.last_y + self.brush_size, fill=self.current_color, outline=self.current_color)
                self.draw.rectangle([self.last_x - self.brush_size, self.last_y - self.brush_size, self.last_x + self.brush_size, self.last_y + self.brush_size], fill=self.current_color)
            elif self.current_brush == "line":
                self.canvas.create_line(self.last_x, self.last_y, x, y, fill=self.current_color, width=self.brush_size)
                self.draw.line([self.last_x, self.last_y, x, y], fill=self.current_color, width=self.brush_size)
            self.last_x, self.last_y = x, y
        self.update_canvas_image()

    def stop_draw(self, event):
        self.drawing = False

    def set_brush(self):
        self.current_brush = self.brush_var.get()

    def choose_color(self):
        self.current_color = colorchooser.askcolor()[1]

    def undo(self):
        if self.history:
            self.image = self.history.pop()
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas_image()

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)
        self.update_canvas_image()

    def save_image(self):
        try:
            file_path = filedialog.asksaveasfilename(initialdir=DEFAULT_SAVE_DIR, defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if file_path:
                self.image.save(file_path)
                logging.info(f"Image saved to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save image: {e}")
            messagebox.showerror("Save Error", f"Failed to save image: {e}")

    def load_image(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
            if file_path:
                loaded_image = Image.open(file_path)
                self.image.paste(loaded_image)
                self.update_canvas_image()
                logging.info(f"Image loaded from {file_path}")
        except Exception as e:
            logging.error(f"Failed to load image: {e}")
            messagebox.showerror("Load Error", f"Failed to load image: {e}")

    def add_text(self):
        text = simpledialog.askstring("Input", "Enter text:")
        if text:
            x, y = self.last_x, self.last_y
            self.canvas.create_text(x, y, text=text, fill=self.current_color, font=("Arial", self.brush_size))
            self.draw.text((x, y), text, fill=self.current_color, font=None, anchor=None)
        self.update_canvas_image()

    def update_canvas_image(self):
        self.canvas_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas_image)

if __name__ == "__main__":
    app = NanoHWApp()
    app.mainloop()
