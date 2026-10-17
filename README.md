# VHH-Bench

## A Benchmarking Framework for Evaluating Nanobody–Antigen Complex Predictions Across CDR3 Conformations


VHH-Bench is an extensible and reproducible benchmark framework designed for evaluating the accuracy of protein structure prediction methods on nanobody-antigen complexes across diverse CDR3 conformations.

<img width="2993" height="1369" alt="image" src="https://github.com/user-attachments/assets/b5a8f36a-9263-4558-8722-c17f1bfbb6c9" />

### Prerequisites

- Python 3.9 or later


### Dependencies

- The Python scripts require the following packages:

MDAnalysis, matplotlib, numpy, pandas, scipy, Biopython and PyMOL (open-source)


### Install the required packages using:

````
pip install MDAnalysis matplotlib numpy pandas scipy biopython
conda install -c conda-forge pymol-open-source
````

### Workflow

**01_dataset**

Contains the benchmark dataset as PDB structures downloaded from SAbDab.


**02_classification**

Classify benchmark structures into CDR3 conformational categories:

````
python classify.py
````
Structures are first classified as Kinked and Extended.

Extended structures are then further classified into Concave, Convex and Loop.

**03_prediction**

Contains example input files and scripts used for structure prediction. 

Generate FASTA inputs for structure prediction:

````
python get_fasta.py
````

The directory includes example FASTA and JSON input files for:

AF3, Boltz-2, Chai-1, ESMFold2, HF3 and Protenix-v2

Run a prediction, for example:

````
bash AF3/run_AF3.sh
````

This step executes structure prediction pipelines on the benchmark sequences.

**04_evaluation**

Contains benchmarking and analysis workflows.

Evaluation pipelines are available for:

AF3, Boltz-2, Chai-1, ESMFold2, HF3 and Protenix-v2

Run an evaluation workflow, for example:

````
bash AF3/extended/seed1/evaluate_AF3.sh
````

The evaluation directory is organised by:

Prediction method and Structural category (all_dataset, extended, kinked)

**05_analysis_plots**

Contains scripts and outputs used to analyse benchmarking results and generate figures.

Analysis includes:
DockQ, ipTM, RMSD, CDR3 analysis and Publication-ready plots 


### Acknowledgements

VHH-Bench makes use of:

•	[SAbDab](https://sabdab.opig.stats.ox.ac.uk)

•	[AlphaFold3](https://github.com/google-deepmind/alphafold3)

•	[Boltz-2](https://github.com/jwohlwend/boltz)

•	[Chai-1](https://github.com/chaidiscovery/chai-lab)

•	[HelixFold3](https://github.com/PaddlePaddle/PaddleHelix/tree/dev/apps/protein_folding/helixfold3)

•	[Protenix-v2](https://github.com/bytedance/Protenix)

•	[DockQ](https://github.com/wallnerlab/DockQ)

•	[MDAnalysis](https://github.com/MDAnalysis/mdanalysis)

•	[PyMOL](https://github.com/schrodinger/pymol-open-source)


### Citation
If you use VHH-Bench in your research, please cite:



