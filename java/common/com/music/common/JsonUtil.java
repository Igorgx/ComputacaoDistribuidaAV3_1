package com.music.common;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class JsonUtil {
    private JsonUtil() {}

    public static String quote(String text) {
        return "\"" + text.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }

    public static String user(User user) {
        return "{\"id\":" + user.id() + ",\"name\":" + quote(user.name()) + ",\"age\":" + user.age() + "}";
    }

    public static String music(Music music) {
        return "{\"id\":" + music.id() + ",\"name\":" + quote(music.name()) + ",\"artist\":" + quote(music.artist()) + "}";
    }

    public static String playlist(Playlist playlist) {
        String ids = playlist.musicIds().stream().map(String::valueOf).collect(Collectors.joining(","));
        return "{\"id\":" + playlist.id() + ",\"name\":" + quote(playlist.name()) + ",\"userId\":" + playlist.userId() + ",\"musicIds\":[" + ids + "]}";
    }

    public static String users(List<User> users) {
        return users.stream().map(JsonUtil::user).collect(Collectors.joining(",", "[", "]"));
    }

    public static String musics(List<Music> musics) {
        return musics.stream().map(JsonUtil::music).collect(Collectors.joining(",", "[", "]"));
    }

    public static String playlists(List<Playlist> playlists) {
        return playlists.stream().map(JsonUtil::playlist).collect(Collectors.joining(",", "[", "]"));
    }

    public static String status(String technology) {
        return "{\"status\":\"ok\",\"technology\":" + quote(technology) + ",\"language\":\"Java\"}";
    }

    public static String error(String message) {
        return "{\"error\":" + quote(message) + "}";
    }

    public static String stringField(String json, String field, String fallback) {
        Matcher matcher = Pattern.compile("\"" + field + "\"\\s*:\\s*\"([^\"]*)\"").matcher(json);
        return matcher.find() ? matcher.group(1) : fallback;
    }

    public static Integer intField(String json, String field, Integer fallback) {
        Matcher matcher = Pattern.compile("\"" + field + "\"\\s*:\\s*(-?\\d+)").matcher(json);
        return matcher.find() ? Integer.parseInt(matcher.group(1)) : fallback;
    }

    public static List<Integer> intListField(String json, String field) {
        Matcher matcher = Pattern.compile("\"" + field + "\"\\s*:\\s*\\[([^]]*)\\]").matcher(json);
        List<Integer> values = new ArrayList<>();
        if (!matcher.find()) return values;
        for (String raw : matcher.group(1).split(",")) {
            String item = raw.trim();
            if (!item.isEmpty()) values.add(Integer.parseInt(item));
        }
        return values;
    }

    public static String xmlEscape(String text) {
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }
}
