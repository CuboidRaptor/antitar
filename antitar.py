# antitar
import logging # imports that I need to configure logging (so I can log other imports)
import os
import sys
import datetime
import tarfile
import argparse
import ntpath
import zipfile
import shutil
import platform
import patoolib

from send2trash import send2trash
from py7zr import unpack_7zarchive

# please, please don't ask about this function randomly defined at the top, I know, I hate it too
def getcfl():
    # holy fuck pyinstaller aslkdjlsdkj
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # running in pyinstaller shitpile
        out = sys.executable

    else:
        # running in calm python dev env
        out = __file__

    return os.path.abspath(procpath(out)) # reprocess the garbage because windows can't do shit

# oh and this function too (my eyes!)
def procpath(pth, slashcompat=True, dbackslash=False):
    # windows filepaths are a piece of dog shat so I fixed it
    # (sorta)
    if slashcompat:
        # we want chad linux style file paths
        pth = pth.replace("\\", "/").replace("//", "/")

    else:
        # we want disgusting windows style paths
        pth = pth.replace("/", "\\").replace("\\\\", "\\")

        if dbackslash:
            # double backslashes are amazing and also terrible
            pth=pth.replace("\\", "\\\\")
            # btw windows I hate you

    return pth

try:
    # make logs folder
    flag = False
    os.mkdir(procpath(os.path.dirname(getcfl())) + "/logs")

except FileExistsError:
    flag = True # add warning later once logger works

logging.basicConfig( # hi Mr. Logger
    level=logging.DEBUG,
    filename=procpath(os.path.dirname(getcfl())) + "/logs/" + datetime.datetime.now().isoformat().replace(":", "-") + ".log",
    format="#%(levelname)s:%(name)s %(message)s"
)

if flag:
    logging.warning("Logs folder exists")

# actual import poo-poo that no one cares about, not even me, the programmer
print("Starting...")
#"""

logging.debug("Defining functions and stuff what do you want from me")

class AttemptedExploitException(Exception):
    # I just wanted funni name exception shut up I know how to code properly
    pass

class UnsupportedFileTypeException(Exception):
    pass # yay

def is_within_directory(directory, target):
    # I don't even know what this is but I mean Trellix wrote it what could go wrong
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)
    prefix = os.path.commonprefix([abs_directory, abs_target])

    return prefix == abs_directory

def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    # thank you TrellixVuln for realizing that I'm a dipshit
    # (CVE-2007-4559 patch)
    global fpath

    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)

        if not is_within_directory(path, member_path):
            logging.error(f"Attempted CVE-2007-4559 exploit (be careful when extracting archive!!), file \"{member.name}\"")

            raise AttemptedExploitException("Attempted Path Traversal in Tarfile (CVE-2007-4559)")

    tar.extractall(path, members, numeric_owner=numeric_owner)

logging.debug("Creating argparser...")
p = argparse.ArgumentParser(description="Decompress .tar.*/archive files") # here ya go argparse, deal with my shit
p.add_argument(
    "File",
    metavar="file",
    type=str,
    help="the path to the .tar.*/archive file"
)

logging.debug("Actually parsing args (wow!)...")
args = p.parse_args()
logging.info(f"args.File: {args.File}")

logging.debug("Verifying file type...") # check file extension
ftypes = [
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.xz",
    ".tar.bz2",
    ".zip",
    ".7z",
    ".rar"
]
valid = False
for item in ftypes:
    if procpath(args.File).endswith(item):
        valid = True

if not valid:
    # not even a supported archive type
    logging.error("Unsupported file type, exiting...")
    raise UnsupportedFileTypeException("Unrecognized filetype, aborting")

#"""
logging.debug("Processing i/o filenames...")
fname = procpath(os.path.abspath(os.path.basename(args.File)))
logging.info(f"fname (proc'd args.File): {fname}")

#print(str(fname.split(".")[0]).split("\\")[-1])
fpath = ".".join((fname.split(".")[:-1]))

if fpath.endswith(".tar"):
    fpath = ".".join((fpath.split(".")[:-1]))

logging.info(f"fpath (output dir): {fpath}")

# check no bullshit non-existent files
if not os.path.exists(fname):
    logging.error("File to extract is supposedly non-existent")
    raise FileNotFoundError("No file to extract")

try:
    logging.debug("Making output folder")
    os.mkdir(rf"{fpath}")

except FileExistsError:
    logging.warning("Overwrite detected", exc_info=True)
    overwrite = input("Output folder exists, would you like to continue? (May overwrite data [Y/N])")[0].upper()
    if overwrite == "Y":
        # no permadelete, because i'm a stinky scared person
        logging.warning("Overwriting, old folder moved to Recycling Bin")
        send2trash(procpath(rf"{fpath}", slashcompat=False))
        os.mkdir(rf"{fpath}")
        # yes I pip installed a lib function just for that shut up

    else:
        logging.error("Cancelled, exiting...")
        print("Exiting...")
        sys.exit()

print("Extracting...")
logging.debug("Omg actually extracting wut")
if fname.endswith(".tar"): # now we just handle every single fuckin' type of archive
    logging.info("Filetype detected: Tar")
    with tarfile.open(fname, "r:") as tar:
        os.chdir(str(fpath))
        safe_extract(tar)

elif fname.endswith(".tar.gz") or fname.endswith(".tgz"):
    logging.info("Filetype detected: Tar.Gzip")
    with tarfile.open(fname, "r:gz") as tar:
        os.chdir(str(fpath))
        safe_extract(tar)

elif fname.endswith(".tar.xz"):
    logging.info("Filetype detected: Tar.Xzip")
    with tarfile.open(fname, "r:xz") as tar:
        os.chdir(str(fpath))
        safe_extract(tar)

elif fname.endswith(".tar.bz2"):
    logging.info("Filetype detected: Tar.Bzip2")
    with tarfile.open(fname, "r:bz2") as tar:
        os.chdir(str(fpath))
        safe_extract(tar)

elif fname.endswith(".zip"):
    logging.info("Filetype detected: Zip")
    with zipfile.ZipFile(fname, "r") as f:
        f.extractall(fpath)
        f.close()

elif fname.endswith(".7z"):
    logging.info("Filetype detected: 7zip")
    shutil.register_unpack_format("7zip", [".7z"], unpack_7zarchive)
    shutil.unpack_archive(fname, fpath)

elif fname.endswith(".rar"):
    logging.info("Filetype detected: Rar")
    patoolib.extract_archive(
        fname,
        outdir=fpath,
        verbosity=-1,
        program="rar"
    )

logging.debug("Yay finished (I hope)")
print("Done!")
