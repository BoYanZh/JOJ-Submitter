# JOJ-Submitter

Submit your work to JOJ via CLI. Greatly improve your efficiency when uploading to JOJ.

## Getting Started

### Setup venv (Optional)

```bash
python3 -m venv env
source env/Scripts/activate
```

### Install

```bash
$ pip install joj-submitter
$ joj-submit --help
Usage: joj-submit [OPTIONS] PROBLEM_URL COMPRESSED_FILE_PATH
                  LANG:[c|cc|llvm-c|llvm-cc|cmake|make|ocaml|matlab|cs|pas|jav
                  a|py|py3|octave|php|rs|hs|js|go|rb|other] [SID]

Arguments:
  PROBLEM_URL                     [required]
  COMPRESSED_FILE_PATH            [required]
  LANG:[c|cc|llvm-c|llvm-cc|cmake|make|ocaml|matlab|cs|pas|java|py|py3|octave|php|rs|hs|js|go|rb|other]
                                  other: other | c: C | cc: C++ | llvm-c: C
                                  (Clang, with memory check) | llvm-cc: C++
                                  (Clang++, with memory check) | cmake: CMake
                                  | make: GNU Make | ocaml: OCaml | matlab:
                                  MATLAB | cs: C# | pas: Pascal | java: Java |
                                  py: Python | py3: Python 3 | octave: Octave
                                  | php: PHP | rs: Rust | hs: Haskell | js:
                                  JavaScript | go: Go | rb: Ruby  [required]

  [SID]                           [env var: JOJ_SID;default: ]

Options:
  -w, --wait  Wait to get the result of submission.  [default: False]
  --help      Show this message and exit.
```

### Example

You can first get your JOJ_SID with <https://github.com/BoYanZh/JI-Auth>.

```bash
$ export JOJ_SID=74cd5a48c680fc3616092a12d242aa3dac3780dd1f0ac709740fd5355ed8281c
$ joj-submit https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/homework/5fb1f1379fedcc0006622a06/5fb1ee8b9fedcc00066229d9 ans.zip cc
ans.zip upload succeed, record url https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/records/60e42b17597d580006c571d6
```

You can either visit the record url to check the result or use `-w` flag to wait for the result to be printed in the terminal.

There will be one extra line to inform you the result if `joj-submit` is run with `-w`:

```bash
$ export JOJ_SID=74cd5a48c680fc3616092a12d242aa3dac3780dd1f0ac709740fd5355ed8281c
$ joj-submit -w https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/homework/5fb1f1379fedcc0006622a06/5fb1ee8b9fedcc00066229d9 ans.zip cc
ans.zip upload succeed, record url https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/records/60e42b17597d580006c571d6
upload result Wrong Answer, 8 cases accepted
```
