# VHH-Bench

A Benchmarking Framework for Evaluating Nanobody–Antigen Complex Predictions Across CDR3 Conformations


VHH-Bench is an extensible and reproducible benchmark framework designed for evaluating the accuracy of protein structure prediction methods on nanobody-antigen complexes across diverse CDR3 conformations.

<img width="3000" height="2100" alt="VHH-Bench" src="https://github.com/user-attachments/assets/c1e0a14d-5b42-49da-9706-42b6cf332b34" />


**Prerequisites**

• Python 3.9 or later


**Dependencies**

The Python scripts require the following packages:

MDAnalysis, matplotlib, numpy, pandas, scipy, Biopython and PyMOL (open-source)


**Install the required packages using:**

pip install MDAnalysis matplotlib numpy pandas scipy biopython
conda install -c conda-forge pymol-open-source


**Workflow**

**01_dataset**

Contains the benchmark dataset as PDB structures downloaded from SAbDab.


**02_classification**

Classify benchmark structures into CDR3 conformational categories:

python classify.py

Structures are first classified as Kinked and Extended.

Extended structures are then further classified into Concave, Convex and Loop.

**03_prediction**

Contains example input files and scripts used for structure prediction. 

Generate FASTA inputs for structure prediction:

python get_fasta.py

The directory includes example FASTA and JSON input files for:

AF3, Boltz-2, Chai-1, ESMFold2, HF3 and Protenix-v2

Run a prediction, for example:

bash AF3/run_AF3.sh

This step executes structure prediction pipelines on the benchmark sequences.

**04_evaluation**

Contains benchmarking and analysis workflows.

Evaluation pipelines are available for:

AF3, Boltz-2, Chai-1, ESMFold2, HF3 and Protenix-v2

Run an evaluation workflow, for example:

bash AF3/extended/seed1/evaluate_AF3.sh

The evaluation directory is organised by:

Prediction method and Structural category (all_dataset, extended, kinked)

**05_analysis_plots**

Contains scripts and outputs used to analyse benchmarking results and generate figures.

Analysis includes:
DockQ, ipTM, RMSD, CDR3 analysis and Publication-ready plots 


**Acknowledgements**

VHH-Bench makes use of:

•	SAbDab

•	AlphaFold3

•	Boltz-2

•	Chai-1

•	HelixFold3

•	Protenix-v2

•	DockQ

•	MDAnalysis

•	PyMOL

•	Python


**Citation**
If you use VHH-Bench in your research, please cite:



