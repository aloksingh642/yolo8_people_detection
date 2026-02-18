import cv2
import os
import time
from ultralytics import YOLO
from email_alert import send_alert
from config import ALERT_THRESHOLD

model = YOLO("yolov8n.pt")

def detect_people(path):
    results = model(path)
    count = 0
    annotated = None
    for r in results:
        annotated = r.plot()
        for box in r.boxes:
            if int(box.cls[0]) == 0:
                count += 1
    output_path = f"outputs/result_{os.path.basename(path)}"
    cv2.imwrite(output_path, annotated)
    return count, output_path

def detect_video(path):
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = f"outputs/result_{os.path.basename(path)}"
    out = cv2.VideoWriter(output_path, fourcc, 20.0,
                          (int(cap.get(3)), int(cap.get(4))))
    total_count = 0
    alert_triggered = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        count = sum(1 for r in results for box in r.boxes if int(box.cls[0]) == 0)
        total_count += count
        annotated = results[0].plot()
        cv2.putText(annotated, f"People: {count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if count > ALERT_THRESHOLD and not alert_triggered:
            send_alert(count)
            alert_triggered = True
            cv2.putText(annotated, "⚠️ ALERT SENT!", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        out.write(annotated)

    cap.release()
    out.release()

    if alert_triggered:
        return total_count, "THRESHOLD_EXCEEDED"
    return total_count, output_path

# Live camera streaming
def detect_camera():
    cap = cv2.VideoCapture(0)
    total_count = 0
    alert_triggered = False
    stop_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        count = sum(1 for r in results for box in r.boxes if int(box.cls[0]) == 0)
        total_count += count
        annotated = results[0].plot()
        cv2.putText(annotated, f"People: {count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if count > ALERT_THRESHOLD and not alert_triggered:
            send_alert(count)
            alert_triggered = True
            stop_time = time.time() + 5  # wait 5 seconds more

        if alert_triggered and time.time() >= stop_time:
            break

        _, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
    # Instead of yielding HTML here, return a flag
    return total_count, alert_triggered