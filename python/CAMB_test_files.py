from __future__ import print_function
import os
import subprocess
import argparse
import fnmatch
import time
import sys
import shutil

parser = argparse.ArgumentParser(description='Run CAMB tests')
parser.add_argument('ini_dir', help='ini file directory')
parser.add_argument('--make_ini', action='store_true', help='if set, output ini files to ini_dir')
parser.add_argument('--out_files_dir', default='test_outputs', help='output files directory')
parser.add_argument('--base_settings', default='params.ini', help='settings to include as defaults for all combinations')
parser.add_argument('--no_run_test', action='store_true', help='don''t run tests on files')
parser.add_argument('--prog', default='./camb', help='executable to run')
parser.add_argument('--clean', action='store_true', help='delete output dir before run')
parser.add_argument('--diff_to', help='output directory to compare to, e.g. test_outputs2')
parser.add_argument('--diff_tolerance', help='the tolerance for the numerical diff [default: 1e-5]', default=1e-5)
parser.add_argument('--verbose', action='store_true', help='during diff_to print more error messages')

args = parser.parse_args()

prog = os.path.abspath(args.prog)
if not os.path.exists(args.ini_dir):
    os.mkdir(args.ini_dir)

out_files_dir = os.path.join(args.ini_dir, args.out_files_dir)

if args.clean:
    if os.path.exists(out_files_dir): shutil.rmtree(out_files_dir)

if not os.path.exists(out_files_dir):
    os.mkdir(out_files_dir)

def runScript(fname):
    now = time.time()
    try:
        res = str(subprocess.check_output([prog, fname]))
        code = 0
    except subprocess.CalledProcessError as e:
        res = e.output
        code = e.returncode
    return time.time() - now, res, code

def getInis(ini_dir):
    inis = []
    for fname in os.listdir(ini_dir):
        if fnmatch.fnmatch(fname, '*.ini'):
            inis.append(os.path.join(args.ini_dir, fname))
    return inis


def getTestParams():
    params = []

    params.append(['base'])

    for lmax in [1000, 2000, 2500, 3000, 4500, 6000]:
        params.append(['lmax%s' % lmax, 'l_max_scalar = %s' % lmax, 'k_eta_max_scalar  = %s' % (lmax * 2.5)])

    for lmax in [1000, 2000, 2500, 3000, 4500]:
        params.append(['nonlin_lmax%s' % lmax, 'do_nonlinear =2', 'get_transfer= T', 'l_max_scalar = %s' % lmax, 'k_eta_max_scalar  = %s' % (lmax * 2.5)])

    for lmax in [400, 600, 1000]:
        params.append(['tensor_lmax%s' % lmax, 'get_tensor_cls = T', 'l_max_tensor = %s' % lmax, 'k_eta_max_tensor  = %s' % (lmax * 2)])

    params.append(['tensoronly', 'get_scalar_cls=F', 'get_tensor_cls = T'])
    params.append(['tensor_tranfer', 'get_scalar_cls=F', 'get_tensor_cls = T', 'get_transfer= T', 'transfer_high_precision = T'])
    params.append(['tranfer_only', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_high_precision = F'])
    params.append(['tranfer_highprec', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_high_precision = T'])

    params.append(['all', 'get_scalar_cls=T', 'get_tensor_cls = T', 'get_transfer= T'])
    params.append(['all_nonlin1', 'get_scalar_cls=T', 'get_tensor_cls = T', 'get_transfer= T', 'do_nonlinear=1'])
    params.append(['all_nonlin2', 'get_scalar_cls=T', 'get_tensor_cls = T', 'get_transfer= T', 'do_nonlinear=2'])
    params.append(['all_nonlinhigh', 'get_scalar_cls=T', 'get_tensor_cls = T', 'get_transfer= T', 'do_nonlinear=2', 'transfer_high_precision = T'])
    params.append(['tranfer_delta10', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_high_precision = T', 'transfer_k_per_logint =10'])
    params.append(['tranfer_redshifts', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_num_redshifts=2']
                  + ['transfer_redshift(1)=1', 'transfer_redshift(2)=0.7', 'transfer_filename(2)=transfer_out2.dat', 'transfer_matterpower(2)=matterpower2.dat']
                  )
    params.append(['tranfer_redshifts2', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_num_redshifts=2']
                  + ['transfer_redshift(1)=0.7', 'transfer_redshift(2)=0', 'transfer_filename(2)=transfer_out2.dat', 'transfer_matterpower(2)=matterpower2.dat']
                  )


    params.append(['tranfer_nonu', 'get_scalar_cls=F', 'get_transfer= T', 'transfer_power_var = 8'])


    params.append(['zre', 're_use_optical_depth = F', 're_redshift  = 8.5'])
    params.append(['nolens', 'lensing = F'])
    params.append(['noderived', 'derived_parameters = F'])
    params.append(['no_rad_trunc', 'do_late_rad_truncation   = F'])

    for acc in [0.95, 1.1, 1.5, 2.2]:
        params.append(['accuracy_boost%s' % acc, 'accuracy_boost = %s' % acc])

    for acc in [1, 1.5, 2]:
        params.append(['l_accuracy_boost%s' % acc, 'l_accuracy_boost = %s' % acc])

    params.append(['acc', 'l_accuracy_boost =2', 'accuracy_boost=2'])
    params.append(['accsamp', 'l_accuracy_boost =2', 'accuracy_boost=2', 'l_sample_boost = 1.5'])

    params.append(['mu_massless', 'omnuh2 =0'])

    for mnu in [0, 0.01, 0.03, 0.1]:
        omnu = mnu / 100.
        params.append(['mu_mass%s' % mnu, 'omnuh2 =%s' % omnu, 'massive_neutrinos  = 3'])
    params.append(['mu_masssplit', 'omnuh2 =0.03', 'massive_neutrinos = 1 1', 'nu_mass_fractions=0.2 0.8',
                    'nu_mass_degeneracies = 1 1', 'nu_mass_eigenstates = 2', 'massless_neutrinos = 1.046'])



    for etamax in [10000, 14000, 20000, 40000]:
        params.append(['acclens_ketamax%s' % etamax, 'do_nonlinear = 2', 'l_max_scalar  = 6000', 'k_eta_max_scalar  = %s' % etamax, 'accurate_BB = F'])

    for etamax in [10000, 14000, 20000, 40000]:
        params.append(['acclensBB_ketamax%s' % etamax, 'do_nonlinear = 2', 'l_max_scalar = 2500', 'k_eta_max_scalar  = %s' % etamax, 'accurate_BB = T'])

    pars = {
     'ombh2':[ 0.0219, 0.0226, 0.0253],
     'omch2':[ 0.1, 0.08, 0.15],
     'omk':[ 0, -0.03, 0.04, 0.001, -0.001],
     'hubble':[ 62, 67, 71, 78],
     'w':[ -1.2, -1, -0.98, -0.75],
     'helium_fraction':[ 0.21, 0.23, 0.27],
     'scalar_spectral_index(1)' :[0.94, 0.98],
     'scalar_nrun(1)' :[-0.015, 0, 0.03],
      're_optical_depth': [0.03, 0.05, 0.08, 0.11],
    }

    for par, vals in pars.iteritems():
        for val in vals:
            params.append(['%s_%.3f' % (par, val), 'get_transfer= T', 'do_nonlinear=1', 'transfer_high_precision = T',
                           '%s = %s' % (par, val)])
    return params

def list_files(file_dir):
    return [f for f in os.listdir(file_dir) if not '.ini' in f]

def output_file_num(file_dir):
    return len(list_files(file_dir))

def makeIniFiles():
    params = getTestParams()
    inis = []
    base_ini = 'inheritbase_'+os.path.basename(args.base_settings)
    shutil.copy(args.base_settings, os.path.join(args.ini_dir,base_ini))
    for pars in params:
        name = 'params_' + pars[0]
        fname = os.path.join(args.ini_dir, name + '.ini')
        inis.append(fname)
        with open(fname, 'w') as f:
            f.write('output_root=' + os.path.join(out_files_dir, name) +
                    '\nDEFAULT(' + base_ini + ')\n' + '\n'.join(pars[1:]))
    return inis

def num_unequal(filename):
    # Check whether two files are unequal for the given tolerance
    import math
    orig_name = os.path.join(args.ini_dir, args.diff_to, filename)
    with open(orig_name) as f:
        origMat = [[float(x) for x in ln.split()] for ln in f]
    new_name = os.path.join(args.ini_dir, args.out_files_dir, filename)
    with open(new_name) as f:
        newMat = [[float(x) for x in ln.split()] for ln in f]
    if len(origMat) != len(newMat):
        if args.verbose:
            print('num rows do not match in %s' % filename)
        return True
    row = 0
    #print(origMat)
    for o_row, n_row in zip(origMat, newMat):
        row = row + 1
        col = 0
        if len(o_row) != len(n_row):
            if args.verbose:
                print('num columns do not match in %s' % filename)
            return True
        for o,n in zip(o_row, n_row):
            col = col + 1
            if math.fabs(o - n)>= args.diff_tolerance:
                if args.verbose:
                    print('value mismatch at %d, %d of %s: |%f - %f| > %f' % (row, col, filename, o, n, args.diff_tolerance))
                return True
    return False

if args.diff_to:
    import filecmp
    out_files_dir2 = os.path.join(args.ini_dir, args.diff_to)
    match, mismatch, errors = filecmp.cmpfiles(out_files_dir, out_files_dir2,
         list(set(list_files(out_files_dir)) | set(list_files(out_files_dir2)))   )
    if len(errors) and len(errors) != 1 and errors[0] != args.diff_to:
        len_errors = len(errors) - 1
        print('Missing/Extra files:')
        for err in errors:
            # Only print files that are not the diff_to
            if (err != args.diff_to):
                print('  '+err)
    else:
        len_errors = 0
    if len(mismatch):
        numerical_mismatch = []
        for f in mismatch:
            if num_unequal(f):
                numerical_mismatch.append(f)
        if len(numerical_mismatch):
            print('Files do not match:')
            for err in numerical_mismatch:
                print('  '+err)
        len_num_mismatch = len(numerical_mismatch)
    else:
        len_num_mismatch = 0

    print("Done with %s mismatches and %s extra/missing files"%(len_num_mismatch, len_errors))
    if len_errors > 0 or len_num_mismatch > 0:
       sys.exit(1)
    else:
        sys.exit()

if args.make_ini:
    inis = makeIniFiles()
else:
    inis = getInis(args.ini_dir)
if not args.no_run_test:
    errors = 0
    files = output_file_num(out_files_dir)
    if files:
        print('Output directory is not empty (run with --clean to force delete): %s' % out_files_dir)
        sys.exit()
    start = time.time()
    error_list = []
    for ini in inis:
        print(os.path.basename(ini) + '...')
        timing, output, return_code = runScript(ini)
        if return_code:
            print('error %s' % return_code)
        nfiles = output_file_num(out_files_dir)
        if nfiles > files:
            msg = '..OK, produced %s files in %.2fs' % (nfiles - files, timing)
        else:
            errors += 1
            error_list.append(os.path.basename(ini))
            msg = '..no files in %.2fs' % (timing)
        print(msg)
        files = nfiles
    print('Done, %s errors in %.2fs (outputs not checked)' % (errors, time.time() - start))
    if errors:
        print('Fails in : %s' % error_list)
