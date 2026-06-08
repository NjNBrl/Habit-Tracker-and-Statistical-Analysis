import matplotlib.pyplot as plt
import json
with open("task_tracker.json","r") as file:
    data = json.load(file)

plt.plot(range(1,len(data[0]["dates"])+1),data[-1]["efficient"] , marker="o")
plt.xlabel("Day")
plt.ylabel("Efficiency")
plt.title("Daily Efficiency Trend")
plt.grid(True)
plt.savefig("statistics/daily_efficiecny.png") 

#-----------------------------------------------------------------------------
import json
import matplotlib.pyplot as plt


tasks = []
streaks = []

for item in data:
    if "task_name" in item:
        tasks.append(item["task_name"])
        streaks.append(item["task_streak"])

# Plot bar graph
plt.figure(figsize=(8, 5))
plt.bar(tasks, streaks)

plt.title("Task vs Streak")
plt.xlabel("Tasks")
plt.ylabel("Streak")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig("statistics/streak.png") 

#---------------------------------------------------------