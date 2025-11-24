from flask import Blueprint, request, jsonify, session, make_response, render_template, redirect, url_for, Response
from functools import wraps
from sqlalchemy import func
from ..models import User, Lead
from ..extentions import db

main_bp = Blueprint("main", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# Frontend and API Routes
# -------------------------

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form or request.json or {}
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            response = make_response(jsonify({"message": "Login successful"}))
            response.headers['HX-Redirect'] = '/'
            return response

        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

@main_bp.route('/')
@login_required
def index():
    total_leads = db.session.query(func.count(Lead.id)).scalar()
    unrouted_leads = db.session.query(func.count(Lead.id)).filter_by(routed=False).scalar()
    
    leads_by_platform = db.session.query(Lead.platform, func.count(Lead.id)) \
        .group_by(Lead.platform) \
        .all()

    stats = {
        'total_leads': total_leads,
        'unrouted_leads': unrouted_leads,
        'leads_by_platform': leads_by_platform
    }
    
    return render_template('index.html', stats=stats)

@main_bp.route('/leads', methods=['GET', 'POST'])
@login_required
def leads():
    if request.method == 'POST':
        data =  request.json or {}
        lead = Lead(**data)
        db.session.add(lead)
        db.session.commit()
        return jsonify({"message": "Lead created", "id": lead.id}), 201

    active_platform = request.args.get('platform', 'all')
    platforms = db.session.query(Lead.platform).distinct().all()
    platforms = [p[0] for p in platforms]
    return render_template('leads.html', platforms=platforms, active_platform=active_platform)

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main_bp.route("/register", methods=['POST'])
def register():
    data =  request.form or request.json or {}
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201

@main_bp.route("/leads/export", methods=['GET'])
@login_required
def export_leads():
    export_type = request.args.get('export_type')
    platform = request.args.get('platform')
    lead_ids = request.args.getlist('lead_ids')

    query = Lead.query

    if platform and platform != 'all':
        query = query.filter_by(platform=platform)

    if export_type == 'selected':
        if not lead_ids:
            return jsonify({"error": "No leads selected"}), 400
        query = query.filter(Lead.id.in_(lead_ids))
    elif export_type == 'unrouted':
        query = query.filter_by(routed=False)

    leads = query.all()

    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'Platform', 'Username', 'Status', 'Routed', 'Discovered At'])
    
    for lead in leads:
        writer.writerow([lead.id, lead.platform, lead.username, lead.status, lead.routed, lead.discovered_at])
    
    output.seek(0)
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=leads.csv"}
    )

@main_bp.route("/leads-data", methods=['GET'])
@login_required
def get_leads_data():
    platform = request.args.get('platform', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Lead.query
    if platform and platform != 'all':
        query = query.filter_by(platform=platform)

    leads = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template("partials/_lead_row.html", leads=leads, active_platform=platform)

    

@main_bp.route('/lead/<int:lead_id>')
@login_required
def view_lead(lead_id):

    lead = Lead.query.get_or_404(lead_id)

    return render_template('lead.html', lead=lead)

    