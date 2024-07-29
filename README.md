# Simulated Web Agent

## Setup
1. `git clone git@github.com:princeton-nlp/WebShop.git`
2. follow [their readme step 1-6/ `setup.sh`](https://github.com/princeton-nlp/WebShop) to download data and build index。
3. `conda env create -f environment.yml -n simulated_web_agent`
4. `conda activate simulated_web_agent`
5. put your `webshop` path in `src/simulated_web_agent/env.py`
6. `pip install -e .`
7. `python3 -m simulated_web_agent.webshop.main`
