import os
from . import constants


class FolderReader(object):
    @staticmethod
    def walk(directory,
             file_extension=constants.DEFAULT_FILE_EXTENSION_FOR_SOURCE_FILES):
        for base_path, directories, files in os.walk(directory):
            for file in files:
                if file.endswith(file_extension):
                    yield os.path.join(base_path, file)

    @staticmethod
    def echo(quiet, text_to_print, blank_before=True):
        if not quiet:
            if blank_before:
                print()
            print(text_to_print)