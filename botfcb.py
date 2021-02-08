import discord
from discord import DMChannel
from discord.ext import commands
from discord.utils import get
import time
import asyncio
import os
from unicodedata import normalize
from datetime import datetime
import pyrebase
import random
from datetime import timedelta
import sys

config = {
  "apiKey": "AIzaSyDSNiMyZF_fdprDfs-HE3QI_eHAnnRTdFc",
  "authDomain": "zapper-bot.firebaseapp.com",
  "databaseURL": "https://zapper-bot-default-rtdb.firebaseio.com/",
  "storageBucket": "zapper-bot.appspot.com" 
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix='.', case_insensitive=True,
    intents=intents, help_command=None
)

def hora_atual():
    atual = (datetime.now()).strftime("%H:%M:%S")
    return atual

@bot.event
async def on_ready():
    global tempo_inicial
    tempo_inicial = hora_atual()
    os.system('cls' if os.name == 'nt' else 'clear')   
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name='algum jogo :v'
        )
    )
    user = await bot.fetch_user(341209316663099394)
    mensagem = await DMChannel.fetch_message(user, 798921161873948745)
    await mensagem.edit(content="Bot ativo desde " + datetime.now().strftime("%d/%m, às %H:%M:%S"))
    print(f'tô online, loguei como {bot.user}')

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    comando = normalize('NFKD', message.content.lower()).encode('ASCII', 'ignore').decode('ASCII')
    ctx = message.channel
    if message.author == bot.user:
        return

    if 'pudim' in comando:
        print(
            f'{hora_atual()}: {message.author.name} disse pudim' +
            f' no server {message.guild}, no canal {message.channel}'
        )
        await ctx.send(
            'Epa, tu falou em pudim???'
        )
        url = "http://pudim.com.br"
        embed = discord.Embed(
            title='Clique aqui para ser redirecionado',
            description='Olha seu pudim ae !',
            colour=discord.Colour(0x349cff),
            url=url,
        )
        await ctx.send(
            content=f'Olha que legal, <@{message.author.id}>',
            embed=embed
        )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Por favor passe todos os argumentos requiridos.')
        await ctx.send(f'Digite .help para uma listagem de comandos!')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            f'Perai {ctx.author.mention},' +
            ' você não tem permissão para executar esse comando 🤨'
        )
    if isinstance(error, discord.Forbidden):
        await ctx.send(
            'Oops, não tenho permissão para executar esse comando 😔'
        )
    if isinstance(error, discord.MemberCacheFlags):
        await ctx.send(
            'Não foi possível encontrar este membro :/'
        )

@bot.command()
async def virarApostador(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Apostador')
    if role in ctx.author.roles:
        await ctx.send(f"Oops <@{ctx.author.id}>, parece que tu já é apostador(a)!")
    else:
        print(ctx.author.name + " se tornou apostador")
        await ctx.author.add_roles(role)
        await ctx.send(f"<@{ctx.author.id}> agora é apostador(a)!")

@bot.command(aliases=['limpadb', 'cleandb'])
@commands.is_owner()
async def limpaFirebase(ctx):
    db.child("corsacoins").child(f"{ctx.guild}").set("")
    print(hora_atual())
    

@bot.command(aliases=['iniciadb', 'startdb'])
@commands.has_role("zapper")
async def iniciaFirebase(ctx):
    for member in ctx.guild.members:
        if member.bot:
            continue
        else:
            db.child("corsacoins").child(f"{ctx.guild}").child(f"{member.id}").set("")
    await ctx.send("Servidor configurado no banco de dados Firebase.")

@bot.command(aliases=['ajuda', 'help'])
async def h(ctx):
    await ctx.send("""```diff
! O prefixo do bot é ".", então todas os comandos abaixo devem ser precedidos deste caractere.


#Comandos principais:


+  virarApostador: dá o cargo de Apostador, necessário para usar as corsacoins =)

+  eu/me [cargo "Apostador"]: exibe as informações sobre as suas corsacoins (por enquanto apenas a quantidade k)

+  sobre (usuário): exibe as informações sobre as corsacoins do usuário escolhido

+  rank: exibe os 10 membros com mais corsacoins no server

+  ap/apostar/aposta/jogar (quantidade) [corsacoins suficientes e o cargo de "Apostador"]: escolhe aleatoriamente entre manter igual a sua quantidade de moedas, somar mais a ela ou subtrair dela. Multiplica o valor de entrada do usuário por um valor aleatório entre 0.1 e 2.0, para depois fazer a operação sorteada.

+  lootbox/lb/loot [cargo de apostador]: é a forma de conseguir as primeiras corsacoins. Só pode ser usada a cada 5 minutos.

+  doar/dar (quantidade, usuário) [cargo de apostador]: doa a quantidade desejada para um determinado usuário, mas não é possível doar para si mesmo e nem doar mais do que tu tem.

+  roubar/hack_corsacoins (quantidade, usuário) [cargo de apostador]: tem uma chance de 1 em 3 de sucesso, mas também pode ficar do jeito que está ou tu perder. Quando tu ganha, a quantidade de moedas inserida sai do usuário de destino e vai pra ti, mas quando tu perde, as moedas que tu tentou roubar vão pra vítima e são retiradas de ti. Obs.: não é possível roubar de si mesmo, nem roubar mais do que alguém tem ou mais do que tu tem, pois, se perder, vai ter que pagar o valor que tentou roubar.

+  help/h/ajuda: exibe esta mensagem, contendo os comandos para o bot =)

```""")

@bot.command()
async def rank(ctx):
    cont = 0
    cru = db.child("corsacoins").child(f"{ctx.guild}").get().val()
    embed = discord.Embed(title=f"Ranking de corsacoins do servidor {ctx.guild}", colour=discord.Colour(0xFE2E2E))
    rank = dict(cru)
    def by_coins(e):
        return rank.get(e).get('moedas')
    ranksorted = sorted(rank, key=by_coins, reverse=True)
    for user in ranksorted:
        if cont >= 10:
            break
        else:
            moedas = rank.get(user).get('moedas')
            usuario = await bot.fetch_user(user)
            embed.add_field(name= usuario.display_name, value= moedas, inline=False)
            cont += 1
    await ctx.send(embed=embed)

@bot.command(aliases=['lb', 'loot'])
@commands.has_role("Apostador")
async def lootBox(ctx):
    hora_destino = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('tempo').get().val()
    agora = (datetime.now()).strftime('%m %d %H %M').replace(' ', '')
    moedas_atuais = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').get().val()
    if hora_destino == None or  int(agora) > int(hora_destino):
        possibilidades = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        premio = possibilidades[random.randint(0, 9)]
        await ctx.send("Você ganhou " + str(premio) + " corsacoins")
        if moedas_atuais == None:
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').set(premio)
        else:
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').set(int(moedas_atuais) + premio)
        db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('tempo').set(int(agora) + 5)
        print(
            f'{hora_atual()}: {ctx.author.name} pediu lootBox' +
            f' no server {ctx.guild}, no canal {ctx.channel}'
        )
    else:
        await ctx.send("Oops, calma aí, ainda falta um tempo para você resgatar a próxima lootbox.")

@bot.command(aliases=['roubar'])
@commands.has_role("Apostador")
async def hack_corsacoins(ctx, valor, *, user: discord.Member):
    ladrao = ctx.author
    vitima = user
    moedasladrao = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ladrao.id}').child('moedas').get().val()
    moedasvitima = db.child("corsacoins").child(f"{ctx.guild}").child(f'{vitima.id}').child('moedas').get().val()
    possibilidades = ['perder', 'ganhar', 'igualar']
    decisao = possibilidades[random.randint(0,2)]
    if moedasladrao == None or moedasladrao == 0:
        await ctx.send(f"Pô <@{ladrao.id}>, pra querer roubar precisa pelo menos ter algo né? Vai criar vergonha e ganhar dinheiro com \".lb\"")
    elif moedasvitima == None or moedasvitima == 0:
        await ctx.send(f"Pô <@{ladrao.id}>, pra querer roubar a pessoa precisa pelo menos ter algo né? Vai ajudar ele(a) a conseguir uma graninha pô")
    elif moedasladrao < int(valor):
        await ctx.send(f"<@{ladrao.id}>, tu precisa de mais moedas pra roubar isso tudo de <@{vitima.id}>")
    elif moedasvitima < int(valor):
        await ctx.send(f"<@{ladrao.id}>, a pessoa precisa de mais moedas pra tu roubar isso dela")
    elif ladrao == vitima:
        await ctx.send(f"<@{ladrao.id}>, roubar de si mesmo é no mínimo burrice, né?")
    elif int(valor) < 0:
        await ctx.send(f"<@{ladrao.id}>, pra roubar alguém tem q roubar alguma quantidade maior que zero, né?")
    else:
        try:
            valor = int(valor)
        except:
            await ctx.send('Passe os parâmetros adequadamente. Para essa função só números inteiros são aceitos')
            return
        if decisao == 'perder':
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{ladrao.id}').child('moedas').set(int(moedasladrao) - int(valor))
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{vitima.id}').child('moedas').set(int(moedasvitima) + int(valor))
            await ctx.send(f"Opa <@{ladrao.id}>, não deu de roubar do(a) <@{vitima.id}>, e ele(a) ganhou o que tu tentou roubar...")
        elif decisao == 'ganhar':
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{ladrao.id}').child('moedas').set(int(moedasladrao) + int(valor))
            db.child("corsacoins").child(f"{ctx.guild}").child(f'{vitima.id}').child('moedas').set(int(moedasvitima) - int(valor))
            await ctx.send(f"Parabéns <@{ladrao.id}>, tu conseguiu roubar do(a) <@{vitima.id}>")
        elif decisao == 'igualar':
            await ctx.send(f"É <@{ladrao.id}>, não deu em nada isso aí...")

    
@bot.command(aliases=['ap', 'aposta', 'jogar'])
@commands.has_role("Apostador")
async def apostar(ctx, valor):
    print(
            f'{hora_atual()}: {ctx.author.name} apostou {valor}' +
            f' no server {ctx.guild}, no canal {ctx.channel}'
        )
    decisao = ['soma', 'igual', 'subtrai']
    valores = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    moedas_atuais = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').get().val()
    if valor == "tudo":
        valor = moedas_atuais
    elif valor == "metade" and valor != 1:
        valor = moedas_atuais / 2
    if moedas_atuais == None or moedas_atuais < int(valor) or int(valor) <= 0:
        await ctx.send('Ops, você não tem corsacoins suficientes para apostar.\nUse o comando .lb para ganhar corsacoins e poder apostar!')
    else:
        try:
            valor = int(valor)
        except:
            await ctx.send('Passe os parâmetros adequadamente. Para essa função só números inteiros são aceitos')
            return
        decidido = decisao[random.randint(0, 2)]
        if decidido == 'soma':
            multiplicado = float(valor) * valores[random.randint(0, 19)]
            if multiplicado < 1:
                await ctx.send(f'Não teve sorte nem azar, <@{ctx.author.id}>, ficou com a mesma quantidade de moedas :)\nContinua com ' + str(moedas_atuais) + ' corsacoins')
            else:
                ganhou = moedas_atuais + int(multiplicado)
                db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').set(ganhou)
                await ctx.send(f'Parabéns, <@{ctx.author.id}>! Você ganhou ' + str(int(multiplicado)) + ' corsacoins!\nFicando com ' + str(ganhou) + ' corsacoins')
        elif decidido == 'subtrai':
            multiplicado = float(valor) * valores[random.randint(0, 9)]
            if multiplicado < 1:
                await ctx.send(f'Não teve sorte nem azar, <@{ctx.author.id}>, ficou com a mesma quantidade de moedas :)\nContinua com ' + str(moedas_atuais) + ' corsacoins')
            else:
                ganhou = moedas_atuais - int(multiplicado)
                db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').set(ganhou)
                await ctx.send(f'Oops <@{ctx.author.id}>, você perdeu ' + str(int(multiplicado)) + ' corsacoins...\nFicando com ' + str(ganhou) + ' corsacoins')
        elif decidido == 'igual':
            await ctx.send(f'Não teve sorte nem azar, <@{ctx.author.id}>, ficou com a mesma quantidade de moedas :)\nContinua com ' + str(moedas_atuais) + ' corsacoins')

@bot.command(aliases=['dar'])
@commands.has_role("Apostador")
async def doar(ctx, qnt, *, user: discord.Member):
    moedasdoador = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').get().val()
    moedasreceptor = db.child("corsacoins").child(f"{ctx.guild}").child(f'{user.id}').child('moedas').get().val()
    if moedasdoador == None or moedasdoador == 0 or moedasdoador < int(qnt):
        await ctx.send(f"Não tem como doar mais do que tu tem pra alguém, <@{ctx.author.id}>")
    elif ctx.author == user:
        await ctx.send(f"Não tem como doar pra ti mesmo, <@{ctx.author.id}>")
    elif int(qnt) < 0:
        await ctx.send(f"Não tem como doar uma quantidade negativa, <@{ctx.author.id}>, se é pra roubar de alguém, usa o .roubar ué...")
    else:
        try:
            qnt = int(qnt)
        except:
            await ctx.send('Passe os parâmetros adequadamente. Para essa função só números inteiros são aceitos')
            return
        db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').set(int(moedasdoador) - int(qnt))
        db.child("corsacoins").child(f"{ctx.guild}").child(f'{user.id}').child('moedas').set(int(moedasreceptor) + int(qnt))
        await ctx.send(f"<@{ctx.author.id}> doou {int(qnt)} para <@{user.id}>")
        print(f"{ctx.author.name} doou {int(qnt)} para {user.name}")

@bot.command(aliases=['me'])
@commands.has_role('Apostador')
async def eu(ctx):
    moedas_atuais = db.child("corsacoins").child(f"{ctx.guild}").child(f'{ctx.author.id}').child('moedas').get().val()
    corsas = ["https://www.cacador.net/fotos/noticias18/1204DSC_0979_g.JPG", "https://zh.rbsdirect.com.br/imagesrc/23388046.jpg?w=700", "https://i.ytimg.com/vi/dhNyAaIDq5c/maxresdefault.jpg"]
    if moedas_atuais == None:
        moedas_atuais = 0
    embed = discord.Embed(title=f"Corsacoins de {ctx.author}", colour=discord.Colour(0xFE2E2E))

    embed.set_thumbnail(url=corsas[random.randint(0, 2)])
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
    embed.add_field(name= "Corsacoins", value=str(ctx.author.name) + " possui " + str(moedas_atuais) + " corsacoins")

    await ctx.send(content="Aqui " + ctx.author.name + ", cuida bem dessa grana, hein!", embed=embed)

@bot.command()
async def sobre(ctx, user: discord.Member):
    moedas_atuais = db.child("corsacoins").child(f"{ctx.guild}").child(f'{user.id}').child('moedas').get().val()
    if moedas_atuais == None:
        moedas_atuais = 0    
    corsas = ["https://www.cacador.net/fotos/noticias18/1204DSC_0979_g.JPG", "https://zh.rbsdirect.com.br/imagesrc/23388046.jpg?w=700", "https://i.ytimg.com/vi/dhNyAaIDq5c/maxresdefault.jpg"]

    embed = discord.Embed(title=f"Corsacoins de {user}", colour=discord.Colour(0xFE2E2E))

    embed.set_thumbnail(url=corsas[random.randint(0, 2)])
    embed.set_author(name=user.name, icon_url=user.avatar_url)
    embed.add_field(name= "Corsacoins", value=str(user.name) + " possui " + str(moedas_atuais) + " corsacoins")

    await ctx.send(content="Aqui <@" + str(ctx.author.id) + ">, as informações sobre " + user.name, embed=embed)

@bot.command(aliases=["t"])
@commands.is_owner()
async def teste(ctx):
    role = discord.utils.get(ctx.guild.roles, name='Apostador')
    print(role)
    print(dir(ctx.author))
    for roles in ctx.author.roles:
        print(roles)


@commands.is_owner()
@bot.command()
async def atualizar(ctx):
    await ctx.message.delete()
    os.chdir('..')
    os.system('sudo rm -R Zapper-Bot')
    os.system(
        'git clone https://github.com/Zapper0/Zapper-bot.git'
    )
    os.chdir('Zapper-Bot')
    os.system('clear')
    os.system('python3 botfcb.py')
    quit()

bot.run("Nzc5MzM3MjcxMDU1NzQ1MDI1.X7fEZA.3SLth7ufSMICvS9mo5zBtNhF_Ys")
