import json
with open('task_tracker.json','r') as file:
    data = json.load(file)
from datetime import date

today = date.today()
if (len(data[0]['dates'])==0):
    data[0]['dates'].append(str(today))
else:
    for item in data[0]['dates']:
        if item == str(today):
            pass
        else :
            data[0]['dates'].append(str(today))
print(f'Tracking the habit routine for : {today}')
print('You can complete your other task, close the program and comeback later as soon as task is completed')

if data[0]['task_tracked_day'] == str(today):
    pass
else:
    wake_up_time = input('Enter wake up time : ')
    if data[0]['wake_up_time'] == wake_up_time:
        data[0]['wake_up_times'].append(wake_up_time)
    for i in range(0,len(data)-2):
            data[i+1]['task_tracked'] = 0
            data[-1]['efficient_num'] = 0 
            data[0]['task_tracked_day'] = str(today)

for i in range(0,len(data)-2):
    if data[i+1]['task_tracked'] == 1:
        continue
    print(f'Task : {data[i+1]['task_name']}')
    status = input('Task completed today?(Y/N) : ')
    if status == 'Y' :
        data[i+1]['task_streak'] = data[i+1]['task_streak'] + 1
        data[-1]['efficient_num'] += 1  
    else :
        data[i+1]['task_missed_date'].append(str(today))
        reason = input('Reason for not completing task : ')
        data[i+1]['reason_for_not_completed'].append(str(reason))
    data[i+1]['task_tracked'] = 1

    with open('task_tracker.json', 'w') as file:
        json.dump(data, file, indent=4)
print(data[-1]['efficient_num'])


data[-1]['efficient'].append((data[-1]['efficient_num']*100/(len(data)-2)))
print(f'{data[-1]['efficient']}+ %')
data[0]['num_of_days'] -= 1
print(f'\033[92m{data[0]['num_of_days']} remaining\033[0m')
with open('task_tracker.json', 'w') as file:
    json.dump(data, file, indent=4)



