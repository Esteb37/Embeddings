import multiprocessing as mp
import numpy as np
import os
import inspect
import time
import linecache

class FileProcessor:
	
	def __init__(self, file):
		self.filename = file
		self.cores = mp.cpu_count()
  
		self.files_dir = "files"
		self.chunk_prefix = self.files_dir+"/chunk"
		self.encoding = "utf8"
		
		self.chunkify()
		
	def chunkify(self):
		files_dir = self.files_dir
		cores = self.cores
  
		with open(self.filename, 'r', encoding=self.encoding) as input_file:
  
			output_files = []

			if(not os.path.exists(files_dir)):
				os.mkdir(files_dir)
			
			num_files = len([name for name in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, name))])
	
			if(num_files != cores):
				
				print("Chunking file "+self.filename+" into "+str(cores)+" chunks. This will only happen once.")
    
				for i in range(0, cores):
					output_files.append(open(self.chunk_prefix + str(i+1) + '.txt', 'w', encoding=self.encoding))
		
				for line in input_file:
					output_files[hash(line) % cores].write(line)
	
				for i in range(0, cores):
					output_files[i].close()
    
	def process_file(self, filename, index, shared_model):
		
		filename = self.chunk_prefix+str(index) + ".txt"
	
		for lineno,line in enumerate(open(filename, 'r', encoding=self.encoding)):
			word_end = line.find(' ')
			word = line[:word_end]
			shared_model[word] = np.fromstring(line[word_end+1:], dtype=float, sep=' ')

		print("Processed chunk #"+str(index))
  
		return shared_model


	def model_from_file(self):
		
		t0 = time.time()
  
		manager = mp.Manager()
		
		model = manager.dict()
		
		processes = list()

		"""
		with open(f'./tmp_func.py', 'w') as file:
			file.write(inspect.getsource(process_file).replace(process_file.__name__, "task"))

		from tmp_func import task"""

		print("Processing file "+self.filename)
  
		with mp.Pool(processes=self.cores) as pool:
			for i in range(self.cores):
				processes.append(pool.apply_async(self.process_file, args=(self.filename, i+1, model)))
	
			for p in processes:
				p.get()

		print("Finished processing file "+self.filename+" in "+str((time.time()-t0)/60)+" minutes")
  
		return model