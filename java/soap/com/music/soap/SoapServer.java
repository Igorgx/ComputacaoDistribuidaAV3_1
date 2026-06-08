package com.music.soap;

import com.music.common.HttpUtil;
import com.music.common.MusicStore;
import com.sun.net.httpserver.HttpServer;

import java.net.InetSocketAddress;
import java.util.Arrays;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SoapServer {
    private static final MusicStore store = new MusicStore();

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8104), 0);
        server.createContext("/", exchange -> {
            try {
                String query = exchange.getRequestURI().getQuery();
                if ("wsdl".equalsIgnoreCase(query)) {
                    HttpUtil.send(exchange, 200, "text/xml", wsdl());
                    return;
                }
                String body = HttpUtil.readBody(exchange);
                HttpUtil.send(exchange, 200, "text/xml", envelope(execute(body)));
            } catch (Exception exc) {
                HttpUtil.send(exchange, 500, "text/xml", envelope(errorXml(exc.getMessage())));
            }
        });
        server.start();
        System.out.println("Java SOAP on http://127.0.0.1:8104/?wsdl");
    }

    private static String execute(String xml) {
        try {
            if (xml.contains("health")) return statusXml();
            if (xml.contains("listUsers")) return usersXml(store.listUsers());
            if (xml.contains("getUser")) return userXml(store.getUser(intTag(xml, "userId", intTag(xml, "id", 0))));
            if (xml.contains("createUser")) return userXml(store.createUser(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "age", 0)));
            if (xml.contains("updateUser")) return userXml(store.updateUser(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "age", 0)));
            if (xml.contains("deleteUser")) {
                store.deleteUser(intTag(xml, "id", 0));
                return deletedXml();
            }
            if (xml.contains("listMusics")) return musicsXml(store.listMusics());
            if (xml.contains("getMusic")) return musicXml(store.getMusic(intTag(xml, "musicId", intTag(xml, "id", 0))));
            if (xml.contains("createMusic")) return musicXml(store.createMusic(intTag(xml, "id", 0), tag(xml, "name", ""), tag(xml, "artist", "")));
            if (xml.contains("updateMusic")) return musicXml(store.updateMusic(intTag(xml, "id", 0), tag(xml, "name", ""), tag(xml, "artist", "")));
            if (xml.contains("deleteMusic")) {
                store.deleteMusic(intTag(xml, "id", 0));
                return deletedXml();
            }
            if (xml.contains("listPlaylistsByUser")) return playlistsXml(store.playlistsByUser(intTag(xml, "userId", 0)));
            if (xml.contains("listMusicsByPlaylist")) return musicsXml(store.musicsByPlaylist(intTag(xml, "playlistId", 0)));
            if (xml.contains("listPlaylistsByMusic")) return playlistsXml(store.playlistsByMusic(intTag(xml, "musicId", 0)));
            if (xml.contains("listPlaylists")) return playlistsXml(store.listPlaylists());
            if (xml.contains("getPlaylist")) return playlistXml(store.getPlaylist(intTag(xml, "playlistId", intTag(xml, "id", 0))));
            if (xml.contains("createPlaylist")) return playlistXml(store.createPlaylist(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "userId", 0), csv(tag(xml, "musicIdsCsv", ""))));
            if (xml.contains("updatePlaylist")) return playlistXml(store.updatePlaylist(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "userId", 0), csv(tag(xml, "musicIdsCsv", ""))));
            if (xml.contains("deletePlaylist")) {
                store.deletePlaylist(intTag(xml, "id", 0));
                return deletedXml();
            }
            return errorXml("operacao SOAP nao reconhecida");
        } catch (Exception exc) {
            return errorXml(exc.getMessage());
        }
    }

    private static String envelope(String xml) {
        return """
                <?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <result>%s</result>
                  </soap:Body>
                </soap:Envelope>
                """.formatted(xml);
    }

    private static String wsdl() {
        return """
                <?xml version="1.0" encoding="UTF-8"?>
                <definitions name="MusicStreamingSoap" targetNamespace="music.streaming.soap">
                  <documentation>Servico SOAP didatico. Todas as operacoes recebem e retornam XML.</documentation>
                  <operation name="listUsers"/>
                  <operation name="listMusics"/>
                  <operation name="listPlaylists"/>
                  <operation name="listPlaylistsByUser"/>
                  <operation name="listMusicsByPlaylist"/>
                  <operation name="listPlaylistsByMusic"/>
                </definitions>
                """;
    }

    private static String elem(String name, Object value) {
        return "<" + name + ">" + xmlEscape(String.valueOf(value)) + "</" + name + ">";
    }

    private static String xmlEscape(String value) {
        return value
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;")
                .replace("'", "&apos;");
    }

    private static String statusXml() {
        return "<health>" + elem("status", "ok") + elem("technology", "SOAP") + elem("language", "Java") + "</health>";
    }

    private static String userXml(com.music.common.User user) {
        return "<user>" + elem("id", user.id()) + elem("name", user.name()) + elem("age", user.age()) + "</user>";
    }

    private static String usersXml(List<com.music.common.User> users) {
        StringBuilder xml = new StringBuilder("<users>");
        for (com.music.common.User user : users) {
            xml.append(userXml(user));
        }
        return xml.append("</users>").toString();
    }

    private static String musicXml(com.music.common.Music music) {
        return "<music>" + elem("id", music.id()) + elem("name", music.name()) + elem("artist", music.artist()) + "</music>";
    }

    private static String musicsXml(List<com.music.common.Music> musics) {
        StringBuilder xml = new StringBuilder("<musics>");
        for (com.music.common.Music music : musics) {
            xml.append(musicXml(music));
        }
        return xml.append("</musics>").toString();
    }

    private static String playlistXml(com.music.common.Playlist playlist) {
        StringBuilder xml = new StringBuilder("<playlist>");
        xml.append(elem("id", playlist.id()));
        xml.append(elem("name", playlist.name()));
        xml.append(elem("userId", playlist.userId()));
        xml.append("<musicIds>");
        for (Integer musicId : playlist.musicIds()) {
            xml.append(elem("musicId", musicId));
        }
        xml.append("</musicIds>");
        return xml.append("</playlist>").toString();
    }

    private static String playlistsXml(List<com.music.common.Playlist> playlists) {
        StringBuilder xml = new StringBuilder("<playlists>");
        for (com.music.common.Playlist playlist : playlists) {
            xml.append(playlistXml(playlist));
        }
        return xml.append("</playlists>").toString();
    }

    private static String deletedXml() {
        return "<deleteResult>" + elem("deleted", "true") + "</deleteResult>";
    }

    private static String errorXml(String message) {
        return "<error>" + elem("message", message) + "</error>";
    }

    private static String tag(String xml, String name, String fallback) {
        Matcher matcher = Pattern.compile("<[^:>]*:?" + name + ">(.*?)</[^:>]*:?" + name + ">", Pattern.DOTALL).matcher(xml);
        return matcher.find() ? matcher.group(1).trim() : fallback;
    }

    private static int intTag(String xml, String name, int fallback) {
        String value = tag(xml, name, "");
        return value.isBlank() ? fallback : Integer.parseInt(value);
    }

    private static List<Integer> csv(String raw) {
        if (raw == null || raw.isBlank()) return List.of();
        return Arrays.stream(raw.split(",")).map(String::trim).filter(item -> !item.isBlank()).map(Integer::parseInt).toList();
    }
}
