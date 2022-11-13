import logging
import time
from enum import Enum
from typing import IO, AnyStr, Dict, List, Optional

import requests
import typer
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from pydantic import BaseModel, FilePath, HttpUrl, ValidationError
from requests.models import Response

__version__ = "0.0.10"
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


class Detail(BaseModel):
    status: str
    extra_info: str
    time_cost: str
    memory_cost: str
    stderr: str
    out: str
    ans: str


class Record(BaseModel):
    status: str
    accepted_count: int
    score: str
    total_time: str
    peak_memory: str
    details: List[Detail] = []
    compiler_text: str


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
        assert (
            self.sess.get("https://joj.sjtu.edu.cn/login/jaccount").status_code == 200
        ), "Unauthorized SID"

    def upload_file(self, problem_url: str, file: IO[AnyStr], lang: str) -> Response:
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
            files={"code": file},
            data={"csrf_token": csrf_token, "lang": lang},
        )
        return response

    def get_status(self, url: str) -> Record:
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
        summaries = [
            item.get_text() for item in soup.select_one("#summary").find_all("dd")
        ]
        summaries[1] = summaries[1].replace("ms", " ms")
        compiler_text = soup.select_one(".compiler-text").get_text().strip()
        details = []
        accepted_count = 0
        body = soup.select_one("#status").find("div", class_="section__body no-padding")
        table_rows = body.table.tbody.find_all("tr") if body else []
        for detail_tr in table_rows:
            status_soup = detail_tr.find("td", class_="col--status typo")
            status_soup_span = status_soup.find_all("span")
            detail_status = status_soup_span[1].get_text().strip()
            accepted_count += "Accepted" == detail_status
            time_cost = (
                detail_tr.find("td", class_="col--time")
                .get_text()
                .strip()
                .replace("ms", " ms")
            )
            memory_cost = detail_tr.find("td", class_="col--memory").get_text().strip()
            stderr, out, ans, extra_info = "", "", "", ""
            if status_soup.find("a") is not None:  # results are not hidden
                detail_url = "https://joj.sjtu.edu.cn" + status_soup.find("a").get(
                    "href"
                )
                detail_html = self.sess.get(detail_url).text
                detail_soup = BeautifulSoup(detail_html, features="html.parser")
                detail_compiler_text = detail_soup.find_all(
                    "pre", class_="compiler-text"
                )
                stderr = detail_compiler_text[0].get_text().strip()
                out = detail_compiler_text[1].get_text().strip()
                ans = detail_compiler_text[2].get_text().strip()
                extra_info = (
                    status_soup_span[2].get_text().strip()
                    if len(status_soup_span) >= 3
                    else ""
                )
                if extra_info:
                    extra_info = " " + extra_info
            details.append(
                Detail(
                    status=detail_status,
                    extra_info=extra_info,
                    time_cost=time_cost,
                    memory_cost=memory_cost,
                    stderr=stderr,
                    out=out,
                    ans=ans,
                )
            )
        return Record(
            status=status,
            accepted_count=accepted_count,
            score=summaries[0],
            total_time=summaries[1],
            peak_memory=summaries[2],
            details=details,
            compiler_text=compiler_text,
        )

    def submit(
        self,
        problem_url: str,
        file_path: str,
        lang: str,
        no_wait: bool,
        show_all: bool,
        show_compiler_text: bool,
        show_detail: bool,
        output_json: bool,
    ) -> bool:
        file = open(file_path, "rb")
        response = self.upload_file(problem_url, file, lang)
        assert (
            response.status_code == 200
        ), f"Upload error with code {response.status_code}"
        self.logger.info(f"{file_path} upload succeed, record url {response.url}")
        if no_wait:
            return True
        res = self.get_status(response.url)
        if output_json:
            print(res.json())
        fore_color = Fore.RED if res.status != "Accepted" else Fore.GREEN
        self.logger.info(
            f"status: {fore_color}{res.status}{Style.RESET_ALL}, "
            + f"accept number: {Fore.BLUE}{res.accepted_count}{Style.RESET_ALL}, "
            + f"score: {Fore.BLUE}{res.score}{Style.RESET_ALL}, "
            + f"total time: {Fore.BLUE}{res.total_time}{Style.RESET_ALL}, "
            + f"peak memory: {Fore.BLUE}{res.peak_memory}{Style.RESET_ALL}"
        )
        if show_compiler_text and res.compiler_text:
            self.logger.info("compiler text:")
            self.logger.info(res.compiler_text)
        if (res.status != "Accepted" or show_all) and res.details:
            self.logger.info("details:")
            for i, detail in enumerate(res.details):
                status_string: str = ""
                print_status: bool = False
                if show_all and detail.status == "Accepted":
                    status_string = (
                        f"#{i + 1}: {Fore.GREEN}{detail.status}{Style.RESET_ALL}, "
                    )
                    print_status = True
                elif detail.status != "Accepted":
                    status_string = f"#{i + 1}: {Fore.RED}{detail.status}{Style.RESET_ALL}{detail.extra_info}, "
                    print_status = True
                if print_status:
                    self.logger.info(
                        status_string
                        + f"time: {Fore.BLUE}{detail.time_cost}{Style.RESET_ALL}, "
                        + f"memory: {Fore.BLUE}{detail.memory_cost}{Style.RESET_ALL}"
                    )
                    if show_detail:
                        self.logger.info("Stderr:")
                        if detail.stderr:
                            self.logger.info(detail.stderr)
                        self.logger.info("")
                        self.logger.info("Your Answer:")
                        if detail.out:
                            self.logger.info(detail.out)
                        self.logger.info("")
                        self.logger.info("JOJ Answer:")
                        if detail.ans:
                            self.logger.info(detail.ans)
                        self.logger.info("")
        return res.status == "Accepted"


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
    show_all: bool
    show_compiler_text: bool
    show_detail: bool
    output_json: bool


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
    show_all: bool = typer.Option(
        False, "-a", "--all", help="Show detail of all cases, even accepted."
    ),
    show_compiler_text: bool = typer.Option(
        False, "-c", "--compiler", help="Show compiler text section."
    ),
    show_detail: bool = typer.Option(
        False, "-d", "--detail", help="Show stderr, Your answer and JOJ answer section."
    ),
    output_json: bool = typer.Option(
        False, "-j", "--json", help="Print the result in json format to stdout."
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
            show_all=show_all,
            show_compiler_text=show_compiler_text,
            show_detail=show_detail,
            output_json=output_json,
        )
        assert sid and sid != "<EMPTY>", "Empty SID"
        worker = JOJSubmitter(sid)
        accepted = worker.submit(
            problem_url,
            compressed_file_path,
            lang.value,
            no_wait,
            show_all,
            show_compiler_text,
            show_detail,
            output_json,
        )
        raise typer.Exit(not accepted)
    except ValidationError as e:
        logging.error(f"Error: {e}")
        raise typer.Exit(128)
    except AssertionError as e:
        logging.error(f"Error: {e.args[0]}")
        raise typer.Exit(128)


if __name__ == "__main__":
    init()
    app()
