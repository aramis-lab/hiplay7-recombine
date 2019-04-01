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


# The second part of the pipeline consists in launching the SPM registration 
###############################################################################
# volumes extensions are supposed to be .nii
# if another extension is used it must be replaced in the whole code
#
# name of the file were the output results should be provided by the user
export output_filename=$1
#
###############################################################################


################################################################################
echo " "
echo "registering images using SPM"
echo " "
################################################################################

./spm_registration.sh \
$output_filename/lr_1a.nii \
$output_filename/s1a_float.nii \
$output_filename/phantom_one_gap_s1a.nii

./spm_registration.sh \
$output_filename/lr_1b.nii \
$output_filename/s1b_float.nii \
$output_filename/phantom_one_gap_s1b.nii

./spm_registration.sh \
$output_filename/lr_2a.nii \
$output_filename/s2a_float.nii \
$output_filename/phantom_one_gap_s2a.nii

./spm_registration.sh \
$output_filename/lr_2b.nii \
$output_filename/s2b_float.nii \
$output_filename/phantom_one_gap_s2b.nii


