# Modelo Compartilhado

Todas as implementacoes usam o mesmo dominio e a mesma massa inicial em memoria.

## Entidades

- User: `id`, `name`, `age`
- Music: `id`, `name`, `artist`
- Playlist: `id`, `name`, `userId`, `musicIds`

## Massa inicial

- 250 usuarios
- 500 musicas
- 400 playlists
- Cada playlist pertence a um usuario e contem 5 musicas.

## Consultas obrigatorias

- Listar todos os usuarios.
- Listar todas as musicas.
- Listar playlists de um usuario.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.
