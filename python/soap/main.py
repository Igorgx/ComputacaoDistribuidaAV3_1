from lxml import etree
from spyne import AnyXml, Application, Integer, Unicode, rpc, ServiceBase
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

from python.common.music_store import Music, NotFoundError, Playlist, User, ValidationError, store


def text_node(parent, name: str, value) -> None:
    node = etree.SubElement(parent, name)
    node.text = str(value)


def status_xml() -> etree._Element:
    root = etree.Element("health")
    text_node(root, "status", "ok")
    text_node(root, "technology", "SOAP")
    text_node(root, "language", "Python")
    return root


def user_xml(item: User) -> etree._Element:
    root = etree.Element("user")
    text_node(root, "id", item.id)
    text_node(root, "name", item.name)
    text_node(root, "age", item.age)
    return root


def music_xml(item: Music) -> etree._Element:
    root = etree.Element("music")
    text_node(root, "id", item.id)
    text_node(root, "name", item.name)
    text_node(root, "artist", item.artist)
    return root


def playlist_xml(item: Playlist) -> etree._Element:
    root = etree.Element("playlist")
    text_node(root, "id", item.id)
    text_node(root, "name", item.name)
    text_node(root, "userId", item.userId)
    music_ids = etree.SubElement(root, "musicIds")
    for music_id in item.musicIds:
        text_node(music_ids, "musicId", music_id)
    return root


def collection_xml(name: str, children: list[etree._Element]) -> etree._Element:
    root = etree.Element(name)
    for child in children:
        root.append(child)
    return root


def deleted_xml() -> etree._Element:
    root = etree.Element("deleteResult")
    text_node(root, "deleted", "true")
    return root


def err(exc: Exception) -> etree._Element:
    code = "not_found" if isinstance(exc, NotFoundError) else "validation_error"
    if not isinstance(exc, (NotFoundError, ValidationError)):
        code = "error"
    root = etree.Element("error")
    text_node(root, "code", code)
    text_node(root, "message", str(exc))
    return root


class MusicStreamingSoap(ServiceBase):
    @rpc(_returns=AnyXml)
    def health(ctx):
        return status_xml()

    @rpc(_returns=AnyXml)
    def listUsers(ctx):
        return collection_xml("users", [user_xml(item) for item in store.list_users()])

    @rpc(Integer, _returns=AnyXml)
    def getUser(ctx, userId):
        try:
            return user_xml(store.get_user(userId))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, _returns=AnyXml)
    def createUser(ctx, id, name, age):
        try:
            data = {"name": name, "age": age}
            if id > 0:
                data["id"] = id
            return user_xml(store.create_user(data))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, _returns=AnyXml)
    def updateUser(ctx, id, name, age):
        try:
            return user_xml(store.update_user(id, {"name": name, "age": age}))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def deleteUser(ctx, id):
        try:
            store.delete_user(id)
            return deleted_xml()
        except Exception as exc:
            return err(exc)

    @rpc(_returns=AnyXml)
    def listMusics(ctx):
        return collection_xml("musics", [music_xml(item) for item in store.list_musics()])

    @rpc(Integer, _returns=AnyXml)
    def getMusic(ctx, musicId):
        try:
            return music_xml(store.get_music(musicId))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Unicode, _returns=AnyXml)
    def createMusic(ctx, id, name, artist):
        try:
            data = {"name": name, "artist": artist}
            if id > 0:
                data["id"] = id
            return music_xml(store.create_music(data))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Unicode, _returns=AnyXml)
    def updateMusic(ctx, id, name, artist):
        try:
            return music_xml(store.update_music(id, {"name": name, "artist": artist}))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def deleteMusic(ctx, id):
        try:
            store.delete_music(id)
            return deleted_xml()
        except Exception as exc:
            return err(exc)

    @rpc(_returns=AnyXml)
    def listPlaylists(ctx):
        return collection_xml("playlists", [playlist_xml(item) for item in store.list_playlists()])

    @rpc(Integer, _returns=AnyXml)
    def getPlaylist(ctx, playlistId):
        try:
            return playlist_xml(store.get_playlist(playlistId))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, Unicode, _returns=AnyXml)
    def createPlaylist(ctx, id, name, userId, musicIdsCsv):
        try:
            music_ids = [int(item) for item in musicIdsCsv.split(",") if item.strip()]
            data = {"name": name, "userId": userId, "musicIds": music_ids}
            if id > 0:
                data["id"] = id
            return playlist_xml(store.create_playlist(data))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, Unicode, Integer, Unicode, _returns=AnyXml)
    def updatePlaylist(ctx, id, name, userId, musicIdsCsv):
        try:
            music_ids = [int(item) for item in musicIdsCsv.split(",") if item.strip()]
            data = {"name": name, "userId": userId, "musicIds": music_ids}
            return playlist_xml(store.update_playlist(id, data))
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def deletePlaylist(ctx, id):
        try:
            store.delete_playlist(id)
            return deleted_xml()
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def listPlaylistsByUser(ctx, userId):
        try:
            return collection_xml(
                "playlists", [playlist_xml(item) for item in store.playlists_by_user(userId)]
            )
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def listMusicsByPlaylist(ctx, playlistId):
        try:
            return collection_xml(
                "musics", [music_xml(item) for item in store.musics_by_playlist(playlistId)]
            )
        except Exception as exc:
            return err(exc)

    @rpc(Integer, _returns=AnyXml)
    def listPlaylistsByMusic(ctx, musicId):
        try:
            return collection_xml(
                "playlists", [playlist_xml(item) for item in store.playlists_by_music(musicId)]
            )
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
