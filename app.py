import streamlit as st
import os
# Remova from google.colab import userdata
# A API Key será configurada nos segredos do Streamlit

# Suas importações do notebook:
from google import genai # Se estiver usando google-generativeai, isso pode mudar para: import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types as genai_types # Renomeado para evitar conflito com st.types
from datetime import date
import textwrap
# Remova from IPython.display import display, Markdown # Streamlit tem suas próprias formas de exibir
import requests
import warnings

warnings.filterwarnings("ignore")

# No início do seu app.py, depois das importações

import streamlit as st
import os
from google import genai # ou import google.generativeai as genai
# ... outras importações

# --- CONFIGURAÇÃO DA API KEY E CLIENTE GEMINI ---
API_KEY = None
GOOGLE_CSE_ID = None
GOOGLE_SEARCH_API_KEY = None # Opcional, se a chave de busca for diferente

try:
    # No Streamlit Cloud, st.secrets é populado pela UI.
    # Localmente (como no Codespaces), st.secrets lê de .streamlit/secrets.toml.
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    # Opcional: carregar chaves para a ferramenta de busca se existirem
    if "GOOGLE_CSE_ID" in st.secrets:
        GOOGLE_CSE_ID = st.secrets["GOOGLE_CSE_ID"]
        os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID # Para o ADK
    if "GOOGLE_SEARCH_API_KEY" in st.secrets:
        GOOGLE_SEARCH_API_KEY = st.secrets["GOOGLE_SEARCH_API_KEY"]
        # Se a google_search do ADK usa a GOOGLE_API_KEY para autenticação de busca
        # e você tem uma chave específica para busca, você pode precisar definir
        # a variável de ambiente que a ferramenta de busca espera.
        # Por padrão, a ferramenta google_search do ADK pode procurar por GOOGLE_API_KEY e GOOGLE_CSE_ID
    elif API_KEY: # Se não houver GOOGLE_SEARCH_API_KEY específica, mas houver a principal
        GOOGLE_SEARCH_API_KEY = API_KEY # Assume que a chave principal também serve para busca

except (KeyError, streamlit.errors.StreamlitAPIException, streamlit.errors.StreamlitSecretNotFoundError) as e:
    # Este bloco é executado se st.secrets não encontrar o arquivo ou a chave específica.
    st.sidebar.warning(f"Não foi possível carregar configurações de st.secrets (erro: {type(e).__name__}). Verifique se '.streamlit/secrets.toml' existe e está configurado para desenvolvimento local.")
    # Tenta como fallback variáveis de ambiente (útil se não quiser usar secrets.toml localmente ou para outros sistemas de deploy)
    API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", API_KEY) # Usa API_KEY como fallback para search key

if not API_KEY:
    st.error("ERRO CRÍTICO: Chave GOOGLE_API_KEY não configurada.")
    st.info("Para rodar este aplicativo, você precisa configurar sua GOOGLE_API_KEY:")
    st.info("1. Se estiver implantando no Streamlit Cloud: adicione-a em 'Settings' -> 'Secrets'.")
    st.info("2. Se estiver rodando localmente (como neste Codespace/VSCode):")
    st.info("   a. Crie um arquivo chamado 'secrets.toml' na pasta '.streamlit' (ex: 'VeracIA/.streamlit/secrets.toml').")
    st.info("   b. Adicione sua chave ao arquivo no formato: GOOGLE_API_KEY = 'sua_chave_aqui'")
    st.info("   (Opcional) Adicione também GOOGLE_CSE_ID e GOOGLE_SEARCH_API_KEY se a ferramenta de busca exigir.")
    st.info("   OU")
    st.info("   c. Defina a variável de ambiente GOOGLE_API_KEY (e outras, se necessário).")
    st.stop() # Para a execução se a chave principal não for encontrada

# Configura a API Key para google-generativeai
try:
    genai.configure(api_key=API_KEY)
    os.environ["GOOGLE_API_KEY"] = API_KEY # Garante que a variável de ambiente seja definida para bibliotecas que a usam

    # Se GOOGLE_SEARCH_API_KEY for diferente da API_KEY principal e for necessária,
    # certifique-se de que a ferramenta `google_search` a utilize corretamente.
    # O ADK pode usar GOOGLE_API_KEY para a busca se GOOGLE_SEARCH_API_KEY não estiver explicitamente configurada para ele.
    # Se a chave de busca é a mesma do Gemini, definir os.environ["GOOGLE_API_KEY"] já pode ser suficiente.

    st.sidebar.success("API Key do Google configurada.")
except Exception as e:
    st.error(f"Falha ao configurar a biblioteca Google GenAI com a API Key: {e}")
    st.stop()

# Se estiver usando o cliente antigo 'from google import genai' e 'genai.Client()'
# client = genai.Client() # Esta linha pode não ser necessária se você usa o ADK ou o novo google-generativeai

MODEL_ID = "gemini-1.5-flash-latest" # Verifique o nome do modelo mais recente ou o que você deseja usar

# --- SUAS FUNÇÕES DE AGENTE E AUXILIARES (COPIADAS DO NOTEBOOK) ---
# Cole aqui as definições das funções:
# call_agent(agent: Agent, message_text: str) -> str:
# to_markdown(text): (Adapte para usar st.markdown)
# agente_verificador_fonte(url):
# agente_analisador_conteudo(fonte_verificada):
# agente_checagem_cruzada(conteudo_analisado):
# agente_sintetizador(cruzada_analisado):

# Exemplo de adaptação da to_markdown para Streamlit
def display_markdown_st(text):
  text = text.replace('•', '  *')
  # textwrap.indent pode não ser necessário ou pode ser feito de outra forma
  # A formatação de citação Markdown ('> ') já é bem renderizada pelo st.markdown
  st.markdown(f"> {text}") # Simplesmente aplicar o estilo de citação

# Cole aqui a função call_agent (adaptada para usar genai_types em vez de types)
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="user1", session_id="session1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)]) # Use genai_types

    final_response = ""
    # O runner.run pode ser um gerador assíncrono. Streamlit roda de forma síncrona.
    # Se run for assíncrono, você precisará de `async def` e `await` ou usar `asyncio.run()`.
    # Por agora, vamos assumir que ele pode ser iterado de forma síncrona ou que o ADK lida com isso.
    # Se der erro aqui, pode ser um ponto de complexidade.
    try:
        for event in runner.run(user_id="user1", session_id="session1", new_message=content):
            if event.is_final_response():
              for part in event.content.parts:
                if part.text is not None:
                  final_response += part.text
                  final_response += "\n"
        return final_response
    except Exception as e:
        st.error(f"Erro ao executar o agente {agent.name}: {e}")
        # st.error("Detalhes do erro: Verifique se as ferramentas como 'google_search' estão configuradas corretamente e se o modelo está acessível.")
        # st.error(f"Certifique-se que a API Key tem permissões para o modelo '{agent.model}' e para as ferramentas (ex: Google Search API se 'google_search' a usa).")
        return f"Erro ao processar com o agente {agent.name}."

# Definições dos agentes (copie do notebook e adapte o nome do modelo se necessário)
# Exemplo para o primeiro agente:
def agente_verificador_fonte(url_noticia):
  # Verifique se 'google_search' requer configuração adicional da API de busca
  # O ADK pode tentar usar uma API de busca que precisa de sua própria chave ou configuração.
  # Por padrão, google_search no ADK pode exigir que você configure a API do Google Custom Search.
  # Se não estiver configurada, chamadas a ferramentas podem falhar.
  # Este é um ponto CRÍTICO. O ADK simplifica o uso de ferramentas, mas elas precisam ser funcionais.
  fonte = Agent(
      name = "agente_verificador_fonte",
      model = MODEL_ID, # Use a variável MODEL_ID
      instruction = """
            Você é um especialista em análise de credibilidade de fontes de notícias na internet.
            Sua tarefa é avaliar a confiabilidade da fonte com base na URL fornecida.
            Considere fatores como: reputação do domínio, se é conhecido por espalhar desinformação,
            se possui uma linha editorial clara, transparência sobre autores e propriedade.
            Seja conciso e direto na sua avaliação.
      """,
      description = "Agente que verifica a fonte da noticia",
      tools = [google_search] # ATENÇÃO: google_search pode precisar de configuração!
)
  entrada_agente_verificador_fonte = f"Url: {url_noticia}\\n"
  fonte_verificada = call_agent(fonte, entrada_agente_verificador_fonte)
  return fonte_verificada

def agente_analisador_conteudo(texto_noticia_e_analise_fonte) :
  conteudo = Agent(
      name = "agente_analisador_conteudo",
      model = MODEL_ID,
      instruction = """
            "Você é um especialista em identificar técnicas de desinformação e manipulação em textos. "
            "Analise o texto da notícia fornecida e aponte possíveis sinais de alerta, como: "
            "linguagem excessivamente emocional ou alarmista, generalizações apressadas, "
            "falta de fontes ou evidências concretas, apelo a teorias da conspiração, "
            "erros grosseiros de português ou formatação que sugiram falta de profissionalismo, "
            "ou alegações extraordinárias sem provas extraordinárias. Seja objetivo.
      """,
      description = "Agente que analisa o conteudo da noticia",
      tools = [google_search] # ATENÇÃO: google_search pode precisar de configuração!
)
  conteudo_analisado = call_agent(conteudo, texto_noticia_e_analise_fonte)
  return conteudo_analisado

def agente_checagem_cruzada(texto_com_analises_anteriores) :
  cruzada = Agent(
      name = "agente_checagem_cruzada",
      model = MODEL_ID,
      instruction = """
            "Você é um assistente de checagem de fatos (fact-checker) muito rigoroso. "
            "Sua tarefa é verificar a veracidade das principais alegações contidas no texto da notícia. "
            "Use seu conhecimento para buscar informações que corroborem ou contradigam essas alegações. "
            "Mencione se há consenso sobre o tema, se é uma informação disputada ou se é amplamente considerada falsa. "
            "Se a notícia for sobre um evento muito recente ou obscuro, admita se não encontrar informações. "
            "Indique fontes confiáveis se possível (conceitualmente, você não navega na web em tempo real, mas use seu conhecimento)\
      """,
      description = "Agente que faz a analise cruzada",
      tools = [google_search] # ATENÇÃO: google_search pode precisar de configuração!
)
  cruzada_analisado = call_agent(cruzada, texto_com_analises_anteriores)
  return cruzada_analisado

def agente_sintetizador(texto_com_todas_analises) :
  sintetizador = Agent(
      name = "agente_sintetizador",
      model = MODEL_ID,
      instruction = """
            "Você é um assistente de IA sênior encarregado de consolidar as análises de outros agentes de IA "
            "para fornecer um parecer final sobre a probabilidade de uma notícia ser fake news. "
            "Considere todos os relatórios: coleta de dados, análise da fonte, análise do conteúdo e checagem cruzada. "
            "Seu parecer deve ser claro, indicar um nível de confiança (ex: 'Alta probabilidade de ser fake news', "
            "'Potencialmente enganosa', 'Informação parece precisa', 'Inconclusivo') e "
            "justificar brevemente com base nos pontos mais críticos dos relatórios."
            "Seja cauteloso e equilibrado em seu julgamento."
            "Sua resposta deve conter no final uma nota que classifique entre:
            'Alta probabilidade de ser fake news',
            'Potencialmente enganosa',
            'Informação parece precisa',
            'Inconclusivo'
      """,
      description = "Agente que faz a sintetização",
      tools = [google_search] # ATENÇÃO: google_search pode precisar de configuração!
)
  sintetizada_analisado = call_agent(sintetizador, texto_com_todas_analises)
  return sintetizada_analisado


# --- INTERFACE DO USUÁRIO COM STREAMLIT ---
st.title("VeracIA: Verificador de Fake News")
st.write("""
Esta ferramenta utiliza agentes de Inteligência Artificial para analisar uma notícia
e fornecer um parecer sobre sua potencial veracidade.
""")

url_usuario = st.text_input("Por favor, cole a URL completa da notícia que você deseja verificar:", "")

if st.button("Analisar Notícia"):
    if url_usuario:
        try:
            # Simular a extração do conteúdo da URL (você precisará de uma biblioteca para isso)
            # Ex: newspaper3k ou requests+BeautifulSoup
            # Por enquanto, vamos apenas passar a URL e pedir ao primeiro agente para obter informações.
            # Idealmente, você baixaria o texto da notícia aqui e o passaria para os agentes.
            # O prompt do agente_verificador_fonte já pede para considerar a URL.

            with st.spinner("Analisando a fonte da notícia... (Agente 1)"):
                # Aqui passamos a URL diretamente. O agente é instruído a avaliar com base na URL.
                # Para uma análise de conteúdo mais profunda, o texto da notícia seria necessário.
                # Vamos assumir que a instrução do agente é suficiente para uma análise inicial baseada na URL e busca.
                entrada_agente1 = f"Analise a credibilidade da fonte da seguinte URL: {url_usuario}. Além disso, se possível, resuma brevemente o principal tópico ou alegação da notícia encontrada nessa URL para que eu possa analisar o conteúdo."
                fonte_check = agente_verificador_fonte(entrada_agente1)
                st.subheader("Resultado da Análise da Fonte:")
                st.markdown(fonte_check)

            # Para os próximos agentes, o ideal seria ter o CONTEÚDO da notícia.
            # O 'fonte_check' atual é a análise da fonte, não o conteúdo da notícia em si.
            # Isso significa que a cadeia de agentes como está no Colab pode não funcionar bem
            # se o conteúdo da notícia não for explicitamente extraído e passado adiante.

            # Modificação: Vamos pedir aos agentes para buscarem e analisarem o conteúdo com base na URL.
            # Ou, melhor ainda, o primeiro agente já poderia resumir e os próximos trabalham nesse resumo.
            # A instrução do agente1 já foi modificada para "resuma brevemente o principal tópico".

            with st.spinner("Analisando o conteúdo com base nas informações da fonte... (Agente 2)"):
                # O 'fonte_check' agora deve conter o resumo da notícia e a análise da fonte.
                conteudo_check = agente_analisador_conteudo(f"Com base na análise da fonte e no resumo da notícia a seguir, analise o conteúdo: {fonte_check}")
                st.subheader("Resultado da Análise de Conteúdo:")
                st.markdown(conteudo_check)

            with st.spinner("Realizando checagem cruzada... (Agente 3)"):
                cruzada_check = agente_checagem_cruzada(f"Realize uma checagem cruzada das alegações presentes na seguinte análise: {conteudo_check}")
                st.subheader("Resultado da Checagem Cruzada:")
                st.markdown(cruzada_check)

            with st.spinner("Gerando parecer final... (Agente 4)"):
                sintetizador_check = agente_sintetizador(f"Sintetize todas as análises anteriores e forneça um parecer final: {cruzada_check}")
                st.subheader("Parecer Final:")
                st.markdown(sintetizador_check)

            st.success("Análise concluída!")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao tentar acessar a URL: {e}. Verifique se a URL está correta e acessível.")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado durante a análise: {e}")
            st.error("Isso pode ser devido à configuração da API Key, problemas com as ferramentas dos agentes (como Google Search API), ou o modelo não estar acessível. Verifique os logs no Streamlit Cloud se o erro persistir.")
    else:
        st.warning("Por favor, insira uma URL para analisar.")

st.markdown("---")
st.markdown("Desenvolvido como parte do projeto VeracIA.")
