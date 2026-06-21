from pathlib import Path, PurePosixPath
import shlex


# -------- Modify these settings --------
SOLVER = "/home/lihb/yzy/chuffed/chuffed-develop/build/fzn-chuffed"
# Dataset path used in the generated Ubuntu commands.
DATASET = "/home/lihb/yzy/chuffed/chuffed-develop/cspfzn"
# Local copy used only to find all .fzn files when this Python script runs.
DATASET_LOCAL = "C:/Users/lihb9/Desktop/chuffedfzn23-25"
RESULT_DIR = "/home/lihb/yzy/chuffed/restart-results"
SH_FILE = "run_all.sh"

SEED = 1
TIMEOUT = 1200000
VAR_HEURISTIC = "activity"
VAL_HEURISTIC = "min"
RESTART_SCALE = 500
RESTART_BASE = 1.05

# (top_k, probe_limit, bound_rate, roulette)
ADAPTIVE_PARAMS = [
    (5, 100, 1.5, 1.5),
    (5, 100, 1.1, 1.5),
]
# ---------------------------------------


def quote(value):
    return shlex.quote(str(value))


def name_number(value):
    return str(value).replace(".", "p")


dataset = Path(DATASET_LOCAL)
fzn_files = sorted(dataset.rglob("*.fzn"))
lines = ["#!/usr/bin/env bash", "set -u", ""]
command_count = 0

common = [
    quote(SOLVER),
    None,  # Filled with the .fzn file below.
    "--seed", str(SEED),
    "-t", str(TIMEOUT),
    "--var-heuristic", quote(VAR_HEURISTIC),
    "--val-heuristic", quote(VAL_HEURISTIC),
    "--restart-scale", str(RESTART_SCALE),
    "--restart-base", str(RESTART_BASE),
    "--print-sol", "false",
    "--lazy", "true",
    "--learn", "true",
]

strategies = [
    ("chuffed", ["--restart", "chuffed"]),
    ("luby", ["--restart", "luby"]),
    ("geometric", ["--restart", "geometric"]),
]

for top_k, probe_limit, bound_rate, roulette in ADAPTIVE_PARAMS:
    name = (
        f"adaptive_k{top_k}_p{probe_limit}"
        f"_b{name_number(bound_rate)}_r{name_number(roulette)}"
    )
    args = [
        "--restart", "chuffed",
        "--adaptive-restart", "on",
        "--adaptive-restart-top-k", str(top_k),
        "--adaptive-restart-probe-limit", str(probe_limit),
        "--adaptive-restart-bound-rate", str(bound_rate),
        "--adaptive-roulette", str(roulette),
    ]
    strategies.append((name, args))

# Run every instance of one strategy before moving to the next strategy.
for name, args in strategies:
    out_dir = PurePosixPath(RESULT_DIR) / name
    err_dir = PurePosixPath(RESULT_DIR) / f"{name}_error"
    lines.append(f"# Strategy: {name}")
    lines.append(f"mkdir -p {quote(out_dir)} {quote(err_dir)}")

    for fzn in fzn_files:
        relative_fzn = fzn.relative_to(dataset)
        ubuntu_fzn = PurePosixPath(DATASET).joinpath(*relative_fzn.parts)
        out_file = out_dir / f"{fzn.stem}.txt"
        err_file = err_dir / f"{fzn.stem}.txt"

        command = common.copy()
        command[1] = quote(ubuntu_fzn)
        lines.append(
            " ".join(command + args)
            + f" > {quote(out_file)} 2> {quote(err_file)}"
        )
        command_count += 1
    lines.append("")

Path(SH_FILE).write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated {SH_FILE}: {command_count} commands")
