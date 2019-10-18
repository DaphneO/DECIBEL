=====================
Aligning tab to audio
=====================

Having completed the tab parsing step, we have extracted the chord labels and their corresponding line and word numbers
from the tab file. However, tab files retain no timing information, so we need an additional step to align the chord
labels to the audio file. There already exist four different algorithms by \cite{mcvicar2011using} that incorporate tab
information into a HMM-based system for audio chord estimation. The most promising of these four algorithms is
Jump Alignment.

Jump Alignment is based on a Hidden Markov Model (HMM).
A HMM models the joint probability distribution P(X, y | Theta) over the feature vectors X and the chord labels y,
where Theta are the parameters of the model.

Preprocessing: feature extraction
---------------------------------
First, the audio file needs to be **preprocessed**. For this purpose, we use the python package librosa.
First, we convert the audio file to mono. Then, we use the HPSS function to separate the harmonic and percussive
elements of the audio. Then, we extract chroma from the harmonic part, using constant-Q transform with a sampling rate
of 22050 and a hop length of 256 samples. Now we have chroma features for each sample, but we expect that the great
majority of chord changes occurs on a beat. Therefore, we beat-synchronize the features: we run a beat-extraction
function on the percussive part of the audio and average the chroma features between the consecutive beat positions.
The chord annotations need to be beat-synchronized as well. We do this by taking the most prevalent chord label between
beats.
Each mean feature vector with the corresponding beat-synchronized chord label is regarded as one frame.
Now we have the feature vectors X and chord labels y for each song, which we feed to our HMM.

.. automodule:: decibel.audio_tab_aligner.feature_extractor
    :members:
    :undoc-members:
    :show-inheritance:

Jump Alignment
--------------
**Jump Alignment** is an extension to the HMM, which utilizes the chords that are parsed from tabs. Following
\cite{mcvicar2011using}, we refer to these chords parsed from tab files as Untimed Chord Sequences (UCSs).
Compared to the original HMM, in the Jump Alignment algorithm the state space and transition probabilities are altered
in such a way that it can align the UCSs to audio, while allowing for jumps to the start of other lines.

.. automodule:: decibel.audio_tab_aligner.jump_alignment
    :members:
    :undoc-members:
    :show-inheritance: