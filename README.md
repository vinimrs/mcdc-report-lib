# mcdc-report-lib

Um repositório contendo a biblioteca para geração de um relatório MC/DC a partir de um teste.

## Como usar?

Navegue até a pasta `v2/` e use o comando `make run-verify program=<cominho-programa-a-ser-testado> test=<caminho-para-arquivo-teste>`.
ex: make run-verify program=../placar.py test=../test_placar
windows: python lib/run_and_verify.py placar.py test_placar.py -o instrumented/ -r mcdc_report.txt

Será realizado uma análise e gerado um relatório no caminho `mcdc_report.txt`.

Install dependencies:
pip install -r requirements.txt
