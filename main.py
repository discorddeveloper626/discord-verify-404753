import os
import discord
from discord import app_commands
from discord.ext import commands
import supabase
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
PASSWORD = "0626094"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="button", description="認証ボタンを送信")
async def button(interaction: discord.Interaction, title: str, description: str):
    embed = discord.Embed(title=title, description=description, color=0x5865F2)
    view = discord.ui.View()
    button = discord.ui.Button(
        label="✅ Verify : 認証",
        url=os.getenv("REDIRECT_URI")
    )
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="user-data", description="ユーザーデータ取得 (管理者限定)")
async def userdata(interaction: discord.Interaction, user: str, password: str):
    if password != PASSWORD:
        return await interaction.response.send_message("Error: パスワードが違います", ephemeral=True)

    data = supabase.get_user(user)
    if not data:
        return await interaction.response.send_message("Error: ユーザーデータが見つかりません")

    embed = discord.Embed(title=f"{user} のデータ", color=0x2ecc71)
    embed.add_field(name="ID", value=data.get("id"), inline=False)
    embed.add_field(name="Email", value=data.get("email"), inline=False)
    embed.add_field(name="IP", value=data.get("ip"), inline=False)
    embed.add_field(name="時刻", value=data.get("timestamp"), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

from web import app as flask_app
def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()
bot.run(TOKEN)
