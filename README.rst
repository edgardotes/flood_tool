Flood Tool
==========

A lightweight flood risk assessment and visualization tool combining a Python-based processing pipeline with a static web interface for scenario exploration.

Repository Structure
--------------------

::

    flood_tool/
    ├── docs/        # Frontend (static web interface)
    └── pipeline/    # Backend processing pipeline (Python)

docs/ — Web Interface
---------------------

Contains the static files used to visualize flood scenarios:

- ``index.html`` – Main entry point  
- ``app.js`` – Application logic  
- ``style.css`` – Styling  
- ``api/`` – JSON endpoints used by the frontend  

  - ``latest.json`` – Latest system status  
  - ``sites.json`` – Available sites  

- ``scenarios/`` – Site-specific flood scenarios  

  Each site (e.g., ``morges``, ``interlaken``) includes:

  - ``scenarios.json`` – Scenario definitions  
  - Hazard & impact maps (PNG images)

pipeline/ — Processing Workflow
-------------------------------

Python modules to evaluate flood conditions, select scenarios, and generate outputs:

- ``run_all_sites.py`` – Main execution script for all sites  
- ``evaluate_sites.py`` – Core evaluation logic  
- ``select_scenario.py`` – Scenario selection framework  
- ``site_thresholds.py`` – Threshold definitions  
- ``sites_config.py`` – Site configuration  
- ``write_status.py`` – Writes outputs for the frontend  

Additional scripts:

- ``morges_select_scenario.py`` – Site-specific logic (demo/custom)  
- ``run_morges_demo.py`` – Demo execution  
- ``plot_impacts.py`` – Visualization utilities  

Workflow Overview
-----------------

1. Run the pipeline
   - Processes input data
   - Evaluates flood conditions
   - Selects appropriate scenarios

2. Generate outputs
   - JSON status files
   - Scenario selections per site

3. Visualize in frontend
   - Static interface reads outputs from ``docs/api/``
   - Displays hazard and impact maps

Usage
-----

Run full pipeline::

    python pipeline/run_all_sites.py

Run demo (Morges)::

    python pipeline/run_morges_demo.py

Launch frontend:

Open ``docs/index.html`` in a browser.

Design Philosophy
-----------------

- Modular pipeline: clear separation of evaluation, selection, and output  
- Static frontend: no backend server required  
- Site-specific flexibility: custom logic per location  
- Lightweight deployment: easily hostable (e.g., GitHub Pages)

Contributors
------------

Major contributions to date:

- Edgar Dolores-Tesillos  
- Gabriela Espejo  
- OpenAI  
