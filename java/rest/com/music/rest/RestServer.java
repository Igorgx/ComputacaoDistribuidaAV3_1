package com.music.rest;

import com.music.common.HttpUtil;
import com.music.common.JsonUtil;
import com.music.common.MusicStore;
import com.music.common.NotFoundException;
import com.music.common.ValidationException;
import com.sun.net.httpserver.HttpServer;

import java.net.InetSocketAddress;
import java.util.List;

public class RestServer {
    private static final MusicStore store = new MusicStore();

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 8101), 0);
        server.createContext("/", exchange -> {
            try {
                route(exchange);
            } catch (NotFoundException exc) {
                HttpUtil.send(exchange, 404, "application/json", JsonUtil.error(exc.getMessage()));
            } catch (ValidationException | IllegalArgumentException exc) {
                HttpUtil.send(exchange, 400, "application/json", JsonUtil.error(exc.getMessage()));
            } catch (Exception exc) {
                HttpUtil.send(exchange, 500, "application/json", JsonUtil.error(exc.getMessage()));
            }
        });
        server.start();
        System.out.println("Java REST on http://127.0.0.1:8101");
    }

    private static void route(com.sun.net.httpserver.HttpExchange exchange) throws Exception {
        String method = exchange.getRequestMethod();
        String path = exchange.getRequestURI().getPath();
        String[] parts = path.substring(1).split("/");
        if (path.equals("/health")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.status("REST"));
            return;
        }
        if (path.equals("/users") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.users(store.listUsers()));
            return;
        }
        if (path.equals("/users") && method.equals("POST")) {
            String body = HttpUtil.readBody(exchange);
            var user = store.createUser(JsonUtil.intField(body, "id", null), JsonUtil.stringField(body, "name", ""), JsonUtil.intField(body, "age", 0));
            HttpUtil.send(exchange, 201, "application/json", JsonUtil.user(user));
            return;
        }
        if (parts.length == 2 && parts[0].equals("users")) {
            int id = HttpUtil.idAt(parts, 1);
            if (method.equals("GET")) HttpUtil.send(exchange, 200, "application/json", JsonUtil.user(store.getUser(id)));
            else if (method.equals("PUT")) {
                String body = HttpUtil.readBody(exchange);
                HttpUtil.send(exchange, 200, "application/json", JsonUtil.user(store.updateUser(id, JsonUtil.stringField(body, "name", ""), JsonUtil.intField(body, "age", 0))));
            } else if (method.equals("DELETE")) {
                store.deleteUser(id);
                HttpUtil.sendNoContent(exchange);
            }
            return;
        }
        if (parts.length == 3 && parts[0].equals("users") && parts[2].equals("playlists") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.playlists(store.playlistsByUser(HttpUtil.idAt(parts, 1))));
            return;
        }
        if (path.equals("/musics") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.musics(store.listMusics()));
            return;
        }
        if (path.equals("/musics") && method.equals("POST")) {
            String body = HttpUtil.readBody(exchange);
            var music = store.createMusic(JsonUtil.intField(body, "id", null), JsonUtil.stringField(body, "name", ""), JsonUtil.stringField(body, "artist", ""));
            HttpUtil.send(exchange, 201, "application/json", JsonUtil.music(music));
            return;
        }
        if (parts.length == 2 && parts[0].equals("musics")) {
            int id = HttpUtil.idAt(parts, 1);
            if (method.equals("GET")) HttpUtil.send(exchange, 200, "application/json", JsonUtil.music(store.getMusic(id)));
            else if (method.equals("PUT")) {
                String body = HttpUtil.readBody(exchange);
                HttpUtil.send(exchange, 200, "application/json", JsonUtil.music(store.updateMusic(id, JsonUtil.stringField(body, "name", ""), JsonUtil.stringField(body, "artist", ""))));
            } else if (method.equals("DELETE")) {
                store.deleteMusic(id);
                HttpUtil.sendNoContent(exchange);
            }
            return;
        }
        if (parts.length == 3 && parts[0].equals("musics") && parts[2].equals("playlists") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.playlists(store.playlistsByMusic(HttpUtil.idAt(parts, 1))));
            return;
        }
        if (path.equals("/playlists") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.playlists(store.listPlaylists()));
            return;
        }
        if (path.equals("/playlists") && method.equals("POST")) {
            String body = HttpUtil.readBody(exchange);
            var playlist = store.createPlaylist(JsonUtil.intField(body, "id", null), JsonUtil.stringField(body, "name", ""), JsonUtil.intField(body, "userId", 0), JsonUtil.intListField(body, "musicIds"));
            HttpUtil.send(exchange, 201, "application/json", JsonUtil.playlist(playlist));
            return;
        }
        if (parts.length == 2 && parts[0].equals("playlists")) {
            int id = HttpUtil.idAt(parts, 1);
            if (method.equals("GET")) HttpUtil.send(exchange, 200, "application/json", JsonUtil.playlist(store.getPlaylist(id)));
            else if (method.equals("PUT")) {
                String body = HttpUtil.readBody(exchange);
                HttpUtil.send(exchange, 200, "application/json", JsonUtil.playlist(store.updatePlaylist(id, JsonUtil.stringField(body, "name", ""), JsonUtil.intField(body, "userId", 0), JsonUtil.intListField(body, "musicIds"))));
            } else if (method.equals("DELETE")) {
                store.deletePlaylist(id);
                HttpUtil.sendNoContent(exchange);
            }
            return;
        }
        if (parts.length == 3 && parts[0].equals("playlists") && parts[2].equals("musics") && method.equals("GET")) {
            HttpUtil.send(exchange, 200, "application/json", JsonUtil.musics(store.musicsByPlaylist(HttpUtil.idAt(parts, 1))));
            return;
        }
        HttpUtil.send(exchange, 404, "application/json", JsonUtil.error("rota nao encontrada"));
    }
}
