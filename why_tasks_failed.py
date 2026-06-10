import json 
from collections import Counter 
import matplotlib.pyplot as plt
import os
from PIL import Image, ImageDraw, ImageFont
os.makedirs("statistics", exist_ok=True)
# ---------- Load Data ----------
with open("task_tracker.json", "r") as file:
    data = json.load(file)

# ---------- Select Task ----------
print("\nYour Tasks:")
for i, item in enumerate(data[1:-1], start=1):
    print(f"{i}. {item['task_name']}")

task_name = input("\nEnter task name: ").strip().lower()

task = None
for item in data:
    if item.get("task_name", "").lower() == task_name:
        task = item
        break

if not task:
    print("Task not found.")
    exit()

# ---------- Data ----------
reasons = task.get("reason_for_not_completed", [])
dates = task.get("task_missed_date", [])

num_records = max(len(reasons), len(dates))

# Dynamic height
height = max(650, 350 + num_records * 100)
width = 1000

# ---------- Create Image ----------
img = Image.new("RGB", (width, height), (245, 247, 250))
draw = ImageDraw.Draw(img)

# ---------- Fonts ----------
try:
    title_font = ImageFont.truetype("arialbd.ttf", 50)
    subtitle_font = ImageFont.truetype("arialbd.ttf", 32)
    text_font = ImageFont.truetype("arial.ttf", 28)
    small_font = ImageFont.truetype("arial.ttf", 24)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# ---------- Header ----------
draw.rectangle([0, 0, width, 100], fill=(41, 128, 185))

draw.text(
    (30, 20),
    "TASK MISSED REPORT",
    fill="white",
    font=title_font
)

# ---------- Task Details ----------
y = 140

draw.text(
    (40, y),
    f"Task: {task['task_name']}",
    fill=(44, 62, 80),
    font=subtitle_font
)

y += 50

draw.text(
    (40, y),
    f"Time: {task['start_time']} - {task['end_time']}",
    fill=(80, 80, 80),
    font=text_font
)

y += 40

draw.text(
    (40, y),
    f"Current Streak: {task['task_streak']} days",
    fill=(39, 174, 96),
    font=text_font
)

y += 70

draw.text(
    (40, y),
    "Missed Records",
    fill=(192, 57, 43),
    font=subtitle_font
)

y += 60

# ---------- Missed Records ----------
if num_records:

    for i in range(num_records):

        reason = reasons[i] if i < len(reasons) else "N/A"
        date = dates[i] if i < len(dates) else "N/A"

        draw.rounded_rectangle(
            [50, y - 10, width - 50, y + 70],
            radius=15,
            fill=(255, 255, 255),
            outline=(220, 220, 220),
            width=2
        )

        draw.text(
            (70, y),
            f"Reason: {reason}",
            fill=(60, 60, 60),
            font=text_font
        )

        draw.text(
            (550, y),
            f"Date: {date}",
            fill=(100, 100, 100),
            font=small_font
        )

        y += 100

else:
    draw.text(
        (70, y),
        "No missed records 🎉",
        fill=(39, 174, 96),
        font=text_font
    )
    y += 60

# ---------- Footer ----------
footer_y = height - 70

draw.line(
    (30, footer_y, width - 30, footer_y),
    fill=(200, 200, 200),
    width=2
)

draw.text(
    (40, footer_y + 10),
    f"Total Misses: {num_records}",
    fill=(100, 100, 100),
    font=text_font
)

# ---------- Save ----------
os.makedirs("statistics", exist_ok=True)

filename = f"{task['task_name']}_report.png"
filepath = os.path.join("statistics", filename)

img.save(filepath)

print(f"\nSaved as {filepath}")
# Count reasons
reason_counter = Counter()

for item in data:
    if "reason_for_not_completed" in item:
        reason_counter.update(item["reason_for_not_completed"])

# Data for plotting
reasons = list(reason_counter.keys())
counts = list(reason_counter.values())

# Plot
plt.figure(figsize=(8, 5))
plt.bar(reasons, counts)

plt.title("Reasons for Not Completing Tasks")
plt.xlabel("Reason")
plt.ylabel("Frequency")
plt.tight_layout()

plt.savefig("statistics/task_failure_reasons.png") 