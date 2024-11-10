import ast

class PythonToCTranslator(ast.NodeVisitor):
    def __init__(self):
        self.c_code = []
        self.indent_level = 0
    
    def indent(self):
        return '    ' * self.indent_level
    
    def visit_Module(self, node):
        self.c_code.append("#include <stdio.h>")
        self.c_code.append("int main() {")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.c_code.append("    return 0;")
        self.c_code.append("}")
    
    def visit_Assign(self, node):
        target = node.targets[0].id
        value = self.visit(node.value)
        self.c_code.append(f"{self.indent()}{target} = {value};")
    
    def visit_Name(self, node):
        return node.id
    
    def visit_Constant(self, node):
        return str(node.value)
    
    def visit_Expr(self, node):
        expr = self.visit(node.value)
        self.c_code.append(f"{self.indent()}{expr};")
    
    def visit_Call(self, node):
        # Handle print function
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            args = ", ".join(self.visit(arg) for arg in node.args)
            return f'printf("{args}\\n");'
        return ""
    
    def visit_If(self, node):
        test = self.visit(node.test)
        self.c_code.append(f"{self.indent()}if ({test}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.c_code.append(f"{self.indent()}}}")
        if node.orelse:
            self.c_code.append(f"{self.indent()}else {{")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.c_code.append(f"{self.indent()}}}")
    
    def visit_Compare(self, node):
        left = self.visit(node.left)
        ops = {ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}
        op = ops[type(node.ops[0])]
        right = self.visit(node.comparators[0])
        return f"{left} {op} {right}"
    
    def visit_For(self, node):
        if isinstance(node.iter, ast.Call) and node.iter.func.id == "range":
            start = self.visit(node.iter.args[0]) if len(node.iter.args) > 1 else "0"
            end = self.visit(node.iter.args[1]) if len(node.iter.args) > 1 else self.visit(node.iter.args[0])
            var = node.target.id
            self.c_code.append(f"{self.indent()}for (int {var} = {start}; {var} < {end}; {var}++) {{")
            self.indent_level += 1
            for stmt in node.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.c_code.append(f"{self.indent()}}}")
    
    def translate(self, python_code):
        tree = ast.parse(python_code)
        self.visit(tree)
        return "\n".join(self.c_code)

    def translate_file(self, input_file, output_file):
        # Read Python code from the input file
        with open(input_file, 'r') as f:
            python_code = f.read()
        
        # Translate Python code to C
        c_code = self.translate(python_code)
        
        # Write C code to the output file
        with open(output_file, 'w') as f:
            f.write(c_code)
        print(f"Traduccion completa. Codigo Python Traducido a {output_file}")

# Ejemplo de uso con archivos
input_file = 'codigo_python.py' 
output_file = 'codigo_c.c'      

translator = PythonToCTranslator()
translator.translate_file(input_file, output_file)
