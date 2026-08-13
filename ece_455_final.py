import heapq
import math
import sys
from decimal import Decimal
from fractions import Fraction


def parse_tasks(filename):
    raw_tasks = []
    max_decimals = 0

    with open(filename, "r") as file_handle:
        for line in file_handle:
            stripped = line.strip()
            if not stripped:
                continue

            row = []
            for value in stripped.split(","):
                decimal_value = Decimal(value.strip())
                row.append(decimal_value)
                max_decimals = max(max_decimals, -decimal_value.as_tuple().exponent)
            raw_tasks.append(row)

    scale = 10 ** max_decimals
    tasks = [[int(value * scale) for value in task] for task in raw_tasks]

    quantum = 0
    for task in tasks:
        for value in task:
            quantum = math.gcd(quantum, value)

    if quantum > 1:
        tasks = [[value // quantum for value in task] for task in tasks]

    return tasks


def clean_ready_heap(ready_heap, jobs):
    while ready_heap and not jobs[ready_heap[0][2]]["active"]:
        heapq.heappop(ready_heap)


def clean_deadline_heap(deadline_heap, jobs):
    while deadline_heap and not jobs[deadline_heap[0][1]]["active"]:
        heapq.heappop(deadline_heap)


def release_jobs(current_time, hyperperiod, task_states, release_heap, ready_heap, deadline_heap, jobs, counters):
    while release_heap and release_heap[0][0] == current_time:
        _, task_index = heapq.heappop(release_heap)
        task = task_states[task_index]
        job_id = counters["job_id"]
        enqueue_order = counters["enqueue_order"]
        counters["job_id"] += 1
        counters["enqueue_order"] += 1

        jobs[job_id] = {
            "task_index": task_index,
            "remaining": task["execution"],
            "deadline": current_time + task["deadline"],
            "active": True,
        }
        heapq.heappush(ready_heap, (task["period"], enqueue_order, job_id))
        heapq.heappush(deadline_heap, (current_time + task["deadline"], job_id))

        next_release = current_time + task["period"]
        if next_release < hyperperiod:
            heapq.heappush(release_heap, (next_release, task_index))


def simulate_rm(tasks):
    hyperperiod = math.lcm(*[task[1] for task in tasks])
    task_states = [
        {
            "execution": execution,
            "period": period,
            "deadline": deadline,
            "preemptions": 0,
        }
        for execution, period, deadline in tasks
    ]

    release_heap = [(0, task_index) for task_index in range(len(task_states))]
    heapq.heapify(release_heap)

    ready_heap = []
    deadline_heap = []
    jobs = {}
    counters = {"job_id": 0, "enqueue_order": 0}

    current_time = 0
    release_jobs(
        current_time,
        hyperperiod,
        task_states,
        release_heap,
        ready_heap,
        deadline_heap,
        jobs,
        counters,
    )

    while current_time < hyperperiod:
        clean_ready_heap(ready_heap, jobs)
        clean_deadline_heap(deadline_heap, jobs)

        if not ready_heap:
            if not release_heap:
                break

            current_time = release_heap[0][0]
            if current_time >= hyperperiod:
                break

            release_jobs(
                current_time,
                hyperperiod,
                task_states,
                release_heap,
                ready_heap,
                deadline_heap,
                jobs,
                counters,
            )
            continue

        running_job_id = ready_heap[0][2]
        running_job = jobs[running_job_id]

        next_release_time = release_heap[0][0] if release_heap else hyperperiod
        next_deadline_time = deadline_heap[0][0] if deadline_heap else hyperperiod
        completion_time = current_time + running_job["remaining"]
        next_event_time = min(next_release_time, next_deadline_time, completion_time, hyperperiod)

        running_job["remaining"] -= next_event_time - current_time
        current_time = next_event_time

        if running_job["remaining"] == 0:
            running_job["active"] = False

        if current_time == hyperperiod:
            break

        clean_deadline_heap(deadline_heap, jobs)
        if deadline_heap and deadline_heap[0][0] <= current_time:
            return False, []

        if release_heap and release_heap[0][0] == current_time:
            was_preemptable = running_job["active"]
            previous_running_id = running_job_id if was_preemptable else None

            release_jobs(
                current_time,
                hyperperiod,
                task_states,
                release_heap,
                ready_heap,
                deadline_heap,
                jobs,
                counters,
            )
            clean_ready_heap(ready_heap, jobs)

            if previous_running_id is not None and ready_heap and ready_heap[0][2] != previous_running_id:
                task_index = jobs[previous_running_id]["task_index"]
                task_states[task_index]["preemptions"] += 1

    return True, [task["preemptions"] for task in task_states]


if __name__ == "__main__":
    filename = sys.argv[1]
    tasks = parse_tasks(filename)

    utilization = sum(Fraction(task[0], task[1]) for task in tasks)
    if utilization > 1:
        print("0")
        print("")
        raise SystemExit

    schedulable, preemptions = simulate_rm(tasks)
    if not schedulable:
        print("0")
        print("")
        raise SystemExit

    print("1")
    print(",".join(str(count) for count in preemptions))
        
        

        
