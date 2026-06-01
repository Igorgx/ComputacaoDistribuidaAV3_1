from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from python.common.music_store import NotFoundError, ValidationError, store

app = FastAPI(title="Music Streaming REST Python")


class UserIn(BaseModel):
    id: int | None = None
    name: str
    age: int


class MusicIn(BaseModel):
    id: int | None = None
    name: str
    artist: str


class PlaylistIn(BaseModel):
    id: int | None = None
    name: str
    userId: int
    musicIds: list[int]


def handle_error(exc: Exception):
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    raise exc


@app.get("/health")
def health():
    return {"status": "ok", "technology": "REST", "language": "Python"}


@app.get("/users")
def list_users():
    return store.to_dicts(store.list_users())


@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        return store.to_dict(store.get_user(user_id))
    except Exception as exc:
        handle_error(exc)


@app.post("/users", status_code=201)
def create_user(user: UserIn):
    try:
        return store.to_dict(store.create_user(user.model_dump(exclude_none=True)))
    except Exception as exc:
        handle_error(exc)


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserIn):
    try:
        return store.to_dict(store.update_user(user_id, user.model_dump(exclude_none=True)))
    except Exception as exc:
        handle_error(exc)


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    try:
        store.delete_user(user_id)
    except Exception as exc:
        handle_error(exc)


@app.get("/musics")
def list_musics():
    return store.to_dicts(store.list_musics())


@app.get("/musics/{music_id}")
def get_music(music_id: int):
    try:
        return store.to_dict(store.get_music(music_id))
    except Exception as exc:
        handle_error(exc)


@app.post("/musics", status_code=201)
def create_music(music: MusicIn):
    try:
        return store.to_dict(store.create_music(music.model_dump(exclude_none=True)))
    except Exception as exc:
        handle_error(exc)


@app.put("/musics/{music_id}")
def update_music(music_id: int, music: MusicIn):
    try:
        return store.to_dict(store.update_music(music_id, music.model_dump(exclude_none=True)))
    except Exception as exc:
        handle_error(exc)


@app.delete("/musics/{music_id}", status_code=204)
def delete_music(music_id: int):
    try:
        store.delete_music(music_id)
    except Exception as exc:
        handle_error(exc)


@app.get("/playlists")
def list_playlists():
    return store.to_dicts(store.list_playlists())


@app.get("/playlists/{playlist_id}")
def get_playlist(playlist_id: int):
    try:
        return store.to_dict(store.get_playlist(playlist_id))
    except Exception as exc:
        handle_error(exc)


@app.post("/playlists", status_code=201)
def create_playlist(playlist: PlaylistIn):
    try:
        return store.to_dict(store.create_playlist(playlist.model_dump(exclude_none=True)))
    except Exception as exc:
        handle_error(exc)


@app.put("/playlists/{playlist_id}")
def update_playlist(playlist_id: int, playlist: PlaylistIn):
    try:
        return store.to_dict(
            store.update_playlist(playlist_id, playlist.model_dump(exclude_none=True))
        )
    except Exception as exc:
        handle_error(exc)


@app.delete("/playlists/{playlist_id}", status_code=204)
def delete_playlist(playlist_id: int):
    try:
        store.delete_playlist(playlist_id)
    except Exception as exc:
        handle_error(exc)


@app.get("/users/{user_id}/playlists")
def playlists_by_user(user_id: int):
    try:
        return store.to_dicts(store.playlists_by_user(user_id))
    except Exception as exc:
        handle_error(exc)


@app.get("/playlists/{playlist_id}/musics")
def musics_by_playlist(playlist_id: int):
    try:
        return store.to_dicts(store.musics_by_playlist(playlist_id))
    except Exception as exc:
        handle_error(exc)


@app.get("/musics/{music_id}/playlists")
def playlists_by_music(music_id: int):
    try:
        return store.to_dicts(store.playlists_by_music(music_id))
    except Exception as exc:
        handle_error(exc)
