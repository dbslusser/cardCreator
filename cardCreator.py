"""
Create a .png of .pdf file for each line of text in a text file

"""
import argparse
import logging
import os
import sys
import tempfile
import shutil
from xml.dom import minidom


__version__ = "0.0.1"


class TempDir(object):
    """ Create an object to handle file in a temporary directory """
    def __init__(self):
        """ Class entry point """
        self.temp_dir = tempfile.mkdtemp()

    def close(self):
        """ delete entire temp directory """
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def list_dir(self):
        """ return a list of all files in temp dir """
        return os.listdir(self.temp_dir)


class Struct:
    """ Creates an object from a dictionary """
    def __init__(self, **entries):
        """ Class entry point"""
        self.svg_file = None
        self.text_file = None
        self.file_type = None
        self.output_path = None
        self.increment_from = None
        self.output_dpi = None
        self.__dict__.update(entries)


def get_opts():
    """ Return an argparse object. """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--verbose', default=logging.INFO, action='store_const',
                        const=logging.DEBUG, help="enable debug logging")
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--svg_file', default=None, required=True, help='source svg file)')
    parser.add_argument('--text_file', default=None, required=True, help='text file containing replacement text')
    parser.add_argument('--file_type', default='png', required=False, help='type of file output (png or pdf')
    parser.add_argument('--output_path', default="./", required=False, help='path to create output file(s)')
    parser.add_argument('--increment_from', default=1, type=int, required=False,
                        help='integer to increment output file from')
    parser.add_argument('--output_dpi', default=300, type=int, required=False, help='DPI of output files')
    args = vars(parser.parse_args())
    logging.basicConfig(level=args["verbose"])
    return Struct(**args)


def create_output_file(input_file, output_path, file_type="png", dpi=300):
    """ Convert the svg file to png or pdf via Inkscape
    example cmd:
        cmd = "inkscape -e a.png a.svg"
    """
    cmd = None
    file_name = input_file.split("/")[-1].split(".")[0]
    if file_type in 'png.pngPNG.PNG':
        cmd = "inkscape -e {}/{}.png {} --export-dpi={}".format(output_path, file_name, input_file, dpi)
    elif file_type in 'pdf.pdfPDF.PDF':
        cmd = "inkscape -A {}/{}.pdf {} --export-dpi={}".format(output_path, file_name, input_file, dpi)
    else:
        logging.error("unsupported file type: %s", file_type)
    if cmd:
        os.popen(cmd)


def get_source_content(source_file):
    """ open a source svg file and read the contents """
    return minidom.parse(source_file)


def get_text_content(text_file):
    """ open the text file containing replacement text """
    with open(text_file, 'r') as f:
        text_content = f.readlines()
    return text_content


def create_temp_svg(doc, replacement_text, output_file):
    """ replace contents of text field with id 'text_id' with 'text' """
    doc.getElementsByTagName("flowPara")[0].childNodes[0].data = replacement_text
    with open(output_file, 'w') as f:
        f.write(doc.toxml())


def process_file(opts):
    """ iterate through replacement text and create a file for each entry """
    # get source svg content
    source_content = get_source_content(opts.svg_file)

    # get replacement_text
    replacement_text = get_text_content(opts.text_file)

    # create tempdir
    temp = TempDir()
    logging.info("TEMP dir is %s", temp.temp_dir)

    # replace text and create temp svg files
    file_counter = opts.increment_from
    for line in replacement_text:

        # replace txt in temp file
        temp_svg_file = "{}/{:03}.svg".format(temp.temp_dir, file_counter)
        create_temp_svg(source_content, line, temp_svg_file)

        # increment file counter
        file_counter += 1

    # convert temp svg files to png/pdf files
    for temp_file in os.listdir(temp.temp_dir):
        create_output_file("{}/{}".format(temp.temp_dir, temp_file), opts.output_path, opts.file_type, opts.output_dpi)

    # clean up
    temp.close()


def main():
    """ script entry point """
    opts = get_opts()
    process_file(opts)


if __name__ == "__main__":
    sys.exit(main())
