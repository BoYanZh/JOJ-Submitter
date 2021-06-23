import logging
import os
import time
from enum import Enum
from typing import Dict, Optional, Tuple

import requests
import typer
from bs4 import BeautifulSoup
from pydantic import BaseModel, FilePath, HttpUrl, ValidationError
from requests.models import Response

__version__ = "0.0.1"

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
        post_url = f"{problem_url}/submit"
        html = self.sess.get(post_url).text
        soup = BeautifulSoup(html, features="html.parser")
        result_set = soup.select(
            "#panel > div.main > div > div.medium-9.columns > "
            + "div:nth-child(2) > div.section__body > form > "
            + "div:nth-child(3) > div > input[type=hidden]:nth-child(1)"
        )
        assert len(result_set), "Invalid problem"
        csrf_token = result_set[0].get("value")
        response = self.sess.post(
            post_url,
            files={"code": open(file_path, "rb")},
            data={"csrf_token": csrf_token, "lang": lang},
        )
        return response

    def get_status(self, url: str) -> Tuple[str, int]:
        while True:
            html = self.sess.get(url).text
            soup = BeautifulSoup(html, features="html.parser")
            status = (
                soup.select("#status > div.section__header > h1 > span:nth-child(2)")[0]
                .get_text()
                .strip()
            )
            if status not in ["Waiting", "Compiling", "Fetched", "Running"]:
                break
            else:
                time.sleep(1)
        if status == "Compile Error":
            return status, -1
        result_set = soup.findAll("td", class_="col--status typo")
        return (
            status,
            sum(
                [
                    "Accepted" == result.find_all("span")[1].get_text().strip()
                    for result in result_set
                ]
            ),
        )

    def submit(self, problem_url: str, file_path: str, lang: str, wait: bool) -> None:
        response = self.upload_file(problem_url, file_path, lang)
        assert (
            response.status_code == 200
        ), f"Upload error with code {response.status_code}"
        self.logger.info(f"{file_path} upload succeed, record url {response.url}")
        if wait:
            res = self.get_status(response.url)
            self.logger.info(f"upload result {res[0]}, {res[1]} cases accepted")


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


class Info(BaseModel):
    problem_url: HttpUrl
    compressed_file_path: FilePath
    lang: Language
    sid: str
    wait: bool


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
    sid: str = typer.Argument("", envvar="JOJ_SID"),
    wait: bool = typer.Option(
        False, "-w", "--wait", help="Wait to get the result of submission."
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, help="Show version."
    ),
) -> None:
    try:
        Info(
            problem_url=problem_url,  # type: ignore
            compressed_file_path=compressed_file_path,  # type: ignore
            lang=lang,
            sid=sid,
            wait=wait,
        )
        assert os.path.exists(compressed_file_path), "File not exist"
        worker = JOJSubmitter(sid)
        worker.submit(problem_url, compressed_file_path, lang.value, wait)
    except ValidationError as e:
        logging.error(e)
        exit(1)
    except AssertionError as e:
        logging.error(e.args[0])
        exit(1)


if __name__ == "__main__":
    app()
