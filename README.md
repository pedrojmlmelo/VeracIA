# VeracIA: Verificador de Fake News com Google Gemini
<h1 align="center">
  <br>
  <img src="https://github.com/pedrojmlmelo/VeracIA/blob/main/veracIA.png" alt="Image" height="200" width="200">
  <br>
  <br><br>
</h1>

<p align="center"><i>"O progresso da humanidade se apoia na busca incessante pela verdade."</i> </p>


[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/pedrojmlmelo/VeracIA/blob/main/Verificador_de_Fake_News.ipynb)

Este projeto, desenvolvido como parte da Imersão Inteligência Artificial da Alura e do Google, utiliza o poder do modelo de linguagem Google Gemini para auxiliar na verificação de notícias e identificar potenciais fake news através de uma arquitetura multi-agente.

## Visão Geral

O VeracIA implementa um sistema com quatro agentes de IA distintos que trabalham em conjunto para analisar a credibilidade de uma notícia fornecida através de sua URL:

1.  **Agente Verificador de Fonte:** Avalia a confiabilidade do site da notícia.
2.  **Agente Analisador de Conteúdo:** Busca por sinais de desinformação e manipulação no texto.
3.  **Agente de Checagem Cruzada:** Tenta verificar a veracidade das alegações da notícia.
4.  **Agente Sintetizador:** Consolida as análises dos outros agentes para fornecer um parecer final sobre a probabilidade de ser fake news.

## Como Funciona

O script em Python utiliza as bibliotecas `google-genai` para interagir com o modelo Gemini e `google-adk` para a criação e gerenciamento dos agentes. O fluxo de operação é o seguinte:

1.  O usuário é solicitado a inserir a URL da notícia a ser verificada.
2.  A função `agente_verificador_fonte` é chamada para analisar a credibilidade da fonte com base na URL.
3.  O resultado da análise da fonte é passado para a função `agente_analisador_conteudo`, que examina o texto em busca de técnicas de desinformação.
4.  A análise do conteúdo é então utilizada pela função `agente_checagem_cruzada` para verificar as alegações presentes na notícia.
5.  Finalmente, a função `agente_sintetizador` recebe o resultado da checagem cruzada e gera um parecer final, indicando o nível de probabilidade da notícia ser fake news e fornecendo uma breve justificativa.
6.  O parecer final é exibido ao usuário no formato Markdown.

## Pré-requisitos

Para executar este projeto, você precisará de:

* Uma conta Google Cloud com acesso à API Gemini.
* Uma chave de API do Google Gemini configurada como um segredo no Google Colab (acessível via `userdata.get('GOOGLE_API_KEY')`).
* As seguintes bibliotecas Python instaladas:
    ```bash
    %pip install google-genai
    %pip install google-adk
    ```

## Utilização

Você pode executar este projeto diretamente no Google Colab através do link no topo deste README. Siga estas etapas:

1.  Execute as células para instalar as bibliotecas necessárias (`google-genai` e `google-adk`).
2.  Certifique-se de ter configurado sua chave de API do Google Gemini como um segredo no Colab com o nome `GOOGLE_API_KEY`.
3.  Execute as células que definem as funções auxiliares (`call_agent` e `to_markdown`) e as funções de cada agente (`agente_verificador_fonte`, `agente_analisador_conteudo`, `agente_checagem_cruzada`, `agente_sintetizador`).
4.  Na última célula, quando solicitado pela entrada `Por favor, digite a url da noticia:`, cole a URL da notícia que você deseja verificar e pressione Enter.
5.  O resultado da análise, incluindo o parecer final do `agente_sintetizador`, será exibido logo abaixo da célula de entrada.

## Estrutura do Código

O código principal é composto por funções que definem a lógica de cada agente e funções auxiliares:

* `call_agent(agent: Agent, message_text: str) -> str`: Função auxiliar para enviar mensagens aos agentes e obter suas respostas.
* `to_markdown(text)`: Função auxiliar para formatar o texto de saída em Markdown para melhor visualização no Colab.
* `agente_verificador_fonte(url)`: Implementa a lógica do agente para verificar a credibilidade da fonte.
* `agente_analisador_conteudo(fonte_verificada)`: Implementa a lógica do agente para analisar o conteúdo da notícia.
* `agente_checagem_cruzada(conteudo_analisado)`: Implementa a lógica do agente para realizar a checagem de fatos.
* `agente_sintetizador(cruzada_analisado)`: Implementa a lógica do agente para consolidar as análises e gerar o parecer final.

## Exemplo de Saída

Ao fornecer a URL `https://medicospelavida.org.br/noticias/a-145a-live-comunica-mpv-de-terca-feira-15-as-20h30-vai-trazer-informacoes-importantes-sobre-audiencias-publicas-a-respeito-da-inoculacao-obrigatoria-de-criancas/`, o sistema gerou a seguinte análise (o resultado pode variar ligeiramente):

> Com base na análise apresentada, o site medicospelavida.org.br apresenta alta probabilidade de disseminar fake news. A reputação questionável, a falta de base em evidências científicas, alegações não comprovadas sobre vacinas (como miocardite e pericardite) e tratamentos como a ivermectina, o questionamento da eficácia das vacinas e a promoção de tratamentos sem comprovação como a hidroxicloroquina são indicativos fortes de desinformação. Além disso, as críticas à cobertura da mídia podem ser uma tática para promover narrativas alternativas.
>
> **Nota:** Alta probabilidade de ser fake news.

## Contribuição

Este projeto foi desenvolvido para fins educacionais durante a Imersão IA da Alura e do Google. Contribuições para melhorias ou novas funcionalidades são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Agradecimentos

Gostaria de agradecer à Alura e ao Google por proporcionarem a Imersão em Inteligência Artificial e a oportunidade de desenvolver este projeto.
