import glob
import json
import re
from os import popen
from pathlib import Path

basepath = Path("output")
for processing in range(60):
    # processing = 29
    if (basepath / f"{processing}/result.json").exists():
        # get latest page_{}.html
        pages = glob.glob(str(basepath / f"{processing}/page_*.html"))
        # sort by number
        pages = sorted(pages, key=lambda x: int(x.split("_")[-1].split(".")[0]))
        # print(pages)
        with open(pages[-1], "r") as f:
            price = re.search(r"\$(\d+(?:\.\d+)?)", f.read()).group(1)
            print(price)
            price = float(price)
        with open(basepath / f"{processing}/result.json", "r") as f:
            data = json.load(f)
            data["price"] = price
        with open(basepath / f"{processing}/result.json", "w") as f:
            json.dump(data, f)
