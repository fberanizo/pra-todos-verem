import mimetypes
import os
from time import sleep
from typing import Generator, Optional

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus


class LinkedInCrawler:
    """
    Crawler para coletar imagens no LinkedIn buscando por publicações de uma query.

    Requer a definição de duas variáveis de ambiente:
    - LINKEDIN_USERNAME
    - LINKEDIN_PASSWORD
    """

    def __init__(
        self,
        query: str,
        save_path: str,
        headless: bool = False,
        max_downloads: int = 10,
    ):
        self.save_path = os.path.join(save_path, "linkedin")
        self.search_url = f"https://www.linkedin.com/feed/hashtag/{query.lower()}/"
        self.logon_url = f"https://www.linkedin.com/uas/login?session_redirect={quote_plus(self.search_url)}&trk=login_reg_redirect"
        self.username = os.environ["LINKEDIN_USERNAME"]
        self.password = os.environ["LINKEDIN_PASSWORD"]
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

        data_id = None
        for _ in range(self.max_downloads):
            try:
                data_id = self.goto_result(data_id)
                self.download_data(data_id)
            except NoSuchElementException:
                print("Unexpected error! Continue to next...")

        self.finalize()

    def launch(self):
        """
        Abre o navegador e acessa a tela de logon do Linkedin.
        """
        self.browser.get(self.logon_url)

    def logon(self):
        """
        Preenche o formulário de logon, envia as informações e aguarda a tela inicial.
        """
        max_wait_in_seconds = 30
        username_element = WebDriverWait(
            self.browser, timeout=max_wait_in_seconds
        ).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='username']")))
        username_element.send_keys(self.username)

        password_element = self.browser.find_element_by_xpath(
            "//input[@id='password']"
        )
        password_element.send_keys(self.password)

        button_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign in']"))
        )
        button_element.click()

        # neste passo, se autenticação de 2 fatores está habilitada, então o usuário precisa autorizar o login

    def goto_result(self, previous_data_id: Optional[str]):
        """
        Procura por um link de uma publicação e o visita para ver os detalhes.
        """
        max_attempts = 3
        max_wait_in_seconds = 10

        for attempt in range(1, max_attempts + 1):
            try:
                if previous_data_id is None:
                    query = "//div[starts-with(@data-id,'urn:li:activity')]"
                else:
                    query = f"//div[@data-id='{previous_data_id}']/../following-sibling::div[{attempt}]//div[starts-with(@data-id,'urn:li:activity')]"

                div_element = WebDriverWait(
                    self.browser, timeout=max_wait_in_seconds
                ).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, query)
                    )
                )
                data_id = div_element.get_attribute("data-id")

                self.browser.execute_script("arguments[0].scrollIntoView();", div_element)

                span_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[@data-id='{data_id}']//span[contains(@class,'feed-shared-inline-show-more-text__see-more-text')]")
                    )
                )
                span_element.click()

                print(f"Visiting post {data_id}")
                return data_id
            except (ElementNotInteractableException, TimeoutException) as e:
                # BUG
                # o wait pode acessar elementos invisíveis. neste caso, ocorre uma ElementNotInteractableException.
                # tenta novamente, no entanto, não garante sucesso.
                print(e)
                print(
                    f"Trying again in a few seconds... Attempt {attempt} of {max_attempts}"
                )
                sleep(2)

    def download_data(self, data_id):
        """
        Faz o download dos dados de interesse da publicação: imagem, texto, autor e data de publicação.
        """
        # cria uma pasta para os dados da publicação
        data_path = os.path.join(self.save_path, data_id.split(":")[-1])
        os.makedirs(data_path, exist_ok=True)

        image_urls = self.find_post_image_urls(data_id)

        for index, image_url in enumerate(image_urls):
            image_filename = f"{index}"
            image_filepath = os.path.join(data_path, image_filename)

            self.download_image(image_url, image_filepath)

        caption = self.find_post_caption(data_id)
        caption_filename = "caption.txt"
        caption_filepath = os.path.join(data_path, caption_filename)
        with open(caption_filepath, "w") as file:
            file.write(caption)

        author = self.find_post_author(data_id)
        author_filename = "author.txt"
        author_filepath = os.path.join(data_path, author_filename)
        with open(author_filepath, "w") as file:
            file.write(author)

        self.browser.find_element_by_xpath("//body").send_keys(Keys.PAGE_DOWN)

    def find_post_image_urls(self, data_id: str) -> Generator[str, None, None]:
        """
        Extrai as URLs das imagens da publicação.

        Returns
        -------
        list
        """
        # procura e salva as imagens da publicação
        max_wait_in_seconds = 10
        for element in WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, f"//div[@data-id='{data_id}']//img")
            )
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

    def find_post_caption(self, data_id: str) -> str:
        """
        Extrai a descrição da publicação.

        Returns
        -------
        str
        """
        max_wait_in_seconds = 10
        div_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f"//div[@data-id='{data_id}']//div[@class='feed-shared-update-v2__description-wrapper']",
                )
            )
        )
        return div_element.text

    def find_post_author(self, data_id: str) -> str:
        """
        Extrai o autor da publicação.

        Returns
        -------
        str
        """
        max_wait_in_seconds = 10
        div_element = WebDriverWait(self.browser, timeout=max_wait_in_seconds).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[@data-id='{data_id}']//span[@class='feed-shared-actor__title']")
            )
        )
        return div_element.text.split("\n")[0]

    def finalize(self):
        """
        Fecha o navegador.
        """
        self.browser.quit()
