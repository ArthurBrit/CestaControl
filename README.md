# CestaControl

Sistema web interno para controlar estoque de cestas basicas e outros utensilios, registrando retiradas por tecnico e emitindo relatorios em PDF e Excel.

## Funcionalidades

- Login interno simples por sessao.
- Cadastro de tecnicos.
- Cadastro de itens de estoque.
- Entrada e ajuste de estoque.
- Lancamento de retiradas por tecnico, item, quantidade e data.
- Historico filtravel por periodo, tecnico e item.
- Relatorio consolidado com total por tecnico e item.
- Exportacao do relatorio em PDF e Excel.

## Como rodar

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Acesse: http://127.0.0.1:8000

Login padrao local:

- Usuario: `admin`
- Senha: `admin123`

Antes de usar no servico, altere `SECRET_KEY` e `ADMIN_PASSWORD` no arquivo `.env`.

## Banco de dados

Para uso em rede local, o projeto usa SQLite por padrao:

```env
DATABASE_URL=sqlite:///./data/cestacontrol.db
```

O banco fica salvo em `data/cestacontrol.db`. Faca backup desse arquivo com frequencia.

## Deploy

Para instalar em um PC servidor Windows e acessar pela rede local, veja:

- `docs/instalacao-rede-local-windows.md`

Para servidor Linux com Nginx, veja `docs/deploy-nginx.md`.

## Estrutura

```text
app/
  core/        configuracoes
  routers/     rotas da aplicacao
  services/    exportacao e regras auxiliares
  static/      css e javascript
  templates/   telas HTML
data/          banco SQLite local
docs/          documentacao do projeto
tests/         testes automatizados
```

## Observacao para portfolio

Este repositorio pode ficar publico no GitHub como portfolio, desde que o arquivo `.env` e o banco em `data/*.db` nao sejam enviados. O `.gitignore` ja protege esses arquivos.
