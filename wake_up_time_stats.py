import os
import matplotlib.pyplot as plt
import json
os.makedirs("statistics")
with open ("task_tracker.json","r") as file:
    data = json.load(file)
plt.bar(data[0]["task_tracked_day"],data[0]["wake_up_on_time_streak"])
plt.xlabel("Day")
plt.ylabel("Streak")
plt.title("Woken up on time streak")
plt.grid(True)
plt.savefig("statistics/wake_up_time_check.png")