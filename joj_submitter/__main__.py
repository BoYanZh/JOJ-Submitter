import logging
import time
from enum import Enum
from typing import Dict, Optional, Tuple

import requests
import typer
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from pydantic import BaseModel, FilePath, HttpUrl, ValidationError
from requests.models import Response

__version__ = "0.0.2"

app = typer.Typer(add_completion=False)

logging.basicConfig(format="%(message)s", datefmt="%m-%d %H:%M:%S", level=logging.INFO)


class Language(str, Enum):
    c = "c"
    cc = "cc"
    llvm_c = "llvm-c"
    llvm_cc = "llvm-cc"
    cmake = "cmake"
    make = "make"
    ocaml = "ocaml"
    matlab = "matlab"
    cs = "cs"
    pas = "pas"
    java = "java"
    py = "py"
    py3 = "py3"
    octave = "octave"
    php = "php"
    rs = "rs"
    hs = "hs"
    js = "js"
    go = "go"
    rb = "rb"
    other = "other"


class JOJSubmitter:
    def __init__(self, sid: str, logger: logging.Logger = logging.getLogger()) -> None:
        def create_sess(cookies: Dict[str, str]) -> requests.Session:
            s = requests.Session()
            s.cookies.update(cookies)
            return s

        self.sess = create_sess(
            cookies={"sid": sid, "JSESSIONID": "dummy", "save": "1"}
        )
        self.logger = logger
        html = self.sess.get("https://joj.sjtu.edu.cn").text
        assert "JAccount Login" not in html, "Unauthorized SID"

    def upload_file(self, problem_url: str, file_path: str, lang: str) -> Response:
        post_url = problem_url
        if not post_url.endswith("/submit"):
            post_url += "/submit"
        html = self.sess.get(post_url).text
        soup = BeautifulSoup(html, features="html.parser")
        csrf_token_node = soup.find("input", {"name": "csrf_token"})
        assert csrf_token_node, "Invalid problem"
        csrf_token = csrf_token_node.get("value")
        response = self.sess.post(
            post_url,
            files={"code": open(file_path, "rb")},
            data={"csrf_token": csrf_token, "lang": lang},
        )
        return response

    def get_status(self, url: str) -> Tuple[str, int, str, str, str, str]:
        while True:
            html = self.sess.get(url).text
            soup = BeautifulSoup(html, features="html.parser")
            status = (
                soup.select_one(
                    "#status > div.section__header > h1 > span:nth-child(2)"
                )
                .get_text()
                .strip()
            )
            if status not in ["Waiting", "Compiling", "Fetched", "Running"]:
                break
            else:
                time.sleep(1)
        result_set = soup.find_all("td", class_="col--status typo")
        accepted_count = 0
        for result in result_set:
            accepted_count += (
                "Accepted" == result.find_all("span")[1].get_text().strip()
            )
        summaries = [
            item.get_text() for item in soup.select_one("#summary").find_all("dd")
        ]
        summaries[1] = summaries[1].replace("ms", " ms")
        compiler_text = soup.select_one(".compiler-text").get_text().strip()
        return (
            status,
            accepted_count,
            summaries[0],
            summaries[1],
            summaries[2],
            compiler_text,
        )

    def submit(
        self, problem_url: str, file_path: str, lang: str, no_wait: bool
    ) -> None:
        response = self.upload_file(problem_url, file_path, lang)
        assert (
            response.status_code == 200
        ), f"Upload error with code {response.status_code}"
        self.logger.info(f"{file_path} upload succeed, record url {response.url}")
        if no_wait:
            return
        res = self.get_status(response.url)
        fore_color = Fore.RED if res[0] != "Accepted" else Fore.GREEN
        self.logger.info(
            f"status: {fore_color}{res[0]}{Style.RESET_ALL}, "
            + f"accept number: {Fore.BLUE}{res[1]}{Style.RESET_ALL}, "
            + f"score: {Fore.BLUE}{res[2]}{Style.RESET_ALL}, "
            + f"total time: {Fore.BLUE}{res[3]}{Style.RESET_ALL}, "
            + f"peak memory: {Fore.BLUE}{res[4]}{Style.RESET_ALL}"
        )
        if res[5]:
            self.logger.info("compiler text:")
            self.logger.info(res[5])


lang_dict = {
    "other": "other",
    "c": "C",
    "cc": "C++",
    "llvm-c": "C (Clang, with memory check)",
    "llvm-cc": "C++ (Clang++, with memory check)",
    "cmake": "CMake",
    "make": "GNU Make",
    "ocaml": "OCaml",
    "matlab": "MATLAB",
    "cs": "C#",
    "pas": "Pascal",
    "java": "Java",
    "py": "Python",
    "py3": "Python 3",
    "octave": "Octave",
    "php": "PHP",
    "rs": "Rust",
    "hs": "Haskell",
    "js": "JavaScript",
    "go": "Go",
    "rb": "Ruby",
}


class arguments(BaseModel):
    problem_url: HttpUrl
    compressed_file_path: FilePath
    lang: Language
    sid: str
    no_wait: bool


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def main(
    problem_url: str,
    compressed_file_path: str,
    lang: Language = typer.Argument(
        ..., help=" | ".join([f"{k}: {v}" for k, v in lang_dict.items()])
    ),
    sid: str = typer.Argument("<EMPTY>", envvar="JOJ_SID"),
    no_wait: bool = typer.Option(
        False, "-s", "--skip", help="Return immediately once uploaded."
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version."
    ),
) -> None:
    try:
        arguments(
            problem_url=problem_url,  # type: ignore
            compressed_file_path=compressed_file_path,  # type: ignore
            lang=lang,
            sid=sid,
            no_wait=no_wait,
        )
        assert sid and sid != "<EMPTY>", "Empty SID"
        worker = JOJSubmitter(sid)
        worker.submit(problem_url, compressed_file_path, lang.value, no_wait)
    except ValidationError as e:
        logging.error(f"Error: {e}")
        exit(1)
    except AssertionError as e:
        logging.error(f"Error: {e.args[0]}")
        exit(1)


if __name__ == "__main__":
    init()
    app()
