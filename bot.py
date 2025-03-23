import discord
from discord.ext import commands
import paramiko


DISCORD_TOKEN = "token"
VPS_IP = "localhost"
VPS_USER = "ubuntu"
VPS_KEY = "path"
REPO_PATH = "path"

# Configurar o bot com intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}!')

async def send_long_message(ctx, content):

    while content:
        if len(content) > 1900:
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

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_IP, username=VPS_USER, key_filename=VPS_KEY)


        await ctx.send("Executando `git pull`...")
        comando_git = f"cd {REPO_PATH} && git pull origin {branch}"
        stdin, stdout, stderr = ssh.exec_command(comando_git)
        output_git = stdout.read().decode().strip()
        error_git = stderr.read().decode().strip()


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


        await ctx.send("Reconstruindo as imagens com `docker-compose build`...")
        comando_build = f"cd {REPO_PATH} && sudo docker-compose build"
        stdin, stdout, stderr = ssh.exec_command(comando_build)
        output_build = stdout.read().decode().strip()
        error_build = stderr.read().decode().strip()


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


        await ctx.send("Parando e removendo os contêineres com `docker-compose down`...")
        comando_down = f"cd {REPO_PATH} && sudo docker-compose down"
        stdin, stdout, stderr = ssh.exec_command(comando_down)
        output_down = stdout.read().decode().strip()
        error_down = stderr.read().decode().strip()


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


        await ctx.send("Iniciando os contêineres com `docker-compose up -d`...")
        comando_up = f"cd {REPO_PATH} && sudo docker-compose up -d"
        stdin, stdout, stderr = ssh.exec_command(comando_up)
        output_up = stdout.read().decode().strip()
        error_up = stderr.read().decode().strip()


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


bot.run(DISCORD_TOKEN)

