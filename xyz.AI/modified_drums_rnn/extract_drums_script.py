
import ast
import os
import time

# internal imports
# download, add build file in this folder & dependencies as needed to run this script from command line

import tensorflow as tf
import magenta
from magenta.music import drums_lib
from magenta.music import melodies_lib
from magenta.music import midi_io, sequences_lib
mode = 2 #1: drum modes, 2: melody mode


home_path = '/home/duong/magenta_experiment/extract_track/'
file_name = 'Michael_Jackson_-_Billie_Jean' # download Michael_Jackson_-_Billie_Jean.mid from midiworld
midi_file = home_path+'input/'+file_name+'.mid'
output_dir = home_path+'output/'+file_name+'/'
qpm = magenta.music.DEFAULT_QUARTERS_PER_MINUTE
if __name__ == '__main__':
    if mode == 1:
        drum_track = drums_lib.midi_file_to_drum_track(midi_file)
        sequence = drum_track.to_sequence(qpm=qpm)
        print(len(sequence.notes))
        print 'drum total time = ', sequence.total_time
        if not tf.gfile.Exists(output_dir):
            tf.gfile.MakeDirs(output_dir)
        output_filename ='drum.mid'  
    elif mode == 2:
        instrument = 9 # set instrument=9 doesn't sound like drum
        seq1 = midi_io.midi_file_to_sequence_proto(midi_file)
        quantized_sequence = sequences_lib.quantize_note_sequence(
      seq1, steps_per_quarter=4)
        track = melodies_lib.Melody()
        track.from_quantized_sequence(quantized_sequence, instrument=instrument) 
        sequence = track.to_sequence(instrument = instrument, qpm=qpm)
        #print(sequence)
        print 'instrument = ',instrument
        print 'notesequence length = ', len(sequence.notes)
        print 'melody total time = ', sequence.total_time
        print sequence.notes[0], sequence.notes[1]
        if not tf.gfile.Exists(output_dir):
            tf.gfile.MakeDirs(output_dir)
        output_filename ='melody_instrument='+str(instrument)+'exp.mid'   

 #      uncomment below 2 lines to save extracted sequence to midi files
         
 #   midi_path = os.path.join(output_dir, output_filename)    
 #   magenta.music.sequence_proto_to_midi_file(sequence, midi_path) 
