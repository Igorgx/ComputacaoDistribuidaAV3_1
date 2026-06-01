from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import RLock


@dataclass
class User:
    id: int
    name: str
    age: int


@dataclass
class Music:
    id: int
    name: str
    artist: str


@dataclass
class Playlist:
    id: int
    name: str
    userId: int
    musicIds: list[int]


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


class MusicStore:
    def __init__(self) -> None:
        self._lock = RLock()
        self.users: dict[int, User] = {}
        self.musics: dict[int, Music] = {}
        self.playlists: dict[int, Playlist] = {}
        self.seed()

    def seed(self) -> None:
        with self._lock:
            self.users = {
                i: User(i, f"Usuario {i}", 18 + (i % 45)) for i in range(1, 251)
            }
            artists = ["Ana Norte", "Banda Delta", "Clara Luz", "DJ Horizonte", "Eco Sul"]
            self.musics = {
                i: Music(i, f"Musica {i}", artists[i % len(artists)])
                for i in range(1, 501)
            }
            self.playlists = {}
            for i in range(1, 401):
                user_id = ((i - 1) % 250) + 1
                first_music = ((i * 7) % 500) + 1
                music_ids = [((first_music + j - 1) % 500) + 1 for j in range(5)]
                self.playlists[i] = Playlist(i, f"Playlist {i}", user_id, music_ids)

    @staticmethod
    def to_dict(item):
        return asdict(item)

    @staticmethod
    def to_dicts(items):
        return [asdict(item) for item in items]

    def _next_id(self, table: dict[int, object]) -> int:
        return max(table.keys(), default=0) + 1

    def list_users(self) -> list[User]:
        return list(self.users.values())

    def get_user(self, user_id: int) -> User:
        try:
            return self.users[user_id]
        except KeyError as exc:
            raise NotFoundError("usuario nao encontrado") from exc

    def create_user(self, data: dict) -> User:
        with self._lock:
            user_id = int(data.get("id") or self._next_id(self.users))
            if user_id in self.users:
                raise ValidationError("id de usuario ja existe")
            user = User(user_id, str(data["name"]), int(data["age"]))
            self.users[user_id] = user
            return user

    def update_user(self, user_id: int, data: dict) -> User:
        with self._lock:
            self.get_user(user_id)
            user = User(user_id, str(data["name"]), int(data["age"]))
            self.users[user_id] = user
            return user

    def delete_user(self, user_id: int) -> None:
        with self._lock:
            self.get_user(user_id)
            del self.users[user_id]
            self.playlists = {
                key: playlist
                for key, playlist in self.playlists.items()
                if playlist.userId != user_id
            }

    def list_musics(self) -> list[Music]:
        return list(self.musics.values())

    def get_music(self, music_id: int) -> Music:
        try:
            return self.musics[music_id]
        except KeyError as exc:
            raise NotFoundError("musica nao encontrada") from exc

    def create_music(self, data: dict) -> Music:
        with self._lock:
            music_id = int(data.get("id") or self._next_id(self.musics))
            if music_id in self.musics:
                raise ValidationError("id de musica ja existe")
            music = Music(music_id, str(data["name"]), str(data["artist"]))
            self.musics[music_id] = music
            return music

    def update_music(self, music_id: int, data: dict) -> Music:
        with self._lock:
            self.get_music(music_id)
            music = Music(music_id, str(data["name"]), str(data["artist"]))
            self.musics[music_id] = music
            for playlist in self.playlists.values():
                playlist.musicIds = [mid for mid in playlist.musicIds if mid in self.musics]
            return music

    def delete_music(self, music_id: int) -> None:
        with self._lock:
            self.get_music(music_id)
            del self.musics[music_id]
            for playlist in self.playlists.values():
                playlist.musicIds = [mid for mid in playlist.musicIds if mid != music_id]

    def list_playlists(self) -> list[Playlist]:
        return list(self.playlists.values())

    def get_playlist(self, playlist_id: int) -> Playlist:
        try:
            return self.playlists[playlist_id]
        except KeyError as exc:
            raise NotFoundError("playlist nao encontrada") from exc

    def _validate_playlist(self, user_id: int, music_ids: list[int]) -> None:
        self.get_user(user_id)
        for music_id in music_ids:
            self.get_music(music_id)

    def create_playlist(self, data: dict) -> Playlist:
        with self._lock:
            playlist_id = int(data.get("id") or self._next_id(self.playlists))
            if playlist_id in self.playlists:
                raise ValidationError("id de playlist ja existe")
            user_id = int(data["userId"])
            music_ids = [int(item) for item in data.get("musicIds", [])]
            self._validate_playlist(user_id, music_ids)
            playlist = Playlist(playlist_id, str(data["name"]), user_id, music_ids)
            self.playlists[playlist_id] = playlist
            return playlist

    def update_playlist(self, playlist_id: int, data: dict) -> Playlist:
        with self._lock:
            self.get_playlist(playlist_id)
            user_id = int(data["userId"])
            music_ids = [int(item) for item in data.get("musicIds", [])]
            self._validate_playlist(user_id, music_ids)
            playlist = Playlist(playlist_id, str(data["name"]), user_id, music_ids)
            self.playlists[playlist_id] = playlist
            return playlist

    def delete_playlist(self, playlist_id: int) -> None:
        with self._lock:
            self.get_playlist(playlist_id)
            del self.playlists[playlist_id]

    def playlists_by_user(self, user_id: int) -> list[Playlist]:
        self.get_user(user_id)
        return [playlist for playlist in self.playlists.values() if playlist.userId == user_id]

    def musics_by_playlist(self, playlist_id: int) -> list[Music]:
        playlist = self.get_playlist(playlist_id)
        return [self.get_music(music_id) for music_id in playlist.musicIds]

    def playlists_by_music(self, music_id: int) -> list[Playlist]:
        self.get_music(music_id)
        return [
            playlist for playlist in self.playlists.values() if music_id in playlist.musicIds
        ]


store = MusicStore()
