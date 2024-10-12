# cmd = python3 -m simulated_web_agent.webshop.batch --persona personas/$i.json --output output/$i;
import os
import random
import subprocess
import threading
import time

from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map

# parallel, max 5


lock = threading.Lock()
last_run = time.time()

rang = range(0, 2)


def run_cmd(i):
    if os.path.exists(f"new_data/simulation/virtual customer {i}"):
        os.system(f"rm -rf new_data/simulation/virtual\ customer\ {i}")
    # don't launch all at the same time
    global last_run
    with lock:
        while time.time() - last_run < 1:
            # print(last_run, time.time())
            time.sleep(1)
        last_run = time.time()
    print("\nRunning virtual customer", i)
    os.makedirs(f"new_data/simulation/virtual customer {i}", exist_ok=True)
    stdout = open(f"new_data/simulation/virtual customer {i}/stdout.txt", "w")
    stderr = open(f"new_data/simulation/virtual customer {i}/stderr.txt", "w")
    if i % 2 == 0:
        cookie = "SEARCH_SES_CATEGORY_DEFECT_REDUCTION_STOP:T1"
    else:
        cookie = "SEARCH_SES_CATEGORY_DEFECT_REDUCTION_STOP:C"
    subprocess.run(
        [
            "python3",
            "-m",
            "simulated_web_agent.main.batch",
            "--persona",
            f"new_data/personas/json/virtual customer {i}.json",
            "--output",
            f"new_data/simulation/virtual customer {i}",
            "--cookie",
            "experiment",
            cookie,
        ],
        stdout=stdout,
        stderr=stderr,
    )


if __name__ == "__main__":
    needed_ids = []
    for i in rang:
        if not os.path.exists(f"new_data/simulation/virtual customer {i}/result.json"):
            needed_ids.append(i)
    thread_map(run_cmd, needed_ids, max_workers=10)
