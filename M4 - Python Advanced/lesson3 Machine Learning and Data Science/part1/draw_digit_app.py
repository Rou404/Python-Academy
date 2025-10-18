"""
Draw-a-Digit App (Tkinter) — Minimal GUI to test your trained digits model.

Usage:
    1) Train and save the model first by running:  python digit_pipeline.py
       -> This creates "digits_logreg.joblib" in the current folder.
    2) Then run this app:                       python draw_digit_app.py
    3) Draw a digit (0–9) in the canvas and click Predict.

Dependencies:
    - Standard library: tkinter
    - Extra: pillow, numpy, scikit-learn, joblib
      pip install pillow numpy scikit-learn joblib

Notes:
    - The app mirrors your strokes into an internal PIL image, so it does NOT rely on screen-grab.
    - It resizes to 8x8 grayscale and scales pixel values to the 0..16 range (like sklearn's digits).
    - If the model file is missing, it will offer to auto-train a quick baseline and save it.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from PIL import Image, ImageDraw, ImageOps
import joblib

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


MODEL_PATH = "digits_logreg.joblib"
CANVAS_SIZE = 280        # drawing canvas (pixels)
BRUSH = 18               # brush radius (pixels)


def ensure_model(model_path: str = MODEL_PATH):
    """Load model+scaler bundle; if missing, offer to train a quick baseline."""
    try:
        bundle = joblib.load(model_path)
        if not isinstance(bundle, dict) or "model" not in bundle or "scaler" not in bundle:
            raise ValueError("Invalid model bundle format.")
        return bundle
    except Exception:
        res = messagebox.askyesno(
            "Model not found",
            "Trained model not found.\n\nDo you want me to train a quick baseline now?"
        )
        if not res:
            raise FileNotFoundError(f"Model bundle '{model_path}' not found.")
        # Quick training (same as in digit_pipeline.py defaults)
        X, y = load_digits(return_X_y=True)
        X = X.astype(np.float32)
        X_tr, X_te, y_tr, y_te = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        clf = LogisticRegression(max_iter=200, solver="lbfgs", multi_class="auto").fit(X_tr_s, y_tr)
        joblib.dump({"model": clf, "scaler": scaler}, model_path)
        messagebox.showinfo("Training complete", f"Saved new model to: {model_path}")
        return {"model": clf, "scaler": scaler}


class DrawDigitApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Draw a Digit (0–9) — Predict with scikit-learn")
        self.resizable(False, False)

        # Load/ensure model
        try:
            self.bundle = ensure_model(MODEL_PATH)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.destroy()
            return

        # Internal PIL image to mirror strokes (white background)
        self.img = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), color=255)
        self.draw = ImageDraw.Draw(self.img)

        # UI layout
        main = ttk.Frame(self, padding=10)
        main.grid(row=0, column=0)

        # Canvas
        self.canvas = tk.Canvas(main, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white", highlightthickness=1, highlightbackground="#bbb")
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Bindings for drawing
        self.canvas.bind("<B1-Motion>", self.on_draw)
        self.canvas.bind("<Button-1>", self.on_draw)

        # Buttons
        ttk.Button(main, text="Predict", command=self.predict).grid(row=1, column=0, pady=10, sticky="ew")
        ttk.Button(main, text="Clear", command=self.clear).grid(row=1, column=1, pady=10, sticky="ew")
        ttk.Button(main, text="Save 8x8 Preview", command=self.save_preview).grid(row=1, column=2, pady=10, sticky="ew")

        # Output label
        self.output = tk.StringVar(value="Draw a digit then click Predict")
        out_label = ttk.Label(main, textvariable=self.output, font=("Arial", 12))
        out_label.grid(row=2, column=0, columnspan=3, pady=(5,0))

        # Pen size control
        self.brush = tk.IntVar(value=BRUSH)
        ttk.Label(main, text="Brush size").grid(row=3, column=0, sticky="e", pady=(8,0))
        ttk.Spinbox(main, from_=4, to=40, textvariable=self.brush, width=5).grid(row=3, column=1, sticky="w", pady=(8,0))

    def on_draw(self, event):
        r = int(self.brush.get())
        x0, y0 = event.x - r, event.y - r
        x1, y1 = event.x + r, event.y + r
        # Draw on Tk canvas (visual)
        self.canvas.create_oval(x0, y0, x1, y1, fill="black", outline="black")
        # Mirror onto PIL image (data)
        self.draw.ellipse([x0, y0, x1, y1], fill=0)  # 0 = black on white background (255)

    def clear(self):
        self.canvas.delete("all")
        self.draw.rectangle([0, 0, CANVAS_SIZE, CANVAS_SIZE], fill=255)
        self.output.set("Canvas cleared. Draw a digit then click Predict.")

    def preprocess(self):
        """Convert the drawn image to 8x8 grayscale with values ~0..16, flattened to (1, 64)."""
        img = self.img
        small = img.resize((8, 8), Image.LANCZOS)
        small = ImageOps.invert(small)  # now ink ~255, background ~0

        arr = np.asarray(small, dtype=np.float32)
        # Scale 0..255 to 0..16 (approximate sklearn digits scale)
        arr = (arr / 255.0) * 16.0
        arr = np.clip(arr, 0.0, 16.0)
        flat = arr.reshape(1, -1)
        return flat, small

    def predict(self):
        X_flat, small = self.preprocess()
        model = self.bundle["model"]
        scaler = self.bundle["scaler"]
        X_scaled = scaler.transform(X_flat)
        pred = model.predict(X_scaled)[0]

        # Try to get probabilities if available
        try:
            proba = model.predict_proba(X_scaled)[0]
            conf = float(np.max(proba))
            self.output.set(f"Prediction: {pred}   (conf: {conf:.2f})")
        except Exception:
            self.output.set(f"Prediction: {pred}")

    def save_preview(self):
        """Save the downsampled 8x8 image as PNG to inspect what the model sees."""
        _, small = self.preprocess()
        path = "preview_8x8.png"
        small = small.resize((80, 80), Image.NEAREST)  # scale up for visibility
        small.save(path)
        messagebox.showinfo("Saved", f"Saved preview image to: {path}")


if __name__ == "__main__":
    app = DrawDigitApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        pass
