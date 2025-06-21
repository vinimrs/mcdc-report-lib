#!/usr/bin/env python3
import ast, astor, runpy, shutil, subprocess, sys, os
from pathlib import Path
import argparse
import json
from instrumenter import Instrumenter, RECORDER_IMPORT
import mcdc_recorder
from mcdc_verify_from_observed import generate_report_from_observed

def main():
    parser = argparse.ArgumentParser(
        description="Instrumenta, executa testes e verifica cobertura MC/DC"
    )
    parser.add_argument("program", help="Arquivo .py a ser instrumentado")
    parser.add_argument("test_suite", help="Arquivo .py de testes (pytest ou script)")
    parser.add_argument("-o", "--outdir", default="instrumented", help="Pasta para o código instrumentado")
    parser.add_argument("-r", "--report", default="mcdc_report.txt", help="Relatório de saída")
    args = parser.parse_args()

    # 1) Prepara caminhos absolutos
    program_src = Path(args.program).resolve()
    test_src    = Path(args.test_suite).resolve()
    outdir      = Path(args.outdir).resolve()
    outdir.mkdir(exist_ok=True)

    # 2) Instrumenta programa.py
    src_code = program_src.read_text(encoding='utf-8')
    tree     = ast.parse(src_code)
    instr    = Instrumenter()
    new_tree = instr.visit(tree)
    ast.fix_missing_locations(new_tree)
    instrumented_code = RECORDER_IMPORT + astor.to_source(new_tree)

    instr_file = outdir / program_src.name
    instr_file.write_text(instrumented_code, encoding='utf-8')

    # 3) Copia o recorder e o teste para instrumented/
    shutil.copy(Path(__file__).parent / "mcdc_recorder.py", outdir / "mcdc_recorder.py")
    shutil.copy(test_src, outdir / test_src.name)

    # 4) Limpa observed e configura ambiente
    mcdc_recorder._observed.clear()
    env = os.environ.copy()
    # PYTHONPATH: primeiro instrumented/, depois raiz
    env["PYTHONPATH"] = str(outdir) + os.pathsep + str(Path(__file__).parent.resolve())

    # 5) Roda pytest via subprocess dentro de instrumented/
    subprocess.run(
        ["pytest", test_src.name, "-q", "-s", "--disable-warnings"],
        cwd=outdir,
        check=True,
        env=env
    )

    obs_file = outdir / 'observed.json'
    if obs_file.exists():
        data = json.loads(obs_file.read_text(encoding='utf-8'))
        # repovoa o recorder do processo principal
        mcdc_recorder._observed = [ (dict(assign), res) for assign,res in data ]
    else:
        print("⚠️  Não achei observed.json em", obs_file, file=sys.stderr)

    # 6) Gera o relatório MC/DC a partir dos casos observados
    # Pode apontar para o arquivo original ou instrumentado; usamos o original para extrair AST
    generate_report_from_observed(str(program_src), args.report)

    # 8) Limpa a pasta instrumented
    shutil.rmtree(outdir)
            
if __name__ == "__main__":
    main()