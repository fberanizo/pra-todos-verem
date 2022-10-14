# #PraTodosVerem (🚧In Progress🚧)

#PraTodosVerem é um projeto para geração automatizada de legendas para imagens de redes sociais.

> :warning: Ferramentas de automação (como esta) **não resolvem o problema da acessibilidade!** Antes de tudo, procure a orientação de um especialista em acessibilidade.

## Exemplo

<img src="./sample.jpg" width="250" />

> #PraCegoVer #PraTodosVerem: Plano de fundo azul claro com branco. No topo da imagem, lado esquerdo, o logotipo com o brasão Cidade de São Paulo Pessoa com Deficiência. Centralizado, a frase: Você conhece? Abaixo, a ilustração de um mapa, com vários ícones de localização, que sinalizam: assistência social, esporte, saúde, educação e cultura. Mais texto, abaixo, em azul: Mapa da Rede serviços acessíveis para pessoas com deficiência.

## Download dos Dados (com o DVC)

Os dados foram versionados com o [DVC](https://dvc.org/) e utilizam o [Google Drive](https://dvc.org/doc/user-guide/how-to/setup-google-drive-remote#using-a-custom-google-cloud-project-recommended) como remote.<br>
Solicite permissão de acesso ao administrador do projeto (`fabio.beranizo@gmail.com`).<br>
A partir do diretório raiz rode o seguinte comando:

```bash
dvc pull
```

A pasta [data/raw/posts/](./data/raw/posts/) possui os dados brutos, adquiridos com a ferramenta de coleta.<br>
O nome de cada pasta indica a data/hora que o post foi publicado (ex: 202210092332). Dentro da pasta estão as imagens, autor e descrição da publicação (sem formatação).

## Data Collection

O Selenium WebDriver automatiza a coleta de dados de publicações em redes sociais (no momento, apenas Instagram).
A imagem docker `docker.io/fberanizo/pra-todos-verem-data-collection:1.0.0` já possui todas as dependências instaladas e é a forma mais fácil de rodar este passo.

A implementação faz uso do [Geckodriver](https://github.com/mozilla/geckodriver/releases) e requer a instalação do [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/).

```bash
export INSTAGRAM_USERNAME="<seu-nome-de-usuario>"
export INSTAGRAM_PASSWORD="<sua-senha-nao-faca-commit-dela>"
python -m pra_todos_verem.data_collection.collect \
    --query PraTodosVerem \
    --output_path data/raw/posts/ \
    --max_downloads 100
```

Parâmetros:

```
usage: collect.py [-h] [--query QUERY] [--output_path OUTPUT_PATH] [--headless] [--max_downloads MAX_DOWNLOADS]

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

## Notebooks

- [Análise exploratória](./notebooks/0_Journey_Through_Data.ipynb)
- [Categorização em Foto, Arte, Heterogêneo](./notebooks/1_Categorization_Procedure.ipynb)

## Materiais Úteis

- [Dataset #PraCegoVer](https://github.com/larocs/PraCegoVer)
- [Accessibility 4DEVS](https://www.linkedin.com/company/accessibility4devs/about/)
