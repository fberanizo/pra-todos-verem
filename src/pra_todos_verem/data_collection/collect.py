"""
Ferramenta de coleta de imagens em publicações #PraTodosVerem.
"""
import argparse
import sys

from pra_todos_verem.data_collection import instagram


DESCRIPTION = "Ferramenta de coleta de imagens em publicações #PraTodosVerem"


def collect(query: str, output_path: str, headless: bool, max_downloads: int):
    """
    Coleta imagens em publicações com Selenium WebDriver.

    Parameters
    ----------
    query : str
    output_path : str
    headless : bool
    max_downloads : int
    """
    instagram.InstagramCrawler(
        query=query,
        save_path=output_path,
        headless=headless,
        max_downloads=max_downloads,
    ).run()


def parse_args(args):
    """
    Recebe argumentos stdin e organiza em parâmetros.
    """
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
    )
    parser.add_argument(
        "--query",
        type=str,
        default="PraTodosVerem",
        help="Query de busca",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="data/raw/posts/",
        help="Diretório onde salvar os dados 'raw' (imagens e textos)",
    )
    parser.add_argument("--headless", action="count", help="Habilita headless browsing")
    parser.add_argument(
        "--max_downloads",
        type=int,
        default=5,
        help="Total de publicações visitadas",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    collect(args.query, args.output_path, args.headless, args.max_downloads)
