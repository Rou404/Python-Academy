# Click-to-Segment - Interactive Segmentation (Suggestions Only)
# Summary:
#   User clicks on an object to get a precise mask, then analyze area/mean color.
# Why it matters:
#   Speeds up quick measurements and background removal tasks.
#
# Suggested components:
#   - Model: SAM/FastSAM or a YOLO segmentation model.
#   - UI: image preview + click coordinates; show the mask overlay with opacity slider.
#   - Analysis: area in pixels, mean BGR/RGB, optional perimeter.
#   - Exports: PNG mask, transparent cutout, and a measurements CSV.
#   - Batch mode: run the same parameters over a folder of images.
#
# Stretch ideas:
#   - Background removal tool with a few simple editing brushes.
#   - Drag-to-refine masks (add/remove strokes).
#
# Notes:
#   Include a help panel with short tips and hotkeys.
