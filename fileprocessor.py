import multiprocessing as mp
import numpy as np
import os
import inspect
import time
import linecache
import h5py
import math


class FileProcessor:

    def __init__(self, file, cores):
        self.filename = file
        self.cores = cores

        self.files_dir = "files"
        self.chunk_prefix = self.files_dir+"/chunk"
        self.encoding = "utf8"

        self.chunkify()

    def chunkify(self):
        files_dir = self.files_dir
        cores = self.cores
        filename = self.filename
        chunk_prefix = self.chunk_prefix
        encoding = self.encoding

        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
        else:
            if (len(os.listdir(files_dir)) == cores):
                return

        start = time.time()

        print("Chunkifying file "+filename+" into " +
              str(cores)+" chunks. This will only happen once.")

        filesize = os.path.getsize(filename)
        first_line_size = len(linecache.getline(filename, 1))
        num_lines = math.ceil(filesize/first_line_size)
        lines_per_chunk = num_lines//cores

        with open(filename, 'r', encoding=encoding) as file:

            for i in range(cores - 1):

                with open(chunk_prefix+str(i+1)+".txt", 'w', encoding=encoding) as chunk:

                    for j in range(lines_per_chunk):
                        line = file.readline()
                        chunk.write(line)

            with open(chunk_prefix+str(cores)+".txt", 'w', encoding=encoding) as chunk:
                chunk.write(file.read())

        print("Chunkifying finished in "+str(time.time()-start)+" seconds.")

    def process_file(self, filename, index, shared_model):

        filename = self.chunk_prefix+str(index) + ".txt"

        for lineno, line in enumerate(open(filename, 'r', encoding=self.encoding)):
            word_end = line.find(' ')
            word = line[:word_end]
            shared_model[word] = np.fromstring(
                line[word_end+1:], dtype=float, sep=' ')

        return shared_model

    def model_from_file(self):

        t0 = time.time()

        manager = mp.Manager()

        model = manager.dict()

        processes = list()

        print("Extracting model from files...")

        with mp.Pool(processes=self.cores) as pool:
            for i in range(self.cores):
                processes.append(pool.apply_async(
                    self.process_file, args=(self.filename, i+1, model)))

            for p in processes:
                p.get()

        print("Finished extracting model from files in " +
              str(time.time()-t0)+" seconds")

        return model
