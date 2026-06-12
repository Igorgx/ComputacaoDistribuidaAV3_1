package com.music.graphql;

import com.music.common.HttpUtil;
import com.music.common.JsonUtil;
import com.music.common.Music;
import com.music.common.MusicStore;
import com.music.common.NotFoundException;
import com.music.common.Playlist;
import com.music.common.User;
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
                String query = queryFromBody(body);
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
            var user = store.createUser(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "age", 0));
            return data("createUser", userJson(user, selection(query, "createUser")));
        }
        if (query.contains("updateUser")) {
            var user = store.updateUser(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "age", 0));
            return data("updateUser", userJson(user, selection(query, "updateUser")));
        }
        if (query.contains("deleteUser")) {
            store.deleteUser(intArg(query, "id", 0));
            return data("deleteUser", "true");
        }
        if (query.contains("createMusic")) {
            var music = store.createMusic(intArg(query, "id", 0), stringArg(query, "name", ""), stringArg(query, "artist", ""));
            return data("createMusic", musicJson(music, selection(query, "createMusic")));
        }
        if (query.contains("updateMusic")) {
            var music = store.updateMusic(intArg(query, "id", 0), stringArg(query, "name", ""), stringArg(query, "artist", ""));
            return data("updateMusic", musicJson(music, selection(query, "updateMusic")));
        }
        if (query.contains("deleteMusic")) {
            store.deleteMusic(intArg(query, "id", 0));
            return data("deleteMusic", "true");
        }
        if (query.contains("createPlaylist")) {
            var playlist = store.createPlaylist(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "userId", 0), intListArg(query, "musicIds"));
            return data("createPlaylist", playlistJson(playlist, selection(query, "createPlaylist")));
        }
        if (query.contains("updatePlaylist")) {
            var playlist = store.updatePlaylist(intArg(query, "id", 0), stringArg(query, "name", ""), intArg(query, "userId", 0), intListArg(query, "musicIds"));
            return data("updatePlaylist", playlistJson(playlist, selection(query, "updatePlaylist")));
        }
        if (query.contains("deletePlaylist")) {
            store.deletePlaylist(intArg(query, "id", 0));
            return data("deletePlaylist", "true");
        }
        if (query.contains("playlistsByUser")) return data("playlistsByUser", playlistListJson(store.playlistsByUser(intArg(query, "userId", 0)), selection(query, "playlistsByUser")));
        if (query.contains("musicsByPlaylist")) return data("musicsByPlaylist", musicListJson(store.musicsByPlaylist(intArg(query, "playlistId", 0)), selection(query, "musicsByPlaylist")));
        if (query.contains("playlistsByMusic")) return data("playlistsByMusic", playlistListJson(store.playlistsByMusic(intArg(query, "musicId", 0)), selection(query, "playlistsByMusic")));
        if (query.contains("user(")) return data("user", userJson(store.getUser(intArg(query, "id", 0)), selection(query, "user")));
        if (query.contains("music(")) return data("music", musicJson(store.getMusic(intArg(query, "id", 0)), selection(query, "music")));
        if (query.contains("playlist(")) return data("playlist", playlistJson(store.getPlaylist(intArg(query, "id", 0)), selection(query, "playlist")));
        if (query.contains("users")) return data("users", userListJson(store.listUsers(), selection(query, "users")));
        if (query.contains("musics")) return data("musics", musicListJson(store.listMusics(), selection(query, "musics")));
        if (query.contains("playlists")) return data("playlists", playlistListJson(store.listPlaylists(), selection(query, "playlists")));
        return "{\"errors\":[{\"message\":\"operacao GraphQL nao reconhecida\"}]}";
    }

    private static String data(String field, String value) {
        return "{\"data\":{\"" + field + "\":" + value + "}}";
    }

    private static String queryFromBody(String body) {
        Matcher matcher = Pattern.compile("\"query\"\\s*:\\s*\"((?:\\\\.|[^\"])*)\"", Pattern.DOTALL).matcher(body);
        if (!matcher.find()) return body;
        return matcher.group(1)
                .replace("\\\"", "\"")
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\r", "\r")
                .replace("\\t", "\t");
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

    private static String selection(String query, String field) {
        int start = query.indexOf(field);
        if (start < 0) return "";
        int cursor = start + field.length();
        cursor = skipWhitespace(query, cursor);
        if (cursor < query.length() && query.charAt(cursor) == '(') {
            cursor = matching(query, cursor, '(', ')') + 1;
        }
        cursor = skipWhitespace(query, cursor);
        if (cursor >= query.length() || query.charAt(cursor) != '{') return "";
        int end = matching(query, cursor, '{', '}');
        if (end < 0) return "";
        return query.substring(cursor + 1, end);
    }

    private static int skipWhitespace(String text, int index) {
        while (index < text.length() && Character.isWhitespace(text.charAt(index))) index++;
        return index;
    }

    private static int matching(String text, int openIndex, char open, char close) {
        int depth = 0;
        for (int index = openIndex; index < text.length(); index++) {
            char current = text.charAt(index);
            if (current == open) depth++;
            if (current == close) {
                depth--;
                if (depth == 0) return index;
            }
        }
        return -1;
    }

    private static boolean wants(String selection, String field) {
        if (selection == null || selection.isBlank()) return true;
        return Pattern.compile("\\b" + Pattern.quote(field) + "\\b").matcher(selection).find();
    }

    private static String userJson(User user, String selection) {
        StringBuilder json = new StringBuilder("{");
        appendField(json, "id", String.valueOf(user.id()), wants(selection, "id"));
        appendField(json, "name", JsonUtil.quote(user.name()), wants(selection, "name"));
        appendField(json, "age", String.valueOf(user.age()), wants(selection, "age"));
        return json.append("}").toString();
    }

    private static String musicJson(Music music, String selection) {
        StringBuilder json = new StringBuilder("{");
        appendField(json, "id", String.valueOf(music.id()), wants(selection, "id"));
        appendField(json, "name", JsonUtil.quote(music.name()), wants(selection, "name"));
        appendField(json, "artist", JsonUtil.quote(music.artist()), wants(selection, "artist"));
        return json.append("}").toString();
    }

    private static String playlistJson(Playlist playlist, String selection) {
        StringBuilder json = new StringBuilder("{");
        appendField(json, "id", String.valueOf(playlist.id()), wants(selection, "id"));
        appendField(json, "name", JsonUtil.quote(playlist.name()), wants(selection, "name"));
        appendField(json, "userId", String.valueOf(playlist.userId()), wants(selection, "userId"));
        appendField(json, "musicIds", "[" + playlist.musicIds().stream().map(String::valueOf).reduce((a, b) -> a + "," + b).orElse("") + "]", wants(selection, "musicIds"));
        return json.append("}").toString();
    }

    private static void appendField(StringBuilder json, String name, String value, boolean include) {
        if (!include) return;
        if (json.length() > 1) json.append(",");
        json.append(JsonUtil.quote(name)).append(":").append(value);
    }

    private static String userListJson(List<User> users, String selection) {
        return users.stream().map(user -> userJson(user, selection)).reduce((a, b) -> a + "," + b).map(value -> "[" + value + "]").orElse("[]");
    }

    private static String musicListJson(List<Music> musics, String selection) {
        return musics.stream().map(music -> musicJson(music, selection)).reduce((a, b) -> a + "," + b).map(value -> "[" + value + "]").orElse("[]");
    }

    private static String playlistListJson(List<Playlist> playlists, String selection) {
        return playlists.stream().map(playlist -> playlistJson(playlist, selection)).reduce((a, b) -> a + "," + b).map(value -> "[" + value + "]").orElse("[]");
    }
}
