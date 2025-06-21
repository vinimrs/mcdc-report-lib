import ast
import itertools
from pathlib import Path
import argparse  # Importa o módulo para argumentos de linha de comando

# IMPORTANTE: assignments é o dicionário onde as condições atômicas e seus valores
# são salvos, a condição, que é a chave é atribuída na função _get_conditions_from_node
# já o valor é passado na chamada de _evaluate_decision, passando True e False para
# cada condição

def _get_conditions_from_node(node):
    """Função auxiliar recursiva para extrair condições de um nó do AST."""
    #Quebra condições em partes menores, no caso:
    if isinstance(node, ast.BoolOp):# Operador lógico
        return {c for value in node.values for c in _get_conditions_from_node(value)}
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        # Se for um 'not', olhamos para o que está sendo negado (o operando)
        return _get_conditions_from_node(node.operand)
    elif isinstance(node, ast.Name):# Variável
        return {node.id}
    elif isinstance(node, ast.Compare):# Operador Aritmético
        return {ast.unparse(node)}
    return set()
    # set elimina condições duplicadas, por exemplo "if a and b and a" retornaria apenas "a and b"
    # Depois de atomizar as condições, elas serão adicionadas no dicionário assignments como chave

def _evaluate_decision(node, assignments):
    """Avalia o resultado de uma decisão (nó do AST) com base nos valores de verdade."""
    # Substitui as condições pelos seus respectivos valores, disponíveis no dicionário
    # assignment, testando todas as combinações possíveis, e retornando os resultados
    # por exemplo: para "if a > 10 and not b", substitui os valores e simula if true and not true
    # faz esse teste para todas as combinações de valores
    # ELE NÃO EXECUTA, ELE SIMULA, ele sabe que para um and ser verdadeiro, os
    # dois valores tem que ser também
    if isinstance(node, ast.Name):
        return assignments[node.id]
    if isinstance(node, ast.Compare):
        return assignments[ast.unparse(node)]
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return all(_evaluate_decision(v, assignments) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(_evaluate_decision(v, assignments) for v in node.values)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        # Avalia o operando e inverte o resultado booleano
        return not _evaluate_decision(node.operand, assignments)
    return False


def _find_mcdc_pairs(conditions, truth_table_results):
    """Encontra e retorna o conjunto mínimo de casos de teste que satisfazem MC/DC."""
    # Testa todas as condições com os valores da tabela verdade, retorna o conjunto
    # mínimo onde a saída é alterada pelos valores, por exemplo a condição a or b or c
    # tem 8 combinações possíveis, mas o retorno seria 4 casos
    # Para cada condição, capture apenas o primeiro par que a isola
    minimal_pairs = {}
    covered = set()
    for cond in conditions:
        for asg1, res1 in truth_table_results:
            for asg2, res2 in truth_table_results:
                # resultados diferentes (muda a decisão)
                if res1 == res2:
                    continue
                # esta condição varia
                if asg1[cond] == asg2[cond]:
                    continue
                # todas as outras fixas
                if all(asg1[c] == asg2[c] for c in conditions if c != cond):
                    minimal_pairs[cond] = (asg1, asg2)
                    covered.add(cond)
                    break
            if cond in minimal_pairs:
                break
    # Agora colhe exatamente 2 casos por condição
    unique_cases = {
        frozenset(asg.items())
        for pair in minimal_pairs.values()
        for asg in pair
    }
    tests = [dict(case) for case in unique_cases]
    return tests, covered


def generate_mcdc_tests_from_file(input_py_file: str, output_report_file: str):
    """Função principal que orquestra a análise do arquivo e a geração do relatório."""
    #Percorre o arquivo de entrada, transformando-o em uma árvore de sintaxe
    try:
        code = Path(input_py_file).read_text(encoding='utf-8')
        tree = ast.parse(code)
    except (FileNotFoundError, SyntaxError, UnicodeDecodeError) as e:
        print(f"Erro ao ler ou analisar o arquivo '{input_py_file}': {e}")
        return

    #Percorre a árvore descartando tudo que não for condicional,
    #então chama _get_conditions_from_node para cada condição
    report_lines = ["Relatório de Testes MC/DC", "=" * 30 + "\n"]
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        try:
            decision_str = ast.unparse(node.test)
            conditions = sorted(_get_conditions_from_node(node.test))
        except Exception:
            # Pula nós que não podem ser descompilados, caso ocorra
            continue

        #Esse monstro aqui estrutura bonitinho o arquivo do relatório
        if not conditions:
            continue
        report_lines.append(f"Decisão: if {decision_str}")
        report_lines.append(f"Condições: {', '.join(conditions)}\n")
        truth_values = list(itertools.product([True, False], repeat=len(conditions)))
        truth_table_results = []
        truth_table_results = [
            (dict(zip(conditions, vals)), _evaluate_decision(node.test, dict(zip(conditions, vals))))
            for vals in truth_values
        ]
        # baseado na tabela verdade obtida, busca a independência das condições
        # e retorna somente o conjunto de casos independentes
        mcdc_test_cases, covered_conditions = _find_mcdc_pairs(conditions, truth_table_results)
        if not mcdc_test_cases:
            report_lines.append("Não foi possível gerar pares MC/DC para esta decisão.\n")
        else:
            # Aqui continua montando o relatório
            report_lines.append("Casos de Teste MC/DC:")
            report_lines.append("-" * 20)
            mcdc_test_cases.sort(key=lambda x: [x[c] for c in conditions])
            for i, test_case in enumerate(mcdc_test_cases):
                outcome = _evaluate_decision(node.test, test_case)
                # imprimir sempre em ordem alfabética de condições
                values_str = " | ".join(f"{c}={str(test_case[c]):<5}" for c in conditions)
                report_lines.append(f"Teste {i+1}: {values_str} | Resultado: {outcome}")
        report_lines.append("\n" + "=" * 30 + "\n")

    #Escreve o relatório no arquivo de saída e monstra o nome no terminal
    Path(output_report_file).write_text("\n".join(report_lines), encoding='utf-8')
    print(f"Relatório de testes MC/DC gerado com sucesso em: {output_report_file}")


# --- BLOCO PRINCIPAL ---
if __name__ == '__main__':
    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description="Gera testes MC/DC para declarações 'if' em um arquivo Python."
    )

    # Argumento obrigatório: o arquivo de entrada
    parser.add_argument(
        "input_file",
        help="O caminho para o arquivo .py que será analisado."
    )

    # Argumento opcional: o arquivo de saída
    parser.add_argument(
        "-o", "--output",
        default="relatorio_mcdc.txt",
        help="O nome do arquivo de relatório a ser gerado. (Padrão: relatorio_mcdc.txt)"
    )

    # Analisa os argumentos fornecidos pelo usuário
    args = parser.parse_args()

    # Chama a função principal com os nomes de arquivo obtidos da linha de comando
    generate_mcdc_tests_from_file(args.input_file, args.output)