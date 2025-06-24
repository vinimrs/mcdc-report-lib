# mcdc-report-lib

Software para geração de relatórios MC/DC.

## Como usar?

Install dependencies:
pip install -r requirements.txt

Run:
python lib/run_and_verify.py inputFiles/placar.py inputFiles/test_placar.py -o instrumented/ -r output/placar_report.txt

python lib/run_and_verify.py placar.py test_placar.py -o instrumented/ -r mcdc_report.txt


Será gerado um relatório no caminho `mcdc_report.txt`.

