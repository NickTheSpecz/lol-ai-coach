import requests
import time
import os
import sys

# Insira aqui a sua Riot API Key
API_KEY = "RGAPI-8b5280c9-4cdc-4ea7-a274-f5356d2732fd"

# Headers padrao para a API da Riot
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Riot-Token": API_KEY
}

# Regioes usadas pela API da Riot
# Riot IDs (Account-v1) e Matches (Match-v5) costumam usar o cluster macro: americas, asia, europe
MACRO_REGION = "americas"
# Algumas outras APIs menores usam server_region (br1, na1, etc)
SERVER_REGION = "br1"


def get_puuid(game_name, tag_line):
    """
    Busca o PUUID do jogador usando o Riot ID (Account-V1).
    Endpoints globais preferem a macro regiao (americas).
    """
    print(f"[*] Buscando PUUID para {game_name}#{tag_line}...")
    url = f"https://{MACRO_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[+] PUUID encontrado: {data['puuid']}")
        return data['puuid']
    elif response.status_code == 403:
         print("[-] ERRO 403: Forbbiden. Sua API Key pode estar vencida (Development Keys vencem em 24h) ou invalida.")
         sys.exit(1)
    elif response.status_code == 404:
        print(f"[-] ERRO 404: Riot ID {game_name}#{tag_line} nao encontrado.")
        sys.exit(1)
    else:
        print(f"[-] Erro na requisicao Account-V1: {response.status_code} - {response.text}")
        sys.exit(1)


def get_match_ids(puuid, count=5):
    """
    Recupera a lista de IDs das ultimas partidas (Match-V5).
    Usamos a API de macro regiao 'americas'.
    """
    print(f"[*] Buscando as ultimas {count} partidas...")
    url = f"https://{MACRO_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        matches = response.json()
        print(f"[+] Encontradas {len(matches)} partidas.")
        return matches
    else:
        print(f"[-] Erro na requisicao Match-V5 (IDs): {response.status_code} - {response.text}")
        return []


def analyze_match(match_id, puuid):
    """
    Baixa os detalhes de uma partida e os analisa para um jogador especifico (Match-V5).
    """
    url = f"https://{MACRO_REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        match_data = response.json()
        info = match_data['info']
        metadata = match_data['metadata']
        
        # O modo de jogo
        game_mode = info['gameMode']
        game_type = info['gameType']
        duration_minutes = info['gameDuration'] // 60
        
        # Encontra o nosso jogador nos participantes
        player_stats = None
        for participant in info['participants']:
            if participant['puuid'] == puuid:
                player_stats = participant
                break
                
        if not player_stats:
            print(f"  [-] Jogador nao encontrado na partida {match_id}")
            return
            
        # Extrai os dados relevantes
        champion = player_stats['championName']
        kills = player_stats['kills']
        deaths = player_stats['deaths']
        assists = player_stats['assists']
        win = player_stats['win']
        result = "VITORIA" if win else "DERROTA"
        
        print(f"  -> Partida: {match_id} | {game_mode} ({game_type}) - {duration_minutes} min")
        print(f"     Resultado: {result} jogando de {champion}")
        print(f"     KDA: {kills}/{deaths}/{assists}")
        print("-" * 50)
        
    else:
        print(f"  [-] Erro ao carregar partida {match_id}: {response.status_code}")
        
    # Rate limit prevention (API dev tem limites rigidos)
    time.sleep(1.2)


def main():
    print("=" * 60)
    print("ANALISADOR DE HISTORICO DE PARTIDAS - RIOT API")
    print("=" * 60)
    print("Lembre-se: Chaves de API de Dev padrao NAO mostram Custom Games de terceiros.\n")
    
    riot_id_input = input("Digite seu Riot ID (Nome#Tag): ")
    
    if "#" not in riot_id_input:
        print("[-] Formato invalido. Certifique-se de incluir a Tagline apos o '#'. Exemplo: Faker#KR1")
        return
        
    game_name, tag_line = riot_id_input.split("#", 1)
    game_name = game_name.strip()
    tag_line = tag_line.strip()
    
    # 1. Pega o PUUID
    puuid = get_puuid(game_name, tag_line)
    
    # 2. Pega a lista com ultimos 5 match IDs
    match_ids = get_match_ids(puuid, count=5)
    
    # 3. Analisa cada match ID
    if match_ids:
        print("\n" + "=" * 60)
        print("RESULTADOS DO HISTORICO")
        print("=" * 60)
        for mid in match_ids:
            analyze_match(mid, puuid)
    else:
        print("[-] Nenhuma partida recente encontrada para analise.")

if __name__ == "__main__":
    main()
