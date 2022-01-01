import json, discord, sqlite3, random, time, asyncio

config = json.loads(open("config.json", "r", encoding="utf-8").read())

client = discord.Client()

현재회차 = 0
홀 = [

]
짝 = [

]
회차목록 = [

]

second = config["second"]

def gen_code(amount):
    code = []
    for _ in range(amount):
        code.append(random.choice("qazwsxedcrfvtgbyhnujmikolp1234567890"))
    return "".join(code)

@client.event
async def on_message(message):
    global 현재회차
    global 홀
    global 짝
    global 회차목록
    global second
    config = json.loads(open("config.json", "r", encoding="utf-8").read())
    command_prefix = config["command_prefix"]
    if message.content.startswith(command_prefix + "충전 "):
        if not isinstance(message.channel, discord.channel.DMChannel):
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute(f"SELECT * FROM users WHERE id == ?;", (message.author.id,))
            userinfo = cur.fetchone()
            con.close()
            if userinfo != None:
                code = message.content.split(" ")[1]
                charging_message = await message.reply("충전 중 입니다. 잠시만 기다려주세요.")
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                cur.execute(f"SELECT * FROM codes WHERE code == ?;", (code,))
                codeinfo = cur.fetchone()
                con.close()
                if codeinfo != None:
                    amount = codeinfo[1]
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (amount + userinfo[1], message.author.id))
                    con.commit()
                    cur.execute("DELETE FROM codes WHERE code == ?;", (code,))
                    con.commit()
                    con.close()
                    try:
                        await client.get_channel(config["channel_ids"]["charge_log_channel_id"]).send(f"<@{message.author.id}> 님이 {amount}원을 충전하셨습니다.")
                    except:
                        pass
                    await charging_message.edit(content=f"{amount}원이 충전되었습니다.\n```css\n[유저 아이디] {message.author.id}\n[돈] {amount + userinfo[1]}원```")
                else:
                    await charging_message.edit(content=f"유효하지 않은 코드입니다.")
            else:
                await message.reply(f"가입이 되어있지 않습니다. '{command_prefix}가입' 명령어로 가입하실 수 있습니다.")

    if message.content.startswith(command_prefix + "차감 "):
        if not isinstance(message.channel, discord.channel.DMChannel):
            if message.author.id in config["admin_ids"]:
                try:
                    userId = int(message.content.split(" ")[1])
                    amount = int(message.content.split(" ")[2])
                except:
                    await message.reply(f"{command_prefix}차감 (유저 아이디) (차감할 돈) 형식으로 입력해주세요.")
                    return
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                cur.execute(f"SELECT * FROM users WHERE id == ?;", (userId,))
                userinfo = cur.fetchone()
                con.close()
                if userinfo != None:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (userinfo[1] - amount, userId))
                    con.commit()
                    con.close()
                    await message.reply("차감 성공")
                else:
                    await message.reply(f"가입이 되어있지 않습니다. '{command_prefix}가입' 명령어로 가입하실 수 있습니다.")

    if message.content == command_prefix + "정보":
        if not isinstance(message.channel, discord.channel.DMChannel):
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute(f"SELECT * FROM users WHERE id == ?;", (message.author.id,))
            userinfo = cur.fetchone()
            con.close()
            if userinfo != None:
                await message.reply(f"```css\n[유저 아이디] {message.author.id}\n[돈] {userinfo[1]}원```")
            else:
                await message.reply(f"가입이 되어있지 않습니다. '{command_prefix}가입' 명령어로 가입하실 수 있습니다.")
    
    if message.content.startswith(command_prefix + "생성 "):
        if not isinstance(message.channel, discord.channel.DMChannel):
            if message.author.id in config["admin_ids"]:
                try:
                    gen_amount = int(message.content.split(" ")[1])
                    gen_money_amount = int(message.content.split(" ")[2])
                except:
                    await message.reply(f"{command_prefix}생성 (생성 갯수) (돈) 형식으로 입력해주세요.")
                    return
                codes = []
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                for _ in range(gen_amount):
                    code = gen_code(15)
                    codes.append(code)
                    cur.execute("INSERT INTO codes Values(?, ?);", (code, gen_money_amount))
                    con.commit()
                con.close()
                if len("\n".join(codes)) < 2000:
                    await message.reply("\n".join(codes))
    
    if message.content == command_prefix + "가입":
        if not isinstance(message.channel, discord.channel.DMChannel):
            con = sqlite3.connect("db.db")
            cur = con.cursor()
            cur.execute(f"SELECT * FROM users WHERE id == ?;", (message.author.id,))
            userinfo = cur.fetchone()
            con.close()
            if userinfo == None:
                con = sqlite3.connect("db.db")
                cur = con.cursor()
                cur.execute("INSERT INTO users VALUES(?, ?);", (message.author.id, 0))
                con.commit()
                con.close()
                await message.reply(f"가입이 완료되었습니다. '{command_prefix}정보' 명령어로 정보를 확인하실 수 있습니다.\n```css\n[유저 아이디] {message.author.id}\n[돈] 0원```")
            else:
                await message.reply(f"이미 가입이 되어있습니다.")

    if message.content.startswith(command_prefix + "배팅 "):
        if message.content.split(" ")[1] == "홀" or message.content.split(" ")[1] == "짝":
            if message.channel.id == config["channel_ids"]["bt_channel_id"]:
                if not 회차목록 == []:
                    con = sqlite3.connect("db.db")
                    cur = con.cursor()
                    cur.execute(f"SELECT * FROM users WHERE id == ?;", (message.author.id,))
                    userinfo = cur.fetchone()
                    con.close()
                    if userinfo != None:
                        try:
                            amount = int(message.content.split(" ")[2])
                        except:
                            return
                        if amount >= 500:
                            con = sqlite3.connect("db.db")
                            cur = con.cursor()
                            cur.execute(f"SELECT * FROM users WHERE id == ?;", (message.author.id,))
                            userinfo = cur.fetchone()
                            if userinfo[1] >= amount:
                                global 홀
                                global 짝
                                hole_or_zzack = message.content.split(" ")[1]
                                hole_ids = []
                                for hole in 홀:
                                    hole_ids.append(json.loads(hole)["id"])
                                zzack_ids = []
                                for zzack in 짝:
                                    zzack_ids.append(json.loads(zzack)["id"])
                                if not message.author.id in zzack_ids and not message.author.id in hole_ids:
                                    if second > 10:
                                        if 현재회차 != 0:
                                            if hole_or_zzack == "홀":
                                                홀.append(json.dumps({"id": message.author.id, "amount": amount}))
                                            else:
                                                짝.append(json.dumps({"id": message.author.id, "amount": amount}))
                                            cur.execute("UPDATE users SET money = ? WHERE id == ?;", (userinfo[1] - amount, message.author.id))
                                            con.commit()
                                            con.close()
                                            await message.reply(f"{현재회차}회차 - '{hole_or_zzack}' 에 배팅이 완료되었습니다.")
                                        else:
                                            await message.reply(f"게임이 없습니다.")
                                    else:
                                        await message.reply(f"지금은 배팅을 할 수 없습니다.")
                                else:
                                    await message.reply("이미 배팅을 하였습니다.")
                            else:
                                await message.reply("돈이 부족합니다.")
                        else:
                            await message.reply("최소 배팅금액은 500원 입니다.")
                    else:
                        await message.reply(f"가입이 되어있지 않습니다. '{command_prefix}가입' 명령어로 가입하실 수 있습니다.")

    if message.content == command_prefix + "시작":
        if not isinstance(message.channel, discord.channel.DMChannel):
            if message.author.id in config["admin_ids"]:
                현재회차 += 1
                msg = await client.get_channel(config["channel_ids"]["turnround_channel_id"]).send(f"```css\n   [ 홀 & 짝 게임 - 1회차 정보 ]    \n  결과까지 남은 시간 : {second}초   ```")
                msg2 = await client.get_channel(config["channel_ids"]["turnround_channel_id"]).send(f"```아직 {현재회차}회차의 결과가 정해지지 않았습니다 !```")
                msg3 = await client.get_channel(config["channel_ids"]["turnround_channel_id"]).send(f"```아직 1회차의 유저정보가 정해지지 않았습니다 !```")
                while True:
                    회차목록.append(f"아직 {현재회차}회차의 결과가 정해지지 않았습니다 !")
                    for _ in range(second):
                        await asyncio.sleep(1)
                        await msg.edit(content=f"```css\n   [ 홀 & 짝 게임 - {현재회차}회차 정보 ]    \n  결과까지 남은 시간 : {second}초   ```")
                        second -= 1
                        if second == 0:
                            await msg.edit(content=f"```css\n   [ 홀 & 짝 게임 - {현재회차}회차 정보 ]    \n  결과까지 남은 시간 : 0초   ```")
                            result = random.choice([random.choice(["홀", "짝", "짝", "짝", "홀"]), random.choice(["짝", "짝", "짝", "홀"]), random.choice(["홀", "홀", "짝", "홀"]), random.choice(["홀", "짝"]), random.choice(["홀", "홀", "짝", "짝", "홀"]), random.choice(["홀", "짝", "짝", "짝", "홀", "홀", "홀", "홀", "홀"]), random.choice(["짝", "짝", "짝", "짝", "홀"])])
                            hole_user_names = []
                            for hole in 홀:
                                hole_user_names.append("<@" + str(json.loads(hole)["id"]) + ">")
                                if result == "홀":
                                    con = sqlite3.connect("db.db")
                                    cur = con.cursor()
                                    cur.execute(f"SELECT * FROM users WHERE id == ?;", (json.loads(hole)["id"],))
                                    userinfo = cur.fetchone()
                                    con.close()
                                    con = sqlite3.connect("db.db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (userinfo[1] + json.loads(hole)["amount"] * 2, json.loads(hole)["id"]))
                                    con.commit()
                                    con.close()
                            zzack_user_names = []
                            for zzack in 짝:
                                zzack_user_names.append("<@" + str(json.loads(zzack)["id"]) + ">")
                                if result == "짝":
                                    con = sqlite3.connect("db.db")
                                    cur = con.cursor()
                                    cur.execute(f"SELECT * FROM users WHERE id == ?;", (json.loads(zzack)["id"],))
                                    userinfo = cur.fetchone()
                                    con.close()
                                    con = sqlite3.connect("db.db")
                                    cur = con.cursor()
                                    cur.execute("UPDATE users SET money = ? WHERE id == ?;", (userinfo[1] + json.loads(zzack)["amount"] * 2, json.loads(zzack)["id"]))
                                    con.commit()
                                    con.close()
                            회차목록.remove(f"아직 {현재회차}회차의 결과가 정해지지 않았습니다 !")
                            회차목록.append(f"{현재회차}회차 - '{result}'")
                            홀 = []
                            짝 = []
                            await msg2.edit(content=f"```{현재회차}회차의 결과 : {result}```")
                            hole_user_names = " ".join(hole_user_names)
                            zzack_user_names = " ".join(zzack_user_names)
                            await msg3.edit(content=f"```{현재회차}회차의 유저정보```\n홀: {hole_user_names}\n짝: {zzack_user_names}")
                            if len(회차목록) >= 10:
                                회차목록.remove(회차목록[0])
                            현재회차 += 1
                            second = 40
                            zzack_user_names = []
                            hole_user_names = []

    if message.content == command_prefix + "회차":
        if not 회차목록 == []:
            await message.reply("```" + "\n".join(회차목록) + "```")

client.run(config["bot_token"])
