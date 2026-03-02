import os
import json
import requests

def get_real_news():
    return ["⚡ Noticia real detectada en Ormuz...", "🔴 Nueva declaración de Trump..."]

def update_json():
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    data['ticker'] = get_real_news()
    
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    update_json()
