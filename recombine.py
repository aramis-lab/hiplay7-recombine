"""Code to combine different slabs into a single high resolution slab

# This code was developed by Linda Marrakchi at the ARAMIS lab.
# Maintainer: Alexis Guyot (2019)
#
# For any use of this code, the following paper must be cited:
# 
# L Marrakchi-Kacem, A Vignaud, J Sein, J Germain, TR Henry, C Poupon, 
# L Hertz-Pannier, S Lehericy, O Colliot, PF Van de Moortele, M Chupin. 
# Robust imaging of hippocampal inner structure at 7T: in vivo
# acquisition protocol and methodological choices.

"""

import sys
import os
import shutil
import gzip
import numpy as np
import nibabel as nib
import nilearn as nil
import nilearn.image
import nipype.interfaces.spm as spm


def usage():
    """CLI helper

    Function called if the user does not provide the right number of
    arguments.
    Display the correct command line call to the program.

    Args:
        N/A

    Returns:
        N/A
    """
    print('Error: wrong number of arguments.')
    print('Usage:')
    cmdline = 'python recombine.py'
    cmdline = '{0} [rep1_s1].nii(.gz)'.format(cmdline)
    cmdline = '{0} [rep1_s2].nii(.gz)'.format(cmdline)
    cmdline = '{0} [rep2_s1].nii(.gz)'.format(cmdline)
    cmdline = '{0} [rep2_s2].nii(.gz)'.format(cmdline)
    cmdline = '{0} [lowres].nii'.format(cmdline)
    cmdline = '{0} [output_dir]'.format(cmdline)
    print(cmdline)
    print('Where:')
    print('[rep1_s1].nii: first slab of first repetition')
    print('[rep1_s2].nii: second slab of first repetition')
    print('[rep2_s1].nii: first slab of second repetition')
    print('[rep2_s2].nii: second slab of second repetition')
    print('[lowres].nii: low resolution volume')
    print('[output_dir]: path where output files will be stored')



def prepare_folders(outdir_path):
    """Create temporary folders

    Will create two subfolders inside the output directory:
    1. 'debug' subfolder: contains all intermediary images generated
        prior to te output recombined images
    2. 'temp' subfolder: contains all temporary data generated for SPM
        processing (SPM modifies the header of the images which it is
        working on, so we duplicate the image to be SPM-processed
        before feeding them to SPM).

    Args:
        outdir_path (string): absolute path to output dir, where
            results will get stored

    Returns:
        debugdir_path (string): path to 'debug' subfolder where all
            intermediary images are stored
        tempdir_path (string): path to temporary subfolder where images
            to be processed with SPM are duplicated and stored
    """
    # Output directory: check if exists and create if not
    if os.path.isdir(outdir_path):
        # check if output directory is empty
        if os.listdir(outdir_path):
            error_msg = 'Error: please provide an empty output dir'
            raise IOError(error_msg)
    else:
        # create the output directory
        os.makedirs(outdir_path)

    # define paths
    debugdir_path = "{0}/debug/".format(outdir_path)
    tempdir_path = "{0}/temp/".format(outdir_path)

    # create subfolders if do not exist already
    #-- debug
    try:
        os.makedirs(debugdir_path)
    except OSError:
        if not os.path.isdir(debugdir_path):
            raise
    #-- temp
    try:
        os.makedirs(tempdir_path)
    except OSError:
        if not os.path.isdir(tempdir_path):
            raise

    return [debugdir_path, tempdir_path]



def nii_copy(im_inpath, im_outpath):
    """Copy from input to output path with output in .nii

    Convenience function to copy an image from an input path to an
    output path, while making sure the destination file has a .nii
    extension (and not a .nii.gz one). This is to make sure we will
    be feeding SPM with uncompressed images.

    Args:
        im_inpath (string): path to the input image. The file can be
            either of type .nii or of type .nii.gz
        im_outpath (string): path to the output copied image. The file
            is of type .nii

    Returns:
        N/A
    """
    # Get extension of input image filename
    imfilename = os.path.basename(im_inpath)
    imfilename_ext = os.path.splitext(imfilename)[1]
    error_msg = 'Error: input image must be of type either .nii or .nii.gz'
    if imfilename_ext == '.nii':
        # if .nii, standard copy
        shutil.copyfile(im_inpath, im_outpath)
    elif imfilename_ext == '.gz':
        # check if the extension is .nii.gz
        imfilename_start = os.path.splitext(imfilename)[0]
        imfilename_start_ext = os.path.splitext(imfilename_start)[1]
        if imfilename_start_ext == '.nii':
            # extension is .nii.gz
            with gzip.open(im_inpath, 'rb') as im_infile:
                with open(im_outpath, 'wb') as im_outfile:
                    shutil.copyfileobj(im_infile, im_outfile)
        else:
            raise IOError(error_msg)
    else:
        raise IOError(error_msg)



def safe_remove(impath, dirpath):
    """Check if image is in right folder before removing

    Make sure the image to be removed is located somewhere within the
    subfolder hierarchy of a defined folder (i.e., temporary folder or
    folder containing the intermediary results).
    This is mostly to ensure avoiding any accidental deletion anywhere
    outside the working directory.

    Args:
        impath (string): path to the image to delete.
        dirpath (string): path to folder containing the image to be
            deleted

    Returns:
        N/A
    """
    # get absolute path + real (i.e., actual path for symlinks)
    impath_real = os.path.realpath(impath)
    dirpath_real = os.path.realpath(dirpath)
    dirpath_real_sep = "{0}{1}".format(dirpath_real, os.sep)

    # check if the path to image encompasses the path to folder
    if not impath_real.startswith(dirpath_real_sep):
        error_msg = 'Error: impath {0}'.format(impath)
        error_msg = '{0} does not belong to dirpath {1}.'.format(
            error_msg, dirpath)
        error_msg = '{0} Cannot safely remove.'.format(error_msg)
        raise IOError(error_msg)

    # remove the image file
    if os.path.isfile(impath_real):
        os.remove(impath_real)
    else:
        error_msg = 'Error: file {0} does not exist'.format(impath)
        raise IOError(error_msg)



def volume_duplication(in_volume, duplication_factor, axis):
    """Replicate voxels along a chosen axis

    Will replicate voxels a certain number of times
    (duplication_factor) along any of the 'x', 'y' or 'z' axis.

    Args:
        in_volume (nibabel volume): data will be a [m,n,o] array
        duplication_factor (int): number of times voxels will get
            replicated
        axis (string): 'x', 'y' or 'z'

    Returns:
        out_volume (nibabel volume): data will be
            [duplication_factor*m, n, o] array if axis='x',
            [m, duplication_factor*n, o] array if axis='y',
            [m, n, duplication_factor*o] array if axis='z'
    """
    # read input volume
    #-- convert to RAS orientation
    in_volume_ras = nib.as_closest_canonical(in_volume)
    in_volume_data = in_volume_ras.get_data()
    in_volume_affine = in_volume_ras.affine.copy()

    # get output matrix affine
    #-- define upsampling factor for all directions
    upsampling_factor_array = np.ones(3, np.float)
    if axis == 'x':
        upsampling_factor_array[0] = duplication_factor
    if axis == 'y':
        upsampling_factor_array[1] = duplication_factor
    if axis == 'z':
        upsampling_factor_array[2] = duplication_factor
    #-- compute output affine from input affine and upsampling array
    #---- 3x3 part of the output affine
    factor_matrix = np.zeros((3, 3), np.float)
    for dim_index in range(3):
        factor_matrix[dim_index, dim_index] = 1.0/upsampling_factor_array[dim_index]
    out_volume_affine3x3 = (in_volume_affine[0:3, 0:3]).dot(factor_matrix)
    #---- translational part: find it using nilearn interpolation
    volume_upsampled = nil.image.resample_img(
        in_volume_ras,
        target_affine=out_volume_affine3x3,
        interpolation='nearest')
    out_volume_affine = volume_upsampled.affine.copy()

    # data array: duplicate according to direction
    if axis == 'x':
        out_volume_data = np.repeat(in_volume_data, duplication_factor, axis=0)
    if axis == 'y':
        out_volume_data = np.repeat(in_volume_data, duplication_factor, axis=1)
    if axis == 'z':
        out_volume_data = np.repeat(in_volume_data, duplication_factor, axis=2)

    # save output volume
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_volume_duplication(
        in_volume_path,
        duplication_factor,
        axis,
        out_volume_path):
    """Replicate voxels from file volume and save

    Will replicate voxels a certain number of times
    (duplication_factor) along any of the 'x', 'y' or 'z' axis.

    Args:
        in_volume_path (string): path to input volume
        duplication_factor (int): number of times voxels will get
            replicated
        axis (string): 'x', 'y' or 'z'
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volume
    in_volume = nib.load(in_volume_path)
    # duplicate volume
    out_volume = volume_duplication(in_volume, duplication_factor, axis)
    # save output volume
    nib.save(out_volume, out_volume_path)



def insert_gap(in_volume, gap_factor, gap_position, axis):
    """Insert empty voxels at regular intervals

    Will insert empty rows/columns/slices (depending on chosen axis)
    every [gap_factor] voxels, with an offset defined by [gap_position]

    Args:
        in_volume (nibabel volume): data will be a [m,n,o] array
        gap_factor (int): positive integer value, interval between empty
            voxels
        gap_position (int): positive integer value, offset
        axis (string): 'x', 'y' or 'z'

    Returns:
        out_volume (nibabel volume): data will be a [m,n,o] array
    """
    # read input volume
    #-- convert to RAS orientation
    in_volume_ras = nib.as_closest_canonical(in_volume)
    in_volume_data = in_volume_ras.get_data()
    in_volume_affine = in_volume_ras.affine.copy()
    #-- sanity checks
    if gap_position < 0:
        error_msg = 'gap position must be a positive integer'
        raise ValueError(error_msg)
    if gap_factor < 0:
        error_msg = 'gap factor must be a positive integer'
        raise ValueError(error_msg)
    if gap_position >= gap_factor:
        error_msg = 'gap position must be lower than gap factor'
        raise ValueError(error_msg)

    # insert gaps
    out_volume_data = in_volume_data.copy()
    out_dim_x = out_volume_data.shape[0]
    out_dim_y = out_volume_data.shape[1]
    out_dim_z = out_volume_data.shape[2]
    if axis == 'x':
        gap_position_array = np.mod(
            np.r_[0:out_dim_x], gap_factor) == gap_position
        out_volume_data[gap_position_array, :, :] = 0
    if axis == 'y':
        gap_position_array = np.mod(
            np.r_[0:out_dim_y], gap_factor) == gap_position
        out_volume_data[:, gap_position_array, :] = 0
    if axis == 'z':
        gap_position_array = np.mod(
            np.r_[0:out_dim_z], gap_factor) == gap_position
        out_volume_data[:, :, gap_position_array] = 0
    out_volume_affine = in_volume_affine.copy()

    # save output volume
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_insert_gap(
        in_volume_path,
        gap_factor,
        gap_position,
        axis,
        out_volume_path):
    """Insert empty voxels at regular intervals and save file

    Reads file, insert empty voxels at regular intervals and save output
    file.

    Args:
        in_volume_path (string): path to input volume
        gap_factor (int): positive integer value, interval between empty
            voxels
        gap_position (int): positive integer value, offset
        axis (string): 'x', 'y' or 'z'
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volume
    in_volume = nib.load(in_volume_path)
    # insert gap
    out_volume = insert_gap(in_volume, gap_factor, gap_position, axis)
    # save output volume
    nib.save(out_volume, out_volume_path)



def create_phantom(in_volume, value):
    """Create constant-valued phantom

    Create a phantom volume having the same size as an input volume and
    being filled with a constant value.

    Args:
        in_volume (nibabel volume): data will be a [m,n,o] array
        value (float): the value given to all voxels of the phantom

    Returns:
        out_volume (nibabel volume): phantom volume, data will be a
            [m,n,o] array
    """
    # read input volume - convert to RAS orientation
    in_volume_ras = nib.as_closest_canonical(in_volume)
    in_volume_data = in_volume_ras.get_data()
    in_volume_affine = in_volume_ras.affine.copy()

    # generate output volume
    out_volume_data = value*np.ones_like(in_volume_data, np.float)
    out_volume_affine = in_volume_affine.copy()
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_create_phantom(in_volume_path, value, out_volume_path):
    """Create constant-valued phantom and save file

    Read input volume, create phantom volume and save output volume

    Args:
        in_volume_path (string): path to input volume
        value (float): the value given to all voxels of the phantom
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volume
    in_volume = nib.load(in_volume_path)
    # create phantom volume
    out_volume = create_phantom(in_volume, value)
    # save output volume
    nib.save(out_volume, out_volume_path)



def int2float(in_volume):
    """int to float conversion

    Convert volume from int to float.

    Args:
        in_volume (nibabel volume): data will be a [m,n,o] array

    Returns:
        out_volume (nibabel volume): phantom volume, data will be a
            [m,n,o] array
    """
    # read input volume - convert to RAS orientation
    in_volume_ras = nib.as_closest_canonical(in_volume)
    in_volume_data = in_volume_ras.get_data()
    in_volume_affine = in_volume_ras.affine.copy()

    # generate output volume - convert data to float
    out_volume_data = in_volume_data.astype(np.float)
    out_volume_affine = in_volume_affine.copy()
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_int2float(in_volume_path, out_volume_path):
    """Convert from int to float and save volume

    Read input volume, convert from int to float and save output volume

    Args:
        in_volume_path (string): path to input volume
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volume
    in_volume = nib.load(in_volume_path)
    # convert from int to float
    out_volume = int2float(in_volume)
    # save output volume
    nib.save(out_volume, out_volume_path)



def process_repetition(repetition, sa_path, sb_path, outdir_path):
    """Process repetition

    Process any of the first ('s1a/b_[...]' files) or second
    ('s2a/b_[...]' files) repetitions.
    Create a series of intermediate results in the output directory

    Args:
        repetition (string): '1' (first repetition) or '2' (second
            repetition)
        sa_path (string): path to first slab of either first or second
            repetition. Should match argument 'repetition'.
        sb_path (string): path to second slab of either first or second
            repetition. Should match argument 'repetition'.
        outdir_path (string): absolute path to output dir, where
            results will get stored
    Returns:
        sa_float_path (string): path to first slab of first/second
            repetition converted to float
        sb_float_path (string): path to second slab of first/second
            repetition converted to float
        sa_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of first/second repetition
        sb_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of first/second repetition
    """
    if repetition == '1':
        repetition_string = 'first'
    if repetition == '2':
        repetition_string = 'second'

    print('processing {0} repetition'.format(repetition_string))
    #-- process first block
    print('processing {0} repetition - first block'.format(repetition_string))
    #---- volume duplication
    sa_duplicated_path = os.path.join(
        outdir_path, 's{0}a_duplicated.nii.gz'.format(repetition))
    file_volume_duplication(sa_path, 2, 'y', sa_duplicated_path)
    #---- insert gaps
    sa_gap_path = os.path.join(
        outdir_path, 's{0}a_with_gap.nii.gz'.format(repetition))
    file_insert_gap(sa_duplicated_path, 2, 0, 'y', sa_gap_path)
    #-- process second block
    print('processing {0} repetition - second block'.format(repetition_string))
    #---- volume duplication
    sb_duplicated_path = os.path.join(
        outdir_path, 's{0}b_duplicated.nii.gz'.format(repetition))
    file_volume_duplication(sb_path, 2, 'y', sb_duplicated_path)
    #---- insert gaps
    sb_gap_path = os.path.join(
        outdir_path, 's{0}b_with_gap.nii.gz'.format(repetition))
    file_insert_gap(sb_duplicated_path, 2, 1, 'y', sb_gap_path)
    #-- process first block
    print('processing {0} repetition - phantom for first block'.format(
        repetition_string))
    #---- phantom creation
    sa_phantom_path = os.path.join(
        outdir_path, 'phantom_one_s{0}a.nii.gz'.format(repetition))
    file_create_phantom(sa_gap_path, 1, sa_phantom_path)
    #---- phantom gap insertion
    # stored as uncompressed .nii because will get used by SPM
    sa_phantom_gap_path = os.path.join(
        outdir_path, 'phantom_one_gap_s{0}a.nii'.format(repetition))
    file_insert_gap(sa_phantom_path, 2, 0, 'y', sa_phantom_gap_path)
    print('processing {0} repetition - phantom for second block'.format(
        repetition_string))
    #---- phantom creation
    sb_phantom_path = os.path.join(
        outdir_path, 'phantom_one_s{0}b.nii.gz'.format(repetition))
    file_create_phantom(sb_gap_path, 1, sb_phantom_path)
    #---- phantom gap insertion
    # stored as uncompressed .nii because will get used by SPM
    sb_phantom_gap_path = os.path.join(
        outdir_path, 'phantom_one_gap_s{0}b.nii'.format(repetition))
    file_insert_gap(sb_phantom_path, 2, 1, 'y', sb_phantom_gap_path)
    #---- convert data to float
    #------ s1a
    # stored as uncompressed .nii because will get used by SPM
    sa_float_path = os.path.join(
        outdir_path, 's{0}a_float.nii'.format(repetition))
    file_int2float(sa_gap_path, sa_float_path)
    #------ s1b
    # stored as uncompressed .nii because will get used by SPM
    sb_float_path = os.path.join(
        outdir_path, 's{0}b_float.nii'.format(repetition))
    file_int2float(sb_gap_path, sb_float_path)

    return [
        sa_float_path, sb_float_path,
        sa_phantom_gap_path, sb_phantom_gap_path]



def create_coregister(ref_path, source_path, other_path, register_prefix):
    """Initialise SPM co-registration

    This initialises the SPM co-registration nipype object with a set of
    pre-defined values (with the exception of input volumes which are
    user-defined).

    Args:
        ref_path (string): path to reference (target) image
        source_path (string): path to the image that will get
            registered to the reference
        other_path (string): path to any other images that will get
            registered to the reference
        register_prefix (string): co-registered output prefix

    Returns:
        coreg (nipype co-registered object): Instance of the
            co-register nipype class
    """
    coreg = spm.Coregister()
    coreg.inputs.target = ref_path
    coreg.inputs.source = source_path
    coreg.inputs.apply_to_files = [other_path]
    coreg.inputs.cost_function = 'nmi'
    coreg.inputs.separation = [4.0, 2.0]
    coreg.inputs.tolerance = [
        0.02, 0.02, 0.02, 0.001,
        0.001, 0.001, 0.01, 0.01,
        0.01, 0.001, 0.001, 0.001]
    coreg.inputs.fwhm = [7.0, 7.0]
    coreg.inputs.write_interp = 1
    coreg.inputs.write_wrap = [0, 0, 0]
    coreg.inputs.write_mask = False
    coreg.inputs.out_prefix = register_prefix

    return coreg



def file_spm_registration(ref_path, source_path, other_path, tempdir_path):
    """Rigid registration using SPM

    This code is based on the SPM registration originally written in
    Matlab by Ludovic Fillon.

    Args:
        ref_path (String): path to reference (target) image.
        source_path (String): path to source image. Will get modified
            (registered) by the function.
        other_path (String): path to any other image to be transformed
            according to the affine transformation from source to ref.
            Will get modified (affine transformed) by the function
        tempdir_path (string): path to temporary subfolder where images
            to be processed with SPM are duplicated and stored

    Returns:
        N/A
    """
    # duplicate source as SPM co-registration modifies the header
    #-- duplicate source
    source_filename = os.path.basename(source_path)
    source_temp_path = os.path.join(tempdir_path, source_filename)
    shutil.copyfile(source_path, source_temp_path)
    #-- duplicate other image
    other_filename = os.path.basename(other_path)
    other_temp_path = os.path.join(tempdir_path, other_filename)
    shutil.copyfile(other_path, other_temp_path)

    # co-register using SPM
    #-- create SPM co-register object
    register_prefix = 'r'
    coreg = create_coregister(
        ref_path, source_temp_path, other_temp_path, register_prefix)
    #-- run SPM co-registration
    coreg.run()

    # copy the output registered file to input (will erase original file)
    #-- source
    source_registered_path = os.path.join(
        tempdir_path, '{0}{1}'.format(register_prefix, source_filename))
    shutil.copyfile(source_registered_path, source_path)
    #-- other
    other_registered_path = os.path.join(
        tempdir_path, '{0}{1}'.format(register_prefix, other_filename))
    shutil.copyfile(other_registered_path, other_path)



def volume_addition(in_volume1, in_volume2):
    """Add two volumes together

    Args:
        in_volume1 (nibabel volume): data will be a [m,n,o] array
        in_volume2 (nibabel volume): data will be a [m,n,o] array

    Returns:
        out_volume (nibabel volume): data will be a [m,n,o] array, sum
            of in_volume1[array] and in_volume2[array], where both
            in_volume1[array] and in_volume2[array] have been reoriented
            to a canonical orientation ('RAS')
    """
    # initialise data and affine matrices from input volumes
    #-- convert both volumes to RAS orientation
    in_volume1_ras = nib.as_closest_canonical(in_volume1)
    in_volume2_ras = nib.as_closest_canonical(in_volume2)
    #-- volumes data and affine
    in_volume1_data = in_volume1_ras.get_data()
    in_volume1_affine = in_volume1_ras.affine.copy()
    in_volume2_data = in_volume2_ras.get_data()
    #-- remove NaN values
    in_volume1_data[np.isnan(in_volume1_data)] = 0
    in_volume2_data[np.isnan(in_volume2_data)] = 0
    #-- sanity check
    if in_volume1_data.shape != in_volume2_data.shape:
        raise ValueError('the input volumes must have the same size')
    # add volumes together
    out_volume_data = in_volume1_data+in_volume2_data
    out_volume_affine = in_volume1_affine.copy()
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_volume_addition(in_volume1_path, in_volume2_path, out_volume_path):
    """Add two volumes from files and save

    Read input volumes from files, add and save.

    Args:
        in_volume1_path (string): path to input volume 1
        in_volume2_path (string): path to input volume 2
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volumes
    in_volume1 = nib.load(in_volume1_path)
    in_volume2 = nib.load(in_volume2_path)
    # add volumes
    out_volume = volume_addition(in_volume1, in_volume2)
    # save output volume
    nib.save(out_volume, out_volume_path)



def volume_division(in_volume1, in_volume2):
    """Divide a volume by another one

    Args:
        in_volume1 (nibabel volume): data will be a [m,n,o] array
        in_volume2 (nibabel volume): data will be a [m,n,o] array

    Returns:
        out_volume (nibabel volume): data will be a [m,n,o] array,
            division of in_volume1[array] by in_volume2[array], where
            both in_volume1[array] and in_volume2[array] have been
            reoriented to a canonical orientation ('RAS')
    """
    # read input volumes
    #-- convert both volumes to RAS orientation
    in_volume1_ras = nib.as_closest_canonical(in_volume1)
    in_volume2_ras = nib.as_closest_canonical(in_volume2)
    #-- volumes data and affine
    in_volume1_data = in_volume1_ras.get_data()
    in_volume1_affine = in_volume1_ras.affine.copy()
    in_volume2_data = in_volume2_ras.get_data()
    #-- sanity check
    if in_volume1_data.shape != in_volume2_data.shape:
        raise ValueError('the input volumes must have the same size')
    #-- get rid of NaN values
    in_volume1_data[np.isnan(in_volume1_data)] = 0
    in_volume2_data[np.isnan(in_volume2_data)] = 0

    # divide the two volumes
    #-- check volume 2 pixels 0-intensities
    volume2_0_x, volume2_0_y, volume2_0_z = np.where(in_volume2_data == 0)
    in_volume2_data[in_volume2_data == 0] = 1
    #-- main division
    out_volume_data = in_volume1_data/in_volume2_data
    #-- re-process volume 2 0-intensity pixels
    out_volume_data[volume2_0_x, volume2_0_y, volume2_0_z] = 0

    # save output
    out_volume_affine = in_volume1_affine.copy()
    out_volume = nib.Nifti1Image(out_volume_data, out_volume_affine)

    return out_volume



def file_volume_division(in_volume1_path, in_volume2_path, out_volume_path):
    """Divide two volumes from files and save

    Read input volumes from files, divide and save.

    Args:
        in_volume1_path (string): path to input volume 1
        in_volume2_path (string): path to input volume 2
        out_volume_path (string): path to output volume

    Returns:
        N/A
    """
    # read input volumes
    in_volume1 = nib.load(in_volume1_path)
    in_volume2 = nib.load(in_volume2_path)
    # add volumes
    out_volume = volume_division(in_volume1, in_volume2)
    # save output volume
    nib.save(out_volume, out_volume_path)



def gzip_images(impath_list, dirpath):
    """Gzip compress all images in a list

    Will copy each image in the list to a compressed file and remove the
    (non-compressed) original file

    Args:
        impath_list (list of strings): list of paths to the images that
            will be compressed
        dirpath (string): path to folder containing the images to be
            deleted. Used to perform a 'safe' deletion of the
            original uncompressed images after we have copied them to a
            compressed version.

    Returns:
        N/A
    """
    for impath in impath_list:
        # check if exists
        if not os.path.isfile(impath):
            error_msg = 'Error: impath {0} does not exist.'.format(impath)
            raise IOError(error_msg)
        # get foldername and filename associated with path to image
        imfoldername = os.path.dirname(impath)
        imfilename = os.path.basename(impath)
        # separate extension in filename
        imfilename_main = os.path.splitext(imfilename)[0]
        imfilename_ext = os.path.splitext(imfilename)[1]
        # check if the image is of type .nii
        if imfilename_ext != '.nii':
            error_msg = 'Error: image extension should be .nii'
            raise IOError(error_msg)
        # compress with gzip
        imgzpath = "{0}/{1}.nii.gz".format(imfoldername, imfilename_main)
        with open(impath, 'rb') as imfile:
            with gzip.open(imgzpath, 'wb') as imgzfile:
                shutil.copyfileobj(imfile, imgzfile)
        # remove original non-compressed image
        safe_remove(impath, dirpath)



def part1(
        highres_r1s1_path,
        highres_r1s2_path,
        highres_r2s1_path,
        highres_r2s2_path,
        lowres_path,
        debugdir_path):
    """Pre-processing prior to SPM registration

    The function will process each slab as follows:
    - duplicate slices of the volume along the y axis
    - fill corresponding slices with the gaps that represent the real
        acquisition
    - create a phantom corresponding to each slab

    Args:
        highres_r1s1_path (string): path to first repetition, first slab
        highres_r1s2_path (string): path to first repetition, second
            slab
        highres_r2s1_path (string): path to second repetition, first
            slab
        highres_r2s2_path (string): path to first repetition, second
            slab
        lowres_path (string): path to low resolution volume
        debugdir_path (string): path to 'debug' subfolder where all
            intermediary images are stored

    Returns:
        lr1a_path (string): low res repeated - first repetion, first
            slab
        s1a_float_path (string): path to first slab of first repetition
            converted to float
        s1a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of first repetition
        lr1b_path (string): low res repeated - first repetion, second
            slab
        s1b_float_path (string): path to second slab of first repetition
            converted to float
        s1b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of first repetition
        lr2a_path (string): low res repeated - second repetion, first
            slab
        s2a_float_path (string): path to first slab of second repetition
            converted to float
        s2a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of second repetition
        lr2b_path (string): low res repeated - second repetion, second
            slab
        s2b_float_path (string): path to second slab of second
            repetition converted to float
        s2b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of second repetition
    """
    # copy files into the output folder (debug subfolder)
    print('copy files into the output folder')
    #-- copy of high-res and low-res volumes
    #---- first (1) repetition, first slab (a)
    s1a_path = os.path.join(debugdir_path, 's1a.nii')
    nii_copy(highres_r1s1_path, s1a_path)
    #---- first (1) repetition, second slab (b)
    s1b_path = os.path.join(debugdir_path, 's1b.nii')
    nii_copy(highres_r1s2_path, s1b_path)
    #---- second (1) repetition, first slab (a)
    s2a_path = os.path.join(debugdir_path, 's2a.nii')
    nii_copy(highres_r2s1_path, s2a_path)
    #---- second (1) repetition, second slab (b)
    s2b_path = os.path.join(debugdir_path, 's2b.nii')
    nii_copy(highres_r2s2_path, s2b_path)
    #-- copy the low-res volumes four times (later used as
    # initialisation to a slab registration)
    #---- first (1) repetition, first slab (a)
    lr1a_path = os.path.join(debugdir_path, 'lr_1a.nii')
    nii_copy(lowres_path, lr1a_path)
    #---- first (1) repetition, second slab (b)
    lr1b_path = os.path.join(debugdir_path, 'lr_1b.nii')
    nii_copy(lowres_path, lr1b_path)
    #---- second (2) repetition, first slab (a)
    lr2a_path = os.path.join(debugdir_path, 'lr_2a.nii')
    nii_copy(lowres_path, lr2a_path)
    #---- second (2) repetition, second slab (b)
    lr2b_path = os.path.join(debugdir_path, 'lr_2b.nii')
    nii_copy(lowres_path, lr2b_path)

    # process repetitions
    #-- first repetition
    [
        s1a_float_path, s1b_float_path,
        s1a_phantom_gap_path, s1b_phantom_gap_path] = process_repetition(
            '1', s1a_path, s1b_path, debugdir_path)
    #-- second repetition
    [
        s2a_float_path, s2b_float_path,
        s2a_phantom_gap_path, s2b_phantom_gap_path] = process_repetition(
            '2', s2a_path, s2b_path, debugdir_path)

    # gzip all the images that will not be fed to SPM in the second
    # part or the recombination pipeline (SPM cannot read .gz
    # compressed images)
    gzip_images([s1a_path, s1b_path, s2a_path, s2b_path], debugdir_path)

    return [
        lr1a_path, s1a_float_path, s1a_phantom_gap_path,
        lr1b_path, s1b_float_path, s1b_phantom_gap_path,
        lr2a_path, s2a_float_path, s2a_phantom_gap_path,
        lr2b_path, s2b_float_path, s2b_phantom_gap_path]



def part2(
        lr1a_path, s1a_float_path, s1a_phantom_gap_path,
        lr1b_path, s1b_float_path, s1b_phantom_gap_path,
        lr2a_path, s2a_float_path, s2a_phantom_gap_path,
        lr2b_path, s2b_float_path, s2b_phantom_gap_path,
        debugdir_path,
        tempdir_path):
    """SPM registration

    Launch the SPM registrations.
    The function will modify the all the input lr[]_path and
    s[]_phantom_path images.

    Args:
        lr1a_path (string): low res repeated - first repetion, first
            slab
        s1a_float_path (string): path to first slab of first repetition
            converted to float
        s1a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of first repetition
        lr1b_path (string): low res repeated - first repetion, second
            slab
        s1b_float_path (string): path to second slab of first repetition
            converted to float
        s1b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of first repetition
        lr2a_path (string): low res repeated - second repetion, first
            slab
        s2a_float_path (string): path to first slab of second repetition
            converted to float
        s2a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of second repetition
        lr2b_path (string): low res repeated - second repetion, second
            slab
        s2b_float_path (string): path to second slab of second
            repetition converted to float
        s2b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of second repetition
        debugdir_path (string): path to 'debug' subfolder where all
            intermediary iamges are stored
        tempdir_path (string): path to temporary subfolder where images
            to be processed with SPM are duplicated and stored

    Returns:
        N/A
    """
    # register first repetition, first slab
    print('SPM register - first repetition, first slab')
    file_spm_registration(
        lr1a_path, s1a_float_path, s1a_phantom_gap_path, tempdir_path)

    # register first repetition, second slab
    print('SPM register - first repetition, second slab')
    file_spm_registration(
        lr1b_path, s1b_float_path, s1b_phantom_gap_path, tempdir_path)

    # register second repetition, first slab
    print('SPM register - second repetition, first slab')
    file_spm_registration(
        lr2a_path, s2a_float_path, s2a_phantom_gap_path, tempdir_path)

    # register second repetition, second slab
    print('SPM register - second repetition, second slab')
    file_spm_registration(
        lr2b_path, s2b_float_path, s2b_phantom_gap_path, tempdir_path)

    # gzip all the images that are not given as input to part 3 of
    # the recombination algorithm
    gzip_images([lr1a_path, lr1b_path, lr2a_path, lr2b_path], debugdir_path)



def part3(
        s1a_float_path, s1a_phantom_gap_path,
        s1b_float_path, s1b_phantom_gap_path,
        s2a_float_path, s2a_phantom_gap_path,
        s2b_float_path, s2b_phantom_gap_path,
        debugdir_path,
        tempdir_path,
        outdir_path):
    """Combine volumes after SPM registration

    The function will combine for each repetition the first and second
    block, then will combine the two repetitions together, using
    volumes registered with SPM.

    Args:
        s1a_float_path (string): path to first slab of first repetition
            converted to float - SPM registered to low-res volume
        s1a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of first repetition
            - SPM aligned to low-res volume
        s1b_float_path (string): path to second slab of first repetition
            converted to float - SPM registered to low-res volume
        s1b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of first repetition
            - SPM aligned to low-res volume
        s2a_float_path (string): path to first slab of second repetition
            converted to float - SPM registered to low-res volume
        s2a_phantom_gap_path (string): path to phantom (with gap)
            corresponding to first slab of second repetition
            - SPM aligned to low-res volume
        s2b_float_path (string): path to second slab of second
            repetition converted to float - SPM registered to low-res
            volume
        s2b_phantom_gap_path (string): path to phantom (with gap)
            corresponding to second slab of second repetition
            - SPM aligned to low-res volume
        debugdir_path (string): path to 'debug' subfolder where all
            intermediary iamges are stored
        tempdir_path (string): path to temporary subfolder where images
            to be processed with SPM are duplicated and stored
            Used here to know what files to delete
        outdir_path (string): path to output dir, where results will
            get stored

    Returns:
        N/A
    """
    # Add blocks
    print('Add blocks/repetitions')
    #-- main slabs
    #---- First repetition: add slabs
    print('First repetition - add slabs')
    rs1_float_path = os.path.join(outdir_path, 'rs1_float.nii.gz')
    file_volume_addition(s1a_float_path, s1b_float_path, rs1_float_path)
    #---- Second repetition: add slabs
    print('Second repetition - add slabs')
    rs2_float_path = os.path.join(outdir_path, 'rs2_float.nii.gz')
    file_volume_addition(s2a_float_path, s2b_float_path, rs2_float_path)
    #---- Add repetitions
    print('Add repetitions')
    rs_float_path = os.path.join(outdir_path, 'rs_float.nii.gz')
    file_volume_addition(rs1_float_path, rs2_float_path, rs_float_path)
    #-- phantoms
    #---- First repetition: add slabs
    print('Phantoms: first repetition - add slabs')
    s1_phantom_gap_path = os.path.join(
        debugdir_path, 'phantom_one_gap_s1.nii.gz')
    file_volume_addition(
        s1a_phantom_gap_path, s1b_phantom_gap_path, s1_phantom_gap_path)
    #---- Second repetition: add slabs
    print('Phantoms: second repetition - add slabs')
    s2_phantom_gap_path = os.path.join(
        debugdir_path, 'phantom_one_gap_s2.nii.gz')
    file_volume_addition(
        s2a_phantom_gap_path, s2b_phantom_gap_path, s2_phantom_gap_path)
    #---- Add repetitions
    print('Phantoms: add repetitions')
    s_phantom_gap_path = os.path.join(debugdir_path, 'phantom_one_gap_s.nii.gz')
    file_volume_addition(
        s1_phantom_gap_path, s2_phantom_gap_path, s_phantom_gap_path)

    # Normalise blocks using phantoms
    print('Normalise blocks using phantoms')
    #-- 'rs'
    print('Normalise \'rs\'')
    rs_float_ponderated_path = os.path.join(
        outdir_path, 'rs_float_ponderated.nii.gz')
    file_volume_division(
        rs_float_path, s_phantom_gap_path, rs_float_ponderated_path)
    #-- 'rs1'
    print('Normalise \'rs1\'')
    rs1_float_ponderated_path = os.path.join(
        outdir_path, 'rs1_float_ponderated.nii.gz')
    file_volume_division(
        rs1_float_path, s1_phantom_gap_path, rs1_float_ponderated_path)
    #-- 'rs2'
    print('Normalise \'rs2\'')
    rs2_float_ponderated_path = os.path.join(
        outdir_path, 'rs2_float_ponderated.nii.gz')
    file_volume_division(
        rs2_float_path, s2_phantom_gap_path, rs2_float_ponderated_path)
    #-- 'rs12' -> add 'rs1' and 'rs2'
    print('\'rs_1_2\': \'rs1\' + \'rs2\'')
    rs12_float_ponderated_path = os.path.join(
        outdir_path, 'rs_1_2_float_ponderated.nii.gz')
    file_volume_addition(
        rs1_float_ponderated_path,
        rs2_float_ponderated_path,
        rs12_float_ponderated_path)

    # gzip all images that have not been gzipped yet
    gzip_images(
        [
            s1a_float_path, s1a_phantom_gap_path,
            s1b_float_path, s1b_phantom_gap_path,
            s2a_float_path, s2a_phantom_gap_path,
            s2b_float_path, s2b_phantom_gap_path],
        debugdir_path)

    # remove temporary folder
    if os.path.isdir(tempdir_path):
        shutil.rmtree(tempdir_path)
    else:
        error_msg = 'Error: folder {0} does not exist'.format(tempdir_path)
        raise IOError(error_msg)




def show_completion_message(outdir_path, debugdir_path):
    """Show message to indicate successfull completion

    Show the list of files that have been created and give the path to
    intermediary ('debug') and temporary ('temp') folders that can be
    removed to save space.

    Args:
        outdir_path (string): absolute path to output dir, where
            results will get stored
        debugdir_path (string): path to 'debug' subfolder where all
            intermediary images are stored
        tempdir_path (string): path to temporary subfolder where images
            to be processed with SPM are duplicated and stored

    Returns:
        N/A
    """
    print('Recombination code successfully run.')
    print('')
    print('Temporary data stored in:')
    print('- {0}'.format(debugdir_path))
    print('Please remove the above folders to save storage space.')
    print('')
    print('Output data to be found in')
    print(outdir_path)



def main():
    """Recombine code: main function

    Launch in turn the three parts of the recombination algorithm.
    Takes the following input:
        - rep1s1_path: path to first slab of the first repetition
        - rep1s2_path: path to second slab of the first repetition
        - rep2s1_path: path to first slab of the second repetition
        - rep2s2_path: path to second slab of the second repetition
        - lowres_path: path to low-resolution volume
        - outdir_path: path to folder where results will be stored
    Will output the following recombined file in the output directory
        - rs_float_ponderated.nii.gz: whole recombined
        - rs1_float_ponderated.nii.gz: first repetition recombined
        - rs2_float_ponderated.nii.gz: second repetition recombined
        - rs_1_2_float_ponderated.nii.gz: first repetition recombined
            + second repetition recombined

    Args:
        N/A

    Returns:
        N/A
    """
    # read command line arguments
    if len(sys.argv) != 7:
        usage()
    #-- slabs 1/2 of repetitions 1/2
    rep1s1_path = sys.argv[1]
    rep1s2_path = sys.argv[2]
    rep2s1_path = sys.argv[3]
    rep2s2_path = sys.argv[4]
    #-- low-resolution image
    lowres_path = sys.argv[5]
    #-- output folder
    outdir_path = sys.argv[6]

    # prepare folders
    [debugdir_path, tempdir_path] = prepare_folders(outdir_path)

    # part 1 - prepare input to SPM
    [
        lr1a_path, s1a_float_path, s1a_phantom_gap_path,
        lr1b_path, s1b_float_path, s1b_phantom_gap_path,
        lr2a_path, s2a_float_path, s2a_phantom_gap_path,
        lr2b_path, s2b_float_path, s2b_phantom_gap_path] = part1(
            rep1s1_path,
            rep1s2_path,
            rep2s1_path,
            rep2s2_path,
            lowres_path,
            debugdir_path)

    # part 2 - register with SPM
    part2(
        lr1a_path, s1a_float_path, s1a_phantom_gap_path,
        lr1b_path, s1b_float_path, s1b_phantom_gap_path,
        lr2a_path, s2a_float_path, s2a_phantom_gap_path,
        lr2b_path, s2b_float_path, s2b_phantom_gap_path,
        debugdir_path,
        tempdir_path)

    # part 3 - register with SPM
    part3(
        s1a_float_path, s1a_phantom_gap_path,
        s1b_float_path, s1b_phantom_gap_path,
        s2a_float_path, s2a_phantom_gap_path,
        s2b_float_path, s2b_phantom_gap_path,
        debugdir_path,
        tempdir_path,
        outdir_path)

    # show completion_message
    show_completion_message(outdir_path, debugdir_path)



if __name__ == "__main__":
    main()
