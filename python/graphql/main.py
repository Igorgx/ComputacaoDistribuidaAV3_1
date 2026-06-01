import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from python.common.music_store import store


@strawberry.type
class User:
    id: int
    name: str
    age: int


@strawberry.type
class Music:
    id: int
    name: str
    artist: str


@strawberry.type
class Playlist:
    id: int
    name: str
    userId: int
    musicIds: list[int]


@strawberry.input
class UserInput:
    name: str
    age: int
    id: int | None = None


@strawberry.input
class MusicInput:
    name: str
    artist: str
    id: int | None = None


@strawberry.input
class PlaylistInput:
    name: str
    userId: int
    musicIds: list[int]
    id: int | None = None


def user_out(item) -> User:
    return User(id=item.id, name=item.name, age=item.age)


def music_out(item) -> Music:
    return Music(id=item.id, name=item.name, artist=item.artist)


def playlist_out(item) -> Playlist:
    return Playlist(id=item.id, name=item.name, userId=item.userId, musicIds=item.musicIds)


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return [user_out(item) for item in store.list_users()]

    @strawberry.field
    def user(self, id: int) -> User:
        return user_out(store.get_user(id))

    @strawberry.field
    def musics(self) -> list[Music]:
        return [music_out(item) for item in store.list_musics()]

    @strawberry.field
    def music(self, id: int) -> Music:
        return music_out(store.get_music(id))

    @strawberry.field
    def playlists(self) -> list[Playlist]:
        return [playlist_out(item) for item in store.list_playlists()]

    @strawberry.field
    def playlist(self, id: int) -> Playlist:
        return playlist_out(store.get_playlist(id))

    @strawberry.field
    def playlists_by_user(self, user_id: int) -> list[Playlist]:
        return [playlist_out(item) for item in store.playlists_by_user(user_id)]

    @strawberry.field
    def musics_by_playlist(self, playlist_id: int) -> list[Music]:
        return [music_out(item) for item in store.musics_by_playlist(playlist_id)]

    @strawberry.field
    def playlists_by_music(self, music_id: int) -> list[Playlist]:
        return [playlist_out(item) for item in store.playlists_by_music(music_id)]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: UserInput) -> User:
        return user_out(store.create_user(input.__dict__))

    @strawberry.mutation
    def update_user(self, id: int, input: UserInput) -> User:
        return user_out(store.update_user(id, input.__dict__))

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        store.delete_user(id)
        return True

    @strawberry.mutation
    def create_music(self, input: MusicInput) -> Music:
        return music_out(store.create_music(input.__dict__))

    @strawberry.mutation
    def update_music(self, id: int, input: MusicInput) -> Music:
        return music_out(store.update_music(id, input.__dict__))

    @strawberry.mutation
    def delete_music(self, id: int) -> bool:
        store.delete_music(id)
        return True

    @strawberry.mutation
    def create_playlist(self, input: PlaylistInput) -> Playlist:
        return playlist_out(store.create_playlist(input.__dict__))

    @strawberry.mutation
    def update_playlist(self, id: int, input: PlaylistInput) -> Playlist:
        return playlist_out(store.update_playlist(id, input.__dict__))

    @strawberry.mutation
    def delete_playlist(self, id: int) -> bool:
        store.delete_playlist(id)
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
app = FastAPI(title="Music Streaming GraphQL Python")


@app.get("/health")
def health():
    return {"status": "ok", "technology": "GraphQL", "language": "Python"}


app.include_router(GraphQLRouter(schema), prefix="/graphql")
