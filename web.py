import os
import requests
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route("/")
def index():
    return "✅ Bot is Running!"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    ip = request.remote_addr
    if not code:
        return "認証失敗"

    # OAuth2 トークン取得
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    tokens = r.json()
    access_token = tokens["access_token"]

    # ユーザー情報取得
    user_info = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    user_id = user_info["id"]

    # Supabase に保存
    app.supabase.save_user(user_info, ip)

    # ロール付与
    guild = app.bot.get_guild(app.GUILD_ID)
    member = guild.get_member(int(user_id))
    if member:
        role = guild.get_role(app.ROLE_ID)
        app.bot.loop.create_task(member.add_roles(role))

    # 認証成功ページ表示
    return render_template("success.html",
                           username=f'{user_info["username"]}#{user_info["discriminator"]}',
                           useravater=f'https://cdn.discordapp.com/avatars/{user_info["id"]}/{user_info["avatar"]}.png')
