=========================
Installation instructions
=========================

How to install DECIBEL?

1. First install dependencies. You need fluidsynth for synthesizing MIDI, which is part of DECIBEL's audio-MIDI alignment
   procedure. For Ubuntu/Debian, use:

   .. code-block:: bash

       sudo apt-get install fluidsynth

   Installation instructions for other operating systems can be found at
   https://github.com/FluidSynth/fluidsynth/wiki/Download

2. Download data folder from https://drive.google.com/drive/folders/1U7FPx29Ugbv7ff-160qnDKrYTQZtIfJL and store it on
   your computer. This folder will be filled with (intermediate) results, tables, figures, etc.
   The total size of this folder will be around 12 GB, so make sure that you have enough space. It is possible to store
   the data on an external hard drive.
3. If you do not yet have python and pip installed, install them. DECIBEL was made in Python 3.5.
4. Clone code from GitHub repository https://github.com/DaphneO/DECIBEL into some directory on your computer and install
   the DECIBEL package.

    .. code-block:: bash

      pip install https://github.com/DaphneO/DECIBEL.git

4. Change the path in decibel.utils.data_path.txt to your local data path (where you put the files in step 2)
5. Find the audio files of the Beatles and Queen songs from the Isophonics reference annotations. Due to copyright
   reasons, I cannot share them. Place them in the Input/Audio folder in your local data path and rename them to
   '[key].wav'. You can find the key-song combinations in the IndexAudio.csv file in the Input folder of your data
   directory. For example, '1.wav' is the audio of the Beatles song *I Saw Her Standing There*.
6. Run DECIBEL! You can reproduce our experiments by running framework.py. Dependent on the number of cores on your
   computer, this will take ca. 15 hours. But since DECIBEL saves intermediate results, you can terminate the run when
   you which; in the next run, DECIBEL will continue where it stopped in the previous run.
