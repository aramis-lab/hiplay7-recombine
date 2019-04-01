#!/bin/sh

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


# The third part of the pipeline contains the processings done in order to 
# combine the volumes after the SPM registration. 




export output_filename=$1


##############################################################################
echo " "
echo "additionning blocs"
echo " "
##############################################################################

python python_code/volumes_addition.py \
       $output_filename/s1a_float.nii \
       $output_filename/s1b_float.nii \
       $output_filename/rs1_float.nii

python python_code/volumes_addition.py \
       $output_filename/s2a_float.nii \
       $output_filename/s2b_float.nii \
       $output_filename/rs2_float.nii

python python_code/volumes_addition.py \
       $output_filename/rs1_float.nii \
       $output_filename/rs2_float.nii \
       $output_filename/rs_float.nii


python python_code/volumes_addition.py \
       $output_filename/phantom_one_gap_s1a.nii \
       $output_filename/phantom_one_gap_s1b.nii \
       $output_filename/phantom_one_gap_s1.nii \

python python_code/volumes_addition.py \
       $output_filename/phantom_one_gap_s2a.nii \
       $output_filename/phantom_one_gap_s2b.nii \
       $output_filename/phantom_one_gap_s2.nii \

python python_code/volumes_addition.py \
       $output_filename/phantom_one_gap_s1.nii \
       $output_filename/phantom_one_gap_s2.nii \
       $output_filename/phantom_one_gap_s.nii \

##############################################################################
echo " "
echo "normalizing blocs using phantoms"
echo " "
##############################################################################

python python_code/volumes_division.py \
       $output_filename/rs_float.nii \
       $output_filename/phantom_one_gap_s.nii \
       $output_filename/rs_float_ponderated.nii

python python_code/volumes_division.py \
       $output_filename/rs1_float.nii \
       $output_filename/phantom_one_gap_s1.nii \
       $output_filename/rs1_float_ponderated.nii

python python_code/volumes_division.py \
       $output_filename/rs2_float.nii \
       $output_filename/phantom_one_gap_s2.nii \
       $output_filename/rs2_float_ponderated.nii

python python_code/volumes_addition.py \
       $output_filename/rs1_float_ponderated.nii \
       $output_filename/rs2_float_ponderated.nii \
       $output_filename/rs_1_2_float_ponderated.nii



\rm $output_filename/*.minf









