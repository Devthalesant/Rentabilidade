import requests, time

def query_crm_api_sync(query: str, variables: dict):
    TOKEN     = "145418|arQc09gsrcSNJipgDRaM4Ep6rl3aJGkLtDMnxa0u" # Ambiente de homologação
    ENDPOINT  = "https://open-api.queromeubotox.com.br/graphql" # Ambiente de homologação

    # Tipo de arquivo, token de autorização
    # Primeira coisa que o sistema olha ao receber uma requisição é o Headers
    HEADERS  = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {TOKEN}"
    }

    start = time.time()
    # request modulo do python (modulo post serve para enviar a solicitação de dados (Query))
    resp = requests.post(
      ENDPOINT,
      json={"query": query, "variables": variables},
      headers=HEADERS,
      timeout=60
    )
    elapsed = time.time() - start
    print(f"HTTP {resp.status_code} in {elapsed:.1f}s")
    resp.raise_for_status()
    return resp.json()