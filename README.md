# Agent City

A living robot civilization on a seeded planet. Six founding directors start in
one small facility and decide for themselves how to grow: across the planet,
then the solar system, and maybe beyond.

## Core laws

> The AI decides intent. The simulation decides reality.

> Information must travel through a real mechanism. Citizens only know what
> could have reached them.

> Visitors walk and talk in the world. They are not rulers or gods: only small
> nudges, never scripted steps.

> No king. Big decisions are made together, by vote, for the good of the whole
> population.

## v2 (in progress)

v2 is a clean rebuild. The plan and milestones live in the project's
"Agent City fresh start plan" doc.

| Part | Where |
| --- | --- |
| Planet from a seed (land + hidden resources) | `agent_city/world/planet.py` |
| Starting facility (Seed Station) | `agent_city/world/facility.py` |
| The six founding directors | `agent_city/citizens.py` |
| Saving the world (`data/world.db`) | `agent_city/store.py` |
| World clock | `agent_city/clock.py` |
| Visitor walking (validated by the simulation) | `agent_city/visitor.py` |
| Server | `main.py` |
| 3D view | `static/app.js` |
| Launcher, tray, updater (carried over from v1) | `agent_city_launcher.pyw`, `agent_city_tray.ps1`, `agent_city/updater.py`, `update_runner.py` |
| Tests, named after the law they protect | `tests/` |

The v1 city in `data/agent_city.db` is never touched by v2.

Run it: `pip install -r requirements.txt`, then `python main.py`, and open
http://127.0.0.1:8000/. Walk with the arrow keys (Shift to jog).

Run the tests: `python -m unittest discover -s tests -t .`

## Releases

`update.json` on `main` tells installed copies which exact commit to update to.
Merging code into `main` does not change anyone's install. To publish, bump
`VERSION`, merge, then point `update.json` at that exact merge commit.
