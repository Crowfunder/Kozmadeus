###############################################################
# by Crowfunder                                               #
# Copyright my ass but also the GPL-3.0 License               #
# Github: https://github.com/Crowfunder                       #
###############################################################

# External Imports
import os
import sys
import argparse

# Internal Imports
from main import RestoreFiles, CheckUpdates, ModuleData, Main, Settings
from main import VERSION_CURRENT, SEPARATOR

# Class for disabling the output log
# strictly for --silent option
# Source: https://stackoverflow.com/questions/8391411/how-to-block-calls-to-print
class HiddenPrints:
    def __init__(self, silent):
        self.silent = silent

    def __enter__(self):
        if self.silent:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.silent:
            sys.stdout.close()
            sys.stdout = self._original_stdout


# Custom action for listing modules
# Source: https://stackoverflow.com/questions/34352405/python-argparse-help-like-option
class modules_action(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(modules_action, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        module_data = ModuleData()
        string = '\nLoaded Modules:\n' + SEPARATOR + '\n'
        for data in module_data:
            string += data
            string += SEPARATOR + '\n'
        print(string)
        parser.exit()


# noupdate_silent is a flag that disables
# error and "no updates available" messages
def PrintUpdates(noupdate_silent):

    try:
        update_data = CheckUpdates()

        if update_data['current'] != update_data['fetched']:
            print('Updates available! \nDownload at: '
                  'https://github.com/Crowfunder/Kozmadeus/releases\n'
                  f'Current version: {update_data["current"]}\n'
                  f'New version: {update_data["fetched"]}')

        else:
            if not noupdate_silent:
                print('Kozmadeus is up to date!')

    except Exception as e:
        if not noupdate_silent:
            print('Unable to fetch updates! '
                  'Check your internet connection.\n', e)


# Command Line Interface, invoked if main is invoked 
# instead of gui.
def CliMenu():

    # Defining argparse args
    # A similar mess to that of GUI defining
    # can't be helped I guess
    parser = argparse.ArgumentParser(description=('Converts models to '
                                                  'Spiral Knights XML.'),
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=('Script written with love by Crowfunder\n'
                                             'Distributed under GPL-3.0 License\n'
                                             f'Version: {VERSION_CURRENT}\n'
                                             'Credits: Puzovoz, XanTheDragon, '
                                             'Kirbeh \nGithub: '
                                             'https://github.com/Crowfunder/Kozmadeus'))

    parser.add_argument('files_list', nargs='+',
                        help='<Required> Input the files to process')
    parser.add_argument('-m', '--mode', choices=['articulated', 'static'],
                        default='articulated', help='Output model type choice\n'
                        '- articulated: used for most cases\n'
                        '- static: used most notably for importing armors')
    parser.add_argument('-s', '--silent', action='store_true',
                        help='Disable all command line messages\n'
                             'Note: Does not apply for unhandled exceptions')
    parser.add_argument('--no-file', action='store_true',
                        help='Output raw data, no write to xml files\n'
                             'This argument also implies --silent')
    parser.add_argument('--restore-files', action='store_true',
                        help='Restore templates on start')
    parser.add_argument('--skip-update', action='store_true', 
                        help='Skip update check on start')
    parser.add_argument('--modules-list', action=modules_action, 
                        help='List all installed modules')
    parser.add_argument('--strip-armature-tree', action='store_true',
                        help='Strip armature tree data.\n'
                             'Necessary for reimporting armors '
                             'utilizing the pc model armature.')

    parser_args = parser.parse_args()

    # --no-file implies --silent by default
    if parser_args.no_file:
        parser_args.silent = True

    with HiddenPrints(parser_args.silent):

        # Make use of argparse args
        # Restore files
        if parser_args.restore_files:
            print('Restoring template files...')
            RestoreFiles()
            print('Success!')
            print(SEPARATOR)

        # Check for updates
        if not parser_args.skip_update:
            PrintUpdates(False)
            print(SEPARATOR)

        settings = Settings(file_names=parser_args.files_list, model_mode=parser_args.mode,
                            no_export_file=parser_args.no_file, strip_armature_tree=parser_args.strip_armature_tree)
        geometry = Main(settings)

    if parser_args.no_file:
        print(geometry)


if __name__ == '__main__':
    CliMenu()
