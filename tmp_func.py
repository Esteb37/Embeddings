def task(filename, index, shared_model):
    
	from numpy import fromstring
    
	filename = "files/chunk"+str(index) + ".txt"
 
	print("Processing file: ", filename)
    
	lineno = 0
	for line in open(filename, 'r', encoding="utf8"):
		word_end = line.find(' ')
		word = line[:word_end]
		lineno += 1
		shared_model[word] = fromstring(line[word_end+1:], dtype=float, sep=' ')
	
	print("Done processing file: ", filename)
	return shared_model
