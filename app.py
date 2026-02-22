import os
import requests
import base64
from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)
# Chave secreta interna do Flask para gerenciar sessoes
app.secret_key = os.urandom(24)

# ======================================================================
# CONFIGURAÇOES RSO (A preencher quando a Riot aprovar sua aplicacao)
# ======================================================================
# Você pegará estas 2 variaveis na aba "RSO" do Riot Developer Portal
RSO_CLIENT_ID = "SEU-CLIENT-ID-AQUI" 
RSO_CLIENT_SECRET = "SEU-CLIENT-SECRET-AQUI"

# URI para onde a Riot te manda devolver após o jogador logar
REDIRECT_URI = "http://localhost:5000/callback" 

# ======================================================================
# CONFIGURAÇOES DA API DE DADOS (Match history, account)
# ======================================================================
MACRO_REGION = "americas"


@app.route("/")
def index():
    """
    Pagina inicial que apenas exibe o botao "Login com a Riot"
    """
    return render_template("index.html")


@app.route("/login")
def login():
    """
    [Passo 1] O botao HTML envia o jogador para cá.
    Aqui nós redirecionamos ele pra tela original de Login da Riot Games.
    """
    # A URL magica e oficial da Riot
    # O parametro scope=openid diz que so queremos ler a identidade basica do jogador
    auth_url = (
        f"https://auth.riotgames.com/authorize?"
        f"client_id={RSO_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid"
    )
    
    print(f"[*] Redirecionando usuario para: {auth_url}")
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """
    [Passo 2] O jogador logou e a Riot o redirecionou pra ca.
    A Riot coloca um "?code=algumacoisa" na URL para nós trocarmos pelo Access Token.
    """
    # 1. Pega o "code" da URL
    code = request.args.get("code")
    
    if not code:
        return "Erro: Falha na autenticacao com a Riot (Nenhum codigo retornado)."

    print(f"[*] Código recebido da Riot: {code[:10]}...")

    # 2. Agora o servidor (app.py) pede o Access Token direto para a Riot (em background)
    token_url = "https://auth.riotgames.com/token"
    
    # O Basic Auth exige que o Client ID e Secret sejam codificados em base64
    credentials = f"{RSO_CLIENT_ID}:{RSO_CLIENT_SECRET}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    # ATENÇAO: Esta request VAI FALHAR porque o seu Client_ID e Secret atuais estao em branco (sao falsos por enguanto).
    token_response = requests.post(token_url, data=data, headers=headers)
    
    if token_response.status_code != 200:
        return (
            f"<h1>Erro no ambiente RSO</h1>"
            f"<p>Como explicamos, a Riot negou gerar o Token porque as chaves configuradas no app.py (RSO_CLIENT_ID e SECRET) estao invalidas/vazias ou nao foram aprovadas na Riot.</p>"
            f"<p>Mensagem da Riot: {token_response.text}</p>"
        )
        
    # Se isso der sucesso no futuro (quando tiver as chaves reais)...
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    
    # Salva o token na sessao do cara
    session["access_token"] = access_token
    
    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():
    """
    [Passo 3] Aqui é a home logada. Voce tem o Bearer Token. Pode puxar o PUUID dele
    sem ele precisar digitar o NOME#TAG. A Riot descobre pelo proprio login.
    """
    if "access_token" not in session:
        return redirect("/")
        
    access_token = session["access_token"]
    
    # Usando a API especial /accounts/me para RSO:
    url_me = f"https://{MACRO_REGION}.api.riotgames.com/riot/account/v1/accounts/me"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    account_resp = requests.get(url_me, headers=headers)
    
    if account_resp.status_code == 200:
        acc_data = account_resp.json()
        puuid = acc_data.get("puuid")
        riot_id = f"{acc_data.get('gameName')}#{acc_data.get('tagLine')}"
        
        return (f"<h1>Bem vindo(a)!</h1>"
                f"<p>A Riot Games confirmou que você logou com sucesso no seu perfil oficial!</p>"
                f"<p><b>Sua conta:</b> {riot_id}</p>"
                f"<p><b>Seu PUUID (Oculto):</b> {puuid}</p>"
                f"<hr>"
                f"<p><i>Com este Bearer Token recém-validado, as chamadas para as MATCH-V5 (Histórico API) "
                f"finalmente exibirão as Custom Games e Campeonatos porque o jogador concedeu expressamente as permissões!</i></p>")
    else:
        return f"Erro ao acessar Account-V1: {account_resp.text}"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
