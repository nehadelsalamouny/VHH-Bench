# VHH-Bench

A Benchmarking Framework for Evaluating Nanobody–Antigen Complex Predictions Across CDR3 Conformations

Nanobodies in VHH-Bench are classified according to their CDR3 conformation using the geometric descriptors α101 and τ101. Structures are initially grouped into kinked and extended classes, with extended conformations further classified into loop and concave based on τ97.


Prerequisites

Python 3.9 or later


Dependencies

The Python scripts require the following packages:

MDAnalysis
matplotlib
numpy
pandas
scipy
Biopython
PyMOL (open-source)


Install the required packages using:

pip install MDAnalysis matplotlib numpy pandas scipy biopython
conda install -c conda-forge pymol-open-source