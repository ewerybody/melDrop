"""
melDrop.pacmel
Super simple Maya deployment utility.

You give it a bunch of files,
a snippet of code to execute and
a target mel file name.

It zips the given files, base64 encodes them along with the code snippet
and creates a Maya droppable mel file.

When dropped onto maya the mel code hands the base64 to python
which decodes, extracts to temp and calls the snippet with a list of the files given.

@created: 14.04.2016
@author: eric
"""
import os
import uuid
import base64
import zipfile


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def pac(files, mel, code=None, pack_flat=True):
    """
    :param list files: list of files to bundle. Alternatively you can put tuples into the list
        which are like (source_path, path_in_zip). these ignore the "pack_flat" setting.
    :param str mel: target mel file path
    :param str code: code snippet to execute after the extraction, if it's
        an existing path to a .py-file it will be read.
    :param bool pack_flat: to strip the paths from the packed files so that they are in the zip
        root. False is the standard zip behavior which retains the path minus the drive letter.
    """
    if not isinstance(files, list):
        files = [files]

    # zip the given files
    file_tuples = []
    for f in files:
        if isinstance(f, tuple):
            filepath = f[0]
            arcname = f[1]
        else:
            filepath = f
            arcname = os.path.basename(f) if pack_flat else f
        if not os.path.isfile(filepath):
            raise RuntimeError('File not existent: "%s"' % filepath)
        else:
            file_tuples.append((filepath, arcname))

    tmp_zip_name = 'pacmel_%s.zip' % str(uuid.uuid4())
    tmp_zip_path = os.path.join(os.getenv('TEMP'), tmp_zip_name)
    with zipfile.ZipFile(tmp_zip_path, 'w', zipfile.ZIP_DEFLATED) as tmpzip:
        for filepath, arcname in file_tuples:
            tmpzip.write(filepath, arcname)

    # encode into mel
    with open(tmp_zip_path, 'rb') as fobj:
        src_data = fobj.read()
    os.remove(tmp_zip_path)
    mel_string = base64.encodestring(src_data).replace('\n', '\\\n')
    mel_code = 'string $stuff = "%s";\n\n' % mel_string

    # append and format python code
    with open(os.path.join(_THIS_DIR, 'pacmel.template'), 'r') as fobj:
        py_code = fobj.read()

    if code is None:
        with open(os.path.join(_THIS_DIR, 'pacmel.dummy.template'), 'r') as fobj:
            code = fobj.read()
    elif os.path.isfile(code):
        with open(code, 'r') as fobj:
            code = fobj.read()

    # make the code snippet work through the packing
    code = code.strip().replace('\n', '\n    ')
    code = code.replace('\\', '\\\\')
    code = code.replace('"', '\\')

    py_code = py_code.format(zipname=tmp_zip_name,
                             code=code)

    py_code = py_code.replace('\r\n', '\\n\\\n')

    c = """python("%s");""" % py_code
    mel_code += c + '\n'

    # write the mel file
    with open(mel, 'w') as fobj:
        fobj.write(mel_code)


def _pac_yourself():
    """
    packs the necessary files of itself into a pacmel.mel
    """
    # provide a code snippet to execute
    install_code = os.path.join(_THIS_DIR, 'pacmel_dropcode.py')
    # assemble a bunch of files
    files = [__file__,
             os.path.join(_THIS_DIR, 'pacmel.template'),
             os.path.join(_THIS_DIR, 'pacmel.dummy.template'),
             install_code]
    # create a path to target mel file
    mel = os.path.join(_THIS_DIR, 'pacmel.mel')
    # and fire it of:
    pac(files, mel, install_code)
    return mel
