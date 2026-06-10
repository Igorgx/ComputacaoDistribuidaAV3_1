# Relatorio - Comparacao de Tecnologias de Invocacao Remota

## Identificacao

Trabalho de Computacao Distribuida sobre comparacao de tecnologias de invocacao remota por meio da implementacao de um servico fake de streaming de musicas.

Membros da equipe:

- Igor Gomes Ximenes - 2217665
- Gabril Abreu Cunha de Alencar - 2315097
- Kalil Smith Pinto Palheta - 2223857

## Resumo do Projeto

O projeto implementa o mesmo servico de streaming de musicas em 8 versoes diferentes, combinando 4 tecnologias de invocacao remota com 2 linguagens de programacao:

- REST
- gRPC
- GraphQL
- SOAP
- Python
- Java

O objetivo é comparar similaridades, diferencas, vantagens, desvantagens e desempenho das tecnologias. O sistema nao transmite MP3 nem audio real. Ele simula o backend de um servico de streaming por meio de metadados de usuarios, musicas e playlists.

Todas as implementacoes oferecem as mesmas funcionalidades:

- CRUD de usuarios.
- CRUD de musicas.
- CRUD de playlists.
- Listagem de todos os usuarios.
- Listagem de todas as musicas.
- Listagem de playlists de um usuario.
- Listagem de musicas de uma playlist.
- Listagem de playlists que contem uma musica.

A persistencia e em memoria, como permitido pelo enunciado. Todas as implementacoes usam a mesma massa inicial de dados para permitir comparacao justa.

## Massa de Dados

Todas as implementacoes inicializam os dados em memoria com o mesmo padrao:

| Recurso | Quantidade inicial | Campos |
|---|---:|---|
| Usuario | 250 | `id`, `name`, `age` |
| Musica | 500 | `id`, `name`, `artist` |
| Playlist | 400 | `id`, `name`, `userId`, `musicIds` |

Relacionamentos:

- Uma playlist pertence a um usuario por meio de `userId`.
- Uma playlist contem uma lista de musicas por meio de `musicIds`.
- As playlists sempre referenciam usuarios e musicas existentes.

Exemplo conceitual dos dados:

```json
{
  "user": {
    "id": 1,
    "name": "Usuario 1",
    "age": 19
  },
  "music": {
    "id": 1,
    "name": "Musica 1",
    "artist": "Banda Delta"
  },
  "playlist": {
    "id": 1,
    "name": "Playlist 1",
    "userId": 1,
    "musicIds": [8, 9, 10, 11, 12]
  }
}
```

## Implementacoes

| Linguagem | Tecnologia | Porta | Protocolo/Formato | Implementacao |
|---|---|---:|---|---|
| Python | REST | 8001 | HTTP + JSON | FastAPI |
| Python | gRPC | 8002 | HTTP/2 + Protobuf | grpcio |
| Python | GraphQL | 8003 | HTTP + JSON GraphQL | Strawberry |
| Python | SOAP | 8004 | HTTP + XML SOAP | Spyne |
| Java | REST | 8101 | HTTP + JSON | HttpServer da JDK |
| Java | gRPC | 8102 | HTTP/2 + Protobuf | grpc-java |
| Java | GraphQL | 8103 | HTTP + JSON GraphQL | HttpServer da JDK |
| Java | SOAP | 8104 | HTTP + XML SOAP | HttpServer da JDK |

Foram implementadas 8 versoes do mesmo servico, atendendo ao requisito de 4 tecnologias em pelo menos 2 linguagens.

## Estrutura do Repositorio

```text
python/rest       REST em Python
python/grpc       gRPC em Python
python/graphql    GraphQL em Python
python/soap       SOAP em Python

java/rest         REST em Java
java/grpc         gRPC em Java
java/graphql      GraphQL em Java
java/soap         SOAP em Java

shared            Documentacao do modelo
scripts           Scripts de setup, execucao e demonstracao
load-tests        Testes de carga
report/results    Resultados CSV/HTML e graficos
```

## Como Executar

### Preparacao

```powershell
cd "C:\AV3 Computação Distribuída 1"
./scripts/setup-python.ps1
./scripts/setup-maven.ps1
```

O Java REST, GraphQL e SOAP usam a JDK. O Java gRPC usa Maven local instalado pelo script.

### Subir os Servicos Python

Abra um terminal para cada servico:

```powershell
./scripts/run-python-rest.ps1
./scripts/run-python-grpc.ps1
./scripts/run-python-graphql.ps1
./scripts/run-python-soap.ps1
```

### Subir os Servicos Java

Abra um terminal para cada servico:

```powershell
./scripts/run-java-rest.ps1
./scripts/run-java-grpc.ps1
./scripts/run-java-graphql.ps1
./scripts/run-java-soap.ps1
```

## Testes de Carga

Foram executadas duas cargas:

| Carga | Usuarios virtuais | Spawn rate | Duracao |
|---|---:|---:|---:|
| Moderada | 100 | 20 usuarios/s | 2 minutos |
| Alta | 400 | 80 usuarios/s | 2 minutos |

Fluxos simulados:

- Listar musicas.
- Consultar usuario.
- Criar playlist.
- Listar musicas de uma playlist.
- Listar playlists que contem uma musica.

Ferramentas:

- REST, GraphQL e SOAP: Locust.
- gRPC: gerador proprio baseado em threads, porque o cliente gRPC Python com Locust/gevent apresentou problemas de finalizacao em alguns testes.

Metricas coletadas:

- Requisicoes totais.
- Requisicoes por segundo.
- Tempo medio de resposta.
- Percentil 95.
- Falhas absolutas.
- Taxa de falha.

Exemplo de execucao REST:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol rest -Out python_rest_moderada
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol rest -Out python_rest_alta
```

Exemplo de execucao GraphQL:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8003 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol graphql -Out python_graphql_alta
```

Exemplo de execucao SOAP:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8004 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol soap -Out python_soap_alta
```

Exemplo de execucao gRPC:

```powershell
./scripts/run-grpc-load.ps1 -Target 127.0.0.1:8002 -Users 400 -SpawnRate 80 -RunTimeSeconds 120 -Out python_grpc_alta
./scripts/run-grpc-load.ps1 -Target 127.0.0.1:8102 -Users 400 -SpawnRate 80 -RunTimeSeconds 120 -Out java_grpc_alta
```

Gerar graficos:

```powershell
./.venv/Scripts/python.exe ./report/generate_charts.py
```

## Resultados Consolidados

| Implementacao | Requisicoes | Req/s | Tempo medio | P95 | Falhas | Taxa de falha |
|---|---:|---:|---:|---:|---:|---:|
| Python REST moderada | 22977 | 192.19 | 57.92 ms | 190 ms | 0 | 0.00% |
| Python REST alta | 22600 | 190.41 | 1604.46 ms | 2300 ms | 0 | 0.00% |
| Python gRPC moderada | 25621 | 215.08 | 1.52 ms | 3 ms | 0 | 0.00% |
| Python gRPC alta | 76391 | 634.64 | 1.39 ms | 3 ms | 0 | 0.00% |
| Python GraphQL moderada | 16954 | 141.82 | 242.55 ms | 460 ms | 0 | 0.00% |
| Python GraphQL alta | 15801 | 132.54 | 2489.79 ms | 3400 ms | 79 | 0.50% |
| Python SOAP moderada | 23707 | 200.12 | 36.62 ms | 510 ms | 0 | 0.00% |
| Python SOAP alta | 40341 | 336.78 | 708.07 ms | 2100 ms | 3136 | 7.77% |
| Java REST moderada | 25485 | 214.10 | 4.61 ms | 8 ms | 0 | 0.00% |
| Java REST alta | 88063 | 741.06 | 67.57 ms | 280 ms | 0 | 0.00% |
| Java gRPC moderada | 25544 | 215.03 | 1.03 ms | 2 ms | 0 | 0.00% |
| Java gRPC alta | 100527 | 832.40 | 3.56 ms | 5 ms | 0 | 0.00% |
| Java GraphQL moderada | 25469 | 214.56 | 4.32 ms | 7 ms | 0 | 0.00% |
| Java GraphQL alta | 84973 | 711.57 | 84.49 ms | 360 ms | 0 | 0.00% |
| Java SOAP moderada | 25612 | 214.13 | 3.29 ms | 6 ms | 0 | 0.00% |
| Java SOAP alta | 83481 | 698.77 | 94.90 ms | 380 ms | 0 | 0.00% |

## Graficos Gerais

### Requisicoes por Segundo

![Requisicoes por segundo](report/results/charts/requests_per_second.png)

### Tempo Medio de Resposta

![Tempo medio de resposta](report/results/charts/average_response_time.png)

### Percentil 95

![Percentil 95](report/results/charts/p95_response_time.png)

### Taxa de Falha

![Taxa de falha](report/results/charts/failure_rate_percent.png)

### Falhas Absolutas

![Falhas absolutas](report/results/charts/failures_absolute.png)

### Crescimento da Latencia

![Crescimento da latencia](report/results/charts/latency_growth_moderada_to_alta.png)

## Graficos por Sistema Remoto

Estes graficos comparam, para cada sistema remoto, os resultados das 4 combinacoes: Python moderada, Python alta, Java moderada e Java alta.

### Sistemas Remotos - Requisicoes por Segundo

![Sistemas remotos - requisicoes por segundo](report/results/charts/remote_systems_rps.png)

### Sistemas Remotos - Tempo Medio

![Sistemas remotos - tempo medio](report/results/charts/remote_systems_avg.png)

### Sistemas Remotos - Percentil 95

![Sistemas remotos - percentil 95](report/results/charts/remote_systems_p95.png)

### Sistemas Remotos - Taxa de Falha

![Sistemas remotos - taxa de falha](report/results/charts/remote_systems_failure_rate.png)

## Graficos por Linguagem

Estes graficos mostram qual tecnologia se destacou mais dentro de cada linguagem.

### Por Linguagem - Requisicoes por Segundo

![Por linguagem - requisicoes por segundo](report/results/charts/language_rps.png)

### Por Linguagem - Tempo Medio

![Por linguagem - tempo medio](report/results/charts/language_avg.png)

### Por Linguagem - Percentil 95

![Por linguagem - percentil 95](report/results/charts/language_p95.png)

### Por Linguagem - Taxa de Falha

![Por linguagem - taxa de falha](report/results/charts/language_failure_rate.png)

## Analise por Tecnologia

### REST

Resultados principais:

- Python REST moderada: 192.19 req/s, 57.92 ms, 0 falhas.
- Python REST alta: 190.41 req/s, 1604.46 ms, 0 falhas.
- Java REST moderada: 214.10 req/s, 4.61 ms, 0 falhas.
- Java REST alta: 741.06 req/s, 67.57 ms, 0 falhas.

Interpretacao:

- Em Python, REST se manteve funcional, mas a latencia subiu muito na carga alta. Isso indica fila de requisicoes e saturacao do processo, principalmente por causa de HTTP/JSON, serializacao de listas e acesso sincronizado ao store em memoria.
- Em Java, REST teve alta vazao e 0 falhas apos correcao do CRUD de playlists. A versao Java usa servidor HTTP simples da JDK, mas mesmo assim foi bem na carga alta.

### gRPC

gRPC foi o melhor resultado geral do trabalho.

Resultados principais:

- Python gRPC moderada: 215.08 req/s, 1.52 ms, 0 falhas.
- Python gRPC alta: 634.64 req/s, 1.39 ms, 0 falhas.
- Java gRPC moderada: 215.03 req/s, 1.03 ms, 0 falhas.
- Java gRPC alta: 832.40 req/s, 3.56 ms, 0 falhas.

Interpretacao:

- gRPC teve as menores latencias.
- Protobuf reduz custo de serializacao.
- O canal gRPC persistente reduz overhead de conexao.
- Java gRPC foi o melhor resultado geral, com maior vazao e baixa latencia.

### GraphQL

GraphQL ofereceu a maior flexibilidade de consulta, mas teve custo maior no Python.

Resultados principais:

- Python GraphQL moderada: 141.82 req/s, 242.55 ms, 0 falhas.
- Python GraphQL alta: 132.54 req/s, 2489.79 ms, 79 falhas, 0.50%.
- Java GraphQL moderada: 214.56 req/s, 4.32 ms, 0 falhas.
- Java GraphQL alta: 711.57 req/s, 84.49 ms, 0 falhas.

Interpretacao:

- Em Python, GraphQL foi pesado sob carga alta porque cada requisicao precisa passar por parse da query, resolucao de campos e execucao de resolvers.
- Em Java, apos correcao do parser da query GraphQL no JSON, a implementacao ficou estavel e com boa vazao.
- Mesmo em Java, GraphQL ficou com latencia maior que gRPC, o que e esperado pelo custo adicional de interpretacao das queries.

### SOAP

SOAP foi implementado com XML puro dentro do envelope SOAP. Os testes finais usam `text/xml` e respostas XML.

Resultados principais:

- Python SOAP moderada: 200.12 req/s, 36.62 ms, 0 falhas.
- Python SOAP alta: 336.78 req/s, 708.07 ms, 3136 falhas, 7.77%.
- Java SOAP moderada: 214.13 req/s, 3.29 ms, 0 falhas.
- Java SOAP alta: 698.77 req/s, 94.90 ms, 0 falhas.

Interpretacao:

- SOAP em Python sofreu na carga alta, com aumento de latencia e falhas.
- O uso de XML aumenta o custo de parsing e serializacao.
- SOAP em Java ficou estavel, mas com latencia maior que gRPC, o que condiz com o overhead do XML.
- SOAP continua sendo adequado quando o contexto exige XML, contrato formal ou integracao com sistemas legados.

## Analise por Linguagem

### Python

Ranking na carga alta por desempenho geral:

| Tecnologia | Req/s | Tempo medio | P95 | Falhas |
|---|---:|---:|---:|---:|
| gRPC | 634.64 | 1.39 ms | 3 ms | 0 |
| SOAP | 336.78 | 708.07 ms | 2100 ms | 3136 |
| REST | 190.41 | 1604.46 ms | 2300 ms | 0 |
| GraphQL | 132.54 | 2489.79 ms | 3400 ms | 79 |

Melhor em Python: **gRPC**.

Motivos:

- Menor latencia.
- Maior vazao.
- Nenhuma falha.
- Menor overhead de serializacao por usar Protobuf.

Observacoes:

- REST Python foi estavel, mas enfileirou requisicoes na carga alta.
- GraphQL Python teve o maior custo de processamento.
- SOAP Python mostrou instabilidade com XML sob carga alta.

### Java

Ranking na carga alta por desempenho geral:

| Tecnologia | Req/s | Tempo medio | P95 | Falhas |
|---|---:|---:|---:|---:|
| gRPC | 832.40 | 3.56 ms | 5 ms | 0 |
| REST | 741.06 | 67.57 ms | 280 ms | 0 |
| GraphQL | 711.57 | 84.49 ms | 360 ms | 0 |
| SOAP | 698.77 | 94.90 ms | 380 ms | 0 |

Melhor em Java: **gRPC**.

Motivos:

- Maior vazao entre todas as implementacoes.
- P95 muito baixo.
- Nenhuma falha.
- Bom aproveitamento do runtime Java com comunicacao binaria.

Observacoes:

- REST Java tambem foi forte e simples de demonstrar.
- GraphQL Java ficou estavel apos correcao do parser.
- SOAP Java mostrou que XML pode ser viavel quando o servidor lida bem com a carga, mas ainda ficou atras de gRPC.

## Melhores Resultados

Melhor resultado geral:

| Criterio | Melhor implementacao | Resultado |
|---|---|---|
| Maior vazao | Java gRPC alta | 832.40 req/s |
| Menor tempo medio | Python gRPC alta | 1.39 ms |
| Menor P95 em carga alta | Python gRPC alta | 3 ms |
| Melhor estabilidade | gRPC Python e Java | 0 falhas |
| Melhor para demonstrar CRUD | REST | Chamadas HTTP simples |
| Melhor em Python | Python gRPC | 634.64 req/s, 1.39 ms |
| Melhor em Java | Java gRPC | 832.40 req/s, 3.56 ms |

Conclusao sobre os melhores:

- **gRPC foi a melhor tecnologia em desempenho e estabilidade.**
- **REST foi a melhor tecnologia para demonstracao manual do CRUD.**
- **GraphQL foi a melhor em flexibilidade de consulta, mas nao em desempenho no Python.**
- **SOAP foi a melhor representacao de integracao formal/legada com XML, mas teve overhead maior.**

## Conclusao

O trabalho implementou o mesmo servico em 8 versoes equivalentes, usando 4 tecnologias de invocacao remota e 2 linguagens.

Todas as versoes implementam CRUD de usuarios, musicas e playlists, consultas relacionais e massa de dados inicial com centenas de registros.

Os testes mostram que a diferenca entre tecnologias aparece principalmente quando a carga aumenta:

- gRPC teve melhor desempenho geral.
- REST foi simples, funcional e excelente para demonstracao.
- GraphQL trouxe flexibilidade, mas com custo de processamento maior.
- SOAP demonstrou o custo do XML e a importancia de implementacao eficiente.

A escolha ideal depende do objetivo:

- APIs simples e publicas: REST.
- Comunicacao interna de alto desempenho: gRPC.
- Consultas flexiveis para clientes diferentes: GraphQL.
- Integracoes formais ou legadas baseadas em XML: SOAP.

No contexto dos testes realizados, **gRPC foi o vencedor tecnico**.
