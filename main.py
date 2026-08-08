import discord #Importe de librerias de discord
import os
from discord import app_commands #Importe de funcion de app_commands para tabulaciones de discord
from discord.ext import commands #Importe la funcion commands de discord.ext
import yt_dlp #Importe para reproductor de Youtube
import requests #Importe de libreria request para realizar solicitudes HTTP por JSON
from dotenv import load_dotenv #Importe de mi archivo my_secrets.py

load_dotenv()
# TOKEN del BOT -- Esto esta en .env
TOKEN=os.getenv("DISCORD_TOKEN")

# Diccionario para comando $f
family={"juli":"https://klipy.com/gifs/ruurd-juli","delfi":"https://klipy.com/gifs/freaky-dolphin",
"patri":"🦆", "eri":"https://klipy.com/gifs/erika-erika-vikman",
"merch":"https://klipy.com/gifs/mercedes-mercedes-benz-6", "elba":"La goti", 
"claudia":"hermosura", "mari":"💝",
"sofi":"https://klipy.com/gifs/ilysofi-sofiisthebest-2","mica":"🍒",
"lulu":"https://klipy.com/gifs/lulu-team-fight-tactics","analia":"👄🍆",
"malvi":"https://klipy.com/gifs/islas-malvinas-son-argentinas",
"andre":"https://klipy.com/gifs/love-love-u-10", "barbi":"https://klipy.com/gifs/te-20"}

# seleccionando varias lineas y apretanto CNTL+k+c las comentas todas en Visual Studio Code

intents= discord.Intents.default()
intents.message_content = True

#Prefijo y llamados 
bot = commands.Bot(command_prefix='$', intents=intents)

# Configuración de lista de canciones iniciando vacia
queue = []
# Configuración de yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True
}

# ======COMANDOS CLASICOS CON PREFIJO "$"=======
# Comando PokeBusqueda
@bot.command()
async def poke(ctx, arg):
    try:
        pokemon = arg.split(" ",1)[0].lower() #recibo un arg, split lo divide cada espacio (" ") un maximo de 1 separacion (,1) y me quedo con la primer pisicion ([0]), además lo transformo en minuscula (.lower())
        result = requests.get("https://pokeapi.co/api/v2/pokemon/"+pokemon) #Guardo en result la solicitud al buscador de Pokeapi con el pokemon ingresado 
        if result.text == "Not Found":
            await ctx.send("Ese Pokemon no existe pa")
        else:
            image_url = result.json()['sprites']['front_default'] #Guardo el json default del sprite (basicamente la URL de la foto del front del pokemon)
            print(image_url) #Lo muestro por terminal para seguridad
            await ctx.send(image_url) #Lo mando por discord
    except Exception as e:
        print("Error: ", e)

# Comando para repetir el mensaje
@bot.command(name="t")
async def test(ctx, *arg):
    respuesta=' '.join(arg)
    await ctx.send(respuesta)

# Comando de las Familys
@bot.command(name="f")
async def bardini(ctx, arg):
    try:
        respuesta=family.get(arg.lower())
        if respuesta is not None:
            await ctx.send(respuesta)
        else:
            await ctx.send("Tiraste cualquiera")
    except Exception as e:
        print("Error: ", e)

# Comando para conectar para poner musica, skipear y detener el bot

def play_next(ctx):
    if queue:
        url = queue.pop(0)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            source = discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
            ctx.voice_client.play(source, after=lambda e: bot.loop.create_task(play_next(ctx)))
        bot.loop.create_task(ctx.send(f"Ahora escuchas: {info['title']}"))
    else:
        bot.loop.create_task(ctx.send("No hay musicas en la lista de reproduccion"))

@bot.command(name="play")
async def play(ctx, url:str):
    # Verificacion del usuario conectado en un canal
    if ctx.author.voice is None:
        await ctx.send("Hay que estar conectado en un canal para reproducir musica")
        return

    channel = ctx.author.voice.channel

    # Conecto al bot al canal
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    # Verifico que no este sonando nada
    if ctx.voice_client.is_playing():
        queue.append(url)
        await ctx.send("Canción añadida a la lista")
    else:
        # Extracción del audio de Youtube
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            # Reproduccion del audio con FFmpeg
            ctx.voice_client.stop() # Se detiene cualquier reproduccion previa
            source = discord.FFmpegPCMAudio(audio_url)
            ctx.voice_client.play(source)
        await ctx.send(f"Estas escuchando: {info['title']}")

# Comando para skipear la cancion
@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        play_next(ctx)
        await ctx.send("Cancion skipeada")
    else:
        await ctx.send("No hay cancion para skipear")

# Comando para detener la musica y desconectarse
@bot.command(name="stop")
async def stop(ctx):
    if ctx.voice_client:
        queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Musica finalizada, lista vaciada y ahora me retiro")

# Comando para ver la lista
@bot.command(name="lista")
async def lista(ctx):
    if not queue:
        await ctx.send("La lista esta vacia")
    else:
        #Muestro las canciones en orden
        mensaje="**La Lista de Reproduccion **\n"
        for i, url in enumerate(queue, start=1):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Titulo desconocido')
            except Exception:
                title = "Error al obtener el titulo"
            mensaje += f"{i}. {title}\n"
        await ctx.send(mensaje)

# Comando para remover canciones de la lista
@bot.command(name="rm")
async def remove(ctx, index: int):
    if not queue:
        await ctx.send("No hay musicas en lista de reproduccion")
        return
    if index < 1 or index > len(queue):
        await ctx.send(f"Indice invalido. Usa un numero de 1 a {len(queue)}.")
        return

    # Eleminacion de la cancion
    url = queue.pop(index -1)
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('tittle', 'Titulo desconocido')
    except Exception:
        title = "Titulo desconocido"

    await ctx.send(f"Titulo: {title} eliminado")

# Limpieza de la lista completa (sin tocar la cancion en repro)
@bot.command(name="cl")
async def clear(ctx):
    if not queue:
        await ctx.send("No hay lista que vaciar")
        return
    else:
        queue.clear()
        # if ctx.voice_client and ctx.voice_client.is_playing(): #Estas 2 lineas peremiten detener la musica en reproduccion además de vaciar, por ahora no se usa
        #     ctx.voice_client.stop()
        await ctx.send("Lista vacia")
# ======COMANDOS AUTOCOMPLETADO CON PREFIJO "/"=======

# Funcion para el autocompletado para family
async def family_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    options = []
    # Filtro las llaves del family según el usuario tipea
    for key in family.keys():
        if not current or current.lower() in key.lower():
            options.append(app_commands.Choice(name=key, value=key))
    # Maximo de sugerencias permitidas por Discord
    return options[:25]

@bot.tree.command(name="f", description="Le das a...")
@app_commands.autocomplete(arg=family_autocomplete) #Vinculo el argumento "arg"
async def bardini(interaction: discord.Interaction, arg:str):
    # Para slash se usa discord.Interaction en lugar de CTX
    try:
        respuesta=family.get(arg.lower())
        if respuesta is not None:
            await interaction.response.send_message(respuesta)
        else:
            await interaction.response.send_message("Tiraste cualquiera")
    except Exception as e:
        print("Error :", e)

# -----EVENTOS-----
@bot.event
async def on_ready():
    print(f"Hola soy {bot.user}")
    print("yt-dlp funciona")

# -----ERRORES DE FUNCIONES-----
@poke.error
async def error_type(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Tenes que ingresar un Pokemon pa")

@bardini.error
async def error_type(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Tenes que ingresar un nombre papa")

#@bot.command()
#async def limpiar(ctx):
    #await ctx.channel.purge() #Funcion que limpia todo el canal
    #await ctx.send("Se eliminaron todos los mensajes", delete_after=3) #Envia un mensaje y 3 seg despues lo borra

bot.run(TOKEN) #Ejecucion
