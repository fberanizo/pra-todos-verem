# #PraTodosVerem (🚧In Progress🚧)

#PraTodosVerem é um projeto para geração automatizada de legendas para imagens de redes sociais.

## Data Collection

O Selenium WebDriver automatiza a coleta de dados de publicações em redes sociais (no momento, apenas Instagram).
A imagem docker `docker.io/fberanizo/pra-todos-verem-data-collection:1.0.0` já possui todas as dependências instaladas e é a forma mais fácil de rodar este passo.

A implementação faz uso do [Geckodriver](https://github.com/mozilla/geckodriver/releases) e requer a instalação do [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/).

```bash
export INSTAGRAM_USERNAME="<seu-nome-de-usuario>"
export INSTAGRAM_PASSWORD="<sua-senha-nao-faca-commit-dela>"
python -m pra_todos_verem.data_collection.collect \
    --query PraTodosVerem \
    --output_path data/raw/posts/
```

Parâmetros:

```
usage: collect.py [-h] [--output_path OUTPUT_PATH] [--headless] [--max_downloads MAX_DOWNLOADS]

Ferramenta de coleta de imagens em publicações #PraTodosVerem

optional arguments:
  -h, --help            show this help message and exit
  --query QUERY         Query de busca. Default: PraTodosVerem
  --output_path OUTPUT_PATH
                        Diretório onde salvar os dados 'raw' (imagens e textos). Default: data/raw/posts/
  --headless            Habilita headless browsing.
  --max_downloads MAX_DOWNLOADS
                        Total de publicações visitadas. Default: 5.
```

## Materiais Úteis

- [Dataset #PraCegoVer](https://github.com/larocs/PraCegoVer)
- [Accessibility 4DEVS](https://www.linkedin.com/company/accessibility4devs/about/)
