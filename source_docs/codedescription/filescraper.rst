===========================
Scraping MIDI and tab files
===========================

DECIBEL uses a data set of audio, MIDI files and tabs. This data set is based on a subset of the Isophonics Reference
Annotations [mauch2009omras2]_. The Isophonics data set contains chord annotations for 180 Beatles songs, 20 songs by
Queen, 7 songs by Carole King and 18 songs by Zweieck. In my experiments, I only used the songs by the Beatles and
Queen, as there were no MIDI or tabs for Zweieck available and there were some inconsistencies in the Carole King
annotations.

The :mod:`decibel.file_scraper.midi_scraper` and :mod:`decibel.file_scraper.tab_scraper` modules contains some handy
functions to automatically scrape a predefined list of MIDI and tab files from the internet. Using these functions, you
can either reproduce my experiments on the Isophonics dataset or create your own data set of MIDI and tab files.

Scraping MIDI files
-------------------

.. automodule:: decibel.file_scraper.midi_scraper
    :members:
    :undoc-members:
    :show-inheritance:

Scraping Tab files
------------------

.. automodule:: decibel.file_scraper.tab_scraper
    :members:
    :undoc-members:
    :show-inheritance:

.. [mauch2009omras2] Mauch, Matthias, et al. "OMRAS2 metadata project 2009." Proc. of 10th International Conference on
   Music Information Retrieval. 2009.
