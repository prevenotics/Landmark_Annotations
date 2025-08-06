# Landmark Annotation Tool

A simple GUI tool to label medical images with **vertical** and **horizontal** stomach landmarks.  
Labels are saved in a `labels.json` file in the selected image folder.

---

## 🔧 Features

- Intuitive image annotation using checkboxes or keyboard shortcuts
- Tracks and saves label status (`checked`, `skipped`, `unchecked`)
- Automatically resumes from where you left off
- Works with `.png`, `.jpg`, `.jpeg` images

---

## 🖥️ How to Use

```bash
git clone https://github.com/prevenotics/Landmark_Annotations.git
cd Landmark_Annotations
pip install Pillow
pip install tkinter
python Label.py
## ⌨️ Shortcut Keys

| Key | Label Type | Label/Action |
|-----|------------|--------------|
| H   | Vertical   | HB           |
| M   | Vertical   | MB           |
| B   | Vertical   | LB           |
| Y   | Vertical   | Antrum       |
| U   | Vertical   | Angle        |
| A   | Horizontal | AW           |
| P   | Horizontal | PW           |
| L   | Horizontal | LC           |
| G   | Horizontal | GC           |
| S   | Action     | Save & Next  |
| N   | Action     | Skip         |
| R   | Action     | Previous     |

Output Format
