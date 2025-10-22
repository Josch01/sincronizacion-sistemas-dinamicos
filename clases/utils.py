import os
import json
import numpy as np
import pandas as pd

def parse_info_file(info_path):
    with open(info_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [ln.strip("\n\r") for ln in lines]

    resta_name = None
    a_start = None
    a_stop = None
    a_step = None
    eq_code_lines = []
    init_dict = {}

    in_equations = False
    in_init = False

    for line in lines:
        if line.startswith("Resta:"):
            resta_name = line.split(":",1)[-1].strip()
        elif line.startswith("a_start ="):
            a_start = float(line.split("=")[-1])
        elif line.startswith("a_stop ="):
            a_stop = float(line.split("=")[-1])
        elif line.startswith("a_step ="):
            a_step = float(line.split("=")[-1])

        elif line.lower().startswith("ecuaciones:"):
            in_equations = True
            in_init = False
            continue
        elif line.lower().startswith("condicionesiniciales:"):
            in_equations = False
            in_init = True
            continue
        else:
            if in_equations:
                eq_code_lines.append(line)
            elif in_init:
                parts = line.split("=")
                if len(parts)==2:
                    var_name = parts[0].strip()
                    val = float(parts[1])
                    init_dict[var_name] = val

    eq_code = "\n".join(eq_code_lines)
    init_values = [
        init_dict.get("x1",0.0),
        init_dict.get("y1",0.0),
        init_dict.get("z1",0.0),
        init_dict.get("x2",0.0),
        init_dict.get("y2",0.0),
        init_dict.get("z2",0.0)
    ]

    return resta_name, a_start, a_stop, a_step, eq_code, init_values

def parse_resta_name(resta_name):
    mapping = {"x1":0,"y1":1,"z1":2,"x2":3,"y2":4,"z2":5}
    r = resta_name.replace(" ","")
    if "-" not in r:
        return (0,3)
    varA, varB = r.split("-",1)
    idxA = mapping.get(varA, 0)
    idxB = mapping.get(varB, 3)
    return (idxA, idxB)
