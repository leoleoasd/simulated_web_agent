import os
import subprocess

for i in range(0, 60):
    # if result.json exists, replay the action
    if os.path.exists(f"output/{i}/action_trace.txt") and not os.path.exists(
        f"output/{i}/replay.mp4"
    ):
        print(f"Replaying output/{i}")
        # python3 -m simulated_web_agent.webshop.replay --trace_dir output/7 --output-video a.mp4
        subprocess.run(
            # f"python3 -m simulated_web_agent.webshop.replay --trace_dir output/{i} --output-video output/{i}/replay.mp4"
            [
                "python3",
                "-m",
                "simulated_web_agent.webshop.replay",
                "--trace_dir",
                f"output/{i}",
                "--output-video",
                f"output/{i}/replay.mp4",
            ]
        )
        print(f"Replay saved to output/{i}/replay.mp4")
