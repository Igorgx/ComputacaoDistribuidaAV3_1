# Resumo para Apresentacao - Servico Fake de Streaming de Musicas

## 1. Ideia geral do trabalho

O trabalho compara quatro tecnologias de invocacao remota usando o mesmo servico em duas linguagens.

Tecnologias:

- REST
- gRPC
- GraphQL
- SOAP

Linguagens:

- Python
- Java

Total:

- 4 tecnologias x 2 linguagens = 8 implementacoes.

O sistema simula um servico de streaming de musicas, mas nao transmite audio ou MP3. Ele trabalha apenas com metadados de:

- usuarios
- musicas
- playlists

O objetivo e mostrar que o mesmo dominio pode ser implementado com diferentes modelos de comunicacao remota e comparar comportamento, facilidade de uso, formato de resposta, desempenho e custo sob carga.

## 2. Modelo de dados

Todos os servicos usam o mesmo modelo logico:

| Recurso | Campos |
|---|---|
| User | `id`, `name`, `age` |
| Music | `id`, `name`, `artist` |
| Playlist | `id`, `name`, `userId`, `musicIds` |

Relacionamentos:

- Uma playlist pertence a um usuario por `userId`.
- Uma playlist contem varias musicas por `musicIds`.
- Uma musica pode aparecer em varias playlists.

Massa inicial:

| Recurso | Quantidade |
|---|---:|
| Usuarios | 250 |
| Musicas | 500 |
| Playlists | 400 |

A persistencia e em memoria. Isso foi escolhido porque o professor permitiu nao usar banco de dados e porque o foco do trabalho e comparar a invocacao remota, nao o banco.

## 3. Funcionalidades implementadas

Todas as 8 implementacoes possuem:

- CRUD de usuarios.
- CRUD de musicas.
- CRUD de playlists.
- Listar todos os usuarios.
- Listar todas as musicas.
- Listar playlists de um usuario.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

Validacoes principais:

- Recurso inexistente retorna erro.
- Playlist so pode referenciar usuario existente.
- Playlist so pode referenciar musicas existentes.
- IDs repetidos nao sao aceitos quando enviados manualmente.

## 4. Implementacoes e portas

| Linguagem | Tecnologia | Porta | Formato principal |
|---|---:|---:|---|
| Python | REST | 8001 | HTTP + JSON |
| Python | gRPC | 8002 | HTTP/2 + Protobuf |
| Python | GraphQL | 8003 | HTTP + JSON GraphQL |
| Python | SOAP | 8004 | HTTP + XML SOAP |
| Java | REST | 8101 | HTTP + JSON |
| Java | gRPC | 8102 | HTTP/2 + Protobuf |
| Java | GraphQL | 8103 | HTTP + JSON GraphQL |
| Java | SOAP | 8104 | HTTP + XML SOAP |

## 5. Bibliotecas e ferramentas usadas

### Python

Bibliotecas principais em `python/requirements.txt`:

| Biblioteca | Uso |
|---|---|
| `fastapi` | Implementacao REST em Python |
| `uvicorn` | Servidor ASGI para REST e GraphQL |
| `pydantic` | Validacao dos corpos JSON no REST |
| `grpcio` | Servidor e cliente gRPC em Python |
| `grpcio-tools` | Geracao de codigo gRPC a partir do `.proto` |
| `strawberry-graphql[fastapi]` | GraphQL em Python integrado ao FastAPI |
| `spyne` | SOAP em Python |
| `lxml` | Manipulacao/retorno XML no SOAP |
| `locust` | Testes de carga para REST, GraphQL e SOAP |

### Java

| Tecnologia | Implementacao |
|---|---|
| REST | `HttpServer` da JDK |
| GraphQL | Implementacao didatica sobre `HttpServer` da JDK |
| SOAP | Implementacao didatica sobre `HttpServer` da JDK, retornando XML |
| gRPC | `grpc-java` com Maven |

Dependencias principais do Java gRPC:

- `grpc-netty-shaded`
- `grpc-protobuf`
- `grpc-stub`
- `protobuf-java`
- `protobuf-maven-plugin`

O Maven e configurado localmente pelo script do projeto, sem exigir Maven instalado globalmente.

## 6. O que cada sistema retorna

### REST

REST usa rotas HTTP e JSON.

Exemplo:

- `GET /users`
- `POST /users`
- `PUT /users/{id}`
- `DELETE /users/{id}`

Retorno:

```json
{
  "id": 1,
  "name": "Usuario 1",
  "age": 19
}
```

REST e o mais simples para demonstrar CRUD, porque cada acao aparece diretamente no metodo HTTP.

### GraphQL

GraphQL usa uma rota principal:

- `/graphql`

O cliente envia uma query ou mutation no corpo da requisicao.

Exemplo:

```graphql
{
  musics {
    id
    name
    artist
  }
}
```

Retorno:

```json
{
  "data": {
    "musics": [
      {
        "id": 1,
        "name": "Musica 1",
        "artist": "Banda Delta"
      }
    ]
  }
}
```

GraphQL e bom para consultas flexiveis, porque o cliente escolhe os campos retornados.

### SOAP

SOAP usa XML com envelope SOAP.

Exemplo de requisicao:

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <listMusics xmlns="music.streaming.soap"/>
  </soap:Body>
</soap:Envelope>
```

Retorno esperado:

```xml
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <musics>
      <music>
        <id>1</id>
        <name>Musica 1</name>
        <artist>Banda Delta</artist>
      </music>
    </musics>
  </soap:Body>
</soap:Envelope>
```

Importante: o SOAP final usa XML puro, nao JSON dentro do XML.

### gRPC

gRPC usa contrato `.proto` e Protobuf.

O retorno nao e JSON nem XML. Ele e binario e e interpretado pelo cliente gRPC.

Conceito:

```proto
service MusicService {
  rpc ListMusics (Empty) returns (MusicList);
}
```

gRPC foi o melhor em desempenho porque usa comunicacao binaria, contrato tipado e menor custo de serializacao.

## 7. Como demonstrar para o professor

### Demonstracao recomendada

1. Subir um servico em um terminal.
2. Abrir Postman.
3. Importar as colecoes da pasta `postman`.
4. Rodar uma chamada de listagem.
5. Rodar uma criacao.
6. Rodar uma atualizacao.
7. Rodar uma exclusao.
8. Mostrar uma consulta relacional.

Colecoes Postman:

- `postman/StreamingMusic-REST.postman_collection.json`
- `postman/StreamingMusic-GraphQL.postman_collection.json`
- `postman/StreamingMusic-SOAP.postman_collection.json`

Para SOAP, usar o Postman e mostrar a resposta em `Body > Pretty`, onde o XML fica formatado.

### Scripts demo

Os scripts `demo` servem para mostrar rapidamente que o servico responde sem precisar montar a requisicao manualmente.

Exemplos:

```powershell
.\scripts\demo-rest.ps1 -BaseUrl http://127.0.0.1:8001
.\scripts\demo-graphql.ps1 -BaseUrl http://127.0.0.1:8003/graphql
.\scripts\demo-soap.ps1 -BaseUrl http://127.0.0.1:8004
```

Eles nao sao testes de carga. Sao scripts de demonstracao/smoke test.

## 8. Testes de carga

Foram usadas duas cargas:

| Carga | Usuarios virtuais | Spawn rate | Duracao |
|---|---:|---:|---:|
| Moderada | 100 | 20 usuarios/s | 2 minutos |
| Alta | 400 | 80 usuarios/s | 2 minutos |

Ferramentas:

- REST, GraphQL e SOAP: Locust.
- gRPC: gerador proprio com threads, porque o cliente gRPC com Locust/gevent apresentou problemas de finalizacao de canais.

Fluxos simulados:

- Listar musicas.
- Buscar usuario.
- Criar playlist.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

Metricas coletadas:

- Total de requisicoes.
- Requisicoes por segundo.
- Tempo medio de resposta.
- Percentil 95.
- Falhas absolutas.
- Taxa de falha.

## 9. Resultados consolidados

| Implementacao | Requisicoes | Req/s | Tempo medio | P95 | Falhas | Taxa de falha |
|---|---:|---:|---:|---:|---:|---:|
| Python REST moderada | 24226 | 202.62 | 34.18 ms | 85 ms | 0 | 0.00% |
| Python REST alta | 25486 | 214.66 | 1373.36 ms | 1600 ms | 8 | 0.03% |
| Python gRPC moderada | 25279 | 209.27 | 3.51 ms | 4.94 ms | 0 | 0.00% |
| Python gRPC alta | 89450 | 740.03 | 63.19 ms | 324.37 ms | 0 | 0.00% |
| Python GraphQL moderada | 17903 | 150.96 | 198.42 ms | 340 ms | 0 | 0.00% |
| Python GraphQL alta | 16407 | 137.02 | 2394.58 ms | 2800 ms | 91 | 0.55% |
| Python SOAP moderada | 23312 | 196.51 | 49.19 ms | 520 ms | 0 | 0.00% |
| Python SOAP alta | 39471 | 329.81 | 735.38 ms | 2100 ms | 3638 | 9.22% |
| Java REST moderada | 25723 | 215.14 | 3.33 ms | 6 ms | 0 | 0.00% |
| Java REST alta | 86807 | 730.35 | 71.62 ms | 310 ms | 0 | 0.00% |
| Java gRPC moderada | 25531 | 211.46 | 1.43 ms | 2.24 ms | 0 | 0.00% |
| Java gRPC alta | 100890 | 835.18 | 2.77 ms | 5.55 ms | 0 | 0.00% |
| Java GraphQL moderada | 25497 | 214.91 | 3.16 ms | 5 ms | 0 | 0.00% |
| Java GraphQL alta | 95465 | 800.94 | 34.20 ms | 110 ms | 0 | 0.00% |
| Java SOAP moderada | 25541 | 215.22 | 3.45 ms | 6 ms | 0 | 0.00% |
| Java SOAP alta | 83188 | 695.97 | 95.35 ms | 370 ms | 0 | 0.00% |

## 10. Melhores resultados

| Criterio | Melhor resultado |
|---|---|
| Melhor geral | Java gRPC |
| Maior vazao | Java gRPC alta, 835.18 req/s |
| Menor tempo medio em carga alta | Java gRPC alta, 2.77 ms |
| Menor P95 em carga alta | Java gRPC alta, 5.55 ms |
| Melhor Python | Python gRPC |
| Melhor Java | Java gRPC |
| Melhor para demonstrar CRUD | REST |
| Melhor para provar XML | SOAP |
| Melhor para consulta flexivel | GraphQL |

## 11. Analise por tecnologia

### REST

Pontos fortes:

- Simples de entender e apresentar.
- Usa HTTP e JSON.
- Facil de testar com navegador, Postman, curl ou PowerShell.
- CRUD fica muito claro pelos metodos `GET`, `POST`, `PUT`, `DELETE`.

Resultados:

- Java REST alta: 730.35 req/s, 71.62 ms, 0 falhas.
- Python REST alta: 214.66 req/s, 1373.36 ms, 8 falhas.

Interpretacao:

- REST funcionou bem para demonstracao.
- Java lidou melhor com a carga.
- Python REST sofreu na carga alta por fila de requisicoes e custo de HTTP/JSON.

### gRPC

Pontos fortes:

- Melhor desempenho geral.
- Usa Protobuf binario.
- Usa contrato `.proto`.
- Bom para comunicacao interna entre servicos.

Resultados:

- Java gRPC alta: 835.18 req/s, 2.77 ms, 0 falhas.
- Python gRPC alta: 740.03 req/s, 63.19 ms, 0 falhas.

Interpretacao:

- gRPC foi o vencedor tecnico.
- Java gRPC teve o melhor resultado de todo o trabalho.
- Python gRPC tambem foi o melhor entre as implementacoes Python.

### GraphQL

Pontos fortes:

- Cliente escolhe os campos retornados.
- Bom para consultas flexiveis.
- Uma unica rota concentra queries e mutations.

Resultados:

- Java GraphQL alta: 800.94 req/s, 34.20 ms, 0 falhas.
- Python GraphQL alta: 137.02 req/s, 2394.58 ms, 91 falhas.

Interpretacao:

- GraphQL tem custo de parse da query e resolucao de campos.
- Python GraphQL sofreu bastante na carga alta.
- Java GraphQL ficou forte e estavel depois das correcoes.

Observacao sobre P95 e falhas:

- O P95 alto no grafico de GraphQL vem principalmente do Python GraphQL em carga alta.
- Python GraphQL alta teve 16.407 requisicoes, 137.02 req/s, tempo medio de 2394.58 ms, P95 de 2800 ms e 91 falhas.
- A taxa de falha foi 0.55%, ou seja, baixa em percentual, mas visivel no grafico.
- As falhas registradas foram `ConnectionRefusedError`, nao erro de regra de negocio nem erro de resposta GraphQL.
- Isso indica saturacao do servidor sob carga alta: o processo nao conseguiu aceitar todas as conexoes novas quando havia 400 usuarios virtuais.
- Na carga moderada, Python GraphQL teve 0 falhas. Em Java GraphQL, tanto carga moderada quanto alta tiveram 0 falhas.
- Portanto, a conclusao correta e que o gargalo apareceu na implementacao Python GraphQL sob carga alta, nao que todo GraphQL esteja incorreto.

### SOAP

Pontos fortes:

- Usa XML e envelope SOAP.
- Representa bem integracoes formais/legadas.
- Possui contrato/WSDL.

Resultados:

- Java SOAP alta: 695.97 req/s, 95.35 ms, 0 falhas.
- Python SOAP alta: 329.81 req/s, 735.38 ms, 3638 falhas.

Interpretacao:

- SOAP usa XML puro no projeto.
- O XML aumenta custo de serializacao e parsing.
- Java SOAP nao falhou, mas teve latencia maior que Java gRPC/GraphQL/REST.
- Python SOAP sofreu mais na carga alta, o que reforca o custo do XML sob concorrencia.

## 12. Por que Java foi melhor que Python nos testes?

Os resultados Java foram melhores principalmente por:

- Melhor comportamento sob concorrencia nos servidores implementados.
- Menor aumento de latencia na carga alta.
- Implementacoes Java mantiveram 0 falhas em todos os cenarios finais.
- Java gRPC aproveitou muito bem Protobuf e comunicacao binaria.

Isso nao significa que Python seja ruim. Significa que, neste projeto e nesta maquina, com essa carga local, as implementacoes Python sofreram mais com enfileiramento e custo de processamento.

## 13. Por que Python teve tempos altos na carga alta?

Isso e esperado nos resultados finais.

Motivos:

- A carga alta usou 400 usuarios virtuais.
- Cliente de carga e servidor rodaram na mesma maquina.
- REST, GraphQL e SOAP usam formatos textuais, como JSON, query GraphQL e XML.
- GraphQL precisa interpretar query e resolver campos.
- SOAP precisa montar e interpretar XML.
- Em carga alta, requisicoes comecam a formar fila.

Python gRPC tambem aumentou em relacao ao Java, mas ainda foi o melhor Python e nao teve falhas.

## 14. Perguntas provaveis do professor

### O sistema faz streaming real de musica?

Nao. O enunciado permitiu um servico fake. O sistema simula um servico de streaming por metadados de usuarios, musicas e playlists.

### Tem banco de dados?

Nao. A persistencia e em memoria, como permitido. Todas as implementacoes usam a mesma massa inicial para comparacao justa.

### O CRUD funciona?

Sim. Usuarios, musicas e playlists possuem criar, listar, buscar, atualizar e excluir. O CRUD pode ser demonstrado principalmente por REST no Postman.

### SOAP esta usando XML puro?

Sim. As requisicoes e respostas SOAP usam `text/xml`, envelope SOAP e dados em XML. Nao ha JSON encapsulado na resposta SOAP final.

### Por que Java SOAP nao teve falhas mesmo usando XML?

Porque XML puro gera overhead, mas nao obriga o sistema a falhar. No Java SOAP, o overhead apareceu na latencia: 95.35 ms em carga alta, pior que Java gRPC. Mesmo assim, a implementacao Java suportou a carga sem falhas.

### Por que Python SOAP teve falhas?

Porque, em carga alta, o custo de XML + servidor Python + concorrencia local causou instabilidade. A taxa de falha foi 9.22%.

### Qual foi o melhor sistema?

Java gRPC foi o melhor geral. Teve maior vazao, menor latencia em carga alta e 0 falhas.

### Qual foi o melhor para mostrar ao professor?

REST e o melhor para demonstrar CRUD, porque os metodos HTTP sao diretos. SOAP e o melhor para demonstrar XML. GraphQL e bom para demonstrar consultas flexiveis.

### As diferencas aparecem mais na carga alta?

Sim. Na carga moderada muitos sistemas ficam parecidos. Na carga alta, aparecem diferencas de serializacao, runtime, concorrencia e overhead do protocolo.

## 15. Conclusao pronta para falar

O trabalho implementou o mesmo servico fake de streaming de musicas em 8 versoes, combinando REST, gRPC, GraphQL e SOAP com Python e Java.

Todas as versoes usam os mesmos recursos, mesmas regras de negocio, mesma massa inicial e persistencia em memoria. Os testes de carga compararam duas cargas, moderada e alta, coletando requisicoes por segundo, tempo medio, P95, falhas e taxa de falha.

O melhor resultado tecnico foi Java gRPC, por usar Protobuf, comunicacao binaria e contrato forte. REST foi a tecnologia mais simples para demonstrar CRUD. GraphQL mostrou flexibilidade nas consultas, mas com custo maior, principalmente em Python. SOAP demonstrou o uso de XML puro e contrato formal, mas tambem mostrou maior overhead, especialmente no Python sob carga alta.

Assim, a escolha depende do objetivo: REST para APIs simples, gRPC para alto desempenho entre servicos, GraphQL para consultas flexiveis e SOAP para integracoes formais ou legadas baseadas em XML.
