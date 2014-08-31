#!/usr/bin env python
from shutil import copytree, rmtree, copyfile
from distutils.core import setup
from os.path import expanduser
import os
import sys
import glob
import subprocess

# expand my home directory
home = expanduser("~")

# Hardcode these in
library_dir = os.path.abspath(os.path.join(home,"/lib/pyig/data_dir"))
bin_path = os.path.abspath(os.path.join(home,"/bin/"))
python_lib = os.path.abspath(os.path.join(home,"/python_lib/")

print "Checking if {0} and {1} exists".format(library_dir, bin_path)
if not os.path.exists(library_dir):
    os.makedirs(library_dir)
if not os.path.exists(bin_path):
    os.makedirs(bin_path)
if not os.path.exists(python_lib):
    os.makedirs(python_lib)


print "Checking Permissions for {0} and {1}".format(library_dir, bin_path)
if not os.access(library_dir, os.W_OK) and not os.access(bin_path, os.W_OK):
    raise OSError("Can't install libraries or binaries at {0} and {1}, permission error, seek administrator".format(
        library_dir, bin_path))


if sys.version_info < (2, 7, 5):
    raise OSError("You need python 2.7.5 or greater")

try:
    import Bio
    print "Have {0}".format(Bio.__file__)
except Exception:
    raise ImportError("You need the Biopython Package...see documentation")


if os.path.exists(library_dir):
    print "Deleting old copy of {0}".format(library_dir)
    rmtree(library_dir)
    copytree('data_dir', library_dir)
else:
    copytree('data_dir', library_dir)


def get_igblast():
    print "Determining OS"
    igblasts = glob.glob('igblast/igblastn_*')
    for binary in igblasts:
        try:
            subprocess.check_call([binary, '-h'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return os.path.abspath(binary)
        except:
            continue
        return ""

# copy igblastn
igblast = get_igblast()
if igblast:
    new_igblast = os.path.join(bin_path,"/igblastn")
    print "Copying {0} to {1}".format(igblast, new_igblast)
    copyfile(igblast, new_igblast)
    print "Changing directory permissions of {0}".format(new_igblast)
    os.chmod(new_igblast, 0755)
else:
    print "Don't have a Igblastn that will run, \
           please see documentation to compile yourself, \
           press anykey to continue"
    raw_input()

#python site_accre_local.setup.py install --install-lib  ~/python_lib/ --install-scripts ~/bin
setup(name='PyIg',
      version='1.1',
      description='Python Immunoglobulin Analysis Tools',
      author='Jordan Willis',
      author_email='jwillis0720@gmail.com',
      packages=['pyig.backend', 'pyig.commandline', 'pyig'],
      package_dir={'pyig': 'src/pyig'},
      scripts=['src/pyig/commandline/PyIg'])
