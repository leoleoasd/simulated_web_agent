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

rang = range(0, 60)


def run_cmd(i):
    if os.path.exists(f"data/simulation/virtual customer {i}"):
        os.system(f"rm -rf data/simulation/virtual\ customer\ {i}")
    # don't launch all at the same time
    global last_run
    with lock:
        while time.time() - last_run < 5:
            # print(last_run, time.time())
            time.sleep(1)
        last_run = time.time()
    print("\nRunning virtual customer", i)
    os.makedirs(f"data/simulation/virtual customer {i}", exist_ok=True)
    stdout = open(f"data/simulation/virtual customer {i}/stdout.txt", "w")
    stderr = open(f"data/simulation/virtual customer {i}/stderr.txt", "w")
    subprocess.run(
        [
            "python3",
            "-m",
            "simulated_web_agent.main.batch",
            "--persona",
            f"data/personas/json/virtual customer {i}.json",
            "--output",
            f"data/simulation/virtual customer {i}",
        ],
        stdout=stdout,
        stderr=stderr,
    )


if __name__ == "__main__":
    needed_ids = []
    for i in rang:
        if not os.path.exists(f"data/simulation/virtual customer {i}/result.json"):
            needed_ids.append(i)
    thread_map(run_cmd, needed_ids, max_workers=10)
