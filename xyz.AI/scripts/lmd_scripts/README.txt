run lmd_generate_dataset with 
comma separated list of artists
comma separated list of tags
absolute path where you want the new folder placed
absolute path to lmd_matched, the folder with the midi files
name of new folder

It reads from output.bin, which is a pickeling of an array created from the metadata.  if you want to pickel your own array, run the create_Array function in lmd_generate_dataset giving it the path to lmd_matched_h5  