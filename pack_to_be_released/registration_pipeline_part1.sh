#! /bin/sh

###############################################################################
# This code was developped by Linda Marrakchi in the ARAMIS lab.
# For any use of this code, the following paper must be cited:
# 
# L Marrakchi-Kacem, A Vignaud, J Sein, J Germain, TR Henry, C Poupon, 
# L Hertz-Pannier, S Lehericy, O Colliot, PF Van de Moortele, M Chupin. 
# Robust imaging of hippocampal inner structure at 7T: in vivo acquisition 
# protocol and methodological choices. Submitted
#
###############################################################################


# The first part of the pipeline contains some preprocessing steps needed to 
# launch the SPM registration. 


###############################################################################
# the following name of files have to be provided by the user:
# volumes extensions are supposed to be .nii
# if another extension is used it must be replaced in the whole code
#
#
# name of first repetition and first slab
export high_res_rep1_slab1=$1
# name of first repetition and second slab
export high_res_rep1_slab2=$2
# name of second repetition and first slab
export high_res_rep2_slab1=$3
# name of second repetition and second slab
export high_res_rep2_slab2=$4

# name of low resolution
export low_res=$5
# name of the file where the output results should be written
export output_filename=$6
#
###############################################################################




###############################################################################
echo " "
echo "copying files into the output folder"
echo " "
###############################################################################

# creating output folder
mkdir $output_filename
# erasing old files if output folder already exists
#\rm $output_filename/*

cp $high_res_rep1_slab1 $output_filename/s1a.nii
cp $high_res_rep1_slab2 $output_filename/s1b.nii
cp $high_res_rep2_slab1 $output_filename/s2a.nii
cp $high_res_rep2_slab2 $output_filename/s2b.nii
cp $low_res $output_filename/lr.nii

###############################################################################
# creating four copies of the low resolution volume
# each copy of this low resolution volume will be used to register a slab
echo " "
echo "creating four copies of the low resolution volume"
echo " "
###############################################################################

cp $output_filename/lr.nii \
   $output_filename/lr_1a.nii

cp $output_filename/lr.nii \
   $output_filename/lr_1b.nii

cp $output_filename/lr.nii \
   $output_filename/lr_2a.nii

cp $output_filename/lr.nii \
   $output_filename/lr_2b.nii

   
###############################################################################
# the following code will process each slab as follows:
# - duplicate slices of the volume along the y axis
# - fill corresponding slices with the gaps that represent the real acquisition
# - create a phantom corresponding to each slab
###############################################################################




###############################################################################
echo " "
echo "processing first repetition"
echo " "
###############################################################################


echo "processing first bloc"

python python_code/voxel_duplication.py \
       $output_filename/s1a.nii \
       2 \
       y \
       $output_filename/s1a_duplicated.nii

python python_code/insert_gap.py \
       $output_filename/s1a_duplicated.nii \
       2 \
       1 \
       y \
       $output_filename/s1a_with_gap.nii

echo "processing second bloc"

python python_code/voxel_duplication.py \
       $output_filename/s1b.nii \
       2 \
       y \
       $output_filename/s1b_duplicated.nii

python python_code/insert_gap.py \
       $output_filename/s1b_duplicated.nii \
       2 \
       0 \
       y \
       $output_filename/s1b_with_gap.nii

echo "processing phantom for first bloc"

python python_code/create_value_phantom.py \
       $output_filename/s1a_with_gap.nii \
       1 \
       $output_filename/phantom_one_s1a.nii

python python_code/insert_gap.py \
       $output_filename/phantom_one_s1a.nii \
       2 \
       1 \
       y \
       $output_filename/phantom_one_gap_s1a.nii


echo "processing phantom for second bloc"

python python_code/create_value_phantom.py \
       $output_filename/s1b_with_gap.nii \
       1 \
       $output_filename/phantom_one_s1b.nii

python python_code/insert_gap.py \
       $output_filename/phantom_one_s1b.nii \
       2 \
       0 \
       y \
       $output_filename/phantom_one_gap_s1b.nii


echo "converting all data to float"

python python_code/convert_int_volume_to_float.py \
       $output_filename/s1a_with_gap.nii \
       $output_filename/s1a_float.nii

python python_code/convert_int_volume_to_float.py \
       $output_filename/s1b_with_gap.nii \
       $output_filename/s1b_float.nii


################################################################################
echo " "
echo "processing second repetition"
echo " "
################################################################################

echo "processing first bloc"


python python_code/voxel_duplication.py \
       $output_filename/s2a.nii \
       2 \
       y \
       $output_filename/s2a_duplicated.nii

python python_code/insert_gap.py \
       $output_filename/s2a_duplicated.nii \
       2 \
       1 \
       y \
       $output_filename/s2a_with_gap.nii

echo "processing second bloc"

python python_code/voxel_duplication.py \
       $output_filename/s2b.nii \
       2 \
       y \
       $output_filename/s2b_duplicated.nii

python python_code/insert_gap.py \
       $output_filename/s2b_duplicated.nii \
       2 \
       0 \
       y \
       $output_filename/s2b_with_gap.nii

echo "processing phantom for first bloc"

python python_code/create_value_phantom.py \
       $output_filename/s2a_with_gap.nii \
       1 \
       $output_filename/phantom_one_s2a.nii

python python_code/insert_gap.py \
       $output_filename/phantom_one_s2a.nii \
       2 \
       1 \
       y \
       $output_filename/phantom_one_gap_s2a.nii


echo "processing phantom for second bloc"

python python_code/create_value_phantom.py \
       $output_filename/s2b_with_gap.nii \
       1 \
       $output_filename/phantom_one_s2b.nii

python python_code/insert_gap.py \
       $output_filename/phantom_one_s2b.nii \
       2 \
       0 \
       y \
       $output_filename/phantom_one_gap_s2b.nii


echo "converting all data to float"

python python_code/convert_int_volume_to_float.py \
       $output_filename/s2a_with_gap.nii \
       $output_filename/s2a_float.nii

python python_code/convert_int_volume_to_float.py \
       $output_filename/s2b_with_gap.nii \
       $output_filename/s2b_float.nii

###############################################################################
echo " "
echo "removing .minf files"
echo " "
###############################################################################

\rm $output_filename/*.minf


