# HIPLAY7 - recombine

`recombine.py` - combine several slabs into a single high resolution slab.

**Author**: Linda Marrakchi-Kacem, Brain and Spine Institute.
**Maintainer**: Alexis Guyot, Brain and Spine Institute.


## Overview

`recombine.py` is a Python script that generates a high-resolution MR
image from the following input:
   - _repetition 1 - slab 1_: high-resolution MR volume, covering part of the head 
   - _repetition 1 - slab 2_: high-resolution MR volume, covering the same part of the head as _repetition  1 - slab 1'_
   - _repetition 2 - slab 1_: high-resolution MR volume, covering a non-overlapping part of the head
   - _repetition 2 - slab 2_: high-resolution MR volume, covering the same part of the head as _repetition  2 - slab 1_
   - _low-res_: low-resolution MR volume, covering a large part of the head, that encompasses the parts from _repetition 1 - slab 1_ and _repetition 2 - slab 1_

For any use of this code, the following paper must be cited:
> L Marrakchi-Kacem, A Vignaud, J Sein, J Germain, TR Henry, C Poupon, 
> L Hertz-Pannier, S Lehericy, O Colliot, PF Van de Moortele, M Chupin. 
> Robust imaging of hippocampal inner structure at 7T: in vivo
> acquisition protocol and methodological choices.


## Installation

`recombine.py` requires the following software and libraries:
- Python (either version 2. or 3.)
    - numpy
    - nibabel
    - nilearn
    - nipype
- Matlab
- SPM

In case you are not sure you already have the relevant Python libraries
(numpy, nibabel, nipype), we recommend installing `Miniconda`, a program
that lets you install and run Python packages and their dependencies
into local, user-defined environments.

Miniconda can be obtained at the following website:
https://docs.conda.io/en/latest/miniconda.html. 
Please make sure you choose version corresponding to your operating
system (Windows, Mac OS X or Linux) and to the architecture of your
computer (32bit or 64bit).

Once you have installed Miniconda, we suggest you create a new Conda
environment. This will let you install new dependencies without
altering your current installation of Python. This can be done with the
following command line: `conda create -n recombine_env`.
Once you have created the new environment, 'activate' it as follows:
`source activate recombine_env`.
Then, install the required dependencies with the following commands:
- `conda install scipy`
- `conda install scikit-learn`
- `conda install pip`
- `pip install nibabel`
- `pip install nilearn`
- `pip install nipype`


## Usage

**Optional**: if you have installed dependencies via miniconda, as described in section 'Install', then activate the conda environment that contains the dependencies with the following command line:
`source activate recombine_env`.

To launch the recombine.py script, run
`python recombine.py [rep1\_s1].nii(.gz) [rep1\_s2].nii(.gz) [rep2\_s1].nii(.gz) [rep2\_s2].nii(.gz) [lowres].nii(.gz) [output_dir]`.
Where:
- [rep1\_s1].nii(.gz): first slab of first repetition
- [rep1\_s2].nii(.gz): second slab of first repetition
- [rep2\_s1].nii(.gz): first slab of second repetition
- [rep2\_s2].nii(.gz): second slab of second repetition
- [lowres].nii(.gz): low resolution volume
- [output\_dir]: path where temporary and output files will be stored. output\_dir has to be empty, otherwise the script will crash.

All files can be provided as either .nii or .nii.gz volume images.

The final output will be found at [output\_dir]/rs\_float\_ponderated.nii

Temporary files will be found in folder [output\_dir]/debug/.
Please manually delete this folder to save storage space.


Last updated: Tue, 02 April 2019
