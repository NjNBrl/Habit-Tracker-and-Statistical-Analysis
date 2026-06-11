import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
os.makedirs('statistics', exist_ok=True)
with open ('task_tracker.json','r') as file:
    data = json.load(file)
sns.kdeplot(data[0]['wake_up_times'],fill = True)
plt.xlabel('Day')
plt.ylabel('Frequency')
plt.title('Wake up times')
plt.grid(True)
plt.savefig('statistics/wake_up_times.png')