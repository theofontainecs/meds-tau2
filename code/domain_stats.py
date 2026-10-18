"""Statistiques descriptives des domaines de tau2-bench (sans appel LLM, coût nul).

Lit directement les fichiers du sous-module third_party/tau2-bench et produit :
  - results/domain_stats.json : toutes les statistiques
  - report/rapport1/tables/*.tex : tableaux inclus dans le rapport

Usage : python code/domain_stats.py
"""

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAU2 = ROOT / "third_party" / "tau2-bench"
DATA = TAU2 / "data" / "tau2" / "domains"
SRC = TAU2 / "src" / "tau2" / "domains"
TABLES = ROOT / "report" / "rapport1" / "tables"
RESULTS = ROOT / "results"

DOMAINS = ["mock", "airline", "retail", "telecom", "banking_knowledge"]
DEFAULT_REWARD_BASIS = ("DB", "COMMUNICATE")
POLICY_FILES = {"telecom": ["main_policy.md", "tech_support_manual.md"]}

TOOL_RE = re.compile(r"@is_tool\(ToolType\.(\w+)\)\s*\n\s*def (\w+)")


def count_tools(path: Path) -> Counter:
    if not path.exists():
        return Counter()
    return Counter(kind for kind, _ in TOOL_RE.findall(path.read_text(encoding="utf-8")))


def policy_words(domain: str) -> int | None:
    files = POLICY_FILES.get(domain, ["policy.md"])
    paths = [DATA / domain / f for f in files if (DATA / domain / f).exists()]
    if not paths:
        return None
    return sum(len(p.read_text(encoding="utf-8").split()) for p in paths)


def write_tool_names(domain: str) -> set[str]:
    names = set()
    for f in ("tools.py", "user_tools.py"):
        path = SRC / domain / f
        if path.exists():
            names |= {n for k, n in TOOL_RE.findall(path.read_text(encoding="utf-8")) if k == "WRITE"}
    return names


def passive_agent_passes(crit: dict, basis: tuple, writes: set[str]) -> bool:
    """Un agent qui n'appelle aucun outil d'écriture et ne communique rien obtient-il 1 ?"""
    actions = crit.get("actions") or []
    checks = {
        "DB": not any(a["name"] in writes for a in actions),
        "COMMUNICATE": not crit.get("communicate_info"),
        "NL_ASSERTION": not crit.get("nl_assertions"),
        "ENV_ASSERTION": not crit.get("env_assertions"),
        "ACTION": not actions,
    }
    return all(checks[b] for b in basis)


def domain_stats(domain: str) -> dict:
    tasks = json.loads((DATA / domain / "tasks.json").read_text(encoding="utf-8"))
    split_file = DATA / domain / "split_tasks.json"
    splits = json.loads(split_file.read_text(encoding="utf-8")) if split_file.exists() else {}
    n_tasks_file = len(tasks)
    # Le split "base" est l'ensemble d'évaluation par défaut (telecom.json en contient 2285)
    if "base" in splits:
        base_ids = set(splits["base"])
        tasks = [t for t in tasks if t["id"] in base_ids]

    writes = write_tool_names(domain)
    reward_bases, n_actions, n_communicate, n_nl = Counter(), [], [], []
    n_llm_judged = n_no_write = n_passive = 0
    for t in tasks:
        crit = t.get("evaluation_criteria") or {}
        basis = tuple(crit.get("reward_basis") or DEFAULT_REWARD_BASIS)
        reward_bases["+".join(basis)] += 1
        # NL_ASSERTION ne pèse que si la liste d'assertions est non vide
        if "NL_ASSERTION" in basis and crit.get("nl_assertions"):
            n_llm_judged += 1
        actions = crit.get("actions") or []
        n_actions.append(len(actions))
        n_no_write += not any(a["name"] in writes for a in actions)
        n_passive += passive_agent_passes(crit, basis, writes)
        n_communicate.append(len(crit.get("communicate_info") or []))
        n_nl.append(len(crit.get("nl_assertions") or []))

    agent_tools = count_tools(SRC / domain / "tools.py")
    user_tools = count_tools(SRC / domain / "user_tools.py")

    return {
        "n_tasks_file": n_tasks_file,
        "n_tasks": len(tasks),
        "tasks_llm_judged": n_llm_judged,
        "splits": {k: len(v) for k, v in splits.items()},
        "agent_tools": dict(agent_tools),
        "n_agent_tools": sum(agent_tools.values()),
        "n_user_tools": sum(user_tools.values()),
        "policy_words": policy_words(domain),
        "reward_basis": dict(reward_bases),
        "mean_gold_actions": round(sum(n_actions) / len(n_actions), 2),
        "max_gold_actions": max(n_actions),
        "tasks_without_gold_actions": sum(1 for n in n_actions if n == 0),
        "tasks_without_gold_write": n_no_write,
        "tasks_passed_by_passive_agent": n_passive,
        "tasks_with_communicate_info": sum(1 for n in n_communicate if n > 0),
        "tasks_with_nl_assertions": sum(1 for n in n_nl if n > 0),
    }


def tex_table(stats: dict) -> str:
    def fmt(v):
        return "--" if v is None else str(v)

    rows = []
    for d in DOMAINS:
        s = stats[d]
        rows.append(
            " & ".join([
                r"\texttt{" + d.replace("_", r"\_") + "}",
                str(s["n_tasks"]),
                str(s["n_agent_tools"]),
                f'{s["agent_tools"].get("READ", 0)}/{s["agent_tools"].get("WRITE", 0)}',
                str(s["n_user_tools"]),
                fmt(s["policy_words"]),
                str(s["mean_gold_actions"]),
                str(s["tasks_without_gold_write"]),
                f'{s["tasks_passed_by_passive_agent"]} ({100 * s["tasks_passed_by_passive_agent"] / s["n_tasks"]:.0f}\\,\\%)',
                ", ".join(f"{k.replace('_', r'\_').replace('+', r'+\allowbreak ')}~({v})" for k, v in s["reward_basis"].items()),
            ]) + r" \\"
        )
    return "\n".join([
        r"\begin{tabular}{lrrrrrrrr>{\raggedright\arraybackslash}p{4.6cm}}",
        r"\toprule",
        r"Domaine & Tâches & Outils & R/W & Outils & Mots & Actions & Gold sans & Réussies par & \texttt{reward\_basis} (nb tâches) \\",
        r" & & agent & & user & politique & gold moy. & écriture & agent passif & \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ])


def main() -> None:
    commit = subprocess.run(
        ["git", "-C", str(TAU2), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    stats = {d: domain_stats(d) for d in DOMAINS}
    RESULTS.mkdir(exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    (RESULTS / "domain_stats.json").write_text(
        json.dumps({"tau2_commit": commit, "domains": stats}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (TABLES / "domains.tex").write_text(
        f"% Généré par code/domain_stats.py (tau2-bench @ {commit}) -- ne pas éditer à la main\n"
        + tex_table(stats) + "\n",
        encoding="utf-8",
    )
    for d in DOMAINS:
        print(d, json.dumps(stats[d], ensure_ascii=False))


if __name__ == "__main__":
    main()
