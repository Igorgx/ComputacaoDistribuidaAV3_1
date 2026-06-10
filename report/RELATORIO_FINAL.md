# Relatorio Final - Comparacao de Tecnologias de Invocacao Remota

## 1. Visao Geral do Sistema

Este projeto implementa um servico fake de streaming de musicas para comparar quatro tecnologias de invocacao de servicos remotos: REST, gRPC, GraphQL e SOAP. O sistema nao transmite arquivos MP3; ele simula o backend de uma aplicacao de streaming por meio do gerenciamento de metadados.

O servico permite gerenciar tres tipos de recursos:

- Usuarios
- Musicas
- Playlists

Todas as implementacoes usam persistencia em memoria e iniciam com a mesma massa de dados:

- 250 usuarios
- 500 musicas
- 400 playlists

As playlists pertencem a usuarios e possuem listas de musicas. Com isso, o sistema consegue atender as consultas exigidas no trabalho:

- Listar todos os usuarios.
- Listar todas as musicas.
- Listar playlists de um usuario.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

## 2. Implementacoes

Foram desenvolvidas 8 implementacoes, combinando 4 tecnologias com 2 linguagens.

| Linguagem | Tecnologia | Porta | Descricao |
|---|---|---:|---|
| Python | REST | 8001 | API HTTP JSON com FastAPI |
| Python | gRPC | 8002 | RPC com Protobuf e grpcio |
| Python | GraphQL | 8003 | Queries e mutations com Strawberry |
| Python | SOAP | 8004 | Servico SOAP com Spyne, envelope SOAP e dados em XML |
| Java | REST | 8101 | API HTTP JSON com servidor HTTP da JDK |
| Java | gRPC | 8102 | RPC com grpc-java e Protobuf |
| Java | GraphQL | 8103 | Endpoint GraphQL didatico em Java |
| Java | SOAP | 8104 | Servico SOAP didatico em Java, envelope SOAP e dados em XML |

Todas as versoes implementam o mesmo conjunto funcional: CRUD de usuarios, CRUD de musicas, CRUD de playlists e consultas relacionais.

## 3. Modelo de Dados

### Usuario

```text
id: identificador numerico
name: nome do usuario
age: idade do usuario
```

### Musica

```text
id: identificador numerico
name: nome da musica
artist: artista da musica
```

### Playlist

```text
id: identificador numerico
name: nome da playlist
userId: usuario dono da playlist
musicIds: lista de musicas da playlist
```

## 4. Metodologia dos Testes de Carga

Os testes foram executados com duas cargas:

| Carga | Usuarios virtuais | Spawn rate | Duracao |
|---|---:|---:|---:|
| Moderada | 100 | 20 usuarios/s | 2 minutos |
| Alta | 400 | 80 usuarios/s | 2 minutos |

Para REST, GraphQL e SOAP foi utilizado Locust. Para gRPC tambem foi criado um gerador proprio de carga baseado em threads, pois a combinacao entre Locust/gevent e o cliente gRPC Python apresentou problemas de finalizacao de canais em alguns testes. O gerador proprio coleta as mesmas metricas principais: total de requisicoes, falhas, requisicoes por segundo, tempo medio e percentil 95.

Os testes SOAP foram executados com requisicoes `text/xml` e respostas em XML dentro do envelope SOAP. A versao corrigida nao retorna JSON encapsulado em SOAP.

Fluxos testados:

- Listar musicas.
- Consultar usuario.
- Criar playlist.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

## 5. Graficos

### Requisicoes por Segundo

![Requisicoes por segundo](results/charts/requests_per_second.png)

### Tempo Medio de Resposta

![Tempo medio de resposta](results/charts/average_response_time.png)

### Percentil 95

![Percentil 95](results/charts/p95_response_time.png)

### Taxa de Falha

![Taxa de falha](results/charts/failure_rate_percent.png)

### Crescimento da Latencia

![Crescimento da latencia](results/charts/latency_growth_moderada_to_alta.png)

### Graficos por Sistemas Remotos

Os graficos abaixo separam os resultados por tecnologia de invocacao remota. Em cada tecnologia aparecem as quatro combinacoes principais: Python moderada, Python alta, Java moderada e Java alta.

![Sistemas remotos - requisicoes por segundo](results/charts/remote_systems_rps.png)

![Sistemas remotos - tempo medio](results/charts/remote_systems_avg.png)

![Sistemas remotos - percentil 95](results/charts/remote_systems_p95.png)

![Sistemas remotos - taxa de falha](results/charts/remote_systems_failure_rate.png)

### Graficos por Linguagem

Os graficos abaixo separam os resultados por linguagem, permitindo observar qual tecnologia se destacou mais em Python e qual se destacou mais em Java.

![Por linguagem - requisicoes por segundo](results/charts/language_rps.png)

![Por linguagem - tempo medio](results/charts/language_avg.png)

![Por linguagem - percentil 95](results/charts/language_p95.png)

![Por linguagem - taxa de falha](results/charts/language_failure_rate.png)

## 6. Resultados Consolidados

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

## 7. Analise dos Resultados

### 7.1 Python REST

O REST em Python apresentou comportamento estavel na carga moderada, com 202.62 req/s, tempo medio de 34.18 ms e nenhuma falha. Na carga alta, a vazao ficou em 214.66 req/s, mas o tempo medio subiu para 1373.36 ms e o P95 chegou a 1600 ms.

Isso indica que o servico continuou aceitando requisicoes, mas passou a formar fila sob carga maior. A taxa de falha foi baixa, 0.03%, com 8 falhas, mostrando que a implementacao ficou proxima do limite, embora ainda funcional. O gargalo principal e o custo de lidar com muitas chamadas HTTP/JSON em um processo Python, com serializacao de listas grandes e acesso ao store em memoria protegido por lock.

### 7.2 Python gRPC

O gRPC em Python teve o melhor desempenho entre as implementacoes Python. Na carga moderada, registrou 209.27 req/s, tempo medio de 3.51 ms e P95 de 4.94 ms. Na carga alta, subiu para 740.03 req/s, com tempo medio de 63.19 ms, P95 de 324.37 ms e nenhuma falha.

Esse resultado mostra a eficiencia do gRPC em chamadas repetidas. O uso de Protobuf e de canal persistente reduz o overhead de serializacao e conexao, principalmente quando comparado com chamadas HTTP/JSON, XML e processamento de queries. A latencia ficou maior do que na rodada anterior, mas ainda foi a melhor combinacao Python na carga alta.

### 7.3 Python GraphQL

O GraphQL em Python teve desempenho inferior ao REST e ao gRPC. Na carga moderada, obteve 150.96 req/s, tempo medio de 198.42 ms e P95 de 340 ms, sem falhas. Na carga alta, ficou em 137.02 req/s, com tempo medio de 2394.58 ms, P95 de 2800 ms e 0.55% de falhas.

A queda de desempenho e esperada porque GraphQL adiciona uma camada de interpretacao e resolucao de queries. Mesmo quando a consulta e simples, o servidor precisa processar o documento GraphQL, mapear campos e executar resolvers.

### 7.4 Python SOAP

O SOAP em Python teve resultado intermediario na carga moderada: 196.51 req/s, tempo medio de 49.19 ms e nenhuma falha. Na carga alta, chegou a 329.81 req/s, mas com tempo medio de 735.38 ms, P95 de 2100 ms e taxa de falha de 9.22%.

Isso indica que a implementacao suportou maior volume de chamadas, mas com instabilidade significativa sob carga. O uso de XML puro dentro do envelope SOAP aumenta o custo de parsing e serializacao, o que aparece especialmente em cargas mais altas.

### 7.5 Java REST

O REST em Java apresentou alta vazao, chegando a 730.35 req/s na carga alta. O tempo medio tambem permaneceu menor que o REST Python, com 71.62 ms na carga alta, P95 de 310 ms e nenhuma falha.

Uma rodada anterior apresentou falhas altas no Java REST, mas a causa foi identificada como bug de implementacao: o `POST /playlists` nao tratava corretamente a ausencia de `id` no JSON, enquanto o teste de carga criava playlists deixando o servidor gerar o ID automaticamente. Apos corrigir esse ponto e refazer os testes, o Java REST ficou estavel. Para uma implementacao de producao, ainda seria esperado usar frameworks como Spring Boot, Quarkus, Micronaut ou Javalin, mas neste trabalho o resultado corrigido mostra que REST em Java foi eficiente.

### 7.6 Java gRPC

O Java gRPC apresentou o melhor resultado geral. Na carga moderada, registrou 211.46 req/s, tempo medio de 1.43 ms e P95 de 2.24 ms. Na carga alta, chegou a 835.18 req/s, com tempo medio de 2.77 ms, P95 de 5.55 ms e nenhuma falha.

Esse resultado reforca que gRPC e adequado para comunicacao servico a servico com alto volume de requisicoes. A combinacao de contrato Protobuf, comunicacao binaria e runtime Java teve o melhor equilibrio entre vazao, baixa latencia e estabilidade.

### 7.7 Java GraphQL

O Java GraphQL teve vazao alta, com 800.94 req/s na carga alta, tempo medio de 34.20 ms, P95 de 110 ms e nenhuma falha.

Uma rodada anterior apresentou falhas no `createPlaylist`, mas a causa era a extracao simplificada da query GraphQL dentro do JSON da requisicao. O parser cortava a query quando encontrava aspas escapadas no campo `name`, fazendo o `userId` virar 0. Apos corrigir a leitura da query e refazer os testes, a implementacao ficou estavel. Ainda assim, o custo de GraphQL aparece na latencia maior que a do gRPC.

### 7.8 Java SOAP

O Java SOAP teve desempenho alto e estavel nos testes. Na carga moderada, registrou 215.22 req/s, tempo medio de 3.45 ms e nenhuma falha. Na carga alta, chegou a 695.97 req/s, tempo medio de 95.35 ms, P95 de 370 ms e nenhuma falha.

Mesmo sendo uma tecnologia mais verbosa por usar XML, a implementacao Java teve boa estabilidade. O resultado ainda ficou abaixo do Java gRPC em latencia e vazao, o que condiz com o overhead do SOAP, mas demonstra que SOAP pode funcionar bem quando o servidor consegue lidar com a carga.

## 8. Comparacao Geral

O gRPC foi a tecnologia com melhor desempenho geral. Tanto em Python quanto em Java, apresentou baixa latencia, alto numero de requisicoes por segundo e nenhuma falha. Isso confirma sua adequacao para comunicacao interna entre servicos, especialmente quando existe grande volume de chamadas.

REST foi simples de implementar e demonstrar, sendo a melhor tecnologia para apresentar o CRUD ao professor. Em Python, teve taxa de falha muito baixa, 0.03%, mas sofreu grande aumento de latencia na carga alta. Em Java, teve alta vazao, baixa latencia relativa e nenhuma falha depois da correcao do CRUD de playlists.

GraphQL mostrou flexibilidade nas consultas, mas teve maior custo no Python sob carga alta. A versao Java ficou estavel depois da correcao do parser da query e melhorou bastante na nova rodada, embora ainda tenha latencia maior que gRPC.

SOAP apresentou overhead maior em Python e boa estabilidade em Java. Como os testes finais usam XML puro no envelope SOAP, o custo de parsing e serializacao aparece principalmente na carga alta. Apesar de ser mais antigo e verboso, ainda pode ser adequado quando ha necessidade de contrato formal e integracao com ambientes corporativos.

Por linguagem, o destaque em Python foi o gRPC: teve a maior vazao na carga alta, 740.03 req/s, tempo medio de 63.19 ms, P95 de 324.37 ms e nenhuma falha. Em Java, o gRPC tambem foi o melhor: 835.18 req/s, tempo medio de 2.77 ms, P95 de 5.55 ms e nenhuma falha. REST foi o caminho mais simples para demonstrar CRUD, mas nao superou gRPC nos testes de desempenho.

## 9. Conclusao

O trabalho mostra que as quatro tecnologias conseguem implementar o mesmo servico funcional, com CRUD e consultas relacionais. A diferenca aparece principalmente sob carga.

O gRPC foi o melhor em desempenho e estabilidade. REST foi o mais simples de testar e demonstrar. GraphQL ofereceu flexibilidade de consulta, mas com maior custo de processamento. SOAP apresentou maior formalidade e verbosidade, com desempenho variando conforme a linguagem e implementacao.

Assim, a escolha da tecnologia depende do contexto:

- Para APIs simples e abertas: REST.
- Para comunicacao interna de alto desempenho: gRPC.
- Para clientes que precisam escolher exatamente os dados retornados: GraphQL.
- Para integracoes formais ou legadas baseadas em contrato XML: SOAP.

## 10. Comandos para Executar o Sistema

### 10.1 Preparacao

```powershell
cd "C:\AV3 Computação Distribuída 1"
./scripts/setup-python.ps1
./scripts/setup-maven.ps1
```

### 10.2 Subir Servicos Python

```powershell
./scripts/run-python-rest.ps1
./scripts/run-python-grpc.ps1
./scripts/run-python-graphql.ps1
./scripts/run-python-soap.ps1
```

### 10.3 Subir Servicos Java

```powershell
./scripts/run-java-rest.ps1
./scripts/run-java-grpc.ps1
./scripts/run-java-graphql.ps1
./scripts/run-java-soap.ps1
```

## 11. Comandos CRUD via REST

Os exemplos abaixo usam REST Python em `http://127.0.0.1:8001`. Para usar REST Java, troque para `http://127.0.0.1:8101`.

```powershell
$base = "http://127.0.0.1:8001"
```

### 11.1 Usuarios

Listar usuarios:

```powershell
Invoke-RestMethod "$base/users"
```

Criar usuario:

```powershell
Invoke-RestMethod -Uri "$base/users" `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    name = "Joao Silva"
    age = 25
  } | ConvertTo-Json)
```

Consultar usuario:

```powershell
Invoke-RestMethod "$base/users/251"
```

Atualizar usuario:

```powershell
Invoke-RestMethod -Uri "$base/users/251" `
  -Method Put `
  -ContentType "application/json" `
  -Body (@{
    name = "Joao Atualizado"
    age = 26
  } | ConvertTo-Json)
```

Remover usuario:

```powershell
Invoke-RestMethod -Uri "$base/users/251" -Method Delete
```

### 11.2 Musicas

Listar musicas:

```powershell
Invoke-RestMethod "$base/musics"
```

Criar musica:

```powershell
Invoke-RestMethod -Uri "$base/musics" `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    name = "Musica Nova"
    artist = "Artista Novo"
  } | ConvertTo-Json)
```

Consultar musica:

```powershell
Invoke-RestMethod "$base/musics/501"
```

Atualizar musica:

```powershell
Invoke-RestMethod -Uri "$base/musics/501" `
  -Method Put `
  -ContentType "application/json" `
  -Body (@{
    name = "Musica Atualizada"
    artist = "Artista Atualizado"
  } | ConvertTo-Json)
```

Remover musica:

```powershell
Invoke-RestMethod -Uri "$base/musics/501" -Method Delete
```

### 11.3 Playlists

Listar playlists:

```powershell
Invoke-RestMethod "$base/playlists"
```

Criar playlist:

```powershell
Invoke-RestMethod -Uri "$base/playlists" `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    name = "Minha Playlist"
    userId = 1
    musicIds = @(1, 2, 3, 4, 5)
  } | ConvertTo-Json)
```

Consultar playlist:

```powershell
Invoke-RestMethod "$base/playlists/401"
```

Atualizar playlist:

```powershell
Invoke-RestMethod -Uri "$base/playlists/401" `
  -Method Put `
  -ContentType "application/json" `
  -Body (@{
    name = "Playlist Atualizada"
    userId = 1
    musicIds = @(10, 11, 12)
  } | ConvertTo-Json)
```

Remover playlist:

```powershell
Invoke-RestMethod -Uri "$base/playlists/401" -Method Delete
```

## 12. Consultas Relacionais

Listar playlists de um usuario:

```powershell
Invoke-RestMethod "$base/users/1/playlists"
```

Listar musicas de uma playlist:

```powershell
Invoke-RestMethod "$base/playlists/1/musics"
```

Listar playlists que contem uma musica:

```powershell
Invoke-RestMethod "$base/musics/1/playlists"
```

## 13. Comandos dos Testes de Carga

### REST, GraphQL e SOAP

Exemplo REST Python moderada:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol rest -Out python_rest_moderada
```

Exemplo REST Python alta:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol rest -Out python_rest_alta
```

Para GraphQL, use `-Protocol graphql` e a porta GraphQL:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8003 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol graphql -Out python_graphql_alta
```

Para SOAP, use `-Protocol soap` e a porta SOAP:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8004 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol soap -Out python_soap_alta
```

### gRPC

Python gRPC carga alta:

```powershell
./scripts/run-grpc-load.ps1 -Target 127.0.0.1:8002 -Users 400 -SpawnRate 80 -RunTimeSeconds 120 -Out python_grpc_alta
```

Java gRPC carga alta:

```powershell
./scripts/run-grpc-load.ps1 -Target 127.0.0.1:8102 -Users 400 -SpawnRate 80 -RunTimeSeconds 120 -Out java_grpc_alta
```

### Gerar Graficos

```powershell
./.venv/Scripts/python.exe ./report/generate_charts.py
```

Os graficos ficam em:

```text
report/results/charts
```
