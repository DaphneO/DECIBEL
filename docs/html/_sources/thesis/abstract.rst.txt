================
What is DECIBEL?
================

**Automatic Chord Estimation (ACE)** is a fundamental task in Music Information Retrieval (MIR), which has applications in both music performance and in research on other MIR tasks. The ACE task consists of segmenting a music recording or score and assigning a chord label to each segment. ACE has been a task in the MIREX competition for 10 years, but is not yet a solved problem: current methods seem to have reached a glass ceiling. Moreover, many recent methods are trained on a limited data set and consequently suffer from overfitting. **DECIBEL** *(DEtection of Chords Improved By Exploiting Linking symbolic formats)* is a novel system that utilizes multiple symbolic music representations in addition to audio in order to improve ACE on popular music.

The **input** for DECIBEL not only consists of the audio file, but also contains a set of MIDI and tab files that are obtained through *web scraping* and *manually matched* to the audio file. Given the audio file and matched MIDI and tab files, the system first estimates *chord sequences* from each file, using a *representation-dependent method*. 

- For *audio* files, DECIBEL uses existing state-of-the-art audio ACE techniques: in my experiments, I use the output of the six ACE submissions from MIREX 2017, as well as a commercial state-of-the-art method.
- *MIDI* files are first aligned to the audio file, using a Dynamic Time Warping-based method; subsequently, chord sequences are estimated from the re-aligned MIDI files using an algorithm based on template matching. 
- *Tab* files are first parsed, resulting in untimed chord sequences and then aligned to the audio, using an existing algorithm based on a Hidden Markov Model. In a final step, DECIBEL uses a data fusion method that integrates all estimated chord sequences into one final output sequence. 

.. image:: DECIBEL.png

The main **contributions** of DECIBEL are twofold. First, by aligning different symbolic formats to audio, DECIBEL automatically creates a heterogeneous harmonic representation that enables large-scale cross-version analysis of popular music. Second, my results show that DECIBEL's data fusion method significantly improves each of the seven evaluated state-of-the-art audio ACE methods in terms of estimation accuracy. Exploiting the musical knowledge that is implicitly incorporated in MIDI and tab files, it breaks the observed glass ceiling, without requiring a lot of additional training, thereby prohibiting further overfitting to the existing chord annotations.

All information on DECIBEL is available in my Master's thesis: https://dspace.library.uu.nl/handle/1874/372620

DECIBEL was presented as a late breaking demo at ISMIR 2018. The abstract can be found here:
https://drive.google.com/file/d/1ivkZtA01e2h-AX-CQwX6ciX9dGrZOohn/view