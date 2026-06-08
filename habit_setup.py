"""
Visually appealing Habit Plan chart -> PNG
Drop-in replacement for the PIL block in your habit tracker.
"""
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ----------------------------------------------------------------------------
# Font loading with graceful fallback (so it never crashes on a missing font)
# ----------------------------------------------------------------------------
FONT_DIRS = [
    "C:/Windows/Fonts/"                    # Windows
]
FONT_FILES = {
    "bold":    ["Poppins-Bold.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"],
    "medium":  ["Poppins-Medium.ttf", "arial.ttf", "DejaVuSans.ttf"],
    "regular": ["Poppins-Regular.ttf", "arial.ttf", "DejaVuSans.ttf"],
    "light":   ["Poppins-Light.ttf", "arial.ttf", "DejaVuSans.ttf"],
}

def load_font(weight, size):
    import os
    for name in FONT_FILES[weight]:
        # absolute / cwd
        if os.path.exists(name):
            return ImageFont.truetype(name, size)
        for d in FONT_DIRS:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    # last resort, also try the fallback dejavu path
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
BG_TOP      = (244, 241, 250)
BG_BOTTOM   = (250, 246, 240)
PANEL       = (255, 255, 255)
INK         = (43, 43, 58)
MUTED       = (138, 138, 160)
ACCENT      = (91, 75, 214)      # indigo
ACCENT_SOFT = (238, 235, 252)    # indigo tint
WAKE        = (245, 158, 35)     # sunrise amber
WAKE_SOFT   = (255, 243, 224)
SLEEP       = (59, 74, 140)      # night indigo
SLEEP_SOFT  = (231, 235, 248)
LINE        = (228, 226, 238)

HEAD_A = (91, 75, 214)           # header gradient start
HEAD_B = (150, 99, 232)          # header gradient end


def vgradient(size, top, bottom):
    w, h = size
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        grad.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return grad.resize((w, h))


def hgradient(size, left, right):
    w, h = size
    grad = Image.new("RGB", (w, 1))
    for x in range(w):
        t = x / max(1, w - 1)
        grad.putpixel((x, 0), tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3)))
    return grad.resize((w, h))


def soft_shadow(base, box, radius, blur=22, dy=12, alpha=55):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0 + dy, x1, y1 + dy], radius=radius, fill=(40, 35, 80, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def draw_sun(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    import math
    for k in range(8):
        a = math.pi * 2 * k / 8
        x1 = cx + math.cos(a) * (r + 5)
        y1 = cy + math.sin(a) * (r + 5)
        x2 = cx + math.cos(a) * (r + 12)
        y2 = cy + math.sin(a) * (r + 12)
        d.line([x1, y1, x2, y2], fill=color, width=4)


def draw_moon(d, cx, cy, r, color, bg):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.ellipse([cx - r + 8, cy - r - 4, cx + r + 8, cy + r - 4], fill=bg)


# ----------------------------------------------------------------------------
# Main generator
# ----------------------------------------------------------------------------
def generate_habit_chart(num_of_days, start_date, end, wake_up_time,
                         sleep_time, tasks, time_range, out_path="habit_plan.png"):
    W = 1200
    pad = 50
    px0, px1 = pad, W - pad           # panel x bounds
    header_h = 250
    row_h = 132
    list_top_gap = 56
    footer_h = 130

    n_rows = len(tasks) + 2           # wake + tasks + sleep
    list_top = pad + header_h + list_top_gap
    panel_bottom = list_top + n_rows * row_h + footer_h
    H = panel_bottom + pad

    # ---- canvas + background ----
    base = Image.new("RGB", (W, H), BG_TOP)
    base.paste(vgradient((W, H), BG_TOP, BG_BOTTOM), (0, 0))
    base = base.convert("RGBA")
    d = ImageDraw.Draw(base)

    # ---- panel with shadow ----
    soft_shadow(base, (px0, pad, px1, panel_bottom), radius=34, blur=28, dy=16, alpha=60)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([px0, pad, px1, panel_bottom], radius=34, fill=PANEL)

    # ---- header gradient band (rounded top corners only) ----
    hb = (px1 - px0, header_h)
    head = hgradient(hb, HEAD_A, HEAD_B).convert("RGBA")
    mask = Image.new("L", hb, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, hb[0], hb[1]], radius=34,
                                           corners=(True, True, False, False), fill=255)
    base.paste(head, (px0, pad), mask)
    d = ImageDraw.Draw(base)

    f_title = load_font("bold", 56)
    f_kicker = load_font("medium", 24)
    f_badge = load_font("medium", 22)
    f_badge_b = load_font("bold", 26)

    cx = W // 2
    d.text((cx, pad + 58), "HABIT BLUEPRINT", font=f_kicker, fill=(255, 255, 255),
           anchor="mm")
    title = f"{num_of_days}-Day Plan"
    d.text((cx, pad + 110), title, font=f_title, fill=(255, 255, 255), anchor="mm")

    # date badges inside header
    def date_badge(center_x, label, value):
        bw, bh = 210, 66
        x0 = center_x - bw // 2
        y0 = pad + 160
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=18, fill="white")
        d.text((center_x, y0 + 19), label, font=load_font("medium", 17),
               fill=(150, 140, 210), anchor="mm")
        d.text((center_x, y0 + 45), value, font=f_badge_b, fill=ACCENT, anchor="mm")

    date_badge(cx - 230, "START", str(start_date))
    date_badge(cx, "DURATION", f"{num_of_days} days")
    date_badge(cx + 230, "FINISH", str(end))

    # ---- timeline list ----
    f_task = load_font("medium", 30)
    f_time = load_font("bold", 22)
    f_num = load_font("bold", 26)

    x_line = px0 + 110          # vertical timeline x
    x_card0 = x_line + 70
    x_card1 = px1 - 50

    # rows data: (kind, label, time_str)
    rows = []
    rows.append(("wake", "Wake up", wake_up_time))
    for i, task in enumerate(tasks):
        s = time_range[i * 2]
        e = time_range[1+ i * 2]
        rows.append(("task", task, f"{s}  -  {e}"))
    rows.append(("sleep", "Sleep", sleep_time))

    # continuous timeline spine
    spine_top = list_top + row_h // 2
    spine_bot = list_top + (n_rows - 1) * row_h + row_h // 2
    d.line([x_line, spine_top, x_line, spine_bot], fill=LINE, width=4)

    for idx, (kind, label, tstr) in enumerate(rows):
        cy = list_top + idx * row_h + row_h // 2

        # card
        card_top = cy - 48
        card_bot = cy + 48
        soft_shadow(base, (x_card0, card_top, x_card1, card_bot),
                    radius=22, blur=14, dy=7, alpha=32)
        d = ImageDraw.Draw(base)
        d.rounded_rectangle([x_card0, card_top, x_card1, card_bot],
                            radius=22, fill=PANEL, outline=LINE, width=1)

        if kind == "wake":
            acc, soft = WAKE, WAKE_SOFT
        elif kind == "sleep":
            acc, soft = SLEEP, SLEEP_SOFT
        else:
            acc, soft = ACCENT, ACCENT_SOFT

        # left accent strip on the card
        d.rounded_rectangle([x_card0, card_top, x_card0 + 10, card_bot],
                            radius=5, fill=acc)

        # timeline badge
        br = 28
        d.ellipse([x_line - br, cy - br, x_line + br, cy + br], fill=acc)
        if kind == "wake":
            draw_sun(d, x_line, cy, 12, (255, 255, 255))
        elif kind == "sleep":
            draw_moon(d, x_line, cy, 13, (255, 255, 255), acc)
        else:
            d.text((x_line, cy), str(idx), font=f_num, fill="white", anchor="mm")

        # connector from badge to card
        d.line([x_line + br, cy, x_card0, cy], fill=LINE, width=4)

        # time pill
        pill_x0 = x_card0 + 32
        pill_y0 = cy - 19
        pill_w = 250
        d.rounded_rectangle([pill_x0, pill_y0, pill_x0 + pill_w, pill_y0 + 38],
                            radius=19, fill=soft)
        d.text((pill_x0 + pill_w // 2, cy), tstr, font=f_time, fill=acc, anchor="mm")

        # task label
        label_x = pill_x0 + pill_w + 30
        # truncate very long labels to fit
        max_w = x_card1 - label_x - 24
        text = label
        while d.textlength(text, font=f_task) > max_w and len(text) > 4:
            text = text[:-2]
        if text != label:
            text = text.rstrip() + "..."
        d.text((label_x, cy), text, font=f_task, fill=INK, anchor="lm")

    # ---- footer ----
    fy = panel_bottom - footer_h + 20
    d.line([px0 + 50, fy, px1 - 50, fy], fill=LINE, width=2)
    f_foot_b = load_font("bold", 30)
    f_foot = load_font("regular", 22)
    d.text((cx, fy + 42), "Show up every day. The streak is the reward.",
           font=f_foot_b, fill=ACCENT, anchor="mm")
    d.text((cx, fy + 78), f"Begin on {start_date}  -  finish strong on {end}",
           font=f_foot, fill=MUTED, anchor="mm")

    base.convert("RGB").save(out_path, "PNG")
    return out_path


# ----------------------------------------------------------------------------
# Demo with sample data (mirrors what your script collects)
# ----------------------------------------------------------------------------
from datetime import datetime, timedelta

def get_habit_data():

    print("How many days do you want to perform these habit? (21, 90, 180)")
    num_of_days = int(input("Days: "))

    start_date = input("Enter start date (YYYY-MM-DD): ")
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = start + timedelta(days=num_of_days)

    print(f"Your journey will end on: {end}")

    print("\nEnter time in HH:MM AM/PM format")

    wake_up_time = input("Wake up time: ")

    tasks = []
    time_range = []

    while True:

        task = input("\nEnter task name: ")
        tasks.append(task)

        task_start = input("Start time: ")
        task_end = input("End time: ")

        time_range.append(task_start)
        time_range.append(task_end)

        more = input("Add another task? (Y/N): ").upper()

        if more == "N":
            break

    sleep_time = input("\nSleep time: ")

    return (
        num_of_days,
        start_date,
        start,
        end,
        wake_up_time,
        sleep_time,
        tasks,
        time_range
    )

def save_data(
        wake_up_time,
        num_of_days,
        start_date,
        end,
        tasks,
        time_range,):

    data = []
    data.append({
        "wake_up_time" : wake_up_time,
        "dates": [],
        "task_tracked_day" : " ",
        "num_of_days" : num_of_days,
        "start_date" : str(start_date),
        "end_date" : str(end),
        "wake_up_on_time_streak" : 0,
        "sleep_on_time_streak" : 0
    })
    for index in range (0,len(tasks)):
        data.append({
            "task_name" :  tasks[index],
            "start_time" : time_range[2*index],
            "end_time" : time_range[2*index + 1],
            "task_missed_date" : [],
            "task_streak" :0, 
            "reason_for_not_completed": [],
            "task_tracked": 0
        }) 
    data.append({
        "efficient_num" : 0,
        "efficient" : []
    })    
    with open("task_tracker.json", "w") as file :
        json.dump(data,file)    



if __name__ == "__main__":

    (
        num_of_days,
        start_date,
        start,
        end,
        wake_up_time,
        sleep_time,
        tasks,
        time_range
    ) = get_habit_data()


    out = generate_habit_chart(
        num_of_days,
        start_date,
        end,
        wake_up_time,
        sleep_time,
        tasks,
        time_range,
        out_path="habit_plan.png"
    )

    print("Saved:", out)
save_data(
        wake_up_time,
        num_of_days,
        start_date,
        end,
        tasks,
        time_range,
)