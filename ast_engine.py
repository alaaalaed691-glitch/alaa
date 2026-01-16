"""
🧠 Phase 3 - AST Engine (Abstract Syntax Tree)
==============================================
محرك التحليل الذكي الذي يحول JSON إلى شجرة تنفيذ حقيقية
والتحقق الدلالي من صحة الكود منطقياً وليس فقط شكلياً
"""

import json
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field


# =====================================================
# 1️⃣ Node Types Definition
# =====================================================
class NodeType(Enum):
    """أنواع العقد في شجرة التحليل"""
    LOOP = "loop"
    IF = "if"
    PRINT = "print"
    VARIABLE = "variable"
    ASSIGNMENT = "assignment"
    FUNCTION = "function"
    FUNCTION_CALL = "function_call"
    RETURN = "return"
    SWITCH = "switch"
    CASE = "case"
    BREAK = "break"
    ROOT = "root"


# =====================================================
# 2️⃣ AST Node Classes
# =====================================================
@dataclass
class ASTNode:
    """عقدة أساسية في شجرة التحليل"""
    node_type: NodeType
    line_number: int = 0
    children: List['ASTNode'] = field(default_factory=list)
    parent: Optional['ASTNode'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: 'ASTNode') -> None:
        """إضافة عقدة فرعية"""
        self.children.append(child)
        child.parent = self

    def get_depth(self) -> int:
        """الحصول على عمق العقدة في الشجرة"""
        if self.parent is None:
            return 0
        return 1 + self.parent.get_depth()

    def __repr__(self):
        return f"<{self.node_type.value}@{self.line_number}>"


@dataclass
class LoopNode(ASTNode):
    """عقدة حلقة (Loop)"""
    iterations: Optional[int] = None  # عدد مرات التكرار
    condition: Optional[str] = None  # شرط الحلقة (for, while)
    has_exit: bool = False  # هل توجد طريقة للخروج من الحلقة؟

    def __post_init__(self):
        self.node_type = NodeType.LOOP


@dataclass
class IfNode(ASTNode):
    """عقدة الشرط (If)"""
    condition: Optional[str] = None
    has_else: bool = False
    else_body: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.IF


@dataclass
class VariableNode(ASTNode):
    """عقدة المتغير (Variable)"""
    var_name: Optional[str] = None
    initial_value: Optional[Any] = None
    data_type: str = "unknown"  # int, string, boolean

    def __post_init__(self):
        self.node_type = NodeType.VARIABLE


@dataclass
class AssignmentNode(ASTNode):
    """عقدة الإسناد (Assignment)"""
    var_name: Optional[str] = None
    value: Optional[Any] = None
    operator: str = "="  # =, +=, -=, etc.

    def __post_init__(self):
        self.node_type = NodeType.ASSIGNMENT


@dataclass
class PrintNode(ASTNode):
    """عقدة الطباعة (Print)"""
    output: Optional[str] = None
    references_variable: Optional[str] = None

    def __post_init__(self):
        self.node_type = NodeType.PRINT


@dataclass
class FunctionNode(ASTNode):
    """عقدة تعريف الدالة (Function Definition)"""
    function_name: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: str = "void"
    body: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.FUNCTION


@dataclass
class FunctionCallNode(ASTNode):
    """عقدة استدعاء الدالة (Function Call)"""
    function_name: Optional[str] = None
    arguments: List[Any] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.FUNCTION_CALL


@dataclass
class SwitchNode(ASTNode):
    """عقدة switch"""
    expression: Optional[str] = None
    cases: Dict[str, List[ASTNode]] = field(default_factory=dict)
    default_body: List[ASTNode] = field(default_factory=list)

    def __post_init__(self):
        self.node_type = NodeType.SWITCH


# =====================================================
# 3️⃣ AST Parser - يحول JSON إلى AST
# =====================================================
class ASTParser:
    """
    محلل JSON → AST
    يقرأ كود JSON من واجهة Blockly ويحوله إلى شجرة تنفيذ
    """

    def __init__(self):
        self.root: Optional[ASTNode] = None
        self.line_counter = 0
        self.variables: Set[str] = set()
        self.functions: Dict[str, FunctionNode] = {}

    def parse(self, code_json: str) -> ASTNode:
        """
        تحويل JSON إلى AST
        Returns: Root node of the AST
        """
        try:
            data = json.loads(code_json)
            blocks = data.get("blocks", [])

            self.root = ASTNode(
                node_type=NodeType.ROOT,
                line_number=0,
                metadata={"total_blocks": len(blocks)}
            )

            for block in blocks:
                node = self._parse_block(block)
                if node:
                    self.root.add_child(node)

            return self.root

        except json.JSONDecodeError as e:
            raise ValueError(f"خطأ في تحليل JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"خطأ في بناء AST: {str(e)}")

    def _parse_block(self, block: Dict[str, Any], parent: Optional[ASTNode] = None) -> Optional[ASTNode]:
        """
        تحليل كتلة واحدة وتحويلها إلى عقدة AST
        """
        self.line_counter += 1
        block_type = block.get("type")

        if block_type == "loop":
            return self._parse_loop(block)
        elif block_type == "if":
            return self._parse_if(block)
        elif block_type == "print":
            return self._parse_print(block)
        elif block_type == "variable":
            return self._parse_variable(block)
        elif block_type == "assignment":
            return self._parse_assignment(block)
        elif block_type == "function":
            return self._parse_function(block)
        elif block_type == "function_call":
            return self._parse_function_call(block)
        elif block_type == "switch":
            return self._parse_switch(block)
        else:
            return None

    def _parse_loop(self, block: Dict[str, Any]) -> LoopNode:
        """تحليل كتلة الحلقة"""
        node = LoopNode(line_number=self.line_counter)
        node.iterations = block.get("iterations")
        node.condition = block.get("condition")

        # تحليل body (محتويات الحلقة)
        body = block.get("body", [])
        for body_block in body:
            child = self._parse_block(body_block, node)
            if child:
                node.add_child(child)

        # التحقق من وجود طريقة للخروج
        node.has_exit = block.get("has_exit", False) or node.condition is not None

        node.metadata = {
            "iterations": node.iterations,
            "condition": node.condition,
            "has_exit": node.has_exit,
            "body_size": len(body)
        }

        return node

    def _parse_if(self, block: Dict[str, Any]) -> IfNode:
        """تحليل كتلة الشرط"""
        node = IfNode(line_number=self.line_counter)
        node.condition = block.get("condition")

        # تحليل body (نعم)
        body = block.get("body", [])
        for body_block in body:
            child = self._parse_block(body_block, node)
            if child:
                node.add_child(child)

        # تحليل else body (لا)
        else_body = block.get("else_body", [])
        if else_body:
            node.has_else = True
            for else_block in else_body:
                child = self._parse_block(else_block, node)
                if child:
                    node.else_body.append(child)

        node.metadata = {
            "condition": node.condition,
            "has_else": node.has_else,
            "body_size": len(body),
            "else_size": len(else_body)
        }

        return node

    def _parse_print(self, block: Dict[str, Any]) -> PrintNode:
        """تحليل كتلة الطباعة"""
        node = PrintNode(line_number=self.line_counter)
        node.output = block.get("text")
        node.references_variable = block.get("references_variable")

        node.metadata = {
            "output": node.output,
            "references_variable": node.references_variable
        }

        return node

    def _parse_variable(self, block: Dict[str, Any]) -> VariableNode:
        """تحليل كتلة المتغير"""
        node = VariableNode(line_number=self.line_counter)
        node.var_name = block.get("name")
        node.initial_value = block.get("value")
        node.data_type = block.get("data_type", "unknown")

        if node.var_name:
            self.variables.add(node.var_name)

        node.metadata = {
            "var_name": node.var_name,
            "initial_value": node.initial_value,
            "data_type": node.data_type
        }

        return node

    def _parse_assignment(self, block: Dict[str, Any]) -> AssignmentNode:
        """تحليل كتلة الإسناد"""
        node = AssignmentNode(line_number=self.line_counter)
        node.var_name = block.get("var_name")
        node.value = block.get("value")
        node.operator = block.get("operator", "=")

        node.metadata = {
            "var_name": node.var_name,
            "value": node.value,
            "operator": node.operator
        }

        return node

    def _parse_function(self, block: Dict[str, Any]) -> FunctionNode:
        """تحليل كتلة تعريف الدالة"""
        node = FunctionNode(line_number=self.line_counter)
        node.function_name = block.get("name")
        node.parameters = block.get("parameters", [])
        node.return_type = block.get("return_type", "void")

        body = block.get("body", [])
        for body_block in body:
            child = self._parse_block(body_block, node)
            if child:
                node.body.append(child)
                node.add_child(child)

        if node.function_name:
            self.functions[node.function_name] = node

        node.metadata = {
            "function_name": node.function_name,
            "parameters": node.parameters,
            "return_type": node.return_type,
            "body_size": len(body)
        }

        return node

    def _parse_function_call(self, block: Dict[str, Any]) -> FunctionCallNode:
        """تحليل كتلة استدعاء الدالة"""
        node = FunctionCallNode(line_number=self.line_counter)
        node.function_name = block.get("function_name")
        node.arguments = block.get("arguments", [])

        node.metadata = {
            "function_name": node.function_name,
            "arguments": node.arguments,
            "arg_count": len(node.arguments)
        }

        return node

    def _parse_switch(self, block: Dict[str, Any]) -> SwitchNode:
        """تحليل كتلة switch"""
        node = SwitchNode(line_number=self.line_counter)
        node.expression = block.get("expression")

        cases = block.get("cases", {})
        for case_value, case_body in cases.items():
            node.cases[case_value] = []
            for case_block in case_body:
                child = self._parse_block(case_block, node)
                if child:
                    node.cases[case_value].append(child)

        default = block.get("default", [])
        for def_block in default:
            child = self._parse_block(def_block, node)
            if child:
                node.default_body.append(child)

        node.metadata = {
            "expression": node.expression,
            "case_count": len(cases),
            "has_default": len(default) > 0
        }

        return node


# =====================================================
# 4️⃣ AST Analyzer - استخراج معلومات مهمة
# =====================================================
class ASTAnalyzer:
    """
    محلل AST - يستخرج معلومات دلالية مهمة من الشجرة
    """

    def __init__(self, ast_root: ASTNode):
        self.root = ast_root
        self.analysis_result = {
            "total_nodes": 0,
            "loops": [],
            "ifs": [],
            "prints": [],
            "variables": [],
            "functions": [],
            "max_nesting": 0,
            "issues": [],
            "warnings": [],
            "metrics": {}
        }

    def analyze(self) -> Dict[str, Any]:
        """تنفيذ التحليل الكامل"""
        self._traverse_tree(self.root, depth=0)
        self._extract_metrics()
        self._validate_logic()
        return self.analysis_result

    def _traverse_tree(self, node: ASTNode, depth: int = 0) -> None:
        """المرور على جميع عقد الشجرة"""
        self.analysis_result["total_nodes"] += 1
        self.analysis_result["max_nesting"] = max(
            self.analysis_result["max_nesting"], depth
        )

        if isinstance(node, LoopNode):
            self._analyze_loop(node, depth)
        elif isinstance(node, IfNode):
            self._analyze_if(node, depth)
        elif isinstance(node, PrintNode):
            self._analyze_print(node)
        elif isinstance(node, VariableNode):
            self._analyze_variable(node)
        elif isinstance(node, FunctionNode):
            self._analyze_function(node, depth)

        # الاستمرار في الأطفال
        for child in node.children:
            self._traverse_tree(child, depth + 1)

    def _analyze_loop(self, node: LoopNode, depth: int) -> None:
        """تحليل الحلقات"""
        loop_data = {
            "line": node.line_number,
            "iterations": node.iterations,
            "condition": node.condition,
            "has_exit": node.has_exit,
            "depth": depth,
            "body_size": len(node.children),
            "issues": []
        }

        # التحقق من المشاكل
        if node.iterations is None and node.condition is None:
            loop_data["issues"].append("❌ حلقة بدون عدد تكرار أو شرط (حلقة لا نهائية محتملة)")

        if node.iterations == 0:
            loop_data["issues"].append("⚠️ الحلقة لن تنفذ (عدد التكرارات = 0)")

        if not node.has_exit and node.condition is None:
            loop_data["issues"].append("⚠️ حلقة بدون طريقة محددة للخروج")

        self.analysis_result["loops"].append(loop_data)

    def _analyze_if(self, node: IfNode, depth: int) -> None:
        """تحليل الشروط"""
        if_data = {
            "line": node.line_number,
            "condition": node.condition,
            "has_else": node.has_else,
            "depth": depth,
            "body_size": len(node.children),
            "else_size": len(node.else_body),
            "issues": []
        }

        # التحقق من المشاكل
        if node.condition is None or node.condition == "":
            if_data["issues"].append("❌ شرط فارغ في كتلة if")

        if len(node.children) == 0 and node.has_else:
            if_data["issues"].append("⚠️ كتلة if فارغة")

        self.analysis_result["ifs"].append(if_data)

    def _analyze_print(self, node: PrintNode) -> None:
        """تحليل الطباعة"""
        print_data = {
            "line": node.line_number,
            "output": node.output,
            "references_variable": node.references_variable,
            "issues": []
        }

        if node.output is None and node.references_variable is None:
            print_data["issues"].append("⚠️ طباعة بدون محتوى")

        self.analysis_result["prints"].append(print_data)

    def _analyze_variable(self, node: VariableNode) -> None:
        """تحليل المتغيرات"""
        var_data = {
            "line": node.line_number,
            "name": node.var_name,
            "data_type": node.data_type,
            "initial_value": node.initial_value,
            "issues": []
        }

        if not node.var_name:
            var_data["issues"].append("❌ متغير بدون اسم")

        self.analysis_result["variables"].append(var_data)

    def _analyze_function(self, node: FunctionNode, depth: int) -> None:
        """تحليل الدوال"""
        func_data = {
            "line": node.line_number,
            "name": node.function_name,
            "parameters": node.parameters,
            "return_type": node.return_type,
            "depth": depth,
            "body_size": len(node.body),
            "issues": []
        }

        if not node.function_name:
            func_data["issues"].append("❌ دالة بدون اسم")

        if len(node.parameters) > 0 and node.return_type == "void":
            func_data["issues"].append("ℹ️ دالة تأخذ معاملات لكن لا ترجع قيمة")

        self.analysis_result["functions"].append(func_data)

    def _extract_metrics(self) -> None:
        """استخراج المقاييس"""
        self.analysis_result["metrics"] = {
            "total_loops": len(self.analysis_result["loops"]),
            "total_ifs": len(self.analysis_result["ifs"]),
            "total_prints": len(self.analysis_result["prints"]),
            "total_variables": len(self.analysis_result["variables"]),
            "total_functions": len(self.analysis_result["functions"]),
            "max_nesting_depth": self.analysis_result["max_nesting"],
            "complexity_score": self._calculate_complexity()
        }

    def _calculate_complexity(self) -> float:
        """حساب درجة التعقيد (Cyclomatic Complexity)"""
        loops = len(self.analysis_result["loops"])
        ifs = len(self.analysis_result["ifs"])
        functions = len(self.analysis_result["functions"])
        nesting = self.analysis_result["max_nesting"]

        complexity = 1 + loops * 2 + ifs + functions * 0.5 + nesting * 0.3
        return round(complexity, 2)

    def _validate_logic(self) -> None:
        """التحقق الدلالي من المنطق"""
        # تجميع جميع المشاكل
        for loop in self.analysis_result["loops"]:
            self.analysis_result["issues"].extend(loop.get("issues", []))

        for if_stmt in self.analysis_result["ifs"]:
            self.analysis_result["issues"].extend(if_stmt.get("issues", []))

        for print_stmt in self.analysis_result["prints"]:
            self.analysis_result["issues"].extend(print_stmt.get("issues", []))

        for var in self.analysis_result["variables"]:
            self.analysis_result["issues"].extend(var.get("issues", []))

        for func in self.analysis_result["functions"]:
            self.analysis_result["issues"].extend(func.get("issues", []))


# =====================================================
# 5️⃣ Semantic Validator - التحقق الدلالي
# =====================================================
class SemanticValidator:
    """
    محقق دلالي متقدم - يتحقق من صحة الكود منطقياً
    ليس فقط شكلياً، بل دلالياً أيضاً
    """

    def __init__(self, ast_root: ASTNode):
        self.root = ast_root
        self.declared_variables: Set[str] = set()
        self.used_variables: Set[str] = set()
        self.declared_functions: Set[str] = set()
        self.called_functions: Set[str] = set()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Dict[str, Any]:
        """تنفيذ التحقق الدلالي"""
        self._collect_declarations(self.root)
        self._check_usages(self.root)
        self._semantic_checks()

        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "declared_variables": list(self.declared_variables),
            "used_variables": list(self.used_variables),
            "declared_functions": list(self.declared_functions),
            "called_functions": list(self.called_functions)
        }

    def _collect_declarations(self, node: ASTNode) -> None:
        """جمع جميع التعريفات (متغيرات، دوال)"""
        if isinstance(node, VariableNode) and node.var_name:
            self.declared_variables.add(node.var_name)

        if isinstance(node, FunctionNode) and node.function_name:
            self.declared_functions.add(node.function_name)

        for child in node.children:
            self._collect_declarations(child)

    def _check_usages(self, node: ASTNode) -> None:
        """التحقق من استخدام المتغيرات والدوال"""
        if isinstance(node, AssignmentNode) and node.var_name:
            self.used_variables.add(node.var_name)

        if isinstance(node, PrintNode) and node.references_variable:
            self.used_variables.add(node.references_variable)

        if isinstance(node, FunctionCallNode) and node.function_name:
            self.called_functions.add(node.function_name)

        for child in node.children:
            self._check_usages(child)

    def _semantic_checks(self) -> None:
        """فحوصات دلالية متقدمة"""
        # التحقق من المتغيرات المستخدمة قبل التعريف
        undefined_vars = self.used_variables - self.declared_variables
        for var in undefined_vars:
            self.errors.append(f"❌ متغير '{var}' مستخدم قبل تعريفه")

        # التحقق من المتغيرات المعرّفة ولم تُستخدم
        unused_vars = self.declared_variables - self.used_variables
        for var in unused_vars:
            self.warnings.append(f"⚠️ متغير '{var}' معرّف لكن لم يُستخدم")

        # التحقق من الدوال المستدعاة قبل التعريف
        undefined_funcs = self.called_functions - self.declared_functions
        for func in undefined_funcs:
            self.errors.append(f"❌ دالة '{func}' مستدعاة قبل تعريفها")

        # التحقق من الدوال المعرّفة ولم تُستدعَ
        unused_funcs = self.declared_functions - self.called_functions
        for func in unused_funcs:
            self.warnings.append(f"⚠️ دالة '{func}' معرّفة لكن لم تُستدعَ")


# =====================================================
# 6️⃣ Main AST Engine Class
# =====================================================
class ASTEngine:
    """
    محرك AST الرئيسي - يجمع كل المكونات معاً
    يوفر واجهة موحدة للعمل مع AST
    """

    def __init__(self):
        self.parser = ASTParser()
        self.ast_root: Optional[ASTNode] = None
        self.analysis: Optional[Dict] = None
        self.validation: Optional[Dict] = None

    def process(self, code_json: str) -> Dict[str, Any]:
        """
        معالجة كاملة للكود من JSON إلى AST مع التحليل والتحقق
        """
        try:
            # 1. تحليل JSON إلى AST
            self.ast_root = self.parser.parse(code_json)

            # 2. تحليل AST
            analyzer = ASTAnalyzer(self.ast_root)
            self.analysis = analyzer.analyze()

            # 3. التحقق الدلالي
            validator = SemanticValidator(self.ast_root)
            self.validation = validator.validate()

            return self._build_report()

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None,
                "validation": None
            }

    def _build_report(self) -> Dict[str, Any]:
        """بناء تقرير شامل"""
        return {
            "success": True,
            "ast": {
                "total_nodes": self.analysis["total_nodes"],
                "root_type": "ROOT"
            },
            "analysis": self.analysis,
            "validation": self.validation,
            "overall_quality": self._calculate_quality_score()
        }

    def _calculate_quality_score(self) -> Dict[str, Any]:
        """حساب درجة جودة الكود"""
        if not self.analysis or not self.validation:
            return {}

        score = 100

        # خصم النقاط للأخطاء
        score -= len(self.validation["errors"]) * 10

        # خصم النقاط للتحذيرات
        score -= len(self.validation["warnings"]) * 3

        # خصم النقاط لمشاكل التحليل
        score -= len(self.analysis["issues"]) * 2

        # خصم النقاط للتعقيد العالي
        complexity = self.analysis["metrics"]["complexity_score"]
        if complexity > 10:
            score -= (complexity - 10) * 1

        score = max(0, score)

        return {
            "score": score,
            "grade": self._grade_score(score),
            "errors_count": len(self.validation["errors"]),
            "warnings_count": len(self.validation["warnings"]),
            "complexity": self.analysis["metrics"]["complexity_score"]
        }

    @staticmethod
    def _grade_score(score: int) -> str:
        """تحديد درجة الجودة"""
        if score >= 90:
            return "ممتاز 🌟"
        elif score >= 75:
            return "جيد جداً 👍"
        elif score >= 60:
            return "جيد 👌"
        elif score >= 45:
            return "مقبول ⚠️"
        else:
            return "ضعيف ❌"


# =====================================================
# مثال على الاستخدام
# =====================================================
if __name__ == "__main__":
    # مثال على كود JSON
    sample_code = """
    {
        "blocks": [
            {
                "type": "variable",
                "name": "i",
                "value": 0,
                "data_type": "int"
            },
            {
                "type": "loop",
                "iterations": 10,
                "condition": "i < 10",
                "body": [
                    {
                        "type": "print",
                        "text": "iteration",
                        "references_variable": "i"
                    }
                ]
            },
            {
                "type": "if",
                "condition": "i > 5",
                "body": [
                    {
                        "type": "print",
                        "text": "greater than 5"
                    }
                ]
            }
        ]
    }
    """

    # تنفيذ المعالجة
    engine = ASTEngine()
    result = engine.process(sample_code)

    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))