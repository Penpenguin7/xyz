import hdf5_getters

import os
import tables
import sys
reload(sys)
import pickle
import shutil
import stat

sys.setdefaultencoding('utf-8')



def create_Array(path):
	w = 0	
	array=[]		
	for filename in os.listdir(path):
		tmppath=os.path.join(path,filename)
		for filename2 in os.listdir(tmppath):
			tmppath2=os.path.join(tmppath,filename2)
			for filename3 in os.listdir(tmppath2):
				tmppath3=os.path.join(tmppath2,filename3)
				for filename4 in os.listdir(tmppath3):
						
					path_to_FILE =(os.path.join(tmppath3,filename4))
				
					FILE = hdf5_getters.open_h5_file_read(os.path.join(tmppath3,filename4))
					
					i = hdf5_getters.get_num_songs(FILE)
					for j in range(0,i):
						index_num=j
						first_folder=os.path.split(tmppath)[1]
						second_folder=os.path.split(tmppath2)[1]
						third_folder=os.path.split(tmppath3)[1]
						dir_chain=first_folder+second_folder+third_folder						   							
						artist_name = hdf5_getters.get_artist_name(FILE,j)
						song_ID = os.path.split(path_to_FILE)[1]
						song_title = str(hdf5_getters.get_title(FILE,j))
						tags = str(hdf5_getters.get_artist_terms(FILE,j))
						time = str(hdf5_getters.get_duration(FILE,j))
						array.append([dir_chain,index_num,song_ID,artist_name,song_title,tags,time])
						w +=1
						if w%100==0:
							print str(100*(1.0*w/31000)) + '%'
						
				        
					FILE.close()

					
	
	with open("output.bin", "wb") as output:
    		pickle.dump(array,output)
	return
	

	



def create_midi_set(artist_array,tag_array,results_path,path_to_midi_files,filename):
	with open("output.bin", "rb") as data:
    		array = pickle.load(data)
	os.mkdir(os.path.join(results_path,filename))
	directory = os.path.join(results_path,filename)
	duration = 0
	for entry in array:
		for artist in artist_array:
			if artist == entry[3]:
				path = os.path.join(path_to_midi_files,entry[0][0])
				path = os.path.join(path,entry[0][1])
				path = os.path.join(path,entry[0][2])
				path = os.path.join(path,entry[2][0:len(entry[2])-3])
				path = os.path.join(path,os.listdir(path)[entry[1]])
				
				shutil.copy2(path,directory)
				duration += float(entry[6])
				print 'added' + ' ' + str(entry[4])
		
			
	        if all(tag in entry[5] for tag in tag_array):
				path = os.path.join(path_to_midi_files,entry[0][0])
				path = os.path.join(path,entry[0][1])
				path = os.path.join(path,entry[0][2])
				path = os.path.join(path,entry[2][0:len(entry[2])-3])
				path = os.path.join(path,os.listdir(path)[entry[1]])
				
				shutil.copy2(path,directory)
				duration += float(entry[6])
				print 'added' + ' ' +str(entry[4])
				


			
	print str(duration/3600) + " " + 'hours of music added'
				
#enter comma separated list of artists, comma separated list of tags, absolute path where you want folder generated, absolute path to 'lmd_matched' midi files, and name of folder.  

def main():
        print str(sys.argv[1].split(','))
	print str(sys.argv[2].split(','))
	create_midi_set(sys.argv[1].split(','),sys.argv[2].split(','),sys.argv[3],sys.argv[4],sys.argv[5])
	

if  __name__ =='__main__':main()
				

		
		
	
	
		
