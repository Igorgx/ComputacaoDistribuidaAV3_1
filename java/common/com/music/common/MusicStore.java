package com.music.common;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class MusicStore {
    private final Map<Integer, User> users = new LinkedHashMap<>();
    private final Map<Integer, Music> musics = new LinkedHashMap<>();
    private final Map<Integer, Playlist> playlists = new LinkedHashMap<>();

    public MusicStore() {
        seed();
    }

    private synchronized void seed() {
        String[] artists = {"Ana Norte", "Banda Delta", "Clara Luz", "DJ Horizonte", "Eco Sul"};
        for (int i = 1; i <= 250; i++) {
            users.put(i, new User(i, "Usuario " + i, 18 + (i % 45)));
        }
        for (int i = 1; i <= 500; i++) {
            musics.put(i, new Music(i, "Musica " + i, artists[i % artists.length]));
        }
        for (int i = 1; i <= 400; i++) {
            int userId = ((i - 1) % 250) + 1;
            int firstMusic = ((i * 7) % 500) + 1;
            List<Integer> musicIds = new ArrayList<>();
            for (int j = 0; j < 5; j++) {
                musicIds.add(((firstMusic + j - 1) % 500) + 1);
            }
            playlists.put(i, new Playlist(i, "Playlist " + i, userId, musicIds));
        }
    }

    private int nextId(Map<Integer, ?> table) {
        return table.keySet().stream().mapToInt(Integer::intValue).max().orElse(0) + 1;
    }

    public synchronized List<User> listUsers() {
        return new ArrayList<>(users.values());
    }

    public synchronized User getUser(int id) {
        User user = users.get(id);
        if (user == null) throw new NotFoundException("usuario nao encontrado");
        return user;
    }

    public synchronized User createUser(Integer id, String name, int age) {
        int newId = id == null || id == 0 ? nextId(users) : id;
        if (users.containsKey(newId)) throw new ValidationException("id de usuario ja existe");
        User user = new User(newId, name, age);
        users.put(newId, user);
        return user;
    }

    public synchronized User updateUser(int id, String name, int age) {
        getUser(id);
        User user = new User(id, name, age);
        users.put(id, user);
        return user;
    }

    public synchronized void deleteUser(int id) {
        getUser(id);
        users.remove(id);
        playlists.entrySet().removeIf(entry -> entry.getValue().userId() == id);
    }

    public synchronized List<Music> listMusics() {
        return new ArrayList<>(musics.values());
    }

    public synchronized Music getMusic(int id) {
        Music music = musics.get(id);
        if (music == null) throw new NotFoundException("musica nao encontrada");
        return music;
    }

    public synchronized Music createMusic(Integer id, String name, String artist) {
        int newId = id == null || id == 0 ? nextId(musics) : id;
        if (musics.containsKey(newId)) throw new ValidationException("id de musica ja existe");
        Music music = new Music(newId, name, artist);
        musics.put(newId, music);
        return music;
    }

    public synchronized Music updateMusic(int id, String name, String artist) {
        getMusic(id);
        Music music = new Music(id, name, artist);
        musics.put(id, music);
        return music;
    }

    public synchronized void deleteMusic(int id) {
        getMusic(id);
        musics.remove(id);
        for (Map.Entry<Integer, Playlist> entry : new ArrayList<>(playlists.entrySet())) {
            Playlist playlist = entry.getValue();
            List<Integer> ids = new ArrayList<>(playlist.musicIds());
            ids.removeIf(musicId -> musicId == id);
            playlists.put(entry.getKey(), new Playlist(playlist.id(), playlist.name(), playlist.userId(), ids));
        }
    }

    public synchronized List<Playlist> listPlaylists() {
        return new ArrayList<>(playlists.values());
    }

    public synchronized Playlist getPlaylist(int id) {
        Playlist playlist = playlists.get(id);
        if (playlist == null) throw new NotFoundException("playlist nao encontrada");
        return playlist;
    }

    private void validatePlaylist(int userId, List<Integer> musicIds) {
        getUser(userId);
        for (int musicId : musicIds) {
            getMusic(musicId);
        }
    }

    public synchronized Playlist createPlaylist(Integer id, String name, int userId, List<Integer> musicIds) {
        int newId = id == null || id == 0 ? nextId(playlists) : id;
        if (playlists.containsKey(newId)) throw new ValidationException("id de playlist ja existe");
        validatePlaylist(userId, musicIds);
        Playlist playlist = new Playlist(newId, name, userId, new ArrayList<>(musicIds));
        playlists.put(newId, playlist);
        return playlist;
    }

    public synchronized Playlist updatePlaylist(int id, String name, int userId, List<Integer> musicIds) {
        getPlaylist(id);
        validatePlaylist(userId, musicIds);
        Playlist playlist = new Playlist(id, name, userId, new ArrayList<>(musicIds));
        playlists.put(id, playlist);
        return playlist;
    }

    public synchronized void deletePlaylist(int id) {
        getPlaylist(id);
        playlists.remove(id);
    }

    public synchronized List<Playlist> playlistsByUser(int userId) {
        getUser(userId);
        return playlists.values().stream().filter(item -> item.userId() == userId).toList();
    }

    public synchronized List<Music> musicsByPlaylist(int playlistId) {
        Playlist playlist = getPlaylist(playlistId);
        return playlist.musicIds().stream().map(this::getMusic).toList();
    }

    public synchronized List<Playlist> playlistsByMusic(int musicId) {
        getMusic(musicId);
        return playlists.values().stream().filter(item -> item.musicIds().contains(musicId)).toList();
    }
}
