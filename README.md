# Bot de Deploy Discord

Este é um bot do Discord desenvolvido para automatizar o processo de deploy em um servidor remoto utilizando SSH e comandos Docker. Ele é ideal para projetos que necessitam de uma integração rápida e eficiente entre o Git e o servidor VPS.

## Funcionalidades

- Executar `git pull` para atualizar o repositório no servidor.
- Construir imagens Docker com `docker-compose build`.
- Parar e remover contêineres com `docker-compose down`.
- Iniciar os contêineres com `docker-compose up -d`.

## Requisitos

Antes de utilizar este bot, certifique-se de que os seguintes requisitos estão instalados:

- Python 3.8 ou superior.
- Discord.py (biblioteca para interagir com o Discord).
- Paramiko (biblioteca para conexões SSH).
- Acesso ao servidor VPS com chave SSH configurada.

## Configuração

1. Clone este repositório para sua máquina local.
2. Instale as dependências listadas no arquivo `requirements.txt`.
3. Configure as variáveis no arquivo principal:
   - `DISCORD_TOKEN`: Token do bot no Discord.
   - `VPS_IP`: Endereço IP do servidor VPS.
   - `VPS_USER`: Nome de usuário no VPS.
   - `VPS_KEY`: Caminho para a chave SSH.
   - `REPO_PATH`: Caminho para o repositório no servidor.

## Uso

Inicie o bot executando o arquivo principal. No Discord, você pode usar o comando `/deploy` seguido pelo nome da branch (padrão: `main`) para iniciar o processo de deploy.

```bash
python3 bot_deploy.py

---

## Licença
Este projeto está licenciado sob a [MIT License](LICENSE)
