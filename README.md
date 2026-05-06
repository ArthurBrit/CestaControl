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
