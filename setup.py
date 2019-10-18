from setuptools import setup

with open('requirements.txt') as fp:
    install_requires = fp.read()

setup(
    name='DECIBEL',
    version='1.0',
    packages=['decibel', 'decibel.utils', 'decibel.evaluator', 'decibel.data_fusion', 'decibel.file_scraper',
              'decibel.tab_chord_parser', 'decibel.audio_tab_aligner', 'decibel.audio_midi_aligner',
              'decibel.midi_chord_recognizer'],
    url='https://github.com/DaphneO/DECIBEL',
    license='MIT',
    author='Daphne Odekerken',
    author_email='D.Odekerken@UU.nl',
    description='DECIBEL: a system for improvement of automatic chord estimation by using tab and MIDI files',
    long_description='DECIBEL is a new system for Automatic Chord Estimation (ACE) which exploits MIDI and tab files ' +
                     'to improve audio ACE, thereby implicitly integrating musical knowledge.' +
                     'Given an audio file and a set of MIDI and tab files corresponding to the same song, DECIBEL ' +
                     'first estimates chord sequences from all files. For the audio file, it uses existing ' +
                     'state-of-the-art audio ACE methods. MIDI files are first aligned to the audio, followed by a ' +
                     'MIDI chord estimation step. Tab files are first parsed to untimed chord sequences and then ' +
                     'aligned to the audio. In a final step, DECIBEL uses a data fusion method that integrates all ' +
                     'estimated chord sequences into one final output sequence.',
    keywords='audio music mir midi tab data fusion, ace',
    install_requires=install_requires
)
