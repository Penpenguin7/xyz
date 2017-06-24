import collections
import operator

import ast
import os
import time


# internal imports

import tensorflow as tf
import magenta
import magenta.music as mm
from magenta.music import constants, drums_lib
from magenta.pipelines import pipeline, dag_pipeline, pipelines_common, drum_pipelines, melody_pipelines
from magenta.protobuf import music_pb2
from magenta.common import sequence_example_lib

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('input', '/home/duong/magenta_experiment/'+
                           'convert_dir_to_note_sequence/output/complex.tfrecord',
                           'TFRecord to read NoteSequence protos from.')
tf.app.flags.DEFINE_string('output_dir', '/home/duong/magenta_experiment/create_dataset_output/',
                           'Directory to write training and eval TFRecord '
                           'files. The TFRecord files are populated with '
                           'SequenceExample protos.')
tf.app.flags.DEFINE_float('eval_ratio', 0.1,
                          'Fraction of input to set aside for eval set. '
                          'Partition is randomly selected.')
tf.app.flags.DEFINE_string('log', 'INFO',
                           'The threshold for what messages will be logged '
                           'DEBUG, INFO, WARN, ERROR, or FATAL.')




class Combo(dict):
    def __init__(self, drum_track, melody_track):
        self['drum_track'] = drum_track
        self['melody_track'] = melody_track


def align_drum_and_melody_tracks(drum_track, melody_track):
    new_drum_track = drums_lib.DrumTrack()
    j = 0
    for i in range(len(melody_track)):
        if melody_track[i] == constants.MELODY_NO_EVENT and len(drum_track) > j:
            new_drum_track.append(drum_track[j])
            j = j+1
        else:
            # default _pad_event = frozenset()
            new_drum_track.append(new_drum_track._pad_event)
    assert len(new_drum_track) == len(melody_track)
    return new_drum_track   

class ComboExtractor(pipeline.Pipeline):
    def __init__(self, drum_extractor, melody_extractor, name=None):
        super(ComboExtractor, self).__init__(
            input_type=music_pb2.NoteSequence,
            output_type=dict([('drum', magenta.music.DrumTrack), ('melody', magenta.music.Melody)]),
            name=name)
        self._drum_extractor = drum_extractor
        self._melody_extractor = melody_extractor

    def transform(self, quantized_sequence):
        melody_tracks = self._melody_extractor.transform(quantized_sequence)
        drum_tracks = self._drum_extractor.transform(quantized_sequence)
        new_drum_tracks = [align_drum_and_melody_tracks(drum_tracks[i], melody_tracks[i])
                           for i in range(min(len(melody_tracks), len(drum_tracks)))]
        return dict([('drum',new_drum_tracks), ('melody',melody_tracks[0:len(new_drum_tracks)])])
## melody default parameters
DEFAULT_MIN_NOTE = 48
DEFAULT_MAX_NOTE  = 84
DEFAULT_TRANSPOSE_TO_KEY = 0

class ComboEncoderPipeline(pipeline.Pipeline):
    def __init__(self, melody_encoder_decoder, drum_encoder_decoder, name,
                 melody_min_note = DEFAULT_MIN_NOTE,
                 melody_max_note = DEFAULT_MAX_NOTE,
                 melody_transpose_to_key = DEFAULT_TRANSPOSE_TO_KEY):
        super(ComboEncoderPipeline, self).__init__(
        input_type=dict([('drum', magenta.music.DrumTrack), ('melody', magenta.music.Melody)]),
        output_type=tf.train.SequenceExample,
        name=name)
        self._melody_encoder_decoder = melody_encoder_decoder
        self._drum_encoder_decoder = drum_encoder_decoder
        self._melody_min_note = melody_min_note
        self._melody_max_note = melody_max_note
        self._melody_transpose_to_key = melody_transpose_to_key
    def transform(self, combo):
        combo['melody'].squash(
        self._melody_min_note,
        self._melody_max_note,
        self._melody_transpose_to_key)
        return [self.encode(combo['drum'], combo['melody'])]
    def encode(self,drum_track, melody_track):
        inputs = []
        labels = []
        assert len(drum_track) == len(melody_track)
        for i in range(len(melody_track)):
          inputs.append(self._melody_encoder_decoder.events_to_input(melody_track, i))
          labels.append(self._drum_encoder_decoder.events_to_label(drum_track, i))
        return sequence_example_lib.make_sequence_example(inputs, labels)


def get_pipeline(melody_encoder_decoder, drum_encoder_decoder, eval_ratio, steps_per_quarter = 2):
    
    partitioner = pipelines_common.RandomPartition(
      music_pb2.NoteSequence,
      ['eval_combo_tracks', 'training_combo_tracks'],
      [eval_ratio])
    dag = {partitioner: dag_pipeline.DagInput(music_pb2.NoteSequence)}    
    for mode in ['eval', 'training']:
        time_change_splitter = pipelines_common.TimeChangeSplitter(
            name='TimeChangeSplitter_' + mode)
        quantizer = pipelines_common.Quantizer(
            steps_per_quarter=steps_per_quarter, name='Quantizer_' + mode)

        drum_extractor = drum_pipelines.DrumsExtractor(
        min_bars=7, max_steps=512, gap_bars=1.0, name='DrumsExtractor_' + mode)
        ##################################
        melody_extractor = melody_pipelines.MelodyExtractor(
        min_bars=7, max_steps=512, min_unique_pitches=5,
        gap_bars=1.0, ignore_polyphonic_notes=False,
        name='MelodyExtractor_' + mode)

        combo_extractor = ComboExtractor(drum_extractor, melody_extractor, name = 'ComboExtractor_'+mode)
        encoder_pipeline = ComboEncoderPipeline(melody_encoder_decoder, drum_encoder_decoder, name = 'EncoderPipeline_'+mode)
        #raise Exception(encoder_pipeline.input_size)
        #raise Exception(encoder_pipeline.input_type)
        #print (encoder_pipeline.input_type)
        dag[time_change_splitter] = partitioner[mode + '_combo_tracks']
        
        dag[quantizer] = time_change_splitter
        dag[combo_extractor] = quantizer
        dag[encoder_pipeline] = combo_extractor
        dag[dag_pipeline.DagOutput(mode + '_combo_tracks')] = encoder_pipeline

    return dag_pipeline.DAGPipeline(dag)



def main(unused_argv):
    print ('hey Im creating dataset')
    #define the input & output necessary for melody config and drum config here
    tf.logging.set_verbosity(FLAGS.log)

    melody_encoder_decoder =  magenta.music.OneHotEventSequenceEncoderDecoder(
            magenta.music.MelodyOneHotEncoding(
                min_note=DEFAULT_MIN_NOTE,
                max_note=DEFAULT_MAX_NOTE))
    drum_encoder_decoder =  magenta.music.OneHotEventSequenceEncoderDecoder(
            magenta.music.MultiDrumOneHotEncoding([
                [39] +  # use hand clap as default when decoding
                range(mm.MIN_MIDI_PITCH, 39) +
                range(39, mm.MAX_MIDI_PITCH + 1)]))
    
    pipeline_instance = get_pipeline(
      melody_encoder_decoder, drum_encoder_decoder, FLAGS.eval_ratio)
    #print pipeline_instance.input_type, pipeline_instance.output_type
    #raise Exception('stop')
    FLAGS.input = os.path.expanduser(FLAGS.input)
    FLAGS.output_dir = os.path.expanduser(FLAGS.output_dir)
    pipeline.run_pipeline_serial(
      pipeline_instance,
      pipeline.tf_record_iterator(FLAGS.input, pipeline_instance.input_type),
      FLAGS.output_dir)

def console_entry_point():
  tf.app.run(main)


if __name__ == '__main__':
  console_entry_point()
