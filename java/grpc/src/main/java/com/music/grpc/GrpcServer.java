package com.music.grpc;

import com.music.common.MusicStore;
import com.music.common.NotFoundException;
import com.music.common.ValidationException;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.Status;
import io.grpc.stub.StreamObserver;

public class GrpcServer {
    private static final MusicStore store = new MusicStore();

    public static void main(String[] args) throws Exception {
        Server server = ServerBuilder.forPort(8102)
                .addService(new Users())
                .addService(new Musics())
                .addService(new Playlists())
                .build()
                .start();
        System.out.println("Java gRPC on 127.0.0.1:8102");
        server.awaitTermination();
    }

    private static User toUser(com.music.common.User item) {
        return User.newBuilder().setId(item.id()).setName(item.name()).setAge(item.age()).build();
    }

    private static Music toMusic(com.music.common.Music item) {
        return Music.newBuilder().setId(item.id()).setName(item.name()).setArtist(item.artist()).build();
    }

    private static Playlist toPlaylist(com.music.common.Playlist item) {
        return Playlist.newBuilder()
                .setId(item.id())
                .setName(item.name())
                .setUserId(item.userId())
                .addAllMusicIds(item.musicIds())
                .build();
    }

    private static void fail(StreamObserver<?> response, Exception exc) {
        Status status = exc instanceof NotFoundException ? Status.NOT_FOUND : Status.INVALID_ARGUMENT;
        if (!(exc instanceof NotFoundException || exc instanceof ValidationException)) status = Status.INTERNAL;
        response.onError(status.withDescription(exc.getMessage()).asRuntimeException());
    }

    private static class Users extends UserServiceGrpc.UserServiceImplBase {
        @Override
        public void listUsers(Empty request, StreamObserver<UserList> response) {
            response.onNext(UserList.newBuilder().addAllItems(store.listUsers().stream().map(GrpcServer::toUser).toList()).build());
            response.onCompleted();
        }

        @Override
        public void getUser(IdRequest request, StreamObserver<User> response) {
            try {
                response.onNext(toUser(store.getUser(request.getId())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void createUser(UserRequest request, StreamObserver<User> response) {
            try {
                User user = request.getUser();
                response.onNext(toUser(store.createUser(user.getId(), user.getName(), user.getAge())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void updateUser(UserRequest request, StreamObserver<User> response) {
            try {
                User user = request.getUser();
                response.onNext(toUser(store.updateUser(user.getId(), user.getName(), user.getAge())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void deleteUser(IdRequest request, StreamObserver<Empty> response) {
            try {
                store.deleteUser(request.getId());
                response.onNext(Empty.newBuilder().build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }
    }

    private static class Musics extends MusicServiceGrpc.MusicServiceImplBase {
        @Override
        public void listMusics(Empty request, StreamObserver<MusicList> response) {
            response.onNext(MusicList.newBuilder().addAllItems(store.listMusics().stream().map(GrpcServer::toMusic).toList()).build());
            response.onCompleted();
        }

        @Override
        public void getMusic(IdRequest request, StreamObserver<Music> response) {
            try {
                response.onNext(toMusic(store.getMusic(request.getId())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void createMusic(MusicRequest request, StreamObserver<Music> response) {
            try {
                Music music = request.getMusic();
                response.onNext(toMusic(store.createMusic(music.getId(), music.getName(), music.getArtist())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void updateMusic(MusicRequest request, StreamObserver<Music> response) {
            try {
                Music music = request.getMusic();
                response.onNext(toMusic(store.updateMusic(music.getId(), music.getName(), music.getArtist())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void deleteMusic(IdRequest request, StreamObserver<Empty> response) {
            try {
                store.deleteMusic(request.getId());
                response.onNext(Empty.newBuilder().build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }
    }

    private static class Playlists extends PlaylistServiceGrpc.PlaylistServiceImplBase {
        @Override
        public void listPlaylists(Empty request, StreamObserver<PlaylistList> response) {
            response.onNext(PlaylistList.newBuilder().addAllItems(store.listPlaylists().stream().map(GrpcServer::toPlaylist).toList()).build());
            response.onCompleted();
        }

        @Override
        public void getPlaylist(IdRequest request, StreamObserver<Playlist> response) {
            try {
                response.onNext(toPlaylist(store.getPlaylist(request.getId())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void createPlaylist(PlaylistRequest request, StreamObserver<Playlist> response) {
            try {
                Playlist playlist = request.getPlaylist();
                response.onNext(toPlaylist(store.createPlaylist(playlist.getId(), playlist.getName(), playlist.getUserId(), playlist.getMusicIdsList())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void updatePlaylist(PlaylistRequest request, StreamObserver<Playlist> response) {
            try {
                Playlist playlist = request.getPlaylist();
                response.onNext(toPlaylist(store.updatePlaylist(playlist.getId(), playlist.getName(), playlist.getUserId(), playlist.getMusicIdsList())));
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void deletePlaylist(IdRequest request, StreamObserver<Empty> response) {
            try {
                store.deletePlaylist(request.getId());
                response.onNext(Empty.newBuilder().build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void listPlaylistsByUser(IdRequest request, StreamObserver<PlaylistList> response) {
            try {
                response.onNext(PlaylistList.newBuilder().addAllItems(store.playlistsByUser(request.getId()).stream().map(GrpcServer::toPlaylist).toList()).build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void listMusicsByPlaylist(IdRequest request, StreamObserver<MusicList> response) {
            try {
                response.onNext(MusicList.newBuilder().addAllItems(store.musicsByPlaylist(request.getId()).stream().map(GrpcServer::toMusic).toList()).build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }

        @Override
        public void listPlaylistsByMusic(IdRequest request, StreamObserver<PlaylistList> response) {
            try {
                response.onNext(PlaylistList.newBuilder().addAllItems(store.playlistsByMusic(request.getId()).stream().map(GrpcServer::toPlaylist).toList()).build());
                response.onCompleted();
            } catch (Exception exc) {
                fail(response, exc);
            }
        }
    }
}
