# Résultats

Chaque fichier cité dans un rapport est listé ici, avec la commande exacte qui l'a produit.
Toutes les simulations utilisent tau2-bench au commit `b7ea907` (sous-module).

| Fichier | Commande (lancée depuis `third_party/tau2-bench`) | Date | Coût |
|---|---|---|---|
| `domain_stats.json` | `python code/domain_stats.py` (depuis la racine du dépôt) | 2026-10-09 | 0 $ |
| `simulations/mock_first_run.json` | `uv run --no-sync tau2 run --domain mock --agent-llm openai/gpt-4.1-mini --user-llm openai/gpt-4.1-mini --task-ids create_task_1 update_task_1 --num-trials 1 --save-to mock_first_run` | 2026-10-17 | ~0.003 $ |
| `simulations/airline_task5.json` | `uv run --no-sync tau2 run --domain airline --agent-llm openai/gpt-4.1-mini --user-llm openai/gpt-4.1-mini --task-ids 5 --num-trials 1 --save-to airline_task5` | 2026-10-17 | ~0.009 $ |
| `simulations/airline_qwen3_14b_no_reasoning.json` | `tau2 run --domain airline --agent-llm .../qwen3-14b --user-llm .../qwen3-14b --num-trials 3` (LM Studio, reasoning=none) | 2026-10-17 | 0.00 $ |
| `simulations/airline_qwen3_14b_reasoning_4096.json` | `tau2 run --domain airline --agent-llm .../qwen3-14b --user-llm .../qwen3-14b --num-trials 3` (LM Studio, reasoning=4096) | 2026-10-17 | 0.00 $ |