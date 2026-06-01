# Servico Fake de Streaming de Musicas

Trabalho de Computacao Distribuida com 8 implementacoes do mesmo servico:

| Linguagem | REST | gRPC | GraphQL | SOAP |
|---|---:|---:|---:|---:|
| Python | 8001 | 8002 | 8003 | 8004 |
| Java | 8101 | 8102 | 8103 | 8104 |

O servico usa persistencia em memoria com 250 usuarios, 500 musicas e 400 playlists.

## Setup

```powershell
./scripts/setup-python.ps1
```

O Java REST, GraphQL e SOAP usam apenas JDK 21. O Java gRPC usa Maven local:

```powershell
./scripts/setup-maven.ps1
```

## Executar Servicos

Abra um terminal por servico.

```powershell
./scripts/run-python-rest.ps1
./scripts/run-python-grpc.ps1
./scripts/run-python-graphql.ps1
./scripts/run-python-soap.ps1

./scripts/run-java-rest.ps1
./scripts/run-java-grpc.ps1
./scripts/run-java-graphql.ps1
./scripts/run-java-soap.ps1
```

Observacao: o script Java gRPC copia o modulo para uma pasta temporaria ASCII antes de executar, porque o `protoc` pode falhar em caminhos Windows com acentos.

## Demonstrar CRUD e Consultas

REST:

```powershell
./scripts/demo-rest.ps1 -BaseUrl http://127.0.0.1:8001
./scripts/demo-rest.ps1 -BaseUrl http://127.0.0.1:8101
```

GraphQL:

```powershell
./scripts/demo-graphql.ps1 -BaseUrl http://127.0.0.1:8003/graphql
./scripts/demo-graphql.ps1 -BaseUrl http://127.0.0.1:8103/graphql
```

SOAP:

```powershell
./scripts/demo-soap.ps1 -BaseUrl http://127.0.0.1:8004
./scripts/demo-soap.ps1 -BaseUrl http://127.0.0.1:8104
```

gRPC Python:

```powershell
$env:PYTHONPATH = "$(Get-Location);$(Join-Path (Get-Location) 'python/grpc/generated')"
./.venv/Scripts/python.exe -m python.grpc.client_demo
```

gRPC Java:

```powershell
$env:GRPC_TARGET = "127.0.0.1:8102"
$env:PYTHONPATH = "$(Get-Location);$(Join-Path (Get-Location) 'python/grpc/generated')"
./.venv/Scripts/python.exe -m python.grpc.client_demo
```

## Testes de Carga

Exemplo de carga moderada REST Python:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol rest -Out python_rest_moderada
```

Exemplo de carga alta REST Python:

```powershell
./scripts/run-load.ps1 -Class MusicHttpUser -HostUrl http://127.0.0.1:8001 -Users 400 -SpawnRate 80 -RunTime 2m -Protocol rest -Out python_rest_alta
```

Protocolos HTTP:

- REST: `-Class MusicHttpUser -Protocol rest`
- GraphQL: `-Class MusicHttpUser -Protocol graphql`
- SOAP: `-Class MusicHttpUser -Protocol soap`

gRPC:

```powershell
./scripts/run-load.ps1 -Class MusicGrpcUser -HostUrl 127.0.0.1:8002 -Users 100 -SpawnRate 20 -RunTime 2m -Protocol grpc -Out python_grpc_moderada
```

Depois gere graficos SVG:

```powershell
./.venv/Scripts/python.exe ./report/generate_charts.py
```
