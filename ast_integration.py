"""
🔗 Phase 3 Integration - AST Engine مع Flask App
================================================
دمج محرك AST مع تطبيق Flask الرئيسي
"""

from flask import Flask, request, jsonify
from ast_engine import ASTEngine, ASTParser, ASTAnalyzer, SemanticValidator
from models import db, User, Challenge, Submission
import json


# =====================================================
# 1️⃣ تحديث دالة التقييم بـ AST Engine
# =====================================================
def evaluate_code_with_ast(code_json: str, required_blocks: str, challenge_type: str,
                           user=None, challenge=None) -> tuple:
    """
    دالة تقييم محسّنة تستخدم AST Engine
    Returns: (result, feedback, ast_analysis)
    """

    feedback_parts = []
    result = "fail"

    try:
        # 1️⃣ تحليل AST
        engine = ASTEngine()
        ast_result = engine.process(code_json)

        if not ast_result["success"]:
            return "fail", f"❌ خطأ في التحليل: {ast_result['error']}", None

        analysis = ast_result["analysis"]
        validation = ast_result["validation"]
        quality = ast_result["overall_quality"]

        # 2️⃣ التغذية الراجعة من التحليل
        feedback_parts.append(f"📊 **تحليل AST:**")
        feedback_parts.append(f"- إجمالي العقد: {analysis['total_nodes']}")
        feedback_parts.append(f"- أقصى عمق تداخل: {analysis['max_nesting']}")
        feedback_parts.append(f"- درجة التعقيد: {analysis['metrics']['complexity_score']}")

        # 3️⃣ التحقق الدلالي
        if validation["errors"]:
            feedback_parts.append("\n❌ **أخطاء دلالية:**")
            for error in validation["errors"]:
                feedback_parts.append(f"  • {error}")

        if validation["warnings"]:
            feedback_parts.append("\n⚠️ **تحذيرات:**")
            for warning in validation["warnings"]:
                feedback_parts.append(f"  • {warning}")

        # 4️⃣ التحقق من المكونات المطلوبة
        if required_blocks:
            required = [b.strip() for b in required_blocks.split(",")]

            # حساب الكتل المستخدمة من AST
            used_blocks = set()
            _collect_block_types(analysis, used_blocks)

            missing = [r for r in required if r not in used_blocks]
            if missing:
                feedback_parts.append(f"\n⚠️ **كتل ناقصة:** {', '.join(missing)}")
            else:
                feedback_parts.append(f"\n✅ **استخدمت جميع الكتل المطلوبة!**")
                result = "success"

        # 5️⃣ جودة الكود
        quality_score = quality.get("score", 0)
        grade = quality.get("grade", "غير معروف")
        feedback_parts.append(f"\n🎯 **جودة الكود:** {grade} ({quality_score}/100)")

        # 6️⃣ المشاكل المحددة
        if analysis["issues"]:
            feedback_parts.append("\n🔍 **مشاكل تم اكتشافها:**")
            for issue in analysis["issues"][:5]:  # أول 5 مشاكل
                feedback_parts.append(f"  • {issue}")

        # 7️⃣ محاولات الطالب السابقة
        if user and challenge:
            attempt_count = Submission.query.filter_by(
                student_id=user.id,
                challenge_id=challenge.id
            ).count()

            if attempt_count == 0:
                feedback_parts.append("\n🎯 هذه أول محاولة لك! حظًا موفقًا.")
            elif attempt_count == 1:
                feedback_parts.append("\n📘 محاولة ثانية ممتازة!")
            elif attempt_count == 2:
                feedback_parts.append("\n💪 أنت تتحسن! استمر بالمحاولة.")
            else:
                feedback_parts.append("\n🌟 إصرارك رائع! لا تستسلم.")

        # تحديد النتيجة النهائية
        if validation["errors"]:
            result = "fail"
        elif validation["warnings"] or analysis["issues"]:
            result = "partial" if result == "success" else "fail"

        feedback_text = "\n".join(feedback_parts)

        return result, feedback_text, ast_result

    except Exception as e:
        return "fail", f"❌ خطأ أثناء التقييم: {str(e)}", None


def _collect_block_types(analysis: dict, block_set: set) -> None:
    """استخراج أنواع الكتل من التحليل"""
    if "loops" in analysis and analysis["loops"]:
        block_set.add("loop")
    if "ifs" in analysis and analysis["ifs"]:
        block_set.add("if")
    if "prints" in analysis and analysis["prints"]:
        block_set.add("print")
    if "variables" in analysis and analysis["variables"]:
        block_set.add("variable")
    if "functions" in analysis and analysis["functions"]:
        block_set.add("function")


# =====================================================
# 2️⃣ New Routes for AST Engine
# =====================================================

def register_ast_routes(app: Flask):
    """تسجيل مسارات AST مع التطبيق"""

    # =====================================================
    # AST Analysis Endpoint
    # =====================================================
    @app.route('/ast/analyze', methods=['POST'])
    def analyze_ast():
        """
        تحليل الكود JSON وإرجاع تحليل AST شامل

        Request:
        {
            "code_json": "{...}",
            "challenge_type": "loop"
        }
        """
        data = request.get_json()
        code_json = data.get('code_json')
        challenge_type = data.get('challenge_type', 'unknown')

        if not code_json:
            return jsonify({'error': 'كود JSON مطلوب'}), 400

        try:
            engine = ASTEngine()
            result = engine.process(code_json)

            return jsonify({
                'success': True,
                'challenge_type': challenge_type,
                'ast_analysis': result,
                'summary': {
                    'total_nodes': result['analysis']['total_nodes'],
                    'complexity': result['analysis']['metrics']['complexity_score'],
                    'quality_score': result['overall_quality']['score'],
                    'grade': result['overall_quality']['grade'],
                    'errors': len(result['validation']['errors']),
                    'warnings': len(result['validation']['warnings'])
                }
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    # =====================================================
    # Semantic Validation Endpoint
    # =====================================================
    @app.route('/ast/validate', methods=['POST'])
    def validate_code():
        """
        التحقق الدلالي من الكود
        """
        data = request.get_json()
        code_json = data.get('code_json')

        if not code_json:
            return jsonify({'error': 'كود JSON مطلوب'}), 400

        try:
            parser = ASTParser()
            ast_root = parser.parse(code_json)

            validator = SemanticValidator(ast_root)
            validation_result = validator.validate()

            return jsonify({
                'success': True,
                'is_valid': validation_result['is_valid'],
                'errors': validation_result['errors'],
                'warnings': validation_result['warnings'],
                'declared_variables': validation_result['declared_variables'],
                'used_variables': validation_result['used_variables'],
                'declared_functions': validation_result['declared_functions'],
                'called_functions': validation_result['called_functions']
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    # =====================================================
    # Code Metrics Endpoint
    # =====================================================
    @app.route('/ast/metrics', methods=['POST'])
    def get_code_metrics():
        """
        الحصول على مقاييس الكود (Metrics)
        """
        data = request.get_json()
        code_json = data.get('code_json')

        if not code_json:
            return jsonify({'error': 'كود JSON مطلوب'}), 400

        try:
            engine = ASTEngine()
            result = engine.process(code_json)

            metrics = result['analysis']['metrics']
            quality = result['overall_quality']

            return jsonify({
                'success': True,
                'metrics': {
                    'total_nodes': metrics['total_loops'] + metrics['total_ifs'] +
                                   metrics['total_prints'] + metrics['total_variables'] +
                                   metrics['total_functions'],
                    'loops': metrics['total_loops'],
                    'conditions': metrics['total_ifs'],
                    'prints': metrics['total_prints'],
                    'variables': metrics['total_variables'],
                    'functions': metrics['total_functions'],
                    'max_nesting': metrics['max_nesting_depth'],
                    'complexity_score': metrics['complexity_score'],
                    'complexity_level': _get_complexity_level(metrics['complexity_score'])
                },
                'quality': quality
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

    # =====================================================
    # Advanced Submission with AST
    # =====================================================
    @app.route('/submit_with_ast', methods=['POST'])
    def submit_with_ast():
        """
        تقديم حل مع تحليل AST متقدم
        """
        data = request.get_json()
        username = data.get('username')
        challenge_id = data.get('challenge_id')
        code_json = data.get('code_json')

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404

        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'التحدي غير موجود'}), 404

        # استدعاء التقييم مع AST
        result, feedback, ast_analysis = evaluate_code_with_ast(
            code_json,
            challenge.required_blocks,
            challenge.challenge_type,
            user=user,
            challenge=challenge
        )

        # حفظ النتيجة
        submission = Submission(
            student_id=user.id,
            challenge_id=challenge.id,
            code_json=code_json,
            result=result,
            feedback_text=feedback
        )
        db.session.add(submission)
        db.session.commit()

        response_data = {
            'message': 'تم حفظ المحاولة بنجاح! ✅',
            'student': user.username,
            'challenge': challenge.title,
            'result': result,
            'feedback': feedback
        }

        # إضافة تفاصيل AST إن وجدت
        if ast_analysis and ast_analysis.get('success'):
            response_data['ast_details'] = {
                'total_nodes': ast_analysis['ast']['total_nodes'],
                'complexity': ast_analysis['analysis']['metrics']['complexity_score'],
                'quality_score': ast_analysis['overall_quality']['score'],
                'grade': ast_analysis['overall_quality']['grade'],
                'semantic_errors': len(ast_analysis['validation']['errors']),
                'warnings': len(ast_analysis['validation']['warnings'])
            }

        return jsonify(response_data), 201

    # =====================================================
    # AST Tree Visualization (JSON)
    # =====================================================
    @app.route('/ast/tree', methods=['POST'])
    def get_ast_tree():
        """
        الحصول على شجرة AST بصيغة قابلة للتصور
        """
        data = request.get_json()
        code_json = data.get('code_json')

        if not code_json:
            return jsonify({'error': 'كود JSON مطلوب'}), 400

        try:
            parser = ASTParser()
            ast_root = parser.parse(code_json)

            tree_json = _convert_ast_to_json(ast_root)

            return jsonify({
                'success': True,
                'tree': tree_json
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400


def _convert_ast_to_json(node) -> dict:
    """تحويل عقدة AST إلى JSON للتصور"""
    return {
        'type': node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
        'line': node.line_number,
        'metadata': node.metadata,
        'children': [_convert_ast_to_json(child) for child in node.children]
    }


def _get_complexity_level(score: float) -> str:
    """تحديد مستوى التعقيد"""
    if score <= 3:
        return "بسيط جداً 🟢"
    elif score <= 6:
        return "متوسط 🟡"
    elif score <= 10:
        return "معقد 🟠"
    else:
        return "معقد جداً 🔴"


# =====================================================
# 3️⃣ Updated Submit Route with AST
# =====================================================
def update_submit_route(app: Flask):
    """تحديث مسار التقديم ليستخدم AST"""

    # احفظ المسار القديم
    original_submit = app.view_functions.get('submit')

    @app.route('/submit', methods=['POST'])
    def submit_updated():
        """مسار التقديم المحدّث مع AST Engine"""
        data = request.get_json()
        username = data.get('username')
        challenge_id = data.get('challenge_id')
        code_json = data.get('code_json')
        use_ast = data.get('use_ast', True)  # استخدام AST افتراضياً

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'المستخدم غير موجود'}), 404

        challenge = Challenge.query.get(challenge_id)
        if not challenge:
            return jsonify({'error': 'التحدي غير موجود'}), 404

        # استخدام AST إذا طُلب ذلك
        if use_ast:
            result, feedback, ast_analysis = evaluate_code_with_ast(
                code_json,
                challenge.required_blocks,
                challenge.challenge_type,
                user=user,
                challenge=challenge
            )
        else:
            # استخدام التقييم القديم
            from app import evaluate_code
            result, feedback = evaluate_code(
                code_json,
                challenge.required_blocks,
                challenge.challenge_type,
                user=user,
                challenge=challenge
            )
            ast_analysis = None

        # حفظ النتيجة
        submission = Submission(
            student_id=user.id,
            challenge_id=challenge.id,
            code_json=code_json,
            result=result,
            feedback_text=feedback
        )
        db.session.add(submission)
        db.session.commit()

        response = {
            'message': 'تم حفظ المحاولة بنجاح! ✅',
            'student': user.username,
            'challenge': challenge.title,
            'result': result,
            'feedback': feedback
        }

        if ast_analysis and ast_analysis.get('success'):
            response['ast_details'] = {
                'total_nodes': ast_analysis['ast']['total_nodes'],
                'complexity': ast_analysis['analysis']['metrics']['complexity_score'],
                'quality_score': ast_analysis['overall_quality']['score'],
                'grade': ast_analysis['overall_quality']['grade']
            }

        return jsonify(response), 201


# =====================================================
# 4️⃣ مثال على كيفية استخدام في app.py
# =====================================================
"""
في ملف app.py الرئيسي، أضف:

from ast_integration import register_ast_routes, update_submit_route

# بعد إنشاء app وتهيئة db
app = Flask(__name__)
# ... config ...
db.init_app(app)

# تسجيل مسارات AST
register_ast_routes(app)

# تحديث مسار التقديم
update_submit_route(app)

if __name__ == '__main__':
    app.run(debug=True)
"""