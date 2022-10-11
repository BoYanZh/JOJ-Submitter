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

  [SID]                           [env var: JOJ_SID;default: <EMPTY>]

Options:
  -s, --skip  Return immediately once uploaded.  [default: False]
  -a, --all     Show detail of all cases, even accepted.  [default: False]
  -d, --detail  Show stderr, Your answer and JOJ answer section.  [default: False]
  -j, --json    Print the result in json format to stdout.  [default: False]
  --version   Show version.
  --help      Show this message and exit.
```

### Example

First get your JOJ_SID with <https://github.com/BoYanZh/JI-Auth> or via browser on your own.

Replace `<YOUR_JOJ_SID>` in the following methods with your actual SID.

#### Method 1 Call directly via CLI

1. Mark `JOJ_SID` shell variable.
2. Run `joj-submit` with arguments.

```bash
$ export JOJ_SID=<YOUR_JOJ_SID>
$ joj-submit https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/homework/5fb1f1379fedcc0006622a06/5fb1ee8b9fedcc00066229d9 ans.zip cc
ans.zip upload succeed, record url https://joj.sjtu.edu.cn/d/vg101_fall_2020_manuel/records/60e42b17597d580006c571d6
status: Accepted, accept number: 49, score: 980, total time: 6167 ms, peak memory: 33.684 MiB
```

#### Method 2 Call from Makefile

1. Add `export JOJ_SID=<YOUR_JOJ_SID>` to your `~/.bashrc` or `~/.zshrc`. Do not forget to restart the shell to load the variable.
2. Edit and add this Makefile to your project <https://gist.github.com/BoYanZh/6ee60b76f0fc70389c9ac0988fd16885>.
3. Run `make joj`.

```bash
$ make joj
tar -cvzf p4-src.tar.gz main.cpp
main.cpp
joj-submit https://joj.sjtu.edu.cn/d/ve281_summer_2021_hongyi/homework/60ed8820597d590006d91e44/60ed869b597d590006d91dad p4-src.tar.gz cc -w
p4-src.tar.gz upload succeed, record url https://joj.sjtu.edu.cn/d/ve281_summer_2021_hongyi/records/60f4451537f07210064b8c20
status: Accepted, accept number: 49, score: 980, total time: 6167 ms, peak memory: 33.684 MiB
```

## Acknowledgements

- [VG101-Grade-Helper](https://github.com/BoYanZh/VG101-Grade-Helper)
