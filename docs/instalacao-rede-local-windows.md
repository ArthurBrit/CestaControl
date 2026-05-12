# Instalacao em rede local no Windows

Este guia e para instalar o CestaControl em um PC da empresa e permitir que outros computadores da mesma rede acessem pelo navegador.

## Como vai funcionar

```text
PC servidor ligado
  -> CestaControl rodando na porta 8000
  -> Banco SQLite salvo em data/cestacontrol.db
  -> Outros PCs acessam pelo navegador
```

O sistema pode ser desligado no fim do expediente. Enquanto o PC servidor estiver desligado, o CestaControl fica fora do ar. Ao ligar novamente e iniciar o sistema, os dados continuam salvos.

## 1. Preparar o PC servidor

Escolha um computador que fique disponivel durante o horario de uso. O ideal e:

- Windows 10 ou 11.
- Conectado na rede por cabo, se possivel.
- Um usuario com permissao para instalar Python.
- Backup em OneDrive, Google Drive, pendrive ou outro computador.

Instale o Python pelo site oficial:

```text
https://www.python.org/downloads/
```

Durante a instalacao, marque a opcao:

```text
Add python.exe to PATH
```

## 2. Copiar o projeto para o PC servidor

Copie a pasta `CestaControl` para um lugar simples, por exemplo:

```text
C:\CestaControl
```

Evite deixar o projeto em pasta temporaria ou em local que outros usuarios apaguem sem querer.

## 3. Instalar dependencias

No PC servidor, abra a pasta do projeto e execute:

```text
scripts\install-windows.cmd
```

Esse script cria o ambiente Python, instala as dependencias e cria o arquivo `.env`.

## 4. Configurar usuario e senha

Abra o arquivo `.env` e altere:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=troque-essa-senha
DATABASE_URL=sqlite:///./data/cestacontrol.db
```

Use uma senha que as pessoas autorizadas conhecam.

## 5. Iniciar o sistema

Execute:

```text
scripts\start-server.cmd
```

No proprio PC servidor, acesse:

```text
http://127.0.0.1:8000
```

O script tambem mostra na tela os enderecos para os outros computadores acessarem.

## 6. Descobrir o IP do PC servidor

O script de inicio mostra os IPs automaticamente. Se quiser conferir manualmente, no PC servidor abra o Prompt de Comando e rode:

```cmd
ipconfig
```

Procure o `Endereco IPv4`, por exemplo:

```text
192.168.0.50
```

Nos outros computadores, acesse:

```text
http://192.168.0.50:8000
```

Troque `192.168.0.50` pelo IP real do PC servidor.

## 7. Liberar no Firewall do Windows

Se os outros computadores nao conseguirem abrir, libere a porta 8000:

1. Abra `Windows Defender Firewall com Seguranca Avancada`.
2. Va em `Regras de Entrada`.
3. Clique em `Nova Regra`.
4. Escolha `Porta`.
5. Escolha `TCP` e informe `8000`.
6. Marque `Permitir a conexao`.
7. Aplique para redes privadas.
8. Nomeie como `CestaControl`.

## 8. Backup diario

O banco fica em:

```text
data\cestacontrol.db
```

Para criar backup manual, execute:

```text
scripts\backup-db.cmd
```

Os backups ficam na pasta:

```text
backups\
```

Recomendacao: copie a pasta `backups` para OneDrive, Google Drive, pendrive ou outro computador ao fim do dia.

## 9. Rotina de uso

Ao chegar:

1. Ligue o PC servidor.
2. Execute `scripts\start-server.cmd`.
3. Deixe a janela aberta.
4. Os outros PCs acessam pelo navegador.

Ao sair:

1. Avise para ninguem estar cadastrando retirada.
2. Rode `scripts\backup-db.cmd`.
3. Feche o servidor com `Ctrl+C`.
4. Desligue o PC.

## 10. Observacoes importantes

- Nao apague a pasta `data`.
- Nao envie o arquivo `.env` para GitHub.
- Se o IP do PC mudar, os outros computadores precisam acessar pelo novo IP.
- Para evitar mudanca de IP, configure IP fixo no roteador ou no Windows.
