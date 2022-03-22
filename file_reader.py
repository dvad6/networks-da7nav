# You need to implement the "get" and "head" functions.
import sys
import os

class FileReader:
    def __init__(self):
        pass

    def get(self, filepath, cookies):
        """
        Returns a binary string of the file contents, or None.

        """
        path_name = filepath
        print(filepath)
        if (os.path.isfile(path_name)):
            File = open(path_name,"rb")
            Data = File.read()
            File.close()
            return Data
        elif (os.path.isdir(path_name)):
            return 1
        else: 
            return None
        
        return None

    def head(self, filepath, cookies):
        """
        Returns the size to be returned, or None.
        """
        path_name = filepath
        if (os.path.isfile(path_name)):
            size = os.path.getsize(path_name)
            return size
        elif (os.path.isdir(path_name)):
            return 1
        else: 
            return None
        