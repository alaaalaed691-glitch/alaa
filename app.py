from flask import Flask, request, jsonify, render_template
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Challenge, Submission, TestCase, SolutionTemplate

print('[boot] app_file:', os.path.abspath(__file__))

app = Flask(__name__)

# Disable caching in development to avoid stale JS/CSS
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# SQLite config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database if not exists
with app.app_context():
    db.create_all()

    try:
        uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        db_abs_path = None
        if isinstance(uri, str) and uri.startswith('sqlite:///'):
            rel = uri.replace('sqlite:///', '', 1)
            db_abs_path = os.path.abspath(rel)
        print('[seed] db_uri:', uri)
        print('[seed] db_path:', db_abs_path if db_abs_path else '(non-sqlite-or-unknown)')

        before_count = Challenge.query.count()
        print('[seed] before:', before_count)
        samples = [
                {
                    'title': 'التحدي 1: اطبع Hello خمس مرات',
                    'description': 'اطبع كلمة Hello خمس مرات باستخدام حلقة while وعدّاد.',
                    'required_blocks': ['init_variable', 'while_loop', 'print_text', 'increment'],
                    'concept': 'loop',
                    'difficulty': 'easy'
                },
                {
                    'title': 'التحدي 2: عدّ من 1 إلى 5',
                    'description': 'اكتب برنامجًا يطبع الأعداد من 1 إلى 5 باستخدام while.',
                    'required_blocks': ['init_variable', 'while_loop', 'print_text', 'increment', 'compare'],
                    'concept': 'loop',
                    'difficulty': 'easy'
                },
                {
                    'title': 'التحدي 3: إذا كان العدد أكبر من 10',
                    'description': 'إذا كان العدد أكبر من 10 اطبع "Big" وإلا اطبع "Small".',
                    'required_blocks': ['init_variable', 'if_condition', 'compare', 'print_text'],
                    'concept': 'condition',
                    'difficulty': 'easy'
                },
                {
                    'title': 'التحدي 4: اطبع مجموع عددين',
                    'description': 'احسب مجموع عددين ثم اطبع الناتج.',
                    'required_blocks': ['init_variable', 'add_subtract', 'print_text', 'number_value'],
                    'concept': 'math',
                    'difficulty': 'easy'
                },
                {
                    'title': 'التحدي 5: اطبع كلمة مكررة',
                    'description': 'اطبع كلمة "Hi" ثلاث مرات باستخدام while.',
                    'required_blocks': ['init_variable', 'while_loop', 'print_text', 'increment', 'text_value'],
                    'concept': 'loop',
                    'difficulty': 'easy'
                },
                {
                    'title': 'التحدي 6: هل العدد زوجي؟',
                    'description': 'تحقق إن كان العدد زوجيًا (باقي القسمة على 2 يساوي 0) ثم اطبع النتيجة.',
                    'required_blocks': ['init_variable', 'if_condition', 'compare', 'add_subtract', 'print_text', 'number_value'],
                    'concept': 'condition',
                    'difficulty': 'medium'
                },
                {
                    'title': 'التحدي 7: أنشئ قائمة واطبع طولها',
                    'description': 'أنشئ قائمة فيها 3 عناصر ثم اطبع طول القائمة.',
                    'required_blocks': ['list_create', 'list_length', 'print_text'],
                    'concept': 'lists',
                    'difficulty': 'medium'
                },
                {
                    'title': 'التحدي 8: اطبع أول عنصر من قائمة',
                    'description': 'أنشئ قائمة ثم اطبع أول عنصر فيها.',
                    'required_blocks': ['list_create', 'list_get', 'print_text'],
                    'concept': 'lists',
                    'difficulty': 'medium'
                },
                {
                    'title': 'التحدي 9: غيّر قيمة متغير',
                    'description': 'أنشئ متغيرًا بقيمة 0 ثم زِده بمقدار 1 مرتين ثم اطبع القيمة النهائية.',
                    'required_blocks': ['init_variable', 'increment', 'print_text', 'number_value'],
                    'concept': 'variables',
                    'difficulty': 'medium'
                },
                {
                    'title': 'التحدي 10: عدّ تنازليًا',
                    'description': 'اطبع الأعداد من 5 إلى 1 باستخدام while (تنازلي).',
                    'required_blocks': ['init_variable', 'while_loop', 'print_text', 'add_subtract', 'compare', 'number_value'],
                    'concept': 'loop',
                    'difficulty': 'hard'
                }
            ]

        added = 0
        for s in samples:
            exists = Challenge.query.filter_by(title=s['title']).first()
            if exists:
                continue
            db.session.add(Challenge(
                title=s['title'],
                description=s['description'],
                required_blocks=json.dumps(s['required_blocks'], ensure_ascii=False),
                concept=s.get('concept'),
                difficulty=s.get('difficulty'),
                json_template='{}'
            ))
            added += 1
        if added:
            db.session.commit()
        after_count = Challenge.query.count()
        print('[seed] added:', added)
        print('[seed] after:', after_count)
    except Exception:
        print('[seed] FAILED')
        import traceback
        traceback.print_exc()
        db.session.rollback()


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# =====================================================
# Home Route
# =====================================================
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api')
def api_home():
    return jsonify({"message": "Welcome to Smart Platform API"})


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')


@app.route('/challenges_ui', methods=['GET'])
def challenges_page():
    return render_template('challenges.html')


@app.route('/challenge', methods=['GET'])
def challenge_page():
    return render_template('challenge.html')


@app.route('/teacher', methods=['GET'])
def teacher_page():
    return render_template('teacher.html')


@app.route('/blockly-demo', methods=['GET'])
def blockly_demo_page():
    return render_template('blockly_demo.html')


@app.route('/blockly-demo/', methods=['GET'])
def blockly_demo_page_slash():
    return render_template('blockly_demo.html')


@app.route('/_routes', methods=['GET'])
def list_routes():
    rules = []
    for rule in app.url_map.iter_rules():
        methods = sorted([m for m in rule.methods if m not in ('HEAD', 'OPTIONS')])
        rules.append({'rule': str(rule), 'endpoint': rule.endpoint, 'methods': methods})
    rules.sort(key=lambda r: r['rule'])
    return jsonify(rules)


@app.route('/_whoami', methods=['GET'])
def whoami():
    return jsonify({
        'app_file': os.path.abspath(__file__),
        'db_uri': app.config.get('SQLALCHEMY_DATABASE_URI')
    })


# =====================================================
# 1️⃣ Registration Endpoint (with Role)
# =====================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')  # default = student

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': f'User {username} registered as {role} successfully!'}), 201


# =====================================================
# 2️⃣ Login Endpoint
# =====================================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'error': 'Invalid username or password'}), 401

    return jsonify({'message': f'Welcome back, {username}!', 'role': user.role}), 200


# =====================================================
# 3️⃣ Get All Users (for testing)
# =====================================================
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role} for u in users])


# =====================================================
# Helper function: Check role manually (simple version)
# =====================================================
def check_role(user_role, allowed_roles):
    if user_role not in allowed_roles and user_role != 'admin':
        return False
    return True


def get_user_from_payload(data):
    username = None
    if isinstance(data, dict):
        username = data.get('username')
    if not username:
        return None
    return User.query.filter_by(username=username).first()


# =====================================================
# 4️⃣ Create a Challenge (Teacher only)
# =====================================================
@app.route('/add_challenge', methods=['POST'])
def add_challenge():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    required_blocks = data.get('required_blocks')
    concept = data.get('concept', 'loop')
    difficulty = data.get('difficulty', 'easy')
    json_template = data.get('json_template', '{}')

    if not title or required_blocks is None:
        return jsonify({'error': 'Title and required_blocks are required'}), 400

    # Allow required_blocks to be either a comma-separated string or a JSON array.
    # We store arrays as JSON text to keep the DB schema unchanged.
    if isinstance(required_blocks, list):
        required_blocks = json.dumps(required_blocks, ensure_ascii=False)

    new_challenge = Challenge(
        title=title,
        description=description,
        required_blocks=required_blocks,
        concept=concept,
        difficulty=difficulty,
        json_template=json_template
    )
    db.session.add(new_challenge)
    db.session.commit()

    return jsonify({'message': f'Challenge "{title}" added successfully!'}), 201

# =====================================================
# 5️⃣ Get All Challenges
# =====================================================
@app.route('/challenges', methods=['GET'])
def get_challenges():
    challenges = Challenge.query.all()
    return jsonify([
        {
            'id': c.id,
            'title': c.title,
            'concept': c.concept,
            'difficulty': c.difficulty
        } for c in challenges
    ])


# =====================================================
# 6️⃣ Get One Challenge by ID
# =====================================================
@app.route('/challenges/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    c = Challenge.query.get_or_404(challenge_id)
    return jsonify({
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'required_blocks': c.required_blocks,
        'concept': c.concept,
        'difficulty': c.difficulty,
        'json_template': c.json_template
    })


# =====================================================
# 7️⃣ Update Challenge (Teacher only)
# =====================================================
@app.route('/challenges/<int:challenge_id>', methods=['PUT'])
def update_challenge(challenge_id):
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    c = Challenge.query.get_or_404(challenge_id)
    c.title = data.get('title', c.title)
    c.description = data.get('description', c.description)
    c.concept = data.get('concept', c.concept)
    c.difficulty = data.get('difficulty', c.difficulty)
    db.session.commit()

    return jsonify({'message': f'Challenge {c.id} updated successfully!'})


# =====================================================
# 8️⃣ Delete Challenge (Teacher only)
# =====================================================
@app.route('/challenges/<int:challenge_id>', methods=['DELETE'])
def delete_challenge(challenge_id):
    data = request.get_json()
    username = data.get('username')
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    c = Challenge.query.get_or_404(challenge_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': f'Challenge {c.title} deleted successfully!'})


# =====================================================
# 🔬 Test Cases (Teacher only)
# =====================================================
@app.route('/challenges/<int:challenge_id>/add_test_case', methods=['POST'])
def add_test_case(challenge_id):
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    challenge = Challenge.query.get_or_404(challenge_id)
    test_case = TestCase(
        challenge_id=challenge.id,
        input_data=data.get('input_data'),
        expected_output=data.get('expected_output'),
        description=data.get('description')
    )
    db.session.add(test_case)
    db.session.commit()

    return jsonify({'message': 'Test case added successfully!', 'id': test_case.id}), 201


@app.route('/test_cases/<int:test_case_id>', methods=['DELETE'])
def delete_test_case(test_case_id):
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    tc = TestCase.query.get_or_404(test_case_id)
    db.session.delete(tc)
    db.session.commit()
    return jsonify({'message': 'Test case deleted successfully!'})


# =====================================================
# 📝 Solution Templates (Teacher only)
# =====================================================
@app.route('/challenges/<int:challenge_id>/add_solution_template', methods=['POST'])
def add_solution_template(challenge_id):
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    name = data.get('name')
    code_json = data.get('code_json')
    if not name or not code_json:
        return jsonify({'error': 'name and code_json are required'}), 400

    challenge = Challenge.query.get_or_404(challenge_id)
    tpl = SolutionTemplate(
        challenge_id=challenge.id,
        name=name,
        code_json=code_json,
        description=data.get('description')
    )
    db.session.add(tpl)
    db.session.commit()
    return jsonify({'message': 'Solution template added successfully!', 'id': tpl.id}), 201


@app.route('/solution_templates/<int:template_id>', methods=['DELETE'])
def delete_solution_template(template_id):
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    tpl = SolutionTemplate.query.get_or_404(template_id)
    db.session.delete(tpl)
    db.session.commit()
    return jsonify({'message': 'Solution template deleted successfully!'})


# =====================================================
# 📤 Export / Copy / Import (Teacher only)
# =====================================================
@app.route('/challenges/<int:challenge_id>/export', methods=['GET'])
def export_challenge(challenge_id):
    c = Challenge.query.get_or_404(challenge_id)
    return jsonify({
        'challenge': {
            'title': c.title,
            'description': c.description,
            'required_blocks': c.required_blocks,
            'concept': c.concept,
            'difficulty': c.difficulty,
            'json_template': c.json_template
        },
        'test_cases': [
            {
                'id': tc.id,
                'input_data': tc.input_data,
                'expected_output': tc.expected_output,
                'description': tc.description
            } for tc in c.test_cases
        ],
        'solution_templates': [
            {
                'id': st.id,
                'name': st.name,
                'code_json': st.code_json,
                'description': st.description
            } for st in c.solution_templates
        ]
    })


@app.route('/challenges/<int:challenge_id>/copy', methods=['POST'])
def copy_challenge(challenge_id):
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    c = Challenge.query.get_or_404(challenge_id)
    new_c = Challenge(
        title=f"{c.title} (Copy)",
        description=c.description,
        required_blocks=c.required_blocks,
        concept=c.concept,
        difficulty=c.difficulty,
        json_template=c.json_template,
        created_by=user.id
    )
    db.session.add(new_c)
    db.session.flush()

    for tc in c.test_cases:
        db.session.add(TestCase(
            challenge_id=new_c.id,
            input_data=tc.input_data,
            expected_output=tc.expected_output,
            description=tc.description
        ))
    for st in c.solution_templates:
        db.session.add(SolutionTemplate(
            challenge_id=new_c.id,
            name=st.name,
            code_json=st.code_json,
            description=st.description
        ))

    db.session.commit()
    return jsonify({'message': 'Challenge copied successfully!', 'new_challenge_id': new_c.id}), 201


@app.route('/import_challenge', methods=['POST'])
def import_challenge():
    data = request.get_json() or {}
    user = get_user_from_payload(data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(user.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    challenge_data = data.get('challenge') or {}
    if not challenge_data.get('title') or not challenge_data.get('required_blocks'):
        return jsonify({'error': 'challenge.title and challenge.required_blocks are required'}), 400

    c = Challenge(
        title=challenge_data.get('title'),
        description=challenge_data.get('description', ''),
        required_blocks=challenge_data.get('required_blocks'),
        concept=challenge_data.get('concept', 'loop'),
        difficulty=challenge_data.get('difficulty', 'easy'),
        json_template=challenge_data.get('json_template', '{"blocks": []}'),
        created_by=user.id
    )
    db.session.add(c)
    db.session.flush()

    for tc in (data.get('test_cases') or []):
        db.session.add(TestCase(
            challenge_id=c.id,
            input_data=tc.get('input_data'),
            expected_output=tc.get('expected_output'),
            description=tc.get('description')
        ))

    for st in (data.get('solution_templates') or []):
        if not st.get('name') or not st.get('code_json'):
            continue
        db.session.add(SolutionTemplate(
            challenge_id=c.id,
            name=st.get('name'),
            code_json=st.get('code_json'),
            description=st.get('description')
        ))

    db.session.commit()
    return jsonify({'message': 'Challenge imported successfully!', 'challenge_id': c.id}), 201

# =====================================================
# Simple Evaluation Function
# =====================================================
import json


def evaluate_code(code_json, required_blocks, user=None, challenge=None):
    """
    دالة تقييم ذكية للكود المرسل من الطالب:
    - تحليل هرمي للكتل
    - التحقق من صحة المنطق داخل الكتل
    - مقارنة مع الكتل المطلوبة للتحدي
    - تحليل العمق البنائي
    - دمج المحاولات السابقة لتوليد تغذية راجعة تربوية
    """

    feedback_parts = []
    result = "fail"

    try:
        # =============================
        # 1️⃣ تحليل JSON واستخراج الكتل
        # =============================
        data = json.loads(code_json)

        # Blockly workspace format: {"blockly_xml": "..."}
        if isinstance(data, dict) and data.get('blockly_xml'):
            feedback_text = "تم حفظ حل Blockly (XML). سيتم تقييمه لاحقًا ضمن مرحلة Python/AST."
            return "partial", feedback_text

        blocks = data.get("blocks", [])
        if not blocks:
            return "fail", "الكود فارغ. أضف بعض الكتل البرمجية للبدء."

        submitted_blocks = extract_blocks_recursive(blocks)
        feedback_parts.append(f"عدد الكتل المكتشفة: {len(submitted_blocks)}.")

        # =============================
        # 2️⃣ التحقق المفاهيمي لكل كتلة
        # =============================
        conceptual_feedback = []
        for block in blocks:
            error = validate_block_logic(block)
            if error:
                conceptual_feedback.append(error)

        if conceptual_feedback:
            feedback_parts.append("تحقق من منطق الكتل:\n- " + "\n- ".join(conceptual_feedback))

        # =============================
        # 3️⃣ مقارنة مع الكتل المطلوبة
        # =============================
        if required_blocks:
            required = [b.strip() for b in required_blocks.split(",")]
            missing = [r for r in required if r not in submitted_blocks]
            if missing:
                feedback_parts.append("الكود غير مكتمل. ينقصك الكتل: " + ", ".join(missing))
            else:
                feedback_parts.append("✅ استخدمت جميع الكتل المطلوبة بنجاح!")
                result = "success"

        # =============================
        # 4️⃣ تحليل العمق البنائي (Nested Depth)
        # =============================
        max_depth = max(block_depth(b) for b in blocks)
        if max_depth > 4:
            feedback_parts.append("الكود معقد قليلاً (عمق التداخل كبير). حاول تبسيط الحل.")

        # =============================
        # 5️⃣ تحليل سلوكي من محاولات الطالب السابقة
        # =============================
        if user and challenge:
            attempt_count = Submission.query.filter_by(
                student_id=user.id,
                challenge_id=challenge.id
            ).count()

            if attempt_count == 0:
                feedback_parts.append("🎯 هذه أول محاولة لك! حظًا موفقًا.")
            elif attempt_count == 1:
                feedback_parts.append("📘 محاولة ثانية ممتازة! فكر أكثر في ترتيب الكتل.")
            elif attempt_count == 2:
                feedback_parts.append("💪 أنت تتحسن! بقيت خطوة بسيطة نحو الحل الكامل.")
            else:
                feedback_parts.append("🌟 رائع! إصرارك واضح، استمر بالمحاولة!")

        # =============================
        # 6️⃣ حساب نسبة التوافق (Scoring)
        # =============================
        if required_blocks:
            required = [b.strip() for b in required_blocks.split(",")]
            correct_count = len([r for r in required if r in submitted_blocks])
            score = int(correct_count / len(required) * 100)
        else:
            score = 0

        feedback_parts.append(f"🔹 النتيجة التقريبية: {score}%")

        # =============================
        # 7️⃣ تحديد النتيجة النهائية
        # =============================
        if result == "success" and conceptual_feedback:
            result = "partial"
            feedback_parts.append("✔ الحل قريب جدًا من الكمال، فقط أصلح الملاحظات أعلاه.")

        # دمج النصوص في تغذية واحدة
        feedback_text = "\n".join(feedback_parts)
        return result, feedback_text

    except json.JSONDecodeError as e:
        return "fail", f"خطأ في تنسيق الكود (JSON): {str(e)}"
    except Exception as e:
        return "fail", f"حدث خطأ أثناء تحليل الكود: {str(e)}"


# ======================================
# 🔧 دوال مساعدة تستخدم داخل التقييم
# ======================================

def extract_blocks_recursive(blocks):
    """استخراج جميع أنواع الكتل بما في ذلك المتداخلة."""
    result = []
    for block in blocks:
        result.append(block.get("type"))
        if "body" in block and isinstance(block["body"], list):
            result.extend(extract_blocks_recursive(block["body"]))
    return result


def validate_block_logic(block):
    """التحقق المفاهيمي من منطق الكتلة الفردية."""
    btype = block.get("type")
    if btype == "if" and "condition" not in block:
        return "كتلة if بدون شرط. أضف شرط المقارنة (مثل > أو ==)."
    if btype == "loop" and not ("iterations" in block or "condition" in block):
        return "كتلة loop بدون عدد تكرار أو شرط خروج."
    if btype == "print" and "text" not in block:
        return "كتلة print بدون نص للطباعة."
    if btype == "variable" and "name" not in block:
        return "كتلة variable بدون اسم متغير."
    return None


def block_depth(block):
    """حساب عمق التداخل البنائي داخل الكتل."""
    if "body" not in block or not block["body"]:
        return 1
    return 1 + max(block_depth(b) for b in block["body"])


# =====================================================
# 🔎 عرض جميع المحاولات الخاصة بطالب معيّن
# =====================================================
@app.route('/submissions/<username>', methods=['GET'])
def get_submissions(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    submissions = Submission.query.filter_by(student_id=user.id).all()
    if not submissions:
        return jsonify({'message': 'No submissions found for this student.'}), 200

    return jsonify([
        {
            'id': s.id,
            'challenge_id': s.challenge_id,
            'result': s.result,
            'feedback_text': s.feedback_text
        } for s in submissions
    ])


# =====================================================
# 🧑‍🏫 Teacher: List / Update Submissions
# =====================================================
@app.route('/teacher/submissions', methods=['POST'])
def teacher_list_submissions():
    data = request.get_json() or {}
    teacher = get_user_from_payload(data)
    if not teacher:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(teacher.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    challenge_id = data.get('challenge_id')
    student_username = (data.get('student_username') or '').strip()

    q = Submission.query
    if challenge_id:
        q = q.filter(Submission.challenge_id == challenge_id)

    if student_username:
        student = User.query.filter_by(username=student_username).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        q = q.filter(Submission.student_id == student.id)

    subs = q.order_by(Submission.id.desc()).limit(200).all()

    # Preload usernames and challenge titles
    user_ids = list({s.student_id for s in subs})
    ch_ids = list({s.challenge_id for s in subs})
    users = {u.id: u.username for u in User.query.filter(User.id.in_(user_ids)).all()} if user_ids else {}
    chs = {c.id: c.title for c in Challenge.query.filter(Challenge.id.in_(ch_ids)).all()} if ch_ids else {}

    return jsonify([
        {
            'id': s.id,
            'student_id': s.student_id,
            'student_username': users.get(s.student_id, ''),
            'challenge_id': s.challenge_id,
            'challenge_title': chs.get(s.challenge_id, ''),
            'result': s.result,
            'feedback_text': s.feedback_text,
            'code_json': s.code_json
        } for s in subs
    ])


@app.route('/teacher/submissions/<int:submission_id>', methods=['PUT'])
def teacher_update_submission(submission_id):
    data = request.get_json() or {}
    teacher = get_user_from_payload(data)
    if not teacher:
        return jsonify({'error': 'User not found'}), 404
    if not check_role(teacher.role, ['teacher']):
        return jsonify({'error': 'Access denied'}), 403

    s = Submission.query.get_or_404(submission_id)
    new_result = data.get('result')
    new_feedback = data.get('feedback_text')

    if new_result is not None:
        s.result = new_result
    if new_feedback is not None:
        s.feedback_text = new_feedback
    db.session.commit()

    return jsonify({'message': 'Submission updated successfully!', 'id': s.id})
# =====================================================
# 9️⃣ Submit Challenge Solution (Student only)
# =====================================================
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    username = data.get('username')
    challenge_id = data.get('challenge_id')
    code_json = data.get('code_json')

    # التأكد من وجود المستخدم
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # التأكد من وجود التحدي
    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({'error': 'Challenge not found'}), 404

    # 🔹 استدعاء التقييم المتقدم مع جميع المعاملات
    result, feedback = evaluate_code(
        code_json,
        challenge.required_blocks,
        user=user,
        challenge=challenge
    )

    # حفظ النتيجة في قاعدة البيانات
    submission = Submission(
        student_id=user.id,
        challenge_id=challenge.id,
        code_json=code_json,
        result=result,
        feedback_text=feedback
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'message': 'Submission recorded successfully!',
        'student': user.username,
        'challenge': challenge.title,
        'result': result,
        'feedback': feedback
    })

# =====================================================
# Run the app
# =====================================================
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
