import discord, asyncio, random, os, sqlite3, json, random, datetime
from discord import Color
from discord.ext import commands, tasks
from discord.utils import get

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='%', description=description, intents=intents)
bot.remove_command("help")

#База данных
connection = sqlite3.connect("server.db")
cursor = connection.cursor()

t_get_slave_role = 1350857825622032496 #Роль - Рабовладелец
t_slave_role = 1350857506934489128 #Роль - раб
t_clear_role = 1158012500432924693 #Роль - Свобоный человек
chanel = 1152899806570754120

banned = []

       

@bot.event
async def on_ready():
    #Если бот зашел в сеть
    earning_f.start()
    channel = bot.get_channel(chanel) # ID Канала где игра
    # БД
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                   name TEXT, 
                   id INT, 
                   cash BIGINT,
                   cost BIGINT, 
                   earning BIGINT,
                   updates BIGINT
                )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
                   name TEXT, 
                   id INT, 
                   cost BIGINT, 
                   earning BIGINT,
                   updates BIGINT
                )""")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS slaves (
                   name_slave TEXT, 
                   id_slave INT,
                   cost BIGINT, 
                   earning BIGINT,
                   updates BIGINT,
                   name_slaveget TEXT, 
                   id_slaveget INT
                )""")

    for guild in bot.guilds:
        for member in guild.members:
            if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                cost = random.randint(20, 50)
                earning = random.randint(1, 5)
                cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, {cost}, {earning}, 300)")
            else:
                pass
    
    connection.commit()
    print("Бот законектился к БД")
    # БД

    print(f'Бот {bot.user} (ID: {bot.user.id}), готов к работе!')
    print('------')

    emb = discord.Embed(title="Slaves снова в работе", color=(1))
    emb.add_field(name="Игра 'Рабство' возобновляется", value="Чтобы посмотреть все команды напиши - %help\n Спронсировать бедного разраба - https://www.donationalerts.com/r/k4min", inline=False)
    await channel.send(embed=emb)
    await channel.send("https://tenor.com/view/bfp-black-flag-pirates-work-get-back-to-work-back-to-work-gif-6618814053542253714")

@bot.event
async def on_member_join(member):
    clear_role = discord.utils.get(member.guild.roles, id=t_clear_role) #Роль - Свобоный человек
    await member.add_roles(clear_role)
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cost = random.randint(20, 50)
        earning = random.randint(5, 20)
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, {cost}, {earning}, 300)")
    else:
        pass


@bot.command()
@commands.has_role(t_get_slave_role)
async def info(ctx, member: discord.Member = None):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        # Инфа о человеке
        embed = discord.Embed(title = f"Информация о {ctx.author}", colour=discord.Color.yellow())
        embed.add_field(name="===============================", value="", inline=False)
        embed.add_field(name=f"""Баланс : **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]}** :coin:""", value="", inline=False)
        embed.add_field(name=f"============= Рабы  ============", value="")
        for row in cursor.execute(f"SELECT name_slave, earning, updates FROM slaves WHERE id_slaveget = {ctx.author.id}"):
            embed.add_field(name=f"Раб : {row[0]}", value=f"Заработок : {row[1]} :coin:/мин\n Апдейт : {row[2]} :coin:\n ===============================", inline=False)

        await channel.send(embed=embed)


@bot.command()
@commands.has_role(t_clear_role)
async def get_role(ctx):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        #Рандомно выдаём роль

        get_slave_role = discord.utils.get(ctx.author.guild.roles, id=t_get_slave_role) #Роль - Рабовладелец
        slave_role = discord.utils.get(ctx.author.guild.roles, id=t_slave_role) #Роль - раб
        clear_role = discord.utils.get(ctx.author.guild.roles, id=t_clear_role) #Роль - Свобоный человек

        if random.random() < 0.3:
            await channel.send(embed=discord.Embed(description=f'{ctx.author} - Рабовладелец', colour=discord.Color.green()))
            await ctx.author.add_roles(get_slave_role)
            await ctx.author.remove_roles(clear_role)
            cursor.execute(f"UPDATE users SET cash = cash + 50 WHERE id = {ctx.author.id}")
            cursor.execute(f"DELETE FROM shop WHERE id = {ctx.author.id}")
            connection.commit()
        else:
            await channel.send(embed=discord.Embed(description=f'{ctx.author} - раб', colour=discord.Color.red()))
            await ctx.author.add_roles(slave_role)
            await ctx.author.remove_roles(clear_role)
            cursor.execute(f"UPDATE users SET cash = 0 WHERE id = {ctx.author.id}")
            cursor.execute(f"INSERT INTO shop VALUES ('{ctx.author}', {ctx.author.id}, {cursor.execute('SELECT cost FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}, {cursor.execute('SELECT earning FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]}, {cursor.execute('SELECT updates FROM users WHERE id = {}'.format(ctx.author.id)).fetchone()[0]})")
            # Переносим в юзерс
            cost = random.randint(20, 50)
            cursor.execute("UPDATE users SET updates = {0} WHERE id = {1}".format(cursor.execute(f'SELECT updates FROM shop WHERE id = {ctx.author.id}').fetchone()[0], ctx.author.id))
            cursor.execute(f"UPDATE users SET cost = {cost} WHERE id = {ctx.author.id}")
            cursor.execute("UPDATE users SET earning = {0} WHERE id = {1}".format(cursor.execute(f'SELECT earning FROM shop WHERE id = {ctx.author.id}').fetchone()[0], ctx.author.id))
            connection.commit()
    

@bot.command()
@commands.has_role(t_get_slave_role)
async def shop(ctx):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        #Магазин
        embed = discord.Embed(title = "Магазин рабов", colour=discord.Color.yellow())
        embed.add_field(name="===============================", value="", inline=False)
        
        cursor.execute("SELECT * FROM shop")
        for shop in cursor.fetchall():
            for row in cursor.execute(f"SELECT name, cost, earning FROM shop WHERE id = {shop[1]}"):
                embed.add_field(name=f"Раб : {row[0]}", value=f"Стоимость : {row[1]} :coin:\n Заработок : {row[2]} :coin:/мин\n ===============================", inline=False)
        connection.commit()
        await channel.send(embed=embed)

@bot.command()
@commands.has_role(t_get_slave_role)
async def buy(ctx, member: discord.Member):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        #Покупка
        if cursor.execute("SELECT cost FROM shop WHERE id = {}".format(member.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await channel.send(f"**{ctx.author}**, у вас недостаточно монет чтобы купить раба")
        else:
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE id = {}".format(member.id)).fetchone()[0], ctx.author.id))
            cursor.execute(f"INSERT INTO slaves VALUES ('{member}', {member.id}, {cursor.execute('SELECT cost FROM shop WHERE id = {}'.format(member.id)).fetchone()[0]}, {cursor.execute('SELECT earning FROM shop WHERE id = {}'.format(member.id)).fetchone()[0]}, {cursor.execute('SELECT updates FROM shop WHERE id = {}'.format(member.id)).fetchone()[0]}, '{ctx.author}', {ctx.author.id})")
            cursor.execute(f"DELETE FROM shop WHERE id = {member.id}")
            await channel.send(f"**{ctx.author}**, успешно купил **{member}**")
        connection.commit()

@tasks.loop(seconds=60)
async def earning_f():
    print("Рабовладельцам выданы деньги выданы")

    cursor.execute("SELECT * FROM slaves")
    for slaves in cursor.fetchall():
        for row in cursor.execute(f"SELECT earning, id_slaveget FROM slaves WHERE id_slave = {slaves[1]}"): #
            cursor.execute(f"UPDATE users SET cash = cash + {row[0]} WHERE id = {row[1]}")

    connection.commit()

@commands.cooldown(1, 60*60, commands.BucketType.user)
@bot.command()
@commands.has_role(t_slave_role)
async def run(ctx):
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        channel = bot.get_channel(chanel) # ID Канала где игра

        slave_role = discord.utils.get(ctx.author.guild.roles, id=t_slave_role) #Роль - раб
        clear_role = discord.utils.get(ctx.author.guild.roles, id=t_clear_role) #Роль - Свобоный человек
        
        cursor.execute("SELECT * FROM shop")
        
        if random.random() < 0.3:
            await channel.send(embed=discord.Embed(description=f'**{ctx.author}** успешно сбежал!', colour=discord.Color.green()))
            await ctx.author.add_roles(clear_role)
            await ctx.author.remove_roles(slave_role)
            cost = random.randint(20, 50)
            earning = random.randint(1, 5)
            for row in cursor.execute(f"SELECT id_slaveget FROM slaves WHERE id_slave = {ctx.author.id}"):
                cursor.execute(f"UPDATE users SET cash = cash / 2 WHERE id = {row[0]}")
                cursor.execute(f"UPDATE users SET cost = {cost} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE users SET earning = earning / 2 WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE users SET updates = updates * 2 WHERE id = {ctx.author.id}")
                cursor.execute(f"DELETE FROM slaves WHERE id_slave = {ctx.author.id}")
        else:
            await channel.send(embed=discord.Embed(description=f'**{ctx.author}** твой побег заметили...', colour=discord.Color.red()))
            for row in cursor.execute(f"SELECT id_slaveget, updates FROM slaves WHERE id_slave = {ctx.author.id}"):
                cursor.execute(f"UPDATE users SET cash = cash + {row[1]} WHERE id = {row[0]}")
                cursor.execute(f"UPDATE slaves SET updates = updates / 2 WHERE id_slave = {ctx.author.id}")
                cursor.execute(f"UPDATE slaves SET cost = cost / 2 WHERE id_slave = {ctx.author.id}")
                cursor.execute(f"UPDATE slaves SET earning = earning * 2 WHERE id_slave = {ctx.author.id}")
                # Переносим в юзерс
                cursor.execute("UPDATE users SET updates = {0} WHERE id = {1}".format(cursor.execute(f'SELECT updates FROM slaves WHERE id_slave = {ctx.author.id}').fetchone()[0], ctx.author.id))
                cursor.execute("UPDATE users SET cost = {0} WHERE id = {1}".format(cursor.execute(f'SELECT cost FROM slaves WHERE id_slave = {ctx.author.id}').fetchone()[0], ctx.author.id))
                cursor.execute("UPDATE users SET earning = {0} WHERE id = {1}".format(cursor.execute(f'SELECT earning FROM slaves WHERE id_slave = {ctx.author.id}').fetchone()[0], ctx.author.id))
    connection.commit()

@bot.event
@commands.has_role(t_slave_role)
async def on_command_error(ctx, error):
    channel = bot.get_channel(chanel) # ID Канала где игра
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
        await channel.send(embed=discord.Embed(description=f'**{ctx.author}**, ты можешь сбежать снова через **{retry_after}**', colour=discord.Color.red()))

@commands.cooldown(1, 10, commands.BucketType.user)
@bot.command()
@commands.has_role(t_slave_role)
async def rising(ctx):
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        channel = bot.get_channel(chanel) # ID Канала где игра
        slave_role = discord.utils.get(ctx.guild.roles, id=t_slave_role) #Роль - раб
        clear_role = discord.utils.get(ctx.guild.roles, id=t_clear_role) #Роль - Свобоный человек
        get_slave_role = discord.utils.get(ctx.guild.roles, id=t_get_slave_role) #Роль - Рабовладелец

        if random.random() < 0.9:
            await channel.send(embed=discord.Embed(description=f'Восстание прошло успешно!', colour=discord.Color.green()))
            cursor.execute("SELECT * FROM slaves")
            for slaves in cursor.fetchall():
                for row in cursor.execute(f"SELECT id_slaveget, name_slaveget FROM slaves WHERE id_slave = {slaves[1]}"):
                    print(slaves[0], slaves[1], row[1], row[0])
                    cursor.execute(f"UPDATE users SET cash = cash / 5 WHERE id = {row[0]}")
                    cursor.execute(f"UPDATE users SET earning = earning / 5 WHERE id = {slaves[1]}")
                    cursor.execute(f"UPDATE users SET updates = updates * 5 WHERE id = {slaves[1]}")
                    await slaves[0].add_roles(clear_role) #РОЛИ НЕ СНИМАЮТСЯ
                    await row[1].add_roles(clear_role)
                    await slaves[0].remove_roles(slave_role)
                    await row[1].remove_roles(get_slave_role)
                    print(slaves[0], slaves[1], row[1], row[0])
                    cursor.execute(f"DELETE FROM slaves WHERE id_slave = {slaves[1]}")        
        else:
            await channel.send(embed=discord.Embed(description=f'**{ctx.author}**, что-то пошло не по плану', colour=discord.Color.red()))
        connection.commit()

@bot.event
@commands.has_role(t_slave_role)
async def on_command_error(ctx, error):
    channel = bot.get_channel(chanel) # ID Канала где игра
    if isinstance(error, commands.CommandOnCooldown):
        retry_after = str(datetime.timedelta(seconds=error.retry_after)).split('.')[0]
        await channel.send(embed=discord.Embed(description=f'**{ctx.author}**, восстание можно сделать через **{retry_after}**', colour=discord.Color.red()))

@bot.command()
@commands.has_role(t_get_slave_role)
async def update(ctx, member: discord.Member):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        if cursor.execute(f"SELECT updates FROM slaves WHERE id_slave = {member.id}").fetchone()[0] > cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()[0]:
            await channel.send(f"**{ctx.author}**, у вас недостаточно монет чтобы прокачать раба")
        else:
            for row in cursor.execute(f"SELECT cost, earning, updates FROM slaves WHERE id_slave = {member.id}"):
                cursor.execute(f"UPDATE users SET cash = cash - {row[2]} WHERE id = {ctx.author.id}")
                cursor.execute(f"UPDATE slaves SET updates = updates * 2 WHERE id_slave = {member.id}")
                cursor.execute(f"UPDATE slaves SET cost = cost * 2 WHERE id_slave = {member.id}")
                cursor.execute(f"UPDATE slaves SET earning = earning * 2 WHERE id_slave = {member.id}")
                # Переносим в юзерс
                cursor.execute("UPDATE users SET updates = {0} WHERE id = {1}".format(cursor.execute(f'SELECT updates FROM slaves WHERE id_slave = {member.id}').fetchone()[0], member.id))
                cursor.execute("UPDATE users SET cost = {0} WHERE id = {1}".format(cursor.execute(f'SELECT cost FROM slaves WHERE id_slave = {member.id}').fetchone()[0], member.id))
                cursor.execute("UPDATE users SET earning = {0} WHERE id = {1}".format(cursor.execute(f'SELECT earning FROM slaves WHERE id_slave = {member.id}').fetchone()[0], member.id))
            connection.commit()  
            await channel.send(f"**{ctx.author}**, успешно прокачал **{member}**")


@bot.command()
async def clear(ctx, amount = 100):
    """Очистить чат"""
    await ctx.channel.purge(limit=amount)
    

@bot.command()
async def help(ctx):
    channel = bot.get_channel(chanel) # ID Канала где игра
    # Проверка на бан
    if ctx.author.id in banned:
        await channel.send(f"**{ctx.author}**, ты в бане")
    else:
        #Help
        embed = discord.Embed(title="Комманды Slaves", color=(1))
        embed.add_field(name="================ Общие команды ============", value="")
        embed.add_field(name="%help", value="Выводит информацию о командах", inline=False)
        embed.add_field(name="%info", value="Информация о игроке", inline=False)
        embed.add_field(name="%get_role", value="Выдает рандомную роль (Рабовладелец / раб)", inline=False)

        embed.add_field(name="================= Команды раба =============", value="")
        embed.add_field(name="%run", value="Сбежать от Рабовладельца", inline=False)
        embed.add_field(name="%rising", value="Поднять восстание рабов (В РАЗРАБОТКЕ)", inline=False)

        embed.add_field(name="=========== Команды Рабовладельца =========", value="")
        embed.add_field(name="%buy @имяраба", value="Купить раба", inline=False)
        embed.add_field(name="%shop", value="Магазин рабов", inline=False)
        embed.add_field(name="%update @имяраба", value="Улучшает раба", inline=False)
        await channel.send(embed=embed)


bot.run("TOKEN")
