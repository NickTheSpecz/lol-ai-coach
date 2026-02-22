# Mirai - Performance Optimizer

Este é um projeto em desenvolvimento focado em analisar partidas competitivas e personalizadas (Custom Games) de League of Legends usando IA.

## Visão Geral
O **Mirai** utiliza a API da Riot Games (Match-V5 e Timeline-V5) para extrair dados avançados minuto a minuto das partidas (como Gold Per Minute, diferença de XP e controle de objetivos). Com esses dados, uma Inteligência Artificial (LLM) analisa as decisões táticas e fornece feedback automático para os jogadores do time.

## Status do Projeto
Em desenvolvimento Alpha. A integração base com as APIs da Riot (Autenticação RSO e extração de histórico) está implementada. O módulo de IA está em fase de integração.

## Tecnologias
- **Python 3**
- **Flask** (Para o servidor web e painel de controle)
- **Riot Games API** (Account-V1, Match-V5, Timeline-V5)
- **OAuth2 / RSO (Riot Sign On)** para privacidade e acesso seguro aos dados
- **Google Generative AI (Gemini)** / LLMs para análise dos dados de timeline

## Como rodar localmente
1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente com o seu `RSO_CLIENT_ID` e `RSO_CLIENT_SECRET`.
4. Execute o servidor: `python app.py`

*Nota para a Riot Games: Este repositório serve como a Product URL provisória enquanto o sistema está em fase de prototipação local e aguardando aprovação das credenciais RSO.*
