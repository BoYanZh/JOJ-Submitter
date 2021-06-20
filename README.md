# JOJ-Submitter

## Getting Started

### Setup venv (Optional)

```bash
python3 -m venv env
source env/Scripts/activate
```

### Install

```bash
pip install joj-submitter
joj-submit --help
```

## Usage

```text
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
