# Arquitetura

O CestaControl foi estruturado como uma aplicacao FastAPI com paginas HTML renderizadas por Jinja2 e banco SQLite local.

## Modulos

- `app/main.py`: inicializacao da aplicacao, middleware de sessao e registro das rotas.
- `app/models.py`: entidades principais do dominio.
- `app/routers/auth.py`: login e logout.
- `app/routers/dashboard.py`: painel inicial.
- `app/routers/inventory.py`: cadastro e ajuste de estoque.
- `app/routers/technicians.py`: cadastro e ativacao de tecnicos.
- `app/routers/withdrawals.py`: lancamento de retiradas.
- `app/routers/reports.py`: historico, filtros e exportacoes.
- `app/services/exports.py`: geracao de PDF e Excel.

## Dados

O banco padrao fica em `data/cestacontrol.db`. Ele nao deve ser enviado ao GitHub, porque pode conter dados internos do servico.

## Uso interno

Para uso real, altere as credenciais no `.env` e mantenha o projeto rodando em uma maquina acessivel apenas pela rede interna ou por VPN.
