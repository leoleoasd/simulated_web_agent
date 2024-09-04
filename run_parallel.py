# cmd = python3 -m simulated_web_agent.webshop.batch --persona personas/$i.json --output output/$i;
import os
import random
import subprocess
import time

from tqdm.contrib.concurrent import process_map  # or thread_map

# parallel, max 5


rang = range(0, 60)


def run_cmd(i):
    # sleep random seconds
    time.sleep(random.randint(0, 20))
    os.makedirs(f"output/{i}", exist_ok=True)
    stdout = open(f"output/{i}/stdout.txt", "w")
    stderr = open(f"output/{i}/stderr.txt", "w")
    subprocess.run(
        [
            "python3",
            "-m",
            "simulated_web_agent.webshop.batch",
            "--persona",
            f"personas/{i}.json",
            "--output",
            f"output/{i}",
        ],
        stdout=stdout,
        stderr=stderr,
    )


if __name__ == "__main__":
    process_map(run_cmd, rang, max_workers=5)
