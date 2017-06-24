
import ast
import os
import time

# internal imports

import tensorflow as tf
import magenta
from magenta.modified_drums_rnn import drums_lib

if __name__ == '__main__':
    midi_file ='/home/duong/magenta_experiment/extract_drum_track/input/Michael_Jackson_-_Billie_Jean.mid'
    qpm = magenta.music.DEFAULT_QUARTERS_PER_MINUTE
    drum_track = drums_lib.midi_file_to_drum_track(midi_file)
    sequence = drum_track.to_sequence(qpm=qpm)    
    output_dir = '/home/duong/magenta_experiment/extract_drum_track/output'
    if not tf.gfile.Exists(output_dir):
        tf.gfile.MakeDirs(output_dir)
    midi_filename ='drum_2.mid'
    midi_path = os.path.join(output_dir, midi_filename)
    magenta.music.sequence_proto_to_midi_file(sequence, midi_path)
