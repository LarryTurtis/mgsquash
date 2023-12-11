# mgsquash
A simple command line utility to remove the silent sections in a wav file and replace them with Morphagene splice markers.

## Installation

Install with pip:

```
pip install mgsquash
```

## Usage

At the time of writing, mgsquash only works on **stereo**, **32-bit** wav files with a sample rate of **48000**. Basically, the file has to *already* be compatible with morphagene. 

If mgsquash doesn't work for you, first make sure that the source wav file can be played by morphagene.

Run mgsquash with 3 arguments: 
- The path to the source wav file.
- The minimum length, in milliseconds, that should be considered when stripping silence. **Example**: You only want to remove a section if the silence lasts one second or more... you would specify 1000. 
- The threshold, in dBFS, that you want to be considered as "silence". Larger numbers will result in more audio being removed. **Example**: You've got an isolated vocal track. The backing track is still slightly audible for the instrumental portions, but it's always -20 dBFS or less. You want it removed. Specify -20.

```
mgsquash ./mywav 1000 -20
```