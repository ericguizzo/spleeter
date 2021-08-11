import os
import cog
import tempfile
import shutil
from pathlib import Path
from spleeter.separator import Separator
from spleeter.audio.adapter import AudioAdapter
import zipfile

class SpleeterPredictor(cog.Predictor):
    def setup(self):
        """Load the Deezer separator model"""
        self.separator = Separator('spleeter:2stems')
        self.audio_loader = AudioAdapter.default()

    @cog.input("input", type=Path, help="Audio mixture path")
    @cog.input("sample_rate", type=int, default=44100, help="Audio sample rate")

    def predict(self, input, sample_rate):
        """Separate the vocal track from an audio mixture"""
        #compute prediction
        waveform, _ = self.audio_loader.load(str(input), sample_rate=sample_rate)
        prediction = self.separator.separate(waveform)

        out_path = Path(tempfile.mkdtemp())
        zip_path = Path(tempfile.mkdtemp()) / "output.zip"

        out_path_vocals = out_path / "vocals.wav"
        out_path_accompaniment = out_path / "accompaniment.wav"

        self.audio_loader.save(str(out_path_vocals), prediction['vocals'], sample_rate=sample_rate)
        self.audio_loader.save(str(out_path_accompaniment), prediction['accompaniment'], sample_rate=sample_rate)

        with zipfile.ZipFile(str(zip_path), "w") as zf:
            zf.write(str(out_path_vocals))
            zf.write(str(out_path_accompaniment))

        return zip_path
