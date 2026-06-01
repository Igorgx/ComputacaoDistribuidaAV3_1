package com.music.soap;

import com.music.common.HttpUtil;
import com.music.common.JsonUtil;
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
                HttpUtil.send(exchange, 500, "text/xml", envelope(JsonUtil.error(exc.getMessage())));
            }
        });
        server.start();
        System.out.println("Java SOAP on http://127.0.0.1:8104/?wsdl");
    }

    private static String execute(String xml) {
        try {
            if (xml.contains("health")) return JsonUtil.status("SOAP");
            if (xml.contains("listUsers")) return JsonUtil.users(store.listUsers());
            if (xml.contains("getUser")) return JsonUtil.user(store.getUser(intTag(xml, "userId", intTag(xml, "id", 0))));
            if (xml.contains("createUser")) return JsonUtil.user(store.createUser(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "age", 0)));
            if (xml.contains("updateUser")) return JsonUtil.user(store.updateUser(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "age", 0)));
            if (xml.contains("deleteUser")) {
                store.deleteUser(intTag(xml, "id", 0));
                return "{\"deleted\":true}";
            }
            if (xml.contains("listMusics")) return JsonUtil.musics(store.listMusics());
            if (xml.contains("getMusic")) return JsonUtil.music(store.getMusic(intTag(xml, "musicId", intTag(xml, "id", 0))));
            if (xml.contains("createMusic")) return JsonUtil.music(store.createMusic(intTag(xml, "id", 0), tag(xml, "name", ""), tag(xml, "artist", "")));
            if (xml.contains("updateMusic")) return JsonUtil.music(store.updateMusic(intTag(xml, "id", 0), tag(xml, "name", ""), tag(xml, "artist", "")));
            if (xml.contains("deleteMusic")) {
                store.deleteMusic(intTag(xml, "id", 0));
                return "{\"deleted\":true}";
            }
            if (xml.contains("listPlaylistsByUser")) return JsonUtil.playlists(store.playlistsByUser(intTag(xml, "userId", 0)));
            if (xml.contains("listMusicsByPlaylist")) return JsonUtil.musics(store.musicsByPlaylist(intTag(xml, "playlistId", 0)));
            if (xml.contains("listPlaylistsByMusic")) return JsonUtil.playlists(store.playlistsByMusic(intTag(xml, "musicId", 0)));
            if (xml.contains("listPlaylists")) return JsonUtil.playlists(store.listPlaylists());
            if (xml.contains("getPlaylist")) return JsonUtil.playlist(store.getPlaylist(intTag(xml, "playlistId", intTag(xml, "id", 0))));
            if (xml.contains("createPlaylist")) return JsonUtil.playlist(store.createPlaylist(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "userId", 0), csv(tag(xml, "musicIdsCsv", ""))));
            if (xml.contains("updatePlaylist")) return JsonUtil.playlist(store.updatePlaylist(intTag(xml, "id", 0), tag(xml, "name", ""), intTag(xml, "userId", 0), csv(tag(xml, "musicIdsCsv", ""))));
            if (xml.contains("deletePlaylist")) {
                store.deletePlaylist(intTag(xml, "id", 0));
                return "{\"deleted\":true}";
            }
            return JsonUtil.error("operacao SOAP nao reconhecida");
        } catch (Exception exc) {
            return JsonUtil.error(exc.getMessage());
        }
    }

    private static String envelope(String json) {
        return """
                <?xml version="1.0" encoding="UTF-8"?>
                <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                  <soap:Body>
                    <result>%s</result>
                  </soap:Body>
                </soap:Envelope>
                """.formatted(JsonUtil.xmlEscape(json));
    }

    private static String wsdl() {
        return """
                <?xml version="1.0" encoding="UTF-8"?>
                <definitions name="MusicStreamingSoap" targetNamespace="music.streaming.soap">
                  <documentation>Servico SOAP didatico. Todas as operacoes retornam JSON no elemento result.</documentation>
                  <operation name="listUsers"/>
                  <operation name="listMusics"/>
                  <operation name="listPlaylists"/>
                  <operation name="listPlaylistsByUser"/>
                  <operation name="listMusicsByPlaylist"/>
                  <operation name="listPlaylistsByMusic"/>
                </definitions>
                """;
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
