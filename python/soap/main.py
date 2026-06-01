import json

from spyne import Application, Integer, Unicode, rpc, ServiceBase
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

from python.common.music_store import NotFoundError, ValidationError, store


def ok(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def err(exc: Exception) -> str:
    code = "not_found" if isinstance(exc, NotFoundError) else "validation_error"
    if not isinstance(exc, (NotFoundError, ValidationError)):
        code = "error"
    return json.dumps({"error": code, "message": str(exc)}, ensure_ascii=False)


class MusicStreamingSoap(ServiceBase):
    @rpc(_returns=Unicode)
    def health(ctx):
        return ok({"status": "ok", "technology": "SOAP", "language": "Python"})

    @rpc(_returns=Unicode)
    def listUsers(ctx):
        return ok(store.to_dicts(store.list_users()))

    @rpc(Integer, _returns=Unicode)
    def getUser(ctx, userId):
        try:
            return ok(store.to_dict(store.get_user(userId)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, _returns=Unicode)
    def createUser(ctx, id, name, age):
        try:
            data = {"name": name, "age": age}
            if id > 0:
                data["id"] = id
            return ok(store.to_dict(store.create_user(data)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, _returns=Unicode)
    def updateUser(ctx, id, name, age):
        try:
            return ok(store.to_dict(store.update_user(id, {"name": name, "age": age})))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def deleteUser(ctx, id):
        try:
            store.delete_user(id)
            return ok({"deleted": True})
        except Exception as exc:
            return err(exc)

    @rpc(_returns=Unicode)
    def listMusics(ctx):
        return ok(store.to_dicts(store.list_musics()))

    @rpc(Integer, _returns=Unicode)
    def getMusic(ctx, musicId):
        try:
            return ok(store.to_dict(store.get_music(musicId)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Unicode, _returns=Unicode)
    def createMusic(ctx, id, name, artist):
        try:
            data = {"name": name, "artist": artist}
            if id > 0:
                data["id"] = id
            return ok(store.to_dict(store.create_music(data)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Unicode, _returns=Unicode)
    def updateMusic(ctx, id, name, artist):
        try:
            return ok(store.to_dict(store.update_music(id, {"name": name, "artist": artist})))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def deleteMusic(ctx, id):
        try:
            store.delete_music(id)
            return ok({"deleted": True})
        except Exception as exc:
            return err(exc)

    @rpc(_returns=Unicode)
    def listPlaylists(ctx):
        return ok(store.to_dicts(store.list_playlists()))

    @rpc(Integer, _returns=Unicode)
    def getPlaylist(ctx, playlistId):
        try:
            return ok(store.to_dict(store.get_playlist(playlistId)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, Unicode, _returns=Unicode)
    def createPlaylist(ctx, id, name, userId, musicIdsCsv):
        try:
            music_ids = [int(item) for item in musicIdsCsv.split(",") if item.strip()]
            data = {"name": name, "userId": userId, "musicIds": music_ids}
            if id > 0:
                data["id"] = id
            return ok(store.to_dict(store.create_playlist(data)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, Unicode, _returns=Unicode)
    def updatePlaylist(ctx, id, name, userId, musicIdsCsv):
        try:
            music_ids = [int(item) for item in musicIdsCsv.split(",") if item.strip()]
            data = {"name": name, "userId": userId, "musicIds": music_ids}
            return ok(store.to_dict(store.update_playlist(id, data)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def deletePlaylist(ctx, id):
        try:
            store.delete_playlist(id)
            return ok({"deleted": True})
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def listPlaylistsByUser(ctx, userId):
        try:
            return ok(store.to_dicts(store.playlists_by_user(userId)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def listMusicsByPlaylist(ctx, playlistId):
        try:
            return ok(store.to_dicts(store.musics_by_playlist(playlistId)))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=Unicode)
    def listPlaylistsByMusic(ctx, musicId):
        try:
            return ok(store.to_dicts(store.playlists_by_music(musicId)))
        except Exception as exc:
            return err(exc)


application = Application(
    [MusicStreamingSoap],
    tns="music.streaming.soap",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)
wsgi_application = WsgiApplication(application)


if __name__ == "__main__":
    print("Python SOAP on http://127.0.0.1:8004/?wsdl")
    make_server("127.0.0.1", 8004, wsgi_application).serve_forever()
