#! /usr/bin/python

"""Code to check whether SPM can be found by Matlab

This will run the 'which SPM' inside Matlab, parse the output and return
the path to Matlab is found.

# This code was developed by Alexis Guyot at the ARAMIS lab.

"""

import os
import argparse
import nipype.interfaces.matlab as mlab


def read_cli_args():
    """Read command-line interface arguments

    Parse the input to the command line with the argparse module.

    Args:
        N/A

    Returns:
        args (argparse.Namespace): parsed arguments
        cli_usage (string): command-line interface usage message
    """
    # read command line arguments
    cli_description = 'Code to check whether Matlab has access to the'
    cli_description = '{0} SPM folder or not.'.format(cli_description)
    parser = argparse.ArgumentParser(description=cli_description)
    # no arguments to be parsed
    # parse all arguments
    args = parser.parse_args()


def check_system_spm_available():
    """Check SPM can be found by Matlab

    Make sure SPM can be found by Matlab and terminate the program if it
    cannot.

    Args:
        N/A

    Returns:
        spm_found (Boolean): True if SPM folder in Matlab path, False
            otherwise
        spm_path (string): path to the SPM folder found by Matlab.
            Retrieved with the 'which spm' Matlab command.
            None if not found
        spmscript_path (string): path to the spm.m in the SPM folder
            found by Matlab.
            None if SPM folder not found.
    """
    # initialise output variables
    #-- SPM found boolean
    spm_found = False
    #-- SPM folder
    spm_path = None
    #-- SPM script ([folder]/spm.m)
    spmscript_path = None

    # Check if SPM path can be found by Matlab
    # (e.g., if file $HOME/matlab/startup.m contains the line
    # addpath [spm_folder])
    res = mlab.MatlabCommand(script='which spm', mfile=False).run()
    whichspm_output = res.runtime.stdout.splitlines()[-2]
    if whichspm_output == '\'spm\' not found.':
        #-- SPM found boolean
        spm_found = False
        #-- SPM folder
        spm_path = None
        #-- SPM script ([folder]/spm.m)
        spmscript_path = None
    else:
        # SPM found
        spm_found = True
        spmscript_path = whichspm_output
        spm_path = os.path.dirname(spmscript_path)

    return spm_found, spm_path, spmscript_path


def main():
    """Check SPM: main function

    Check whether Matlab can access the spm.m script or not (i.e., if
    the path to the SPM folder has been properly set up).

    Args:
        N/A

    Returns:
        N/A
    """
    # parse command-line arguments
    read_cli_args()

    # check SPM available
    spm_found, spm_path, dummy = check_system_spm_available()

    # output message depending on whether SPM was found or not
    if spm_found:
        # SPM found
        print('The SPM was found by Matlab.')
        print('SPM path: {0}'.format(spm_path))
    else:
        # SPM not found
        print('The SPM was NOT found by Matlab.')
        print('Please use script recombine.py with -spm [SPM_PATH] flag.')


if __name__ == "__main__":
    main()
