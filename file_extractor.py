#!/usr/bin/env python3
"""
Process raw disk images to create dfxml and extract files
"""

__author__ = "David Cirella"
__contact__ = "david.cirella@yale.edu"
__version__ = "0.1.0"


import os
import shutil
import pathlib
import subprocess
import argparse
import hashlib
import functools
import xml.dom.minidom


def get_img_re(dir_path):
    p = pathlib.Path(dir_path)
    for x in p.iterdir():
        # prevent accessing dir created by script, avoid temp files
        if x.suffix:
            pass
        elif 'extraction' in str(x) or '~' in str(x):
            pass
        else:
            get_img(str(x))
    return 0

def get_img(dir_path):
    # parse dir contents, get image file
    dir_contents = os.listdir(path = dir_path)
    for entry in dir_contents:
        if '.img' in entry:
            img_path = dir_path + "/" + entry
            img_fiwalk(img_path)
            break
        else:
            print(dir_path + "/" + entry, 'No disk image files')
    return 0

def img_fiwalk(img_path):
    #run fiwalk over file, generate dfxml file
    dfxml_path = img_path[:-4] + '.xml'
    dfxml_gen = subprocess.call(["fiwalk","-X", dfxml_path, img_path])
    #dfxml_gen.wait()
    
    get_img_info(dfxml_path, img_path)
    return 0

def get_img_info(dfxml_path, img_path):
    # parse dfxml file
    img_path = img_path[:-4] + '.img'
    dom = xml.dom.minidom.parse(dfxml_path)
    partition_offset = dom.getElementsByTagName('partition_offset')[0].firstChild.data
    sector_size = dom.getElementsByTagName('sector_size')[0].firstChild.data
    offset = int(partition_offset) / int(sector_size)
    get_file_info(dom, offset, img_path)
    return 0

def get_file_info(dom, part_offset, img_path):
    # for each <fileobject>
    #  <filename>
    #  <inode>
    #  <hashdigest type='md5'>
    fileobjects = dom.getElementsByTagName('fileobject')
    for fileObj in fileobjects:
        file_name_Obj = fileObj.getElementsByTagName('filename')[0]
        file_name = getText(file_name_Obj.childNodes)
        
        inode_Obj = fileObj.getElementsByTagName('inode')[1]
        inode = getText(inode_Obj.childNodes)
        
        hash_stored_Obj = fileObj.getElementsByTagName('hashdigest')
        hash_stored = 'none'
        for hashtype in hash_stored_Obj:
            if hashtype.getAttribute('type') == 'md5':
                hash_stored = getText(hashtype.childNodes)        
        meta_type_Obj = fileObj.getElementsByTagName('meta_type')[0]
        meta_type = getText(meta_type_Obj.childNodes)
        
        if int(meta_type) != 1:
            pass
        else:
            icat_extract(file_name, inode, part_offset, hash_stored, img_path)
    moveExtraction(img_path)
    return 0

def icat_extract(file_name, file_inode, part_offset, hash_stored, img_path):
    # call icat on infor to perform extract
    working_dir = img_path.rsplit('/', 1)[0] + "/extraction/"  
    part_offset = str(part_offset)[:-2]
    icat_job = subprocess.run(["icat","-o", part_offset, img_path, file_inode], stdout=subprocess.PIPE)
    working_dir2 = working_dir + file_name.rsplit('/', 1)[0]
    pathlib.Path(working_dir2).mkdir(parents=True, exist_ok=True) 
    try:
        with open(working_dir + file_name, 'wb') as outfile:
            outfile.write(icat_job.stdout)
        check_hash(hash_stored, working_dir + file_name)
    except IsADirectoryError as e:
        pass
    return 0

def check_hash(file_hashdigest, file_name):
    # check md5 against stored value
    extracted_file_hash = checkSumFile(file_name)
    if extracted_file_hash == file_hashdigest:
        pass
    else:
        print('checksum failure: ', file_name )
    return 0
    
def checkSumFile(source):
    hashAlgo = 'md5'
    h = hashlib.new(hashAlgo)
    # read by chunk to for low memory sys
    with open(source, 'rb') as f:
        [h.update(chunk) for chunk in iter(functools.partial(f.read, 256), b'')]
    checksum = h.hexdigest()
    computedChecksum = checksum
    return computedChecksum


# source: https://docs.python.org/3.0/library/xml.dom.minidom.html#id2
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def moveExtraction(img_path):
    img_path = img_path.rsplit('/', 1)[0] + "/extraction/"
    # for all dirs, if (Volume Label Entry), moave all other files
    p = pathlib.Path(img_path)
    new_file_root = ""
    for x in p.iterdir():
        if '(Volume Label Entry)' in str(x):
            new_file_root = x
    for x in p.iterdir():
        if '(Volume Label Entry)' in str(x):
            pass
        else:
            shutil.move(str(x), str(new_file_root))
            

def main(args):
    if args.dfxml:
        get_img_info(args.arg, args.arg)
    elif args.recursive:
        get_img_re(args.arg)
    else:
        get_img(args.arg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process raw disk images to create dfxml and extract files')

    # Required positional argument
    parser.add_argument("arg", help="Provide path to directory holding a image or directory of")

    # Optional argument flag
    parser.add_argument("-r", "--recursive", action="store_true", default=False, help="Recursive allows processing directories/subdirectories of images")

    # Optional argument
    parser.add_argument("-d", "--dfxml", action="store_true", dest="dfxml", help="Specifiy location of dfxml file if it already exisits")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
