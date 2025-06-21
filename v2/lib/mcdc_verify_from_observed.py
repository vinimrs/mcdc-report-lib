import ast
from pathlib import Path
import argparse
import mcdc_recorder

# Reuse functions: _get_conditions_from_node, _evaluate_decision, _find_mcdc_pairs
from mcdc_tool import _get_conditions_from_node, _evaluate_decision, _find_mcdc_pairs


def generate_report_from_observed(input_py, output_report):
    # 1) Extrai AST do arquivo original
    code = Path(input_py).read_text(encoding='utf-8')
    tree = ast.parse(code)

    # 2) Puxa tudo que o recorder gravou
    observed = mcdc_recorder.get_observed()

    report_lines = ["Relatório de Verificação MC/DC", "="*30 + "\n"]

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        decision_str = ast.unparse(node.test)
        conditions = sorted(_get_conditions_from_node(node.test))
        if not conditions:
            continue

        # 3) Filtra só as observações que têm o mesmo conjunto de chaves
        relevant = [
            (asg, outcome)
            for (asg, outcome) in observed
            if set(asg.keys()) == set(conditions)
        ]

        # 4) Agrupa para remover duplicatas, mantendo a primeira ocorrência
        unique = {}
        for asg, outcome in relevant:
            key = tuple(sorted(asg.items()))  # e.g. (('ano < 1', True), ('ano > 9999', False))
            if key not in unique:
                unique[key] = outcome

        unique_cases = [(dict(k), unique[k]) for k in unique]

        report_lines.append(f"Decisão: if {decision_str}")
        report_lines.append(f"Condições: {', '.join(conditions)}\n")

        if not unique_cases:
            report_lines.append("Nenhum caso observado para esta decisão.\n")
        else:
            report_lines.append("Casos Observados (únicos):")
            report_lines.append("-"*20)
            for asg, outcome in unique_cases:
                vals = " | ".join(f"{c}={asg[c]}" for c in conditions)
                report_lines.append(f"{vals} | Resultado: {outcome}")

            # 5) Calcule MC/DC só sobre esses casos únicos
            mcdc_cases, covered = _find_mcdc_pairs(conditions, unique_cases)
            missing = set(conditions) - covered
            if not missing:
                report_lines.append("\nMC/DC Coverage: PASS\n")
            else:
                report_lines.append(
                    f"\nMC/DC Coverage: FAIL (faltam: {', '.join(sorted(missing))})\n"
                )
                

        report_lines.append("\n" + "="*30 + "\n")

    # 6) Escreve o relatório final
    with open(output_report, "w", encoding="utf-8") as f:
        print(*report_lines, sep="\n", file=f)    
    print(f"Relatório de verificação gerado: {output_report}")