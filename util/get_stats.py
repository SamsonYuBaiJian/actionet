import os
from collections import defaultdict
import re
import statistics
import numpy as np
import csv
import re

def get_total_number_of_tasks(data_dir):
    """
    Summary:
        Print statistics for total number of tasks and task instances.
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    tasks = []
    task_instances = 0

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]

            if '+' in ' '.join(task_list):
                task_instances += 1

                # Check if there are repeated tasks
                done = False
                for t in tasks:
                    # If task value in dictionaries is already the shortest and is repeated
                    if len(t) <= len(task_name):
                        length = len(t)
                        if task_name[:length] == t:
                            done = True
                            break
                    # If task value in dictionaries is not the shortest and is repeated
                    else:
                        length = len(task_name)
                        if t[:length] == task_name:
                            tasks.append(task_name)
                            tasks.remove(t)
                            done = True
                            break
                if not done:
                    tasks.append(task_name)

    print("Total number of tasks: " + str(len(tasks)))
    print("Total number of tasks (instances): " + str(task_instances))


def get_number_of_tasks_by_category(data_dir):
    """
    Summary:
        Print statistics for total number of tasks and task instances by category.
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    tasks_by_category = defaultdict(lambda: [])
    task_instances_by_category = defaultdict(lambda: 0)

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]
            floor_plan = task_list[1]
            floor_plan = int(re.findall('\d+', floor_plan)[0])

            if floor_plan < 200:
                scene = 'kitchen'
            elif floor_plan > 200 and floor_plan < 300:
                scene = 'living_room'
            elif floor_plan > 300 and floor_plan < 400:
                scene = 'bedroom'
            else:
                scene = 'bathroom'

            if '+' in ' '.join(task_list):
                task_instances_by_category[scene] += 1

                # Check if there are repeated tasks
                done = False
                for t in tasks_by_category[scene]:
                    # If task value in dictionaries is already the shortest and is repeated
                    if len(t) <= len(task_name):
                        length = len(t)
                        if task_name[:length] == t:
                            done = True
                            break
                    # If task value in dictionaries is not the shortest and is repeated
                    else:
                        length = len(task_name)
                        if t[:length] == task_name:
                            tasks_by_category[scene].append(task_name)
                            tasks_by_category[scene].remove(t)
                            done = True
                            break
                if not done:
                    tasks_by_category[scene].append(task_name)

    tasks_by_category_count = defaultdict(lambda: 0)
    for s in tasks_by_category.keys():
        tasks_by_category_count[s] = len(tasks_by_category[s])
    test = []
    for s in tasks_by_category.keys():
        test.extend(tasks_by_category[s])

    # if len(test) == len(set(test)):
    #     print("GGGG")
    # else:
    #     print(set([x for x in test if test.count(x) > 1]))

    print("Number of tasks by category: " + str(tasks_by_category_count.items()))
    print("Number of tasks by category (instances): " + str(task_instances_by_category.items()))


def get_total_stats(data_dir):
    """
    Summary:
        Print max, min, median and standard deviation for all tasks.
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    task_steps = []

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            # task_name = task_list[0]
            floor_plan = task_list[1]
            floor_plan = int(re.findall('\d+', floor_plan)[0])

            if '+' in ' '.join(task_list):
                task_steps.append(len(task_list) - 2)

    max_step = max(task_steps)
    min_step = min(task_steps)
    median_step = statistics.mean(task_steps)
    sd = np.std(task_steps)

    print("Max step for total: " + str(max_step))
    print("Min step for total: " + str(min_step))
    print("Mean step for total: " + str(median_step))
    print("SD for total: " + str(sd))


def get_category_stats(data_dir):
    """
    Summary:
        Print statistics for max, min, median and SD for each category.
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    task_steps_by_category = defaultdict(lambda: [])

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]
            floor_plan = task_list[1]
            floor_plan = int(re.findall('\d+', floor_plan)[0])

            if floor_plan < 200:
                scene = 'kitchen'
            elif floor_plan > 200 and floor_plan < 300:
                scene = 'living_room'
            elif floor_plan > 300 and floor_plan < 400:
                scene = 'bedroom'
            else:
                scene = 'bathroom'

            if '+' in ' '.join(task_list):
                task_steps_by_category[scene].append(len(task_list) - 2)

    max_dict = defaultdict(lambda: 0)
    min_dict = defaultdict(lambda: 0)
    median_dict = defaultdict(lambda: 0)
    sd_dict = defaultdict(lambda: 0)

    for s in task_steps_by_category.keys():
        max_dict[s] = max(task_steps_by_category[s])
        min_dict[s] = min(task_steps_by_category[s])
        median_dict[s] = statistics.mean(task_steps_by_category[s])
        sd_dict[s] = np.std(task_steps_by_category[s])

    print("Max step by category: " + str(max_dict.items()))
    print("Min step by category: " + str(min_dict.items()))
    print("Mean step by category: " + str(median_dict.items()))
    print("SD by category: " + str(sd_dict.items()))


def get_task_complexity(data_dir):
    """
    Summary:
        Print tasks categorised by complexity (i.e. number of steps).
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    tasks = []
    task_count = defaultdict(lambda: 0)
    step_count = defaultdict(lambda: 0)
    avg_step = defaultdict(lambda: 0)

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]

            # Check if there are repeated tasks
            if '+' in ' '.join(task_list):  
                done = False
                for t in tasks:
                    # If task value in dictionaries is already the shortest and is repeated
                    if len(t) <= len(task_name):
                        length = len(t)
                        if task_name[:length] == t:
                            task_count[t] += 1
                            step_count[t] += len(task_list) - 2
                            done = True
                            break
                    # If task value in dictionaries is not the shortest and is repeated
                    else:
                        length = len(task_name)
                        if t[:length] == task_name:
                            task_count[task_name] += 1
                            step_count[task_name] += len(task_list) - 2
                            del task_count[t]
                            del step_count[t]
                            done = True
                            break
                if not done:
                    task_count[task_name] += 1
                    step_count[task_name] += len(task_list) - 2

    for t in task_count.keys():
        avg_step[t] = step_count[t] / task_count[t]
    task_sorted_by_steps = [k for k, v in sorted(avg_step.items(), key=lambda item: item[1])]
    task_by_complexity = defaultdict(lambda:[])
    task_by_complexity['easy'] = task_sorted_by_steps[0:21]
    task_by_complexity['moderate'] = task_sorted_by_steps[21:42]
    task_by_complexity['complex'] = task_sorted_by_steps[42:63]

    print("Tasks sorted by complexity: " + str(task_by_complexity.items()))

    task_by_category_count = defaultdict(lambda: defaultdict(lambda: 0))
    step_by_category_count = defaultdict(lambda: defaultdict(lambda: 0))
    avg_step_by_category = defaultdict(lambda: defaultdict(lambda: 0))
    task_sorted_by_steps_and_category = defaultdict(lambda: [])
    task_by_category_and_complexity = defaultdict(lambda: defaultdict(lambda:[]))

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]
            floor_plan = task_list[1]
            floor_plan = int(re.findall('\d+', floor_plan)[0])

            if floor_plan < 200:
                scene = 'kitchen'
            elif floor_plan > 200 and floor_plan < 300:
                scene = 'living_room'
            elif floor_plan > 300 and floor_plan < 400:
                scene = 'bedroom'
            else:
                scene = 'bathroom'

            if '+' in ' '.join(task_list):
                # Check if there are repeated tasks
                done = False
                for t in tasks:
                    # If task value in dictionaries is already the shortest and is repeated
                    if len(t) <= len(task_name):
                        length = len(t)
                        if task_name[:length] == t:
                            task_by_category_count[scene][t] += 1
                            step_by_category_count[scene][t] += len(task_list) - 2
                            done = True
                            break
                    # If task value in dictionaries is not the shortest and is repeated
                    else:
                        length = len(task_name)
                        if t[:length] == task_name:
                            task_by_category_count[scene][task_name] += 1
                            step_by_category_count[scene][task_name] += len(task_list) - 2
                            del task_by_category_count[scene][t]
                            del step_by_category_count[scene][t]
                            done = True
                            break
                if not done:
                    task_by_category_count[scene][task_name] += 1
                    step_by_category_count[scene][task_name] += len(task_list) - 2

    for s in task_by_category_count.keys():
        for t in task_by_category_count[s].keys():
            avg_step_by_category[s][t] = step_by_category_count[s][t] / task_by_category_count[s][t]
    for s in avg_step_by_category.keys():
        task_sorted_by_steps_and_category[s] = [k for k, v in sorted(avg_step_by_category[s].items(), key=lambda item: item[1])]
        length = len(task_sorted_by_steps_and_category[s])
        size = round(length / 3)
        task_by_category_and_complexity[s]['easy'] = task_sorted_by_steps_and_category[s][0:size]
        task_by_category_and_complexity[s]['moderate'] = task_sorted_by_steps_and_category[s][size:size * 2]
        task_by_category_and_complexity[s]['complex'] = task_sorted_by_steps_and_category[s][size * 2:length]

    print("Tasks sorted by complexity and category: " + str(task_by_category_and_complexity.items()))


def get_middle_level_total_and_category_mean(desc_dir):
    """
    Summary:
        Print mean of middle level tasks for categories and all.
    Args:
        desc_dir (string): Path of the folder containing the descriptions of the tasks for all human annotation instances.
    """
    task_desc_by_category = defaultdict(lambda: {})
    task_desc = {}
    mean_mid = 0
    mean_mid_by_category = defaultdict(lambda: 0)
    mean_mid_by_category_count = defaultdict(lambda: 0)
    mean_mid_by_category_value = defaultdict(lambda: 0)
                    
    for task in desc_dir:
        with open(task, encoding='cp1252') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    row = [d.replace('and', ',') for d in row]
                    task_desc[row[0].split('_')[0]] = len(re.split('[,.]',row[1]))
                    task = row[0].split('_')[0] + '_' + row[0].split('_')[1]
                    task_desc_by_category[task] = row[1]
                    line_count += 1

    cnt = 0
    length = 0
    for k,v in task_desc.items():
        cnt += 1
        length += v
    mean_mid = length/cnt

    for k,v in task_desc_by_category.items():
        floor_plan = int(k.split('_')[1])

        if floor_plan < 200:
            scene = 'kitchen'
        elif floor_plan > 200 and floor_plan < 300:
            scene = 'living_room'
        elif floor_plan > 300 and floor_plan < 400:
            scene = 'bedroom'
        else:
            scene = 'bathroom'

        mean_mid_by_category_count[scene] += 1
        mean_mid_by_category_value[scene] += len(re.split('[,.]',v))

    for k in mean_mid_by_category_count.keys():
        mean_mid_by_category[k] = mean_mid_by_category_value[k] / mean_mid_by_category_count[k]

    print("Mean of mid level tasks: " + str(mean_mid))
    print("Mean of mid level tasks by category: " + str(mean_mid_by_category.items()))


def get_instances_by_category_and_task(data_dir):
    """
    Summary:
        Print the number of instances by category and task.
    Args:
        data_dir (string): Path of the human annotated dataset.
    """
    instances_by_category_and_task = defaultdict(lambda: defaultdict(lambda: 0))

    for num_dir in data_dir:
        user_tasks = [os.path.join(num_dir, d) for d in os.listdir(num_dir) 
                    if os.path.isfile(os.path.join(num_dir, d))]
                    
        for task in user_tasks:
            with open(task) as f:
                data = f.read()

            data = data.replace('][', ',')
            data = data.replace('[','')
            data = data.replace(']','')
            data = data.replace("'", '')
            task_list =  data.split(",")

            task_name = task_list[0]
            floor_plan = task_list[1]
            floor_plan = int(re.findall('\d+', floor_plan)[0])

            if floor_plan < 200:
                scene = 'kitchen'
            elif floor_plan > 200 and floor_plan < 300:
                scene = 'living_room'
            elif floor_plan > 300 and floor_plan < 400:
                scene = 'bedroom'
            else:
                scene = 'bathroom'

            if '+' in ' '.join(task_list):
                # Check if there are repeated tasks
                done = False
                for t in instances_by_category_and_task[scene].keys():
                    # If task value in dictionaries is already the shortest and is repeated
                    if len(t) <= len(task_name):
                        length = len(t)
                        if task_name[:length] == t:
                            done = True
                            instances_by_category_and_task[scene][t] += 1
                            break
                    # If task value in dictionaries is not the shortest and is repeated
                    else:
                        length = len(task_name)
                        if t[:length] == task_name:
                            done = True
                            instances_by_category_and_task[scene][task_name] += instances_by_category_and_task[scene][t] + 1
                            del instances_by_category_and_task[scene][t]
                            break
                if not done:
                    instances_by_category_and_task[scene][task_name] += 1

    print("Number of instances by category and by task: " + str(instances_by_category_and_task.items()))


def main(actionet_path):
    """
    Summary:
        Print statistics of dataset.
    Args:
        data_dir (string): Path of the human annotated dataset.
        desc_dir (string): Path of the folder containing the descriptions of the tasks for all human annotation instances.
    """
    data_path = os.path.join(actionet_path, 'dataset')
    desc_path = os.path.join(actionet_path, 'dataset/resources/task_descriptions')
    data_dir = [os.path.join(data_path, d) for d in os.listdir(data_path) 
                        if os.path.isdir(os.path.join(data_path, d))]
    desc_dir = [os.path.join(desc_path, d) for d in os.listdir(desc_path) 
                        if os.path.isfile(os.path.join(desc_path, d))]

    get_total_number_of_tasks(data_dir)
    print('\n')
    get_number_of_tasks_by_category(data_dir)
    print('\n')
    get_total_stats(data_dir)
    print('\n')
    get_category_stats(data_dir)
    print('\n')
    get_task_complexity(data_dir)
    print('\n')
    get_middle_level_total_and_category_mean(desc_dir)
    print('\n')
    get_instances_by_category_and_task(data_dir)


if __name__ == '__main__':
    with open('./settings.txt') as f:
        txt = f.readlines()
        f.close()
    my_dict = {}
    for t in txt:
        t = t.split('=')
        my_dict[t[0]] = t[1].strip('\n')

    main(my_dict['actionet_path'])