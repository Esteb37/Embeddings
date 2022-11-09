import fileprocessor
import os
import math
import win32file
max_stdio = win32file._getmaxstdio()
win32file._setmaxstdio(2048)

if __name__ == "__main__":
    processor = fileprocessor.FileProcessor("glove.42B.300d.txt", 5000)
    processor.chunkify()
    model = processor.model_from_file()
