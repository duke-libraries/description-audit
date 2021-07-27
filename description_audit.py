import argparse
import os
import sys
from scripts.description_audit_driver import main
from scripts.description_audit_GUI import main as run_gui

guiparser = argparse.ArgumentParser()
guiparser.add_argument('--nogui', default=False, action="store_true")

if __name__ == '__main__':

    preargs = guiparser.parse_known_args()

    if not preargs[0].nogui:
        # launch GUI
        args_from_gui = run_gui()
        lexicon_csv_path = args_from_gui[0]
        lexicon_test = args_from_gui[1]
        hatebase_include = args_from_gui[2]
        output_path = args_from_gui[3]
        ead_path = args_from_gui[4]
        marcxml_path = args_from_gui[5]

    else:
        noguiparser = guiparser
        noguiparser.add_argument('lexicon_csv_path', type=str, help="Path to CSV file containing lexicons")
        noguiparser.add_argument('lexicon_test', type=str, help="Headers to CSV indicating lexicons to match to. "
                                                                "To use multiple, separate by underscores. To use all, "
                                                                "type 'ALL'.")
        # If you have any particularly lengthy or false positive-prone lexicons that you want to only include if
        # they are explicitly declared, modify references to the below variable in parse_lexicon() driver function.
        noguiparser.add_argument('hatebase_include', type=int, help="Boolean True or False indicating "
                                                                                    "whether the lengthy HateBase "
                                                                                    "lexicons should be included. "
                                                                                    "Default is False.")
        noguiparser.add_argument('output_path', type=str, help="Path to folder where CSV reports should be stored")
        noguiparser.add_argument('ead_path', type=str, help="Path to folder comprised of EAD archive files in XML.")
        noguiparser.add_argument('marcxml_path', type=str, help="Path to XML file containing MARCXML archive.")

        args = noguiparser.parse_args()
        print(args)
        lexicon_csv_path = args.lexicon_csv_path
        lexicon_test = args.lexicon_test
        hatebase_include = args.hatebase_include
        output_path = args.output_path
        ead_path = args.ead_path
        marcxml_path = args.marcxml_path

    if not os.path.isfile(lexicon_csv_path):
        print("The lexicon CSV file specified does not exist on this path.")
        sys.exit()

    if not os.path.isdir(output_path):
        print("The output path given is not a file directory.")
        sys.exit()

    if marcxml_path == ead_path:
        print("Path to at least one archival structure must be specified")
        sys.exit()

    if not (os.path.isdir(ead_path) or (ead_path == "NONE")):
        print("The EAD path given does not lead to a directory of archival information.")
        sys.exit()

    if not (os.path.isfile(marcxml_path) or (marcxml_path == "NONE")):
        print("The MARCXML archival structure does not exist on this path.")
        sys.exit()

    main(lexicon_csv_path, lexicon_test, hatebase_include, output_path, ead_path, marcxml_path)
