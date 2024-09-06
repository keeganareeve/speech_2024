# speech_2024

Working with speech data. 

## Workflow:

1. (Setting up) Speech-Silence (intervals)
  Sectioning up long audio sequences into speech-silence intervals.
   Preferably, I'd like a single stream to handle any particular language for this initial bit of preprocessing.
   Outputs a PRAAT TextGrid with 'speech' and '' (silence) intervals.
   
3. (Adding) Transcription
   Sectioning up written transcription of audio into these intervals (including creating corresponding PRAAT TextGrid of its own).
   Automatic transcription with a LLM or other pretrained model serves as an alternative option.
   
5. Forced Alignment
   Forced Alignment of phones and words, ending up with csv files with intervals.
   
7. Features / Patterns
   Building systems to experiment with extracting different acoustic features and evaluating importance, primarily for prosody.
   Intensity,energy,power,pitch,amplitude. Likely will use parselmouth along with method to make it continuous.

## Scripts & Notebooks

**speech-silence0-pub.ipynb**: first version of (public) notebook for sectioning speech and non-speech (*silence* serves as a catch-all term) intervals.







