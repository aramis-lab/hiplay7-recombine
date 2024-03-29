# HIPLAY7 - recombine

**Authors**: Linda Marrakchi-Kacem ([ARAMIS Lab](http://www.aramislab.fr)), Alexis
Guyot ([ARAMIS Lab](http://www.aramislab.fr)).

This software tool allows to automatically recombine multiple MRI slabs
into a single high resolution slab. This is used for 7T MRI acquisitions
dedicated to the study of hippocampal subregions.
More tools and resources to study the hippocampus using 7T MRI are
available at http://www.aramislab.fr/sevenhipp/ .


## Overview

`recombine.py` is a Python script that generates a high-resolution MR
image from the following input:
   - _repetition 1 - slab 1_: high-resolution MR volume, covering part of the head 
   - _repetition 1 - slab 2_: high-resolution MR volume, covering the same part of the head as _repetition  1 - slab 1'_
   - _repetition 2 - slab 1_: high-resolution MR volume, covering a non-overlapping part of the head
   - _repetition 2 - slab 2_: high-resolution MR volume, covering the same part of the head as _repetition  2 - slab 1_
   - _low-res_: low-resolution MR volume, covering a large part of the head, that encompasses the parts from _repetition 1 - slab 1_ and _repetition 2 - slab 1_

For any use of this code, please cite the following article:
> L Marrakchi-Kacem, A Vignaud, J Sein, J Germain, TR Henry, C Poupon, 
> L Hertz-Pannier, S Lehericy, O Colliot, PF Van de Moortele, M Chupin, 2016. 
> Robust imaging of hippocampal inner structure at 7T: in vivo
> acquisition protocol and methodological choices.
> _Magnetic Resonance Materials in Physics, Biology and Medicine_  29(3), pp.475-489.

This article is available at https://hal.inria.fr/hal-01321870/document .


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
(numpy, nibabel, nipype), we recommend installing Miniconda, a program
that lets you install and run Python packages and their dependencies
into local, user-defined environments.

Miniconda can be obtained at the following website:
https://docs.conda.io/en/latest/miniconda.html. 
Please make sure you choose the version corresponding to your operating
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

```
python recombine.py [rep1_s1] [rep1_s2] [rep2_s1] [rep2_s2] [lowres] [output_dir] (--spm_path [SPM_PATH])
```

Where:
- [rep1_s1]: .nii(.gz) image file. First slab of first repetition
- [rep1_s2]: .nii(.gz) image file. Second slab of first repetition
- [rep2_s1]: .nii(.gz) image file. First slab of second repetition
- [rep2_s2]: .nii(.gz) image file. Second slab of second repetition
- [lowres]: .nii(.gz) image file. Low resolution volume
- [output_dir]: path where temporary and output files will be stored. output\_dir has to be empty, otherwise the script will crash
- [SPM_PATH]: (optional) path to the SPM folder (i.e., the folder that contains the script spm.m)

**Note:**
- All files must be provided as either .nii or .nii.gz volume images
- The final output will be found at [output\_dir]/rs\_float\_ponderated.nii
- Temporary files will be found in folder [output\_dir]/debug/. Please manually delete this folder to save storage space. Contains:
    - intermediary images used to produce the final output
    - file 'spm_location.txt' that shows the path to the SPM folder that was used inside the script
- The path to SPM only needs to be provided if no installation of SPM has been detected by Matlab. You can check this by launching the following command: `python check_spm.py`
