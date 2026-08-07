import sys
import math

if __name__ == "__main__":
    filename = sys.argv[1]
    tasks = []
    with open(filename, 'r') as f:
        for line in f:
            values = [int(float(v) * 1000) for v in line.strip().split(',')]
            tasks.append(values)

    # e p d curr_exec curr_dl
    print(f"tasks: {tasks}")

    hyperperiod = math.lcm(*[t[1] for t in tasks])
    print(f"hyperperiod: {hyperperiod}")

    # check utilization
    utilization = 0
    for task in tasks:
        utilization += task[0]/task[1]
    if utilization > 1:
        print("0")
        exit()

    queue = list(tasks)
    for task in queue:
        task.append(0)
        task.append(task[2])
        task.append(0)
    cooldown = []

    last_running = None

    for i in range(hyperperiod):
        #print(f"queue:{queue}")
        shortest_idx = 0
        if len(queue) > 0:
            for q in range(len(queue)):
                if queue[q][1] < queue[shortest_idx][1]:
                    shortest_idx = q
            sp = queue[shortest_idx]
            if last_running is not None and sp is not last_running and last_running in queue:
                last_running[5] += 1
            last_running = sp
            sp[3] += 1
            if sp[3] >= sp[0]:
                sp[3] = 0       # reset current executed time
                sp[4] = (i // sp[1] + 1) * sp[1] + sp[2]      # set deadline to next period + deadline
                cooldown.append(sp)
                queue.pop(shortest_idx)

            # check for overrun deadlines
            for task in queue:
                if task[4] <= i:
                    print("0")
                    exit()

        # check for tasks past cooldowns
        for task in cooldown[:]:
            if (i+1)%task[1] == 0:
                cooldown.remove(task)
                task[4] = i+1 + task[2]
                queue.append(task)

    print("1")
    print(",".join(str(t[5]) for t in tasks))
        
        

        
