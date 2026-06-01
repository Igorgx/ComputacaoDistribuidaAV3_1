import grpc
import os

from python.grpc.generated import music_pb2, music_pb2_grpc


def main():
    target = os.getenv("GRPC_TARGET", "127.0.0.1:8002")
    with grpc.insecure_channel(target) as channel:
        users = music_pb2_grpc.UserServiceStub(channel)
        musics = music_pb2_grpc.MusicServiceStub(channel)
        playlists = music_pb2_grpc.PlaylistServiceStub(channel)

        print("users:", len(users.ListUsers(music_pb2.Empty()).items))
        print("musics:", len(musics.ListMusics(music_pb2.Empty()).items))
        print("playlist 1 musics:", len(playlists.ListMusicsByPlaylist(music_pb2.IdRequest(id=1)).items))

        created = users.CreateUser(
            music_pb2.UserRequest(user=music_pb2.User(name="Usuario Demo gRPC", age=30))
        )
        print("created user:", created)


if __name__ == "__main__":
    main()
