# Projet MEDS — Évaluation des agents avec τ²-bench

Projet du cours MEDS, partie « méthodologie projet », O. Schwander.
Le but n'est pas d'obtenir le meilleur score sur [τ²-bench](https://github.com/sierra-research/tau2-bench) : il s'agit d'étudier **ce que le benchmark mesure vraiment**, puis de concevoir un protocole d'évaluation rigoureux et de l'appliquer à 2 ou 3 agents simples.

Sujet : <https://schwander.isir.upmc.fr/enseignement/m2mind_meds/projet.html>

**Groupe :** _Théo Fontaine_, _Jean-Léo Serrano_

| Rendu | Échéance | Contenu |
|---|---|---|
| Rapport 1 | mi-octobre 2026 | Prise en main, domaines/tâches/outils, biais et limites |
| Rapport 2 | mi-novembre 2026 | + questions de recherche, protocole, expériences proposées |
| Rapport final | fin novembre 2026 | + résultats, analyse, pistes d'amélioration, limites, conclusion |


## Organisation du dépôt

```
report/
  refs.bib                 bibliographie commune
  rapport1/                main.tex + sections/ + tables/ (générées)
code/
  domain_stats.py          statistiques des domaines (sans LLM, coût nul)
results/                   sorties des scripts et des simulations, versionnées
third_party/tau2-bench/    sous-module, figé au commit b7ea907 (v1.0.1)
```

Le sous-module fixe la version exacte du benchmark : tous les chiffres du rapport s'y rapportent.
Pour changer de version, il faut le faire **explicitement** (`git -C third_party/tau2-bench checkout <commit>`, puis commit) et régénérer les tables.

## Installation

```bash
git clone -c core.longpaths=true --recurse-submodules https://github.com/theofontainecs/meds-tau2.git   # longpaths : requis sous Windows
cd meds-tau2/third_party/tau2-bench
uv sync
uv pip install websockets   # contournement : la version core importe un module vocal non déclaré
uv run --no-sync tau2 --help
```

Clé API dans `third_party/tau2-bench/.env`, fichier ignoré par git :

```
OPENAI_BASE_URL=https://litellm.isir.upmc.fr
OPENAI_API_KEY=sk-XXXX
```

## Utilisation

```bash
# Statistiques des domaines -> results/domain_stats.json et report/rapport1/tables/domains.tex
python code/domain_stats.py

# Simulation à bas coût (domaine mock)
cd third_party/tau2-bench
uv run --no-sync tau2 run --domain mock --agent-llm <modele> --user-llm <modele> --num-trials 1 --num-tasks 2
uv run --no-sync tau2 view
```

Les simulations sont écrites dans `third_party/tau2-bench/data/simulations/`, qui est ignoré par git. **Copiez dans `results/` celles que vous citez dans un rapport**, en notant la commande exacte utilisée.


## Compiler le rapport

```bash
cd report/rapport1
latexmk main.tex           # PDF produit dans build/main.pdf
```
