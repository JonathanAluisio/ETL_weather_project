# Projeto ETL: clima de São Paulo

Pipeline de dados que consulta a API OpenWeather, transforma as condições
climáticas de São Paulo e carrega os resultados em PostgreSQL. O agendamento e a
execução das etapas são feitos pelo Apache Airflow em containers Docker.

## Fluxo

1. **Extract:** consulta a API OpenWeather e salva a resposta bruta localmente.
2. **Transform:** normaliza os dados JSON, renomeia colunas e converte os
   horários para o fuso `America/Sao_Paulo`.
3. **Load:** grava os dados transformados na tabela `sp_weather`.

A DAG `weather_pipeline` está agendada para executar a cada hora. Ela também
pode ser iniciada manualmente pela interface do Airflow.

## Tecnologias

- Python, pandas, requests e SQLAlchemy
- Apache Airflow com CeleryExecutor
- PostgreSQL e Redis
- Docker Compose

## Pré-requisitos

- Docker com Docker Compose
- Uma chave de API da [OpenWeather](https://openweathermap.org/api)
- Acesso à internet para consultar a API

## Configuração local

1. Crie os arquivos de configuração locais a partir dos modelos:

   ```bash
   cp .env.example .env
   cp config/.env.example config/.env
   ```

2. Edite `.env` e substitua `FERNET_KEY` por uma chave gerada localmente:

   ```bash
   docker run --rm apache/airflow:3.3.2 \
     python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

   Defina também `AIRFLOW_UID` como o resultado de `id -u` em Linux, se
   aplicável.

3. Edite `config/.env` e informe sua chave da OpenWeather em `API_KEY`.
   Os valores `DB_*` deste arquivo são usados como fallback fora do Compose;
   dentro do Compose, a conexão usa as variáveis `ETL_DB_*` definidas para o
   serviço Airflow e o serviço `postgres`.

4. Inicie os serviços:

   ```bash
   docker compose up -d
   ```

   A primeira inicialização pode levar alguns minutos. Acompanhe os serviços
   com `docker compose ps`.

## Executar a DAG

Abra `http://localhost:8080`, entre no Airflow com as credenciais locais
configuradas no `.env` (no modelo, o usuário é `airflow` e a senha inicial é
`change-me`) e inicie a DAG `weather_pipeline` pela interface.

Também é possível iniciar uma execução pelo terminal:

```bash
docker compose exec airflow-scheduler airflow dags trigger weather_pipeline
```

## Consultar os dados

O serviço PostgreSQL publica a porta `5433` apenas em `localhost`. Para conectar
com o pgAdmin instalado na máquina:

- Host: `127.0.0.1`
- Porta: `5433`
- Banco: `airflow`
- Usuário e senha: os valores locais definidos no `docker-compose.yaml`

No Query Tool, consulte os dados com:

```sql
SELECT * FROM public.sp_weather;
```

## Encerrar os serviços

```bash
docker compose down
```

Os dados do PostgreSQL permanecem no volume Docker. Para apagar o volume e os
dados persistidos, seria necessário usar `docker compose down -v`; faça isso
somente se realmente quiser removê-los.

## Estrutura do projeto

```text
.
├── dags/                  # Definição da DAG do Airflow
├── config/                # Configuração local; segredos não versionados
├── data/                  # Dados intermediários gerados pela pipeline
├── notebooks/             # Exploração e análise dos dados
├── src/
│   ├── extract_data.py     # Extração da API
│   ├── transform_data.py  # Transformação dos dados
│   └── load_data.py       # Carga no PostgreSQL
├── docker-compose.yaml    # Serviços Airflow, PostgreSQL e Redis
└── pyproject.toml          # Metadados e dependências Python
```

## Segurança

Arquivos `.env`, chaves da API, configurações locais do Airflow, logs e dados
gerados estão excluídos do Git pelo `.gitignore`. Não publique credenciais reais
nem as inclua diretamente no código. As credenciais padrão deste Compose são
somente para desenvolvimento local; altere-as antes de qualquer uso exposto ou
de produção.
