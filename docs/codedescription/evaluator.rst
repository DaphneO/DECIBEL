==========
Evaluation
==========

In order to evaluate both the performance of DECIBEL's representation-specific subsystems and its final output
chord sequence, we need evaluation measures. The quality of a chord sequence is usually determined by comparing it to a
ground truth created by one or more human annotators. Commonly used **data sets** with chord annotations, which are
also used in the MIREX ACE contest, are Isophonics, Billboard, RobbieWilliams, RWC-Popular and USPOP2002Chords.
DECIBEL uses the Isophonics data set, augmented with matched MIDI and tab files.

The standard quality measure to evaluate the quality of an automatic transcription is **chord symbol recall** (CSR).
This measure is also used in MIREX. CSR is the summed duration of time periods where the correct chord has been
identified, normalized by the total duration of the song. Until 2013, MRIEX used an approximate, frame-based CSR
calculated by sampling both the ground-truth and the automatic annotations every 10 ms and dividing the number of
correctly annotated samples by the total number of samples. Since 2013, MIREX has used segment-based CSR, which is more
precise and computationally more efficient.

For results that are calculated for the whole data set, we weigh the CSR by the length of the song when computing an
average for a given corpus. This final number is referred to as the **weighted chord symbol recall** (WCSR). Calculating
the WCSR is basically the same as treating the data set as one big audio file, and calculating the CSR between the
concatenation of all ground-truth annotations and the concatenation of all estimated annotations.

The CSR correctly indicates the accuracy of an ACE algorithm in terms of whether the estimated chord for a given instant
in the audio is correct. It it therefore widely used in the evaluation of ACE systems. However, the annotation with the
highest CSR is not always the annotation that would be considered the best by human listeners. For this purpose,
we also use measures based on the **directional hamming distance**, which describes how fragmented a chord segmentation
is with respect to the ground truth chord segmentation.

.. automodule:: decibel.evaluator.evaluator
    :members:
    :undoc-members:
    :show-inheritance: