# People Flow Tracker - Multi-Object Tracking (Suggestions Only)
# Summary:
#   Count entries, exits, and dwell time in zones using detection + tracking.
# Why it matters:
#   Useful for occupancy analytics and queue monitoring.
#
# Suggested components:
#   - Pretrained detector (e.g., YOLO) feeding a tracker (DeepSORT or ByteTrack).
#   - Virtual lines or polygon zones drawn on the frame for counting.
#   - Track IDs: overlay each person ID; compute direction across lines.
#   - Dwell time: start a timer when a track enters a zone; stop on exit.
#   - Outputs: JSON summary per hour (entries, exits, avg dwell), plus per-frame CSV.
#   - UI: live video with counts; history chart of entries per minute.
#   - Privacy: face blur toggle; storage retention control.
#
# Stretch ideas:
#   - Heatmap of presence over time.
#   - Basic anomaly alerts (sudden spikes in occupancy).
#
# Notes:
#   Make thresholds (confidence, NMS, tracker buffer) editable via a sidebar/config.
