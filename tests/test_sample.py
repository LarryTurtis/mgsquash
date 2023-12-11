# content of test_sample.py
from mgsquash import WavData
import pytest, struct

header_bytes = 8
sample_rate = 48000
channels = 2
bytes_per_sample = 4
one_second_of_audio = sample_rate * channels * bytes_per_sample
data_size = header_bytes + one_second_of_audio
class TestWavData:
       
    def test_should_have_the_right_size(self, simple_file):
        wavData = WavData(simple_file.name, 0, data_size) 
        wavData.detect_silence(50, -24) == simple_file 
        assert wavData.size == one_second_of_audio

    def test_should_detect_silence_correctly(self, simple_file):
        wavData = WavData(simple_file.name, 0, data_size) 
        markers = wavData.detect_silence(50, -24) 
        assert markers == [[59876, 120136]]

    def test_should_strip_silence_correctly(self, simple_file):
        wavData = WavData(simple_file.name, 0, data_size) 
        markers = wavData.detect_silence(50, -24) 
        wavData.strip_sections(markers) 
        assert wavData.size == one_second_of_audio - (120136 - 59876 + 4)

@pytest.fixture
def simple_file(tmp_path):
   with open(tmp_path / "file.wav", "wb") as file:
    file.write(b'data')
    file.write((one_second_of_audio).to_bytes(4, 'little'))
    for i in range(0, sample_rate * channels):
        # This writes 4 bytes by default.
        if i > 15000 and i < 30000:
            file.write(struct.pack('<f', 0.0))
        else:
            file.write(struct.pack('<f', 0.75))
   return file