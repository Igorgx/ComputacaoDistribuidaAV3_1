import os
import random
import time

from locust import HttpUser, User, between, events, task


PROTOCOL = os.getenv("PROTOCOL", "rest").lower()
GRPC_GEVENT_READY = False


class MusicHttpUser(HttpUser):
    wait_time = between(0.1, 0.8)

    @task(4)
    def list_musics(self):
        if PROTOCOL == "graphql":
            self.client.post(
                "/graphql",
                json={"query": "{ musics { id name artist } }"},
                name="graphql:listMusics",
            )
        elif PROTOCOL == "soap":
            self.client.post("/", data=soap("listMusics"), headers=soap_headers(), name="soap:listMusics")
        else:
            self.client.get("/musics", name="rest:listMusics")

    @task(2)
    def get_user(self):
        user_id = random.randint(1, 250)
        if PROTOCOL == "graphql":
            self.client.post(
                "/graphql",
                json={"query": f"{{ user(id: {user_id}) {{ id name age }} }}"},
                name="graphql:getUser",
            )
        elif PROTOCOL == "soap":
            self.client.post("/", data=soap("getUser", f"<userId>{user_id}</userId>"), headers=soap_headers(), name="soap:getUser")
        else:
            self.client.get(f"/users/{user_id}", name="rest:getUser")

    @task(2)
    def create_playlist(self):
        suffix = random.randint(100000, 999999)
        user_id = random.randint(1, 250)
        music_ids = [random.randint(1, 500) for _ in range(5)]
        if PROTOCOL == "graphql":
            query = (
                "mutation { createPlaylist(input: { "
                f'name: "Carga {suffix}", userId: {user_id}, musicIds: {music_ids}'
                " }) { id name userId musicIds } }"
            )
            self.client.post("/graphql", json={"query": query}, name="graphql:createPlaylist")
        elif PROTOCOL == "soap":
            body = (
                f"<id>0</id><name>Carga {suffix}</name><userId>{user_id}</userId>"
                f"<musicIdsCsv>{','.join(map(str, music_ids))}</musicIdsCsv>"
            )
            self.client.post("/", data=soap("createPlaylist", body), headers=soap_headers(), name="soap:createPlaylist")
        else:
            self.client.post(
                "/playlists",
                json={"name": f"Carga {suffix}", "userId": user_id, "musicIds": music_ids},
                name="rest:createPlaylist",
            )

    @task(3)
    def musics_by_playlist(self):
        playlist_id = random.randint(1, 400)
        if PROTOCOL == "graphql":
            self.client.post(
                "/graphql",
                json={
                    "query": f"{{ musicsByPlaylist(playlistId: {playlist_id}) {{ id name artist }} }}"
                },
                name="graphql:musicsByPlaylist",
            )
        elif PROTOCOL == "soap":
            self.client.post(
                "/",
                data=soap("listMusicsByPlaylist", f"<playlistId>{playlist_id}</playlistId>"),
                headers=soap_headers(),
                name="soap:musicsByPlaylist",
            )
        else:
            self.client.get(f"/playlists/{playlist_id}/musics", name="rest:musicsByPlaylist")

    @task(2)
    def playlists_by_music(self):
        music_id = random.randint(1, 500)
        if PROTOCOL == "graphql":
            self.client.post(
                "/graphql",
                json={
                    "query": f"{{ playlistsByMusic(musicId: {music_id}) {{ id name userId musicIds }} }}"
                },
                name="graphql:playlistsByMusic",
            )
        elif PROTOCOL == "soap":
            self.client.post(
                "/",
                data=soap("listPlaylistsByMusic", f"<musicId>{music_id}</musicId>"),
                headers=soap_headers(),
                name="soap:playlistsByMusic",
            )
        else:
            self.client.get(f"/musics/{music_id}/playlists", name="rest:playlistsByMusic")


def soap(operation, body=""):
    return f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <{operation} xmlns="music.streaming.soap">{body}</{operation}>
  </soap:Body>
</soap:Envelope>"""


def soap_headers():
    return {"Content-Type": "text/xml; charset=utf-8"}


class MusicGrpcUser(User):
    wait_time = between(0.1, 0.8)

    def on_start(self):
        global GRPC_GEVENT_READY
        import grpc
        import grpc.experimental.gevent as grpc_gevent
        from python.grpc.generated import music_pb2, music_pb2_grpc

        if not GRPC_GEVENT_READY:
            grpc_gevent.init_gevent()
            GRPC_GEVENT_READY = True

        self.pb = music_pb2
        self.channel = grpc.insecure_channel(self.host.replace("http://", "").replace("https://", ""))
        self.users = music_pb2_grpc.UserServiceStub(self.channel)
        self.musics = music_pb2_grpc.MusicServiceStub(self.channel)
        self.playlists = music_pb2_grpc.PlaylistServiceStub(self.channel)

    def on_stop(self):
        if hasattr(self, "channel"):
            try:
                self.channel.close()
            except RuntimeError:
                pass

    def timed(self, name, fn):
        started = time.perf_counter()
        try:
            result = fn()
            events.request.fire(
                request_type="grpc",
                name=name,
                response_time=(time.perf_counter() - started) * 1000,
                response_length=result.ByteSize() if hasattr(result, "ByteSize") else 0,
                exception=None,
            )
        except Exception as exc:
            events.request.fire(
                request_type="grpc",
                name=name,
                response_time=(time.perf_counter() - started) * 1000,
                response_length=0,
                exception=exc,
            )

    @task(4)
    def list_musics(self):
        self.timed("grpc:listMusics", lambda: self.musics.ListMusics(self.pb.Empty()))

    @task(2)
    def get_user(self):
        self.timed("grpc:getUser", lambda: self.users.GetUser(self.pb.IdRequest(id=random.randint(1, 250))))

    @task(2)
    def create_playlist(self):
        user_id = random.randint(1, 250)
        music_ids = [random.randint(1, 500) for _ in range(5)]
        playlist = self.pb.Playlist(name=f"Carga {random.randint(100000, 999999)}", user_id=user_id, music_ids=music_ids)
        self.timed("grpc:createPlaylist", lambda: self.playlists.CreatePlaylist(self.pb.PlaylistRequest(playlist=playlist)))

    @task(3)
    def musics_by_playlist(self):
        self.timed("grpc:musicsByPlaylist", lambda: self.playlists.ListMusicsByPlaylist(self.pb.IdRequest(id=random.randint(1, 400))))

    @task(2)
    def playlists_by_music(self):
        self.timed("grpc:playlistsByMusic", lambda: self.playlists.ListPlaylistsByMusic(self.pb.IdRequest(id=random.randint(1, 500))))
