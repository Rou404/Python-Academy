# Smart Shelf Monitor - Object Detection (Suggestions Only)
# Summary:
#   Build an app that counts products on a shelf and alerts when stock is low.
# Why it matters:
#   Widely used in retail and small stores for restocking decisions.
#
# Suggested components:
#   - Pretrained detector (e.g., YOLO small model) for boxes and classes.
#   - ROI selection per shelf (draw rectangles once and save to a JSON/YAML config).
#   - Per-class counting and low-stock thresholds (configurable per shelf).
#   - Simple UI (Streamlit/Gradio) showing the camera feed and current counts.
#   - Logging: CSV or JSON lines with timestamp, per-class counts, and alerts.
#   - Performance: show FPS and p95 latency overlay; option to downscale input.
#   - Privacy: avoid saving raw frames; keep only annotated screenshots for bugs.
#
# Stretch ideas:
#   - Multi-camera support; aggregate counts across shelves.
#   - Alert channels: desktop notification, email, or webhook.
#   - Basic re-identification across adjacent cameras (optional).
#
# Notes:
#   Keep a README with setup steps and shortcuts. Provide a sample video for offline testing.
