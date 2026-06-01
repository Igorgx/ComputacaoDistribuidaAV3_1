package com.music.graphql;

import com.music.common.HttpUtil;
import com.music.common.JsonUtil;
import com.music.common.MusicStore;
import com.music.common.NotFoundException;
import com.music.common.ValidationException;
import com.sun.net.httpserver.HttpServer;

import java.net.InetSocketAddress;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class GraphQlServer {
    private static final MusicStore store = new MusicStore();

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8103), 0);
        server.createContext("/", exchange -> {
            try {
                if (exchange.getRequestURI().getPath().equals("/health")) {
                    HttpUtil.send(exchange, 200, "application/json", JsonUtil.status("GraphQL"));
                    return;
                }
                if (!exchange.getRequestURI().getPath().equals("/graphql")) {
                    HttpUtil.send(exchange, 404, "application/json", JsonUtil.error("rota nao encontrada"));
                    return;
                }
                String body = HttpUtil.readBody(exchange);
                String query = JsonUtil.stringField(body, "query", body).replace("\\\"", "\"");
                HttpUtil.send(exchange, 200, "application/json", execute(query));
            } catch (NotFoundException exc) {
                HttpUtil.send(exchange, 200, "application/json", "{\"errors\":[{\"message\":" + JsonUtil.quote(exc.getMessage()) + "}]}");
            } catch (ValidationException | IllegalArgumentException exc) {
                HttpUtil.send(exchange, 200, "application/json", "{\"errors\":[{\"message\":" + JsonUtil.quote(exc.getMessage()) + "}]}");
            } catch (Exception exc) {
                HttpUtil.send(exchange, 500, "application/json", JsonUtil.error(exc.getMessage()));
            }
        });
        server.start();
        System.out.println("Java GraphQL on http://127.0.0.1:8103/graphql");
    }

    private static String execute(String query) {
        if (query.contains("createUser")) {
            var user = store.createUser(intArg(query, "id", null), stringArg(query, "name", ""), intArg(query, "age", 0));
            return data("createUser", JsonUtil.user(user));
        }
        if (query.contains("updateUser")) {
            var user = store.updateUser(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "age", 0));
            return data("updateUser", JsonUtil.user(user));
        }
        if (query.contains("deleteUser")) {
            store.deleteUser(intArg(query, "id", 0));
            return data("deleteUser", "true");
        }
        if (query.contains("createMusic")) {
            var music = store.createMusic(intArg(query, "id", null), stringArg(query, "name", ""), stringArg(query, "artist", ""));
            return data("createMusic", JsonUtil.music(music));
        }
        if (query.contains("updateMusic")) {
            var music = store.updateMusic(intArg(query, "id", 0), stringArg(query, "name", ""), stringArg(query, "artist", ""));
            return data("updateMusic", JsonUtil.music(music));
        }
        if (query.contains("deleteMusic")) {
            store.deleteMusic(intArg(query, "id", 0));
            return data("deleteMusic", "true");
        }
        if (query.contains("createPlaylist")) {
            var playlist = store.createPlaylist(intArg(query, "id", null), stringArg(query, "name", ""), intArg(query, "userId", 0), intListArg(query, "musicIds"));
            return data("createPlaylist", JsonUtil.playlist(playlist));
        }
        if (query.contains("updatePlaylist")) {
            var playlist = store.updatePlaylist(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "userId", 0), intListArg(query, "musicIds"));
            return data("updatePlaylist", JsonUtil.playlist(playlist));
        }
        if (query.contains("deletePlaylist")) {
            store.deletePlaylist(intArg(query, "id", 0));
            return data("deletePlaylist", "true");
        }
        if (query.contains("playlistsByUser")) return data("playlistsByUser", JsonUtil.playlists(store.playlistsByUser(intArg(query, "userId", 0))));
        if (query.contains("musicsByPlaylist")) return data("musicsByPlaylist", JsonUtil.musics(store.musicsByPlaylist(intArg(query, "playlistId", 0))));
        if (query.contains("playlistsByMusic")) return data("playlistsByMusic", JsonUtil.playlists(store.playlistsByMusic(intArg(query, "musicId", 0))));
        if (query.contains("user(")) return data("user", JsonUtil.user(store.getUser(intArg(query, "id", 0))));
        if (query.contains("music(")) return data("music", JsonUtil.music(store.getMusic(intArg(query, "id", 0))));
        if (query.contains("playlist(")) return data("playlist", JsonUtil.playlist(store.getPlaylist(intArg(query, "id", 0))));
        if (query.contains("users")) return data("users", JsonUtil.users(store.listUsers()));
        if (query.contains("musics")) return data("musics", JsonUtil.musics(store.listMusics()));
        if (query.contains("playlists")) return data("playlists", JsonUtil.playlists(store.listPlaylists()));
        return "{\"errors\":[{\"message\":\"operacao GraphQL nao reconhecida\"}]}";
    }

    private static String data(String field, String value) {
        return "{\"data\":{\"" + field + "\":" + value + "}}";
    }

    private static Integer intArg(String query, String name, Integer fallback) {
        Matcher matcher = Pattern.compile(name + "\\s*:\\s*(-?\\d+)").matcher(query);
        return matcher.find() ? Integer.parseInt(matcher.group(1)) : fallback;
    }

    private static String stringArg(String query, String name, String fallback) {
        Matcher matcher = Pattern.compile(name + "\\s*:\\s*\"([^\"]*)\"").matcher(query);
        return matcher.find() ? matcher.group(1) : fallback;
    }

    private static List<Integer> intListArg(String query, String name) {
        Matcher matcher = Pattern.compile(name + "\\s*:\\s*\\[([^]]*)\\]").matcher(query);
        if (!matcher.find()) return List.of();
        return Pattern.compile("-?\\d+").matcher(matcher.group(1)).results().map(item -> Integer.parseInt(item.group())).toList();
    }
}
