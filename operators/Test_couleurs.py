import colorsys
import tkinter as tk


def show_colors(rgb_tuples):
    root = tk.Tk()
    root.title("Visualisation couleurs")
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, width=600, height=300)
    canvas.grid(row=0, column=0, sticky="nsew")

    scroll_bar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_bar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scroll_bar.set)

    box_height = 15
    x0, x1 = 10, 300

    for i, (r, g, b) in enumerate(rgb_tuples):
        hex_color = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

        y0 = 10 + i * (box_height + 5)
        y1 = y0 + box_height

        canvas.create_rectangle(x0, y0, x1, y1, fill=hex_color, outline="black")
        canvas.create_text(350, (y0 + y1) // 2, text=i)

    canvas.configure(scrollregion=canvas.bbox("all"))

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    root.mainloop()


if __name__ == "__main__":
    N = 50  # Nombre de couleurs
    hsv_tuples = [(n / N, 0.8, 0.9) for n in range(N)]
    rgb_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    show_colors(rgb_tuples)
