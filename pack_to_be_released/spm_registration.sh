#!/bin/sh

path_SPM=/home/user/software/SPM
path_MP=/home/user/matlab


image_ref=$1
image_source=$2
image_other=$3

matlab -r """addpath('"$path_SPM"');addpath(genpath('"$path_MP"'));spm('pet');recalageRigide_spm8({'"$image_source"'},{'"$image_ref"'},{'"$image_other"'});quit""" -nodisplay

