# content of test_sample.py
from morphagently import WavData
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
        wavData.remove_silence(50, -50) == simple_file 
        assert wavData.size == one_second_of_audio

@pytest.fixture
def simple_file(tmp_path):
   with open(tmp_path / "file.wav", "wb") as file:
    file.write(b'data')
    file.write((one_second_of_audio).to_bytes(4, 'little'))
    for i in range(0, sample_rate * channels):
        # This writes 4 bytes by default.
        file.write(struct.pack('<f', 0.75))
   return file