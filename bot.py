import discord
from discord.ext import commands
import paramiko

# Configurações
DISCORD_TOKEN = "MTM1MzE0MDIzNzM4Mjk3NTU1OQ.GvzmHc.LyFDm285izDG23aQH0hR7WTyxAu38WPHez49J0"  # Substitua pelo token do bot
VPS_IP = "localhost"  # Se o repositório está na mesma VPS, use "localhost"
VPS_USER = "ubuntu"  # Substitua pelo seu usuário na VPS
VPS_KEY = "/home/ubuntu/deploy-bot/ssh-key-2025-03-19.key"  # Caminho para sua chave SSH (ajuste conforme necessário)
REPO_PATH = "/home/ubuntu/cerberus-api"  # Caminho do repositório na VPS

# Configurar o bot com intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}!')

async def send_long_message(ctx, content):
    # Dividir a mensagem em partes menores que 2000 caracteres
    while content:
        if len(content) > 1900:  # Deixar margem para formatação
            split_point = content[:1900].rfind('\n')
            if split_point == -1:
                split_point = 1900
            await ctx.send(content[:split_point])
            content = content[split_point:].strip()
        else:
            await ctx.send(content)
            break

@bot.command()
async def deploy(ctx, branch="main"):
    await ctx.send(f"Iniciando deploy da branch `{branch}`...")

    try:
        # Conectar via SSH (mesmo que seja localhost, para manter a consistência)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, username=VPS_USER, key_filename=VPS_KEY)

        # Passo 1: Executar git pull
        await ctx.send("Executando `git pull`...")
        comando_git = f"cd {REPO_PATH} && git pull origin {branch}"
        stdin, stdout, stderr = ssh.exec_command(comando_git)
        output_git = stdout.read().decode().strip()
        error_git = stderr.read().decode().strip()

        # Exibir o log do git pull
        git_log = ""
        if output_git:
            git_log += f"Saída do `git pull`:\n```\n{output_git}\n```"
        if error_git:
            git_log += f"\nErros do `git pull`:\n```\n{error_git}\n```"

        if error_git and "error" in error_git.lower():
            await ctx.send(f"❌ Erro ao executar `git pull` para a branch `{branch}`!")
            await send_long_message(ctx, git_log)
            ssh.close()
            return

        await ctx.send(f"✅ `git pull` concluído para a branch `{branch}`!")
        await send_long_message(ctx, git_log)

        # Passo 2: Reconstruir as imagens com docker-compose build
        await ctx.send("Reconstruindo as imagens com `docker-compose build`...")
        comando_build = f"cd {REPO_PATH} && sudo docker-compose build"
        stdin, stdout, stderr = ssh.exec_command(comando_build)
        output_build = stdout.read().decode().strip()
        error_build = stderr.read().decode().strip()

        # Exibir o log do docker-compose build
        build_log = ""
        if output_build:
            build_log += f"Saída do `docker-compose build`:\n```\n{output_build}\n```"
        if error_build:
            build_log += f"\nErros do `docker-compose build`:\n```\n{error_build}\n```"

        if error_build and "error" in error_build.lower():
            await ctx.send(f"❌ Erro ao executar `docker-compose build`!")
            await send_long_message(ctx, build_log)
            ssh.close()
            return

        await ctx.send("✅ Imagens reconstruídas com sucesso!")
        await send_long_message(ctx, build_log)

        # Passo 3: Parar e remover os contêineres com docker-compose down
        await ctx.send("Parando e removendo os contêineres com `docker-compose down`...")
        comando_down = f"cd {REPO_PATH} && sudo docker-compose down"
        stdin, stdout, stderr = ssh.exec_command(comando_down)
        output_down = stdout.read().decode().strip()
        error_down = stderr.read().decode().strip()

        # Exibir o log do docker-compose down
        down_log = ""
        if output_down:
            down_log += f"Saída do `docker-compose down`:\n```\n{output_down}\n```"
        if error_down:
            down_log += f"\nErros do `docker-compose down`:\n```\n{error_down}\n```"

        if error_down and "error" in error_down.lower():
            await ctx.send(f"❌ Erro ao executar `docker-compose down`!")
            await send_long_message(ctx, down_log)
            ssh.close()
            return

        await ctx.send("✅ Contêineres parados e removidos com sucesso!")
        await send_long_message(ctx, down_log)

        # Passo 4: Iniciar os contêineres com docker-compose up -d
        await ctx.send("Iniciando os contêineres com `docker-compose up -d`...")
        comando_up = f"cd {REPO_PATH} && sudo docker-compose up -d"
        stdin, stdout, stderr = ssh.exec_command(comando_up)
        output_up = stdout.read().decode().strip()
        error_up = stderr.read().decode().strip()

        # Exibir o log do docker-compose up
        up_log = ""
        if output_up:
            up_log += f"Saída do `docker-compose up`:\n```\n{output_up}\n```"
        if error_up:
            up_log += f"\nErros do `docker-compose up`:\n```\n{error_up}\n```"

        if error_up and "error" in error_up.lower():
            await ctx.send(f"❌ Erro ao iniciar os contêineres com `docker-compose up`!")
            await send_long_message(ctx, up_log)
            ssh.close()
            return

        await ctx.send(f"✅ Deploy concluído com sucesso! Contêineres iniciados para a branch `{branch}`!")
        await send_long_message(ctx, up_log)

        ssh.close()

    except Exception as e:
        await ctx.send(f"❌ Falha no deploy da branch `{branch}`: {str(e)}")

# Iniciar o bot
bot.run(DISCORD_TOKEN)

