from concurrent import futures

import grpc

from python.common.music_store import NotFoundError, ValidationError, store
from python.grpc.generated import music_pb2, music_pb2_grpc


def abort(context, exc: Exception):
    code = grpc.StatusCode.NOT_FOUND if isinstance(exc, NotFoundError) else grpc.StatusCode.INVALID_ARGUMENT
    if not isinstance(exc, (NotFoundError, ValidationError)):
        code = grpc.StatusCode.INTERNAL
    context.abort(code, str(exc))


def user_msg(item):
    return music_pb2.User(id=item.id, name=item.name, age=item.age)


def music_msg(item):
    return music_pb2.Music(id=item.id, name=item.name, artist=item.artist)


def playlist_msg(item):
    return music_pb2.Playlist(
        id=item.id, name=item.name, user_id=item.userId, music_ids=item.musicIds
    )


class UserService(music_pb2_grpc.UserServiceServicer):
    def ListUsers(self, request, context):
        return music_pb2.UserList(items=[user_msg(item) for item in store.list_users()])

    def GetUser(self, request, context):
        try:
            return user_msg(store.get_user(request.id))
        except Exception as exc:
            abort(context, exc)

    def CreateUser(self, request, context):
        try:
            data = {"id": request.user.id, "name": request.user.name, "age": request.user.age}
            if data["id"] == 0:
                data.pop("id")
            return user_msg(store.create_user(data))
        except Exception as exc:
            abort(context, exc)

    def UpdateUser(self, request, context):
        try:
            return user_msg(
                store.update_user(
                    request.user.id, {"name": request.user.name, "age": request.user.age}
                )
            )
        except Exception as exc:
            abort(context, exc)

    def DeleteUser(self, request, context):
        try:
            store.delete_user(request.id)
            return music_pb2.Empty()
        except Exception as exc:
            abort(context, exc)


class MusicService(music_pb2_grpc.MusicServiceServicer):
    def ListMusics(self, request, context):
        return music_pb2.MusicList(items=[music_msg(item) for item in store.list_musics()])

    def GetMusic(self, request, context):
        try:
            return music_msg(store.get_music(request.id))
        except Exception as exc:
            abort(context, exc)

    def CreateMusic(self, request, context):
        try:
            data = {
                "id": request.music.id,
                "name": request.music.name,
                "artist": request.music.artist,
            }
            if data["id"] == 0:
                data.pop("id")
            return music_msg(store.create_music(data))
        except Exception as exc:
            abort(context, exc)

    def UpdateMusic(self, request, context):
        try:
            return music_msg(
                store.update_music(
                    request.music.id,
                    {"name": request.music.name, "artist": request.music.artist},
                )
            )
        except Exception as exc:
            abort(context, exc)

    def DeleteMusic(self, request, context):
        try:
            store.delete_music(request.id)
            return music_pb2.Empty()
        except Exception as exc:
            abort(context, exc)


class PlaylistService(music_pb2_grpc.PlaylistServiceServicer):
    def ListPlaylists(self, request, context):
        return music_pb2.PlaylistList(
            items=[playlist_msg(item) for item in store.list_playlists()]
        )

    def GetPlaylist(self, request, context):
        try:
            return playlist_msg(store.get_playlist(request.id))
        except Exception as exc:
            abort(context, exc)

    def CreatePlaylist(self, request, context):
        try:
            data = {
                "id": request.playlist.id,
                "name": request.playlist.name,
                "userId": request.playlist.user_id,
                "musicIds": list(request.playlist.music_ids),
            }
            if data["id"] == 0:
                data.pop("id")
            return playlist_msg(store.create_playlist(data))
        except Exception as exc:
            abort(context, exc)

    def UpdatePlaylist(self, request, context):
        try:
            return playlist_msg(
                store.update_playlist(
                    request.playlist.id,
                    {
                        "name": request.playlist.name,
                        "userId": request.playlist.user_id,
                        "musicIds": list(request.playlist.music_ids),
                    },
                )
            )
        except Exception as exc:
            abort(context, exc)

    def DeletePlaylist(self, request, context):
        try:
            store.delete_playlist(request.id)
            return music_pb2.Empty()
        except Exception as exc:
            abort(context, exc)

    def ListPlaylistsByUser(self, request, context):
        try:
            return music_pb2.PlaylistList(
                items=[playlist_msg(item) for item in store.playlists_by_user(request.id)]
            )
        except Exception as exc:
            abort(context, exc)

    def ListMusicsByPlaylist(self, request, context):
        try:
            return music_pb2.MusicList(
                items=[music_msg(item) for item in store.musics_by_playlist(request.id)]
            )
        except Exception as exc:
            abort(context, exc)

    def ListPlaylistsByMusic(self, request, context):
        try:
            return music_pb2.PlaylistList(
                items=[playlist_msg(item) for item in store.playlists_by_music(request.id)]
            )
        except Exception as exc:
            abort(context, exc)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    music_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    music_pb2_grpc.add_MusicServiceServicer_to_server(MusicService(), server)
    music_pb2_grpc.add_PlaylistServiceServicer_to_server(PlaylistService(), server)
    server.add_insecure_port("127.0.0.1:8002")
    server.start()
    print("Python gRPC on 127.0.0.1:8002")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
