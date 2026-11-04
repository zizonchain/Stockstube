"""Print the top-30 and deep-cut tables for MORNING_REPORT.md."""
import json, os
d = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'data', 'ranked.json')))
print('| # | Title | People | Communities | Years |\n|---|---|---|---|---|')
for k, x in enumerate(d[:30]): print(f"| {k+1} | {x['t']} | {x['r']} | {x['n']} | {x['ny']} |")
print('\n**Top 20 deep cuts** (3+ people, under 250k views, ranked by people / log10(views))\n\n| # | Title | People |\n|---|---|---|')
for k, x in enumerate(sorted([x for x in d if x['r'] >= 3 and x['v'] < 250000], key=lambda x: -x['dc'])[:20]): print(f"| {k+1} | {x['t']} | {x['r']} |")
