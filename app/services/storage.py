import json
import os.path

def save_token(user_id:str, access_token: str, item_id:str, institution_id:str, institution_name:str, file_path ="app/services/token.json"):
    data = {}

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("warning: JSON 格式错误，已忽略原始内容")

    if user_id in data:
        existings_insts = [entry["institution_id"] for entry in data[user_id]]
        if institution_id not in existings_insts:
            data[user_id].append({
                "access_token": access_token,
                "item_id": item_id,
                "institution_id": institution_id,
                "institution_name": institution_name
            })
    else:
        data[user_id] = [{
            "access_token": access_token,
            "item_id": item_id,
            "institution_id": institution_id,
            "institution_name": institution_name
        }]

    #write into the file
    with open(file_path, "w") as f:
        json.dump(data,f,indent=2)
    print(f"Token saved for user: {user_id}")
