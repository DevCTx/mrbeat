from audiostream import get_output

from audio_source_mixer import AudioSourceMixer
from audio_source_one_shot import AudioSourceOneShot


class AudioEngine():
    NB_CHANNEL = 2          # 1 = Mono  / 2 = Stereo
    FRAME_RATE = 22050      # Frequence de hachage du son (44100Hz ou 22050Hz etant de bon compromis)
    BUFFER_SIZE = 1024      # Taille du buffer de sortie audio
    output_stream = None    # sortie audio

    audio_source_one_shot = None     # source audio (fichier a lire en entier)

    def __init__(self):
        self.output_stream = get_output(channels=self.NB_CHANNEL,
                                        rate=self.FRAME_RATE,
                                        buffersize=self.BUFFER_SIZE)

        self.audio_source_one_shot = AudioSourceOneShot(self.output_stream)
        self.audio_source_one_shot.start()

    def play_one_shot_sound(self, wav_frames, wav_volume):
        self.audio_source_one_shot.set_wav_frames(wav_frames, wav_volume)

    def create_mixer(self, all_wav_frames, all_wav_volumes, bpm, min_bpm, nb_steps, on_clock_mixer_get_bytes ):
        audio_source_mixer = AudioSourceMixer(self.output_stream, all_wav_frames, all_wav_volumes,
                                              bpm, min_bpm, self.FRAME_RATE,
                                              nb_steps, on_clock_mixer_get_bytes )
        # audio_source_track.set_steps_sequence( () ) [sera fait plus tard à cause du get_bytes]
        audio_source_mixer.start()
        return audio_source_mixer