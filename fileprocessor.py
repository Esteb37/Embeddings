import multiprocessing as mp
import numpy as np
import os
import inspect
import time
import linecache
import h5py
import math
import threading


class FileProcessor:

    class Chunk:
        chunkNumber: int
        name: str
        size: int
        offset: int

    def __init__(self, file, threads):
        self.filename = file
        self.threads = threads

        self.files_dir = "files"
        self.chunk_prefix = self.files_dir+"/chunk"
        self.encoding = "utf8"

        # self.chunkify()

    def write_chunk(self, filename: str, chunk: Chunk):
        with open(filename, "r", encoding=self.encoding) as f:
            f.seek(chunk.offset)

            # Move to the end of the current line
            f.readline()
            data = f.read(chunk.size)
            with open(chunk.name, "w", encoding=self.encoding) as chunk_file:
                chunk_file.write(data)

    def chunkify(self):
        files_dir = self.files_dir
        threads = self.threads
        filename = self.filename
        chunk_prefix = self.chunk_prefix
        encoding = self.encoding

        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
        else:
            if (len(os.listdir(files_dir)) == threads):
                return

        start = time.time()

        print("Chunkifying file "+filename+" into " +
              str(threads)+" chunks. This will only happen once.")

        for file in os.listdir(files_dir):
            os.remove(os.path.join(files_dir, file))

        file_size = os.path.getsize(filename)

        chunks = [None]*threads

        chunk_size = file_size // threads
        offset = 0

        for i in range(threads):
            chunk = self.Chunk()
            chunk.chunkNumber = i+1
            chunk.name = "files/chunk" + str(i+1) + ".txt"
            chunk.size = chunk_size
            chunk.offset = offset
            offset += chunk_size
            chunks[i] = chunk

        chunks[-1].size += file_size % threads

        threads = list()
        for chunk in chunks:
            t = threading.Thread(target=self.write_chunk,
                                 args=(filename, chunk))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("Finished chunkifying file in " +
              str(time.time()-start)+" seconds")

    def process_file(self, filename, index, shared_model):

        filename = self.chunk_prefix+str(index) + ".txt"

        for lineno, line in enumerate(open(filename, 'r', encoding=self.encoding)):
            word_end = line.find(' ')
            word = line[:word_end]
            shared_model[word] = np.fromstring(
                line[word_end+1:], dtype=float, sep=' ')
        print("Finished processing file "+filename)

    def model_from_file(self):

        t0 = time.time()
        manager = mp.Manager()
        model = {}
        threads = list()

        print("Extracting model from files...")

        # Use threads
        for i in range(self.threads):
            t = threading.Thread(target=self.process_file,
                                 args=(self.filename, i+1, model))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        print("Finished extracting model from files in " +
              str(time.time()-t0)+" seconds")

        return model
