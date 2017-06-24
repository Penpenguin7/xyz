
import ast
import os
import time

# internal imports

import tensorflow as tf
import magenta
from magenta.music import drums_lib
from magenta.music import melodies_lib
from magenta.music import midi_io, sequences_lib, melody_encoder_decoder
from magenta.pipelines import dag_pipeline
from magenta.pipelines import melody_pipelines
from magenta.pipelines import pipeline
from magenta.pipelines import pipelines_common
from magenta.protobuf import music_pb2
DEFAULT_MIN_NOTE = 48
DEFAULT_MAX_NOTE  = 84
DEFAULT_TRANSPOSE_TO_KEY = 0
class EncoderPipeline(pipeline.Pipeline):
  """A Module that converts monophonic melodies to a model specific encoding."""

  def __init__(self, encoder_decoder, name):
    """Constructs an EncoderPipeline.

    Args:
      config: A MelodyRnnConfig that specifies the encoder/decoder, pitch range,
          and what key to transpose into.
      name: A unique pipeline name.
    """
    super(EncoderPipeline, self).__init__(
        input_type=magenta.music.Melody,
        output_type=tf.train.SequenceExample,
        name=name)
    self._melody_encoder_decoder = encoder_decoder
    self._min_note = DEFAULT_MIN_NOTE
    self._max_note = DEFAULT_MAX_NOTE 
    self._transpose_to_key = DEFAULT_TRANSPOSE_TO_KEY

  def transform(self, melody):
    print ('before squash ', melody[0], melody[1],melody[2])
    
    melody.squash(
        self._min_note,
        self._max_note,
        self._transpose_to_key)
    
    print ('afer squash ', melody[0], melody[1],melody[2])
    
    encoded = self._melody_encoder_decoder.encode(melody)
    return [encoded]

def new_pipeline():
    eval_ratio = 0.1
    partitioner = pipelines_common.RandomPartition(
      music_pb2.NoteSequence,
      ['eval_melodies', 'training_melodies'],
      [eval_ratio])
    dag = {partitioner: dag_pipeline.DagInput(music_pb2.NoteSequence)}

    for mode in ['eval', 'training']:
        time_change_splitter = pipelines_common.TimeChangeSplitter(
            name='TimeChangeSplitter_' + mode)
        quantizer = pipelines_common.Quantizer(
            steps_per_quarter=4, name='Quantizer_' + mode)
        melody_extractor = melody_pipelines.MelodyExtractor(
            min_bars=7, max_steps=512, min_unique_pitches=5,
            gap_bars=1.0, ignore_polyphonic_notes=False,
            name='MelodyExtractor_' + mode)
        encoder_pipeline = EncoderPipeline(magenta.music.OneHotEventSequenceEncoderDecoder(melody_encoder_decoder.MelodyOneHotEncoding(min_note = DEFAULT_MIN_NOTE, max_note = DEFAULT_MAX_NOTE)), name='EncoderPipeline_' + mode)
        #print encoder_pipeline
        drum_encoder_pipeline = magenta.music.encoder_decoder.
                EncoderPipeline(
        #print encoder_pipeline.input_type, encoder_pipeline.output_type
        dag[time_change_splitter] = partitioner[mode + '_melodies']
        dag[quantizer] = time_change_splitter
        dag[melody_extractor] = quantizer
        dag[encoder_pipeline] = melody_extractor
        dag[dag_pipeline.DagOutput(mode + '_melodies')] = encoder_pipeline

    return dag_pipeline.DAGPipeline(dag)

mode = 3 #1: drum modes, 2: melody mode


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
    elif mode == 3:
        pipeline_instance = new_pipeline()
        output = pipeline.load_pipeline(pipeline_instance,pipeline.tf_record_iterator(
            '/home/duong/magenta_experiment/convert_dir_to_note_sequence/output/melody_without_break.tfrecord', pipeline_instance.input_type))
        f = open('/home/duong/new_pipeline.txt','w')
        f.write(str(output))
        f.close()
 #      uncomment below 2 lines to save extracted sequence to midi files
##         
##    midi_path = os.path.join(output_dir, output_filename)    
##    magenta.music.sequence_proto_to_midi_file(sequence, midi_path) 






    
