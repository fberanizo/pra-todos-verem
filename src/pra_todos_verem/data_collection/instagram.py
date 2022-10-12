import mimetypes
import os
from typing import Generator, Optional

import dateutil.parser
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus


class InstagramCrawler:
    """
    Crawler para coletar imagens no Instagram buscando por publicações de uma query.

    Requer a definição de duas variáveis de ambiente:
    - INSTAGRAM_USERNAME
    - INSTAGRAM_PASSWORD
    """

    def __init__(
        self,
        query: str,
        save_path: str,
        headless: bool = False,
        max_downloads: int = 10,
    ):
        self.save_path = save_path
        self.search_url = quote_plus(
            f"https://www.instagram.com/explore/tags/{query.lower()}/"
        )
        self.logon_url = (
            f"https://www.instagram.com/accounts/login/?next={self.search_url}"
        )
        self.username = os.environ["INSTAGRAM_USERNAME"]
        self.password = os.environ["INSTAGRAM_PASSWORD"]
        self.max_downloads = max_downloads

        # headless=True permite rodar a automação em um processo de CI, sem um display
        options = Options()
        options.headless = headless
        self.browser = webdriver.Firefox(options=options)

    def run(self):
        """
        Orquestra o webcrawler realizando navegação e download dos dados de interesse.
        """
        self.launch()
        self.logon()

        for index in range(0, self.max_downloads):
            try:
                print(f"Visiting post {index + 1} of {self.max_downloads}", sep=" ")
                self.goto_result(index)
                self.download_data()
                # retorna aos resultados para visitar a próxima publicação
                self.browser.back()
            except NoSuchElementException:
                print("Unexpected error! Continue to next...")

        self.finalize()

    def launch(self):
        """
        Abre o navegador e acessa a tela de logon do Instagram.
        """
        self.browser.get(self.logon_url)

    def logon(self):
        """
        Preenche o formulário de logon, envia as informações e aguarda a tela inicial.
        """
        max_wait_in_seconds = 30
        username_element = WebDriverWait(
            self.browser, timeout=max_wait_in_seconds
        ).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='username']")))
        username_element.send_keys(self.username)

        # uma ação de espera é necessária porque input type=password leva alguns milisegundos para carregar na tela.
        # se não carregar em até 10 segundos, interrompe o teste com uma exceção
        password_element = self.browser.find_element_by_xpath(
            "//input[@name='password']"
        )
        password_element.send_keys(self.password)

        button_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable((By.XPATH, "//button[./div/text()='Log In']"))
        )
        button_element.click()

        # neste passo, se autenticação de 2 fatores está habilitada, então o usuário precisa autorizar o login

    def goto_result(self, index: int):
        """
        Procura por um link de uma publicação e o visita para ver os detalhes.
        """
        # uma ação de espera é necessária até que os resultados da busca estejam prontos para uso.
        try:
            max_wait_in_seconds = 60
            result_element = WebDriverWait(
                self.browser, timeout=max_wait_in_seconds
            ).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//article[last()]//a[starts-with(@href, '/p/')]")
                )
            )[
                index
            ]

            if result_element.is_displayed():
                post_url = result_element.get_attribute("href")
                print(post_url)
                self.browser.get(post_url)

        except IndexError:
            print(f"All results were visited. Exiting...")

    def download_data(self):
        """
        Faz o download dos dados de interesse da publicação: imagem, texto, autor e data de publicação.
        """
        post_datetime_str = self.find_post_datetime()

        # cria uma pasta para os dados da publicação
        data_path = os.path.join(self.save_path, post_datetime_str)
        os.makedirs(data_path, exist_ok=True)

        image_urls = self.find_post_image_urls()

        for index, image_url in enumerate(image_urls):
            image_filename = f"{index}"
            image_filepath = os.path.join(data_path, image_filename)

            self.download_image(image_url, image_filepath)

        caption = self.find_post_caption()
        caption_filename = "caption.txt"
        caption_filepath = os.path.join(data_path, caption_filename)
        with open(caption_filepath, "w") as file:
            file.write(caption)

        author = self.find_post_author()
        author_filename = "author.txt"
        author_filepath = os.path.join(data_path, author_filename)
        with open(author_filepath, "w") as file:
            file.write(author)

    def find_post_datetime(self) -> str:
        """
        Extrai a data de publicação.

        Returns
        -------
        str
        """
        max_wait_in_seconds = 30
        time_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable((By.XPATH, "//article[last()]//time"))
        )
        post_datetime_str = time_element.get_attribute("datetime")

        post_datetime = dateutil.parser.parse(post_datetime_str)
        return post_datetime.strftime("%Y%m%d%H%M")

    def find_post_image_urls(self) -> Generator[str, None, None]:
        """
        Extrai as URLs das imagens da publicação.

        Returns
        -------
        list
        """
        # procura e salva as imagens da publicação
        max_wait_in_seconds = 10
        for element in WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.presence_of_all_elements_located((By.XPATH, "//article[last()]//img"))
        ):
            image_url = element.get_attribute("src")
            yield image_url

    def download_image(self, image_url: Optional[str], image_filepath: str):
        """
        Faz o download de uma imagem a partir de uma URL.

        Utiliza os cookies do Selenium para não precisar passar pelo login.

        Parameters
        ----------
        image_url : str, optional
        image_filepath : str
        """
        # algumas vezes o elemento img tem src definido. apenas retornamos neste caso
        if not isinstance(image_url, str):
            return

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        }
        s = requests.session()
        s.headers.update(headers)

        for cookie in self.browser.get_cookies():
            c = {cookie["name"]: cookie["value"]}
            s.cookies.update(c)

        r = s.get(image_url, allow_redirects=True)
        extension = mimetypes.guess_extension(
            r.headers.get("content-type", "").split(";")[0]
        )
        image_filepath = f"{image_filepath}{extension}"
        with open(image_filepath, "wb") as file:
            file.write(r.content)

    def find_post_caption(self) -> str:
        """
        Extrai a descrição da publicação.

        Returns
        -------
        str
        """
        max_wait_in_seconds = 30
        span_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//article[last()]//h2/following-sibling::div/span")
            )
        )
        return span_element.text

    def find_post_author(self) -> str:
        """
        Extrai o autor da publicação.

        Returns
        -------
        str
        """
        max_wait_in_seconds = 30
        link_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable((By.XPATH, "//article[last()]//h2//a"))
        )
        return link_element.text

    def finalize(self):
        """
        Fecha o navegador.
        """
        self.browser.quit()
