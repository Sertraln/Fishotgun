from ursina import Entity, Audio, destroy
import client.data as g

class MusicManager(Entity):
    def __init__(self):
        super().__init__(ignore_paused=True)
        self._paused = False
        self._started = False
        self._first = True

    def start(self):
        """Démarre ou reprend la playlist."""
        def start(self):
            if self._started:
                if self._paused and g.current_music:
                    g.current_music.resume()
                    self._paused = False
            else:
                self._started = True
                self._paused = False
                g.remaining_music = g.music_playlist_paths.copy()
                g.remaining_music.remove(g.life_is_awesome_path)
                g.current_music_path = g.life_is_awesome_path
                g.current_music = Audio(
                    g.current_music_path,
                    autoplay=True,
                    loop=False,
                    volume=0.4,
                    ignore_paused=True
                )

    def pause_playlist(self):
        if self._started and not self._paused and g.current_music:
            g.current_music.pause()
            self._paused = True

    def update(self):
        if not self._started or self._paused:
            return

        if g.current_music and not g.current_music.playing:
            self._first = False
            g.play_random_music()