package com.music.common;

import java.util.List;

public record Playlist(int id, String name, int userId, List<Integer> musicIds) {}
