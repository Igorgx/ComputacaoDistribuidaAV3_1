# Servico de Streaming de Musicas

## Identificacao da Equipe

- Integrante 1: preencher
- Integrante 2: preencher
- Integrante 3: preencher

## Objetivo

Este trabalho compara REST, gRPC, GraphQL e SOAP por meio da implementacao de um mesmo servico fake de streaming de musicas em Python e Java. O servico nao transmite arquivos MP3; ele expoe operacoes de catalogo e relacionamento entre usuarios, musicas e playlists.

Todas as implementacoes usam persistencia em memoria, mesma massa inicial e mesmas operacoes: CRUD de usuarios, musicas e playlists, listagem de musicas por playlist, playlists por usuario e playlists que contem uma musica.

## Tecnologias

REST e um estilo arquitetural baseado em recursos, normalmente expostos por HTTP e JSON. E simples de testar, facil de consumir por navegadores, Postman e scripts, mas pode exigir varias chamadas para montar dados relacionados.

gRPC usa contratos Protobuf e HTTP/2. Tende a ser eficiente, fortemente tipado e bom para comunicacao servico a servico, mas e menos conveniente para uso direto em navegadores e exige geracao de codigo.

GraphQL expoe um endpoint com schema de queries e mutations. A vantagem principal e permitir que o cliente escolha exatamente os campos desejados, reduzindo overfetching. A desvantagem e maior complexidade no servidor e cuidado extra com queries caras.

SOAP usa XML e contrato WSDL. E verboso, mas historicamente forte em ambientes corporativos por padronizar contrato, envelope, tipos e integracoes com ferramentas enterprise.

## Implementacao

Foram criadas 8 implementacoes:

| Linguagem | Tecnologia | Porta | Observacao |
|---|---|---:|---|
| Python | REST/FastAPI | 8001 | HTTP JSON |
| Python | gRPC/grpcio | 8002 | Protobuf |
| Python | GraphQL/Strawberry | 8003 | Query/mutation |
| Python | SOAP/Spyne | 8004 | XML SOAP |
| Java | REST/JDK HttpServer | 8101 | HTTP JSON |
| Java | gRPC/grpc-java | 8102 | Protobuf via Maven |
| Java | GraphQL/JDK HttpServer | 8103 | Endpoint GraphQL didatico |
| Java | SOAP/JDK HttpServer | 8104 | XML SOAP didatico |

Exemplo REST em Python:

```python
@app.get("/playlists/{playlist_id}/musics")
def musics_by_playlist(playlist_id: int):
    return store.to_dicts(store.musics_by_playlist(playlist_id))
```

Exemplo gRPC no arquivo `.proto`:

```proto
rpc ListMusicsByPlaylist(IdRequest) returns (MusicList);
rpc ListPlaylistsByMusic(IdRequest) returns (PlaylistList);
```

Exemplo Java REST:

```java
if (parts.length == 3 && parts[0].equals("playlists") && parts[2].equals("musics")) {
    HttpUtil.send(exchange, 200, "application/json",
        JsonUtil.musics(store.musicsByPlaylist(id)));
}
```

## Testes de Carga

Ferramenta: Locust.

Cenario moderado sugerido:

- 100 usuarios virtuais.
- Spawn rate 20 usuarios/s.
- Duracao 2 minutos.

Cenario alto sugerido:

- 400 usuarios virtuais.
- Spawn rate 80 usuarios/s.
- Duracao 2 minutos.

Fluxos simulados:

- Listar musicas.
- Consultar usuario.
- Criar playlist.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

Comandos exemplo:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol rest -Out python_rest_moderada
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol rest -Out python_rest_alta
```

Para gRPC:

```powershell
./scripts/run-load.ps1 -Class MusicGrpcUser -HostUrl 127.0.0.1:8002 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol grpc -Out python_grpc_moderada
```

Depois dos testes:

```powershell
./.venv/Scripts/python.exe ./report/generate_charts.py
```

Os graficos gerados ficam em `report/results`.

## Analise Esperada

REST deve ser o mais simples de demonstrar e debugar, com boa compatibilidade geral.

gRPC deve ter boa eficiencia em chamadas repetidas, principalmente por usar Protobuf e contrato binario, mas exige mais setup.

GraphQL deve ser flexivel nas consultas relacionais, porque o cliente pede o formato desejado, mas o processamento da query adiciona custo.

SOAP deve ser o mais verboso e tende a ter maior overhead por XML, mas e o mais formal em contrato e envelope.

## Conclusao

As quatro tecnologias resolvem o mesmo problema funcional, mas com tradeoffs diferentes. Para APIs publicas simples, REST e direto. Para comunicacao interna de alto desempenho, gRPC e forte. Para clientes que precisam consultar relacoes variadas, GraphQL oferece flexibilidade. Para cenarios corporativos legados ou contratos XML formais, SOAP continua relevante.
