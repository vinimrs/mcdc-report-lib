import ast
import astor
from pathlib import Path

# recorder module to collect assignments and results
RECORDER_IMPORT = "import mcdc_recorder\n"


class Instrumenter(ast.NodeTransformer):
    def visit_If(self, node):
        # 1. Extract atomic conditions text and AST nodes
        cond_nodes = []
        def gather(n):
            if isinstance(n, ast.BoolOp):
                for v in n.values:
                    gather(v)
            elif isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not):
                gather(n.operand)
            elif isinstance(n, ast.Compare) or isinstance(n, ast.Name):
                cond_nodes.append(n)
        gather(node.test)

        # 2. Build assignments dict AST
        keys = [ast.Constant(value=ast.unparse(c)) for c in cond_nodes]
        values = [c for c in cond_nodes]
        assign_dict = ast.Assign(
            targets=[ast.Name(id='_mcdc_assignments', ctx=ast.Store())],
            value=ast.Dict(keys=keys, values=values)
        )
        # 3. Call recorder before the if
        call = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(value=ast.Name(id='mcdc_recorder', ctx=ast.Load()),
                                   attr='record_call', ctx=ast.Load()),
                args=[ast.Name(id='_mcdc_assignments', ctx=ast.Load()),
                      ast.Call(func=ast.Name(id='bool', ctx=ast.Load()),
                               args=[node.test], keywords=[])],
                keywords=[]
            )
        )
        # 4. Insert import and instrumentation
        return [
            assign_dict,
            call,
            self.generic_visit(node)
        ]

    def parse_and_instrument(self, src_path: Path) -> ast.Module:
        """Lê, parseia e instrumenta o AST do arquivo em src_path."""
        code = src_path.read_text(encoding='utf-8')
        tree = ast.parse(code)
        new_tree = self.visit(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree
    
    def write_out(self, tree: ast.Module, dst_path: Path):
        """Serializa o AST instrumentado e escreve no caminho dst_path."""
        src = RECORDER_IMPORT + astor.to_source(tree)
        dst_path.write_text(src, encoding='utf-8')

if __name__ == '__main__':
    import argparse, runpy, sys
    parser = argparse.ArgumentParser(description='Instrumenta código para MC/DC')
    parser.add_argument('input', help='módulo Python a instrumentar')
    parser.add_argument('output_dir', help='diretório para salvar código instrumentado')
    args = parser.parse_args()

    src = Path(args.input)
    tree = ast.parse(src.read_text())
    instr = Instrumenter()
    new_tree = instr.visit(tree)
    ast.fix_missing_locations(new_tree)

    # prepend recorder import
    code = RECORDER_IMPORT + astor.to_source(new_tree)

    out_path = Path(args.output_dir) / src.name
    out_path.write_text(code)
    print(f'Instrumentado e salvo em: {out_path}')

    # adiciona output_dir ao sys.path e executa a suite de testes
    sys.path.insert(0, args.output_dir)
    runpy.run_module(src.stem, run_name='__main__')
    # após execução, mcdc_recorder.get_observed() tem os casos
