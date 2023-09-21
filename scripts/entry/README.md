# scripts/entry

This script is used for generation of the cloudformation entry-stack.
The entry-stack is an adapter for the main stack for taking in a blob
representing the totality of CloudFormation parameters and presenting
those parameters for the etnry stack.

## Usage ⚡


### Setup

#### Install Required Packages

```
python3 -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt

```

#### Stage Main Tempalte

Stage in `input/main.yaml`


### Run Script

From command line: python3 `python3 generate-entry-stack.py`

Generated entry stack in `output/entry.yaml`


## What's Here? 👀


```
.
├── app.py
├── input
│   ├── boilerplate.yaml
│   ├── config.json
│   ├── demo
│   ├── main.yaml
│   └── test
├── output
│   ├── entry.json
│   └── entry.yaml
├── requirements.txt
└── run.py
```




