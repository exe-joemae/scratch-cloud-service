import requests
import json
import os

# Scratch API
PROJECT_ID = "あなたのScratchプロジェクトID"
CLOUD_API = f"https://clouddata.scratch.mit.edu/logs?projectid={PROJECT_ID}&limit=1"

# 返信用クラウド変数
CLOUD_SET_API = "https://clouddata.scratch.mit.edu/set"

def fetch_cloud():
    r = requests.get(CLOUD_API)
    logs = r.json()
    if not logs:
        return None
    return logs[0]["value"]

def parse_protocol(value):
    if "." not in value:
        return None

    account, payload = value.split(".", 1)

    command = payload[0]          # 1=セーブ, 2=ロード
    data = payload[1:]            # データ本体（ロード時は空）

    return {
        "account": account,
        "command": command,
        "data": data
    }

def load_db():
    with open("server/data/users.json", "r") as f:
        return json.load(f)

def save_db(db):
    with open("server/data/users.json", "w") as f:
        json.dump(db, f, indent=2)

def send_to_scratch(account, data):
    """
    返信クラウド変数に書き込む
    形式: [アカウント番号].3[データ本体]
    """
    payload = f"{account}.3{data}"

    requests.post(
        CLOUD_SET_API,
        json={
            "projectid": PROJECT_ID,
            "name": "reply",  # 返信用クラウド変数名
            "value": payload
        }
    )

def main():
    value = fetch_cloud()
    if not value:
        print("No cloud data.")
        return

    parsed = parse_protocol(value)
    if not parsed:
        print("Invalid format.")
        return

    account = parsed["account"]
    command = parsed["command"]
    data = parsed["data"]

    db = load_db()

    # ユーザーが未登録なら初期化
    if account not in db:
        db[account] = {}

    # セーブ（スロット1）
    if command == "1":
        db[account]["saveSlot1"] = data
        save_db(db)
        print(f"Saved slot1 for {account}")

    # ロード（スロット2）
    elif command == "2":
        saved = db[account].get("saveSlot1", "")
        send_to_scratch(account, saved)
        print(f"Returned save data to {account}")

if __name__ == "__main__":
    main()
