import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

HORIZONTAL_LABELS = ["AW", "PW", "LC", "GC"]
VERTICAL_LABELS = ["HB", "MB", "LB", "Antrum", "Angle"]

def get_all_image_files(image_dir):
    return sorted([f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

def load_all_labels(label_json_path):
    if os.path.exists(label_json_path):
        with open(label_json_path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
    return {}

def save_label_json(label_json_path, filename, vertical, horizontal):
    labels = load_all_labels(label_json_path)
    status = "checked" if vertical and horizontal else "skipped"
    labels[filename] = {
        "vertical_labels": vertical,
        "horizontal_labels": horizontal,
        "status": status
    }
    with open(label_json_path, "w") as f:
        json.dump(labels, f, indent=2)

def load_label_json(label_json_path, filename):
    labels = load_all_labels(label_json_path)
    entry = labels.get(filename)
    if entry:
        vert = entry.get("vertical_labels", [])
        horiz = entry.get("horizontal_labels", [])
        if vert and horiz:
            status = "checked"
        elif not vert and not horiz:
            status = "unchecked"
        else:
            status = "skipped"
        return vert, horiz, status
    else:
        return [], [], "unchecked"

class LabelTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Labeling Tool")
        self.geometry("550x700")

        # Initial empty values
        self.image_dir = None
        self.label_json_path = None
        self.source_folder_name = ""
        self.all_files = []
        self.labels_dict = {}
        self.current_idx = 0
        self.current_filename = None
        self.horiz_vars = [tk.BooleanVar() for _ in HORIZONTAL_LABELS]
        self.vert_vars = [tk.BooleanVar() for _ in VERTICAL_LABELS]

        # Upload Button
        self.create_upload_menu()

        # GUI Elements
        self.create_widgets()

        # Key bindings
        self.key_label_map = {
            'h': ('vertical', 'HB'),
            'm': ('vertical', 'MB'),
            'b': ('vertical', 'LB'),
            'y': ('vertical', 'Antrum'),
            'u': ('vertical', 'Angle'),
            'a': ('horizontal', 'AW'),
            'p': ('horizontal', 'PW'),
            'l': ('horizontal', 'LC'),
            'g': ('horizontal', 'GC'),
        }

        for key in self.key_label_map:
            self.bind(key, self.toggle_label)
            self.bind(key.upper(), self.toggle_label)

        self.bind("s", lambda e: self.save_and_next())
        self.bind("S", lambda e: self.save_and_next())
        self.bind("n", lambda e: self.skip_and_next())
        self.bind("N", lambda e: self.skip_and_next())
        self.bind("r", lambda e: self.prev_image())
        self.bind("R", lambda e: self.prev_image())

    def create_upload_menu(self):
        top_frame = tk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        upload_btn = tk.Button(top_frame, text="Upload", command=self.select_folder,
                               font=("Arial", 9), bg="#f0f0f0", relief="raised", width=6)
        upload_btn.pack(side=tk.RIGHT, padx=10, pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder Containing Images")
        if not folder:
            return
        self.image_dir = folder
        self.label_json_path = os.path.join(self.image_dir, "labels.json")
        self.source_folder_name = os.path.basename(os.path.normpath(self.image_dir))
        self.all_files = get_all_image_files(self.image_dir)
        self.labels_dict = load_all_labels(self.label_json_path)
        self.current_idx = self.find_first_unchecked()
        if self.current_idx is None:
            messagebox.showinfo("All Done", "All images are labeled/skipped!\nYou can review/edit any image.")
            self.current_idx = len(self.all_files) - 1 if self.all_files else 0
        self.current_filename = self.all_files[self.current_idx] if self.all_files else None
        self.load_image()

    def find_first_unchecked(self):
        for idx, fname in enumerate(self.all_files):
            _, _, status = load_label_json(self.label_json_path, fname)
            if status == "unchecked":
                return idx
        return len(self.all_files) - 1 if self.all_files else None

    def create_widgets(self):
        self.canvas = tk.Canvas(self, width=500, height=500, highlightthickness=0, bg="lightgray")
        self.canvas.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.vert_frame = tk.Frame(self, bd=2, relief="groove", padx=5, pady=5)
        self.vert_frame.grid(row=2, column=0, columnspan=2, pady=(15, 2), sticky="ew")
        tk.Label(self.vert_frame, text="Vertical Labels:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.vert_checks = [tk.Checkbutton(self.vert_frame, text=label, variable=self.vert_vars[i], font=("Arial", 10)).pack(side=tk.LEFT, padx=3) for i, label in enumerate(VERTICAL_LABELS)]

        self.horiz_frame = tk.Frame(self, bd=2, relief="groove", padx=5, pady=5)
        self.horiz_frame.grid(row=3, column=0, columnspan=2, pady=(2, 15), sticky="ew")
        tk.Label(self.horiz_frame, text="Horizontal Labels:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.horiz_checks = [tk.Checkbutton(self.horiz_frame, text=label, variable=self.horiz_vars[i], font=("Arial", 10)).pack(side=tk.LEFT, padx=3) for i, label in enumerate(HORIZONTAL_LABELS)]

        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(self.button_frame, text="Save & Next (S)", width=18, command=self.save_and_next, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(self.button_frame, text="Skip (N)", width=12, command=self.skip_and_next, bg="#FFC107", fg="black", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(self.button_frame, text="Previous (R)", width=12, command=self.prev_image, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

    def clear_checks(self):
        for var in self.horiz_vars:
            var.set(False)
        for var in self.vert_vars:
            var.set(False)

    def set_checks(self, vert, horiz):
        for i, label in enumerate(HORIZONTAL_LABELS):
            self.horiz_vars[i].set(label in horiz)
        for i, label in enumerate(VERTICAL_LABELS):
            self.vert_vars[i].set(label in vert)

    def load_image(self):
        if not self.all_files or self.current_filename is None:
            messagebox.showinfo("Done", "No more images to label!")
            return

        img_path = os.path.join(self.image_dir, self.current_filename)
        try:
            img = Image.open(img_path)
            img.thumbnail((500, 500))
            self.tkimg = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            canvas_width = int(self.canvas['width'])
            canvas_height = int(self.canvas['height'])
            x = canvas_width // 2
            y = canvas_height // 2
            self.canvas.create_image(x, y, image=self.tkimg, anchor='center')

            # Display folder name
            self.canvas.create_text(canvas_width // 2, 20,
                                    text=f"Area: {self.source_folder_name}",
                                    fill="blue", font=("Arial", 14, "bold"))

            vert, horiz, status = load_label_json(self.label_json_path, self.current_filename)
            self.clear_checks()
            self.set_checks(vert, horiz)
            self.title(f"Image {self.current_idx + 1}/{len(self.all_files)}: {self.current_filename}   [{status.upper()}]")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load {img_path}.\n\n{e}")

    def get_selected_labels(self):
        horiz = [label for var, label in zip(self.horiz_vars, HORIZONTAL_LABELS) if var.get()]
        vert = [label for var, label in zip(self.vert_vars, VERTICAL_LABELS) if var.get()]
        return horiz, vert

    def _save_current_labels(self, horiz, vert):
        if not horiz or not vert:
            messagebox.showwarning("Validation Needed", "Select at least one horizontal and one vertical label to save!")
            return False
        save_label_json(self.label_json_path, self.current_filename, vert, horiz)
        self.labels_dict = load_all_labels(self.label_json_path)
        return True

    def _prompt_and_handle_unsaved_changes(self):
        current_horiz, current_vert = self.get_selected_labels()
        prev_vert, prev_horiz, _ = load_label_json(self.label_json_path, self.current_filename)
        if set(current_horiz) == set(prev_horiz) and set(current_vert) == set(prev_vert):
            return True
        response = messagebox.askyesnocancel("Unsaved Changes", f"Labels for {self.current_filename} have changed. Save before moving?")
        if response is True:
            return self._save_current_labels(current_horiz, current_vert)
        elif response is False:
            return True
        else:
            return False

    def save_and_next(self):
        horiz, vert = self.get_selected_labels()
        if not self._save_current_labels(horiz, vert):
            return
        if self.current_idx + 1 < len(self.all_files):
            self.current_idx += 1
            self.current_filename = self.all_files[self.current_idx]
        self.load_image()

    def skip_and_next(self):
        if not self._prompt_and_handle_unsaved_changes():
            return
        _, _, current_status = load_label_json(self.label_json_path, self.current_filename)
        if current_status == "unchecked":
            save_label_json(self.label_json_path, self.current_filename, [], [])
            self.labels_dict = load_all_labels(self.label_json_path)
        if self.current_idx + 1 < len(self.all_files):
            self.current_idx += 1
            self.current_filename = self.all_files[self.current_idx]
            self.load_image()
        else:
            messagebox.showinfo("All Done", "All images are labeled/skipped!")
            self.load_image()

    def prev_image(self):
        if not self._prompt_and_handle_unsaved_changes():
            return
        if self.current_idx > 0:
            self.current_idx -= 1
            self.current_filename = self.all_files[self.current_idx]
            self.load_image()

    def toggle_label(self, event):
        key = event.char.lower()
        if key not in self.key_label_map:
            return
        label_type, label_value = self.key_label_map[key]
        if label_type == 'vertical':
            for i, label in enumerate(VERTICAL_LABELS):
                if label == label_value:
                    self.vert_vars[i].set(not self.vert_vars[i].get())
                    break
        elif label_type == 'horizontal':
            for i, label in enumerate(HORIZONTAL_LABELS):
                if label == label_value:
                    self.horiz_vars[i].set(not self.horiz_vars[i].get())
                    break

if __name__ == "__main__":
    app = LabelTool()
    app.mainloop()
