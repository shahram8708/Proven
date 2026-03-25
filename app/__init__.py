import os
import logging
from datetime import datetime
from flask import Flask, send_from_directory
from app.config import config_map
from app.extensions import db, migrate, login_manager, mail, limiter, csrf

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(config_name, config_map['development']))

    # Ensure upload folder exists for local storage
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Jinja2 Filters ───────────────────────────────────────────────────

    @app.template_filter('time_ago')
    def time_ago_filter(dt):
        if dt is None:
            return 'never'
        now = datetime.utcnow()
        diff = now - dt
        seconds = diff.total_seconds()
        if seconds < 60:
            return 'just now'
        minutes = int(seconds // 60)
        if minutes < 60:
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        hours = int(minutes // 60)
        if hours < 24:
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        days = int(hours // 24)
        if days < 30:
            return f'{days} day{"s" if days != 1 else ""} ago'
        months = int(days // 30)
        if months < 12:
            return f'{months} month{"s" if months != 1 else ""} ago'
        years = int(months // 12)
        return f'{years} year{"s" if years != 1 else ""} ago'

    @app.template_filter('inr')
    def inr_format(amount):
        if amount is None:
            return '₹0'
        return f'₹{int(amount):,}'

    @app.template_filter('verification_color')
    def verification_color(score):
        if score is None:
            return 'low'
        if score >= 80:
            return 'high'
        elif score >= 50:
            return 'medium'
        return 'low'

    # ── Blueprints ────────────────────────────────────────────────────────

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.onboarding import onboarding_bp
    from app.routes.talent_dashboard import talent_dashboard_bp
    from app.routes.employer_dashboard import employer_dashboard_bp
    from app.routes.evidence import evidence_bp
    from app.routes.verification import verification_bp
    from app.routes.challenges import challenges_bp
    from app.routes.discover import discover_bp
    from app.routes.profile import profile_bp
    from app.routes.settings import settings_bp
    from app.routes.billing import billing_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(talent_dashboard_bp)
    app.register_blueprint(employer_dashboard_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(discover_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(admin_bp)

    # ── Serve local uploads in development ────────────────────────────────

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ── Error Handlers ────────────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    # ── Import all models so tables are known to SQLAlchemy ───────────────

    with app.app_context():
        from app.models import user, evidence, verification, skill, challenge, employer, connection  # noqa: F811,F401

    return app


# ═══════════════════════════════════════════════════════════════════════════
#  Startup helpers — called from run.py
# ═══════════════════════════════════════════════════════════════════════════

def init_database(app):
    """Create all database tables if they don't already exist.

    This uses db.create_all() which is safe to call repeatedly —
    it only creates tables that are missing.
    """
    with app.app_context():
        # Import all models to ensure they are registered
        from app.models import user, evidence, verification, skill, challenge, employer, connection  # noqa: F401
        db.create_all()
        logger.info('Database tables ensured.')


def seed_data(app):
    """Seed skills, challenges, and admin user — idempotent (skips existing).

    Safe to call every startup; only inserts rows that don't exist yet.
    """
    with app.app_context():
        _seed_admin(app)
        _seed_skills()
        _seed_challenges()


def _seed_admin(app):
    """Create the default admin user if it doesn't exist."""
    from app.models.user import User

    admin_email = app.config['ADMIN_EMAIL']
    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return

    admin = User(
        email=admin_email,
        first_name=app.config['ADMIN_FIRST_NAME'],
        last_name=app.config['ADMIN_LAST_NAME'],
        username=app.config['ADMIN_USERNAME'],
        account_type='talent',
        is_admin=True,
        is_email_verified=True,
        onboarding_complete=True,
        primary_domain='Software Engineering',
    )
    admin.set_password(app.config['ADMIN_PASSWORD'])
    db.session.add(admin)
    db.session.commit()
    logger.info('Default admin user created: %s', admin_email)


def _seed_skills():
    """Seed skill taxonomy — only inserts missing skills."""
    from app.models.skill import SkillTaxonomy

    SKILLS_DATA = {
        'Technical': {
            'Software Engineering': [
                'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'Rust', 'Ruby',
                'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'FastAPI',
                'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'GraphQL',
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
                'CI/CD', 'Git', 'Linux', 'REST APIs', 'Microservices',
                'Machine Learning', 'Data Engineering', 'System Design', 'Cloud Architecture',
                'Mobile Development', 'iOS Development', 'Android Development', 'Flutter',
                'DevOps', 'Infrastructure as Code', 'Terraform', 'Monitoring',
            ],
            'Data Science': [
                'Statistical Analysis', 'Predictive Modeling', 'Deep Learning', 'NLP',
                'Computer Vision', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas',
                'Data Visualization', 'Tableau', 'Power BI', 'A/B Testing',
                'Feature Engineering', 'Time Series Analysis', 'Recommendation Systems',
                'Data Pipeline Design', 'ETL', 'Spark', 'Hadoop',
            ],
            'Product Management': [
                'Product Roadmapping', 'User Story Writing', 'Agile/Scrum', 'Jira',
                'Product Analytics', 'Wireframing', 'Prototyping', 'Figma',
                'Market Research', 'Competitive Analysis', 'Product-Market Fit',
                'Feature Prioritization', 'OKR Setting', 'Product Launch',
            ],
            'Design': [
                'UI Design', 'UX Design', 'User Research', 'Interaction Design',
                'Design Systems', 'Figma', 'Sketch', 'Adobe XD',
                'Responsive Design', 'Accessibility (WCAG)', 'Information Architecture',
                'Visual Design', 'Typography', 'Color Theory', 'Motion Design',
            ],
            'Marketing': [
                'SEO', 'SEM', 'Google Ads', 'Facebook Ads', 'Content Marketing',
                'Email Marketing', 'Marketing Automation', 'HubSpot', 'Mailchimp',
                'Social Media Marketing', 'Influencer Marketing', 'Brand Strategy',
                'Conversion Rate Optimization', 'Google Analytics', 'Attribution Modeling',
            ],
            'Sales': [
                'B2B Sales', 'B2C Sales', 'Enterprise Sales', 'Consultative Selling',
                'Sales Pipeline Management', 'CRM (Salesforce)', 'Cold Outreach',
                'Negotiation', 'Contract Management', 'Account Management',
                'Sales Forecasting', 'Demo Presentation', 'Objection Handling',
            ],
            'Finance': [
                'Financial Modeling', 'Valuation', 'DCF Analysis', 'Excel Advanced',
                'Budgeting', 'Forecasting', 'Financial Reporting', 'Audit',
                'Tax Planning', 'M&A Analysis', 'Risk Assessment', 'Compliance',
                'QuickBooks', 'SAP Finance', 'Tally', 'GST Compliance',
            ],
            'Operations': [
                'Supply Chain Management', 'Logistics', 'Procurement', 'Vendor Management',
                'Process Optimization', 'Lean Six Sigma', 'Quality Assurance',
                'Inventory Management', 'ERP Systems', 'Warehouse Management',
                'ISO Standards', 'SOPs Development', 'Cost Reduction',
            ],
            'Human Resources': [
                'Talent Acquisition', 'Employee Engagement', 'Performance Management',
                'Compensation & Benefits', 'HR Analytics', 'HRIS', 'Onboarding',
                'Training & Development', 'Employer Branding', 'Labor Law Compliance',
                'Diversity & Inclusion', 'Succession Planning', 'Conflict Resolution',
            ],
        },
        'Leadership': {
            '_all': [
                'Team Building', 'Mentoring & Coaching', 'Cross-functional Leadership',
                'Change Management', 'Delegation', 'Conflict Resolution',
                'Performance Reviews', 'Vision Setting', 'Talent Development',
                'Organizational Design', 'Board Communication', 'Executive Presence',
                'Remote Team Management', 'Stakeholder Alignment', 'Culture Building',
                'Managing Up', 'Decision Making Under Pressure', 'Crisis Management',
                'Inclusive Leadership', 'Servant Leadership',
            ],
        },
        'Strategic': {
            '_all': [
                'Strategic Planning', 'Business Strategy', 'Go-to-Market Strategy',
                'Market Analysis', 'Competitive Intelligence', 'Business Development',
                'Partnership Development', 'Revenue Growth', 'P&L Management',
                'OKR Framework', 'KPI Development', 'Scenario Planning',
                'Digital Transformation', 'Innovation Management', 'Design Thinking',
                'Pricing Strategy', 'Customer Segmentation', 'Unit Economics',
                'Fundraising', 'Investor Relations', 'Pitch Deck Creation',
            ],
        },
        'Communication': {
            '_all': [
                'Public Speaking', 'Presentation Design', 'Technical Writing',
                'Business Writing', 'Storytelling', 'Stakeholder Communication',
                'Client Relationship Management', 'Cross-cultural Communication',
                'Active Listening', 'Facilitation', 'Workshop Design',
                'Feedback Delivery', 'Negotiation', 'Persuasion',
                'Executive Briefings', 'Internal Communications', 'Crisis Communication',
                'Copywriting', 'Content Strategy', 'Proposal Writing',
            ],
        },
        'Analytical': {
            '_all': [
                'Critical Thinking', 'Problem Solving', 'Root Cause Analysis',
                'Data-Driven Decision Making', 'Quantitative Analysis', 'Qualitative Research',
                'Process Mapping', 'Systems Thinking', 'Hypothesis Testing',
                'Benchmarking', 'Cost-Benefit Analysis', 'Risk Analysis',
                'Pattern Recognition', 'Trend Analysis', 'Research Methodology',
                'Survey Design', 'Report Writing', 'Dashboard Design',
                'Troubleshooting', 'Debugging Complex Systems',
            ],
        },
    }

    count = 0
    for dimension, domains in SKILLS_DATA.items():
        for domain, skills in domains.items():
            actual_domain = None if domain == '_all' else domain
            for skill_name in skills:
                existing = SkillTaxonomy.query.filter_by(
                    name=skill_name, dimension=dimension
                ).first()
                if not existing:
                    skill = SkillTaxonomy(
                        name=skill_name,
                        dimension=dimension,
                        domain=actual_domain,
                    )
                    db.session.add(skill)
                    count += 1

    if count > 0:
        db.session.commit()
        logger.info('Seeded %d new skills (total: %d)', count, SkillTaxonomy.query.count())
    else:
        logger.info('Skills already seeded — skipped.')


def _seed_challenges():
    """Seed work challenges — only inserts missing challenges."""
    from app.models.challenge import WorkChallenge

    CHALLENGES = [
        {
            'title': 'Debug a Production API Failure',
            'domain': 'Software Engineering',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'A critical REST API endpoint is returning 500 errors intermittently. You have access to logs, metrics, and the codebase. Walk through your debugging process, identify the root cause, and propose a fix with prevention measures.',
            'rubric': {
                'Technical Depth': {'weight': 30, 'description': 'Understanding of systems, tools, and debugging techniques'},
                'Problem-Solving Process': {'weight': 25, 'description': 'Structured approach to isolating and diagnosing the issue'},
                'Communication': {'weight': 20, 'description': 'Clarity of explanation for both technical and non-technical audiences'},
                'Prevention & Improvement': {'weight': 15, 'description': 'Proposed monitoring, testing, or architectural improvements'},
                'Practical Feasibility': {'weight': 10, 'description': 'Realism and implementability of the proposed solution'},
            },
        },
        {
            'title': 'Design a Scalable Notification System',
            'domain': 'Software Engineering',
            'difficulty': 'advanced',
            'time_limit_minutes': 60,
            'brief': 'Design a notification system for a platform with 10M users that supports email, push, SMS, and in-app notifications. Address delivery guarantees, user preferences, rate limiting, and template management.',
            'rubric': {
                'System Design': {'weight': 30, 'description': 'Architecture quality, component choices, scalability considerations'},
                'Technical Depth': {'weight': 25, 'description': 'Understanding of messaging patterns, queues, delivery mechanisms'},
                'Trade-off Analysis': {'weight': 20, 'description': 'Discussion of alternatives and rationale for decisions'},
                'Operational Readiness': {'weight': 15, 'description': 'Monitoring, failure handling, and deployment considerations'},
                'Communication': {'weight': 10, 'description': 'Clarity and organization of the design document'},
            },
        },
        {
            'title': 'Analyze a Customer Churn Dataset',
            'domain': 'Data Science',
            'difficulty': 'intermediate',
            'time_limit_minutes': 60,
            'brief': 'Describe your approach to building a churn prediction model, including EDA, feature engineering, model selection, evaluation metrics, and actionable business recommendations.',
            'rubric': {
                'Analytical Approach': {'weight': 25, 'description': 'Structured methodology for exploration and modeling'},
                'Feature Engineering': {'weight': 20, 'description': 'Creativity and relevance of derived features'},
                'Model Selection': {'weight': 20, 'description': 'Appropriate choice and justification of algorithms'},
                'Business Impact': {'weight': 20, 'description': 'Actionable insights and recommendations for stakeholders'},
                'Communication': {'weight': 15, 'description': 'Clear presentation of findings and methodology'},
            },
        },
        {
            'title': 'Prioritize a Product Backlog',
            'domain': 'Product Management',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'You have 12 feature requests, 3 critical bugs, and a tech debt item. Describe your prioritization framework, items selected, and how you would communicate this to stakeholders.',
            'rubric': {
                'Prioritization Framework': {'weight': 30, 'description': 'Clear, defensible methodology (RICE, impact/effort, etc.)'},
                'Strategic Thinking': {'weight': 25, 'description': 'Alignment with business goals and customer needs'},
                'Stakeholder Management': {'weight': 20, 'description': 'Communication plan for decisions and trade-offs'},
                'Data Usage': {'weight': 15, 'description': 'Use of metrics, customer data, and evidence in decisions'},
                'Execution Plan': {'weight': 10, 'description': 'Realistic roadmap and success criteria'},
            },
        },
        {
            'title': 'Redesign a Checkout Flow',
            'domain': 'Design',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'An e-commerce platform has a 68% cart abandonment rate. Describe your redesign approach, including UX principles, wireframe descriptions, and success measurement.',
            'rubric': {
                'UX Methodology': {'weight': 25, 'description': 'Research approach and user-centered design process'},
                'Design Decisions': {'weight': 25, 'description': 'Layout, flow, micro-interactions, and friction reduction'},
                'Accessibility': {'weight': 15, 'description': 'Inclusive design considerations and WCAG awareness'},
                'Measurement': {'weight': 20, 'description': 'Success metrics, A/B testing plan, analytics setup'},
                'Communication': {'weight': 15, 'description': 'Ability to articulate and justify design choices'},
            },
        },
        {
            'title': 'Create a Go-to-Market Strategy',
            'domain': 'Marketing',
            'difficulty': 'advanced',
            'time_limit_minutes': 60,
            'brief': 'A fintech startup is launching a UPI-based micro-investment app for Tier 2/3 cities in India. Budget: 50 lakhs for 6 months. Define target segments, positioning, channel strategy, and KPIs.',
            'rubric': {
                'Market Understanding': {'weight': 25, 'description': 'Insight into target demographics and competitive landscape'},
                'Strategic Clarity': {'weight': 25, 'description': 'Clear positioning, messaging, and differentiation'},
                'Channel Strategy': {'weight': 20, 'description': 'Appropriate channel mix and budget allocation'},
                'Measurement Framework': {'weight': 15, 'description': 'KPIs, attribution model, and optimization plan'},
                'Creativity': {'weight': 15, 'description': 'Innovative approaches suited to the target market'},
            },
        },
        {
            'title': 'Close a Complex Enterprise Deal',
            'domain': 'Sales',
            'difficulty': 'advanced',
            'time_limit_minutes': 45,
            'brief': 'Selling a 75L/year enterprise SaaS platform to a large Indian bank. Multiple stakeholders with different concerns. Describe your strategy to close this deal.',
            'rubric': {
                'Stakeholder Mapping': {'weight': 25, 'description': 'Understanding of decision-makers, influencers, and blockers'},
                'Sales Strategy': {'weight': 25, 'description': 'Multi-threaded approach, timing, and tactics'},
                'Objection Handling': {'weight': 20, 'description': 'Addressing pricing, ROI, and competitive concerns'},
                'Negotiation': {'weight': 15, 'description': 'Creative deal structuring and win-win outcomes'},
                'Communication': {'weight': 15, 'description': 'Clarity and persuasiveness of approach'},
            },
        },
        {
            'title': 'Build a 3-Year Financial Model',
            'domain': 'Finance',
            'difficulty': 'advanced',
            'time_limit_minutes': 60,
            'brief': 'A Series A SaaS startup needs a 3-year financial model for fundraising. Describe model structure, key assumptions, revenue drivers, cost categories, and investor metrics.',
            'rubric': {
                'Model Structure': {'weight': 25, 'description': 'Logical flow, sheets, and interconnections'},
                'Assumptions': {'weight': 25, 'description': 'Realistic, well-justified assumptions with sensitivity analysis'},
                'SaaS Metrics': {'weight': 20, 'description': 'Understanding of ARR, churn, LTV, CAC, burn rate'},
                'Presentation': {'weight': 15, 'description': 'Investor-ready output, charts, and summary'},
                'Scenario Analysis': {'weight': 15, 'description': 'Bull/base/bear cases and key variable sensitivity'},
            },
        },
        {
            'title': 'Optimize a Warehouse Operation',
            'domain': 'Operations',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'A D2C brand warehouse handles 2,000 orders/day with 4% error rate. Propose process improvements to achieve <1% error and <24hr fulfillment.',
            'rubric': {
                'Problem Analysis': {'weight': 25, 'description': 'Identification of root causes and bottlenecks'},
                'Solution Design': {'weight': 25, 'description': 'Practical, implementable process improvements'},
                'Metrics & Measurement': {'weight': 20, 'description': 'KPIs, monitoring, and success criteria'},
                'Change Management': {'weight': 15, 'description': 'Rollout plan, training, and adoption strategy'},
                'Cost Awareness': {'weight': 15, 'description': 'Budget implications and ROI of improvements'},
            },
        },
        {
            'title': 'Design an Employee Engagement Program',
            'domain': 'Human Resources',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'A 500-person tech company has seen engagement scores drop. Design a comprehensive engagement improvement program with measurable outcomes.',
            'rubric': {
                'Root Cause Analysis': {'weight': 25, 'description': 'Deep understanding of engagement drivers and barriers'},
                'Program Design': {'weight': 25, 'description': 'Comprehensive, multi-faceted intervention strategy'},
                'Manager Enablement': {'weight': 20, 'description': 'Training, tools, and accountability for people managers'},
                'Measurement': {'weight': 15, 'description': 'Leading/lagging indicators and feedback loops'},
                'Implementation': {'weight': 15, 'description': 'Phased rollout, resources, and timeline'},
            },
        },
        {
            'title': 'Write a Technical RFC',
            'domain': 'Software Engineering',
            'difficulty': 'beginner',
            'time_limit_minutes': 30,
            'brief': 'Write an RFC for migrating a monolithic auth module to microservices. Include problem statement, proposed solution, alternatives, migration plan, and risks.',
            'rubric': {
                'Problem Framing': {'weight': 20, 'description': 'Clear articulation of the problem and motivations'},
                'Solution Design': {'weight': 25, 'description': 'Technical approach, API contracts, data migration'},
                'Trade-off Discussion': {'weight': 20, 'description': 'Alternatives considered with pros/cons'},
                'Risk Assessment': {'weight': 15, 'description': 'Identified risks and mitigation strategies'},
                'Writing Quality': {'weight': 20, 'description': 'Clarity, structure, and completeness of the document'},
            },
        },
        {
            'title': 'Conduct a Competitive Analysis',
            'domain': 'Product Management',
            'difficulty': 'beginner',
            'time_limit_minutes': 30,
            'brief': 'Building a project management tool competing with Asana, Monday.com, and ClickUp. Conduct a competitive analysis and identify differentiation opportunities.',
            'rubric': {
                'Research Depth': {'weight': 25, 'description': 'Thoroughness of competitive landscape coverage'},
                'Framework Usage': {'weight': 20, 'description': 'Structured analysis methodology'},
                'Strategic Insight': {'weight': 25, 'description': 'Quality of differentiation opportunities identified'},
                'Market Understanding': {'weight': 15, 'description': 'Awareness of market trends and customer needs'},
                'Presentation': {'weight': 15, 'description': 'Clear, actionable format for decision-makers'},
            },
        },
        {
            'title': 'Plan a Performance Improvement',
            'domain': 'Human Resources',
            'difficulty': 'beginner',
            'time_limit_minutes': 30,
            'brief': 'Design a fair, structured performance improvement plan (PIP) that balances support with accountability for an underperforming employee.',
            'rubric': {
                'Process Design': {'weight': 25, 'description': 'Fair, clear, and legally sound PIP structure'},
                'Goal Setting': {'weight': 25, 'description': 'Specific, measurable improvement targets'},
                'Support Mechanisms': {'weight': 20, 'description': 'Resources, mentorship, and check-in cadence'},
                'Documentation': {'weight': 15, 'description': 'Proper record-keeping and communication templates'},
                'Empathy & Fairness': {'weight': 15, 'description': 'Balanced approach respecting employee dignity'},
            },
        },
        {
            'title': 'Develop a Content Marketing Strategy',
            'domain': 'Marketing',
            'difficulty': 'beginner',
            'time_limit_minutes': 30,
            'brief': 'A B2B cybersecurity startup wants 50 qualified leads/month. Define content pillars, formats, distribution channels, and measurement approach.',
            'rubric': {
                'Strategy Clarity': {'weight': 25, 'description': 'Clear pillars, audience definition, and goals'},
                'Content Planning': {'weight': 25, 'description': 'Format mix, calendar structure, and production plan'},
                'Distribution': {'weight': 20, 'description': 'Channel strategy and amplification approach'},
                'Lead Generation': {'weight': 15, 'description': 'Conversion funnel and lead capture mechanics'},
                'Measurement': {'weight': 15, 'description': 'KPIs, attribution, and optimization cadence'},
            },
        },
        {
            'title': 'Create an API Testing Strategy',
            'domain': 'Software Engineering',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'Design a comprehensive API testing strategy for 40+ REST endpoints covering unit, integration, contract, performance, and security testing.',
            'rubric': {
                'Testing Coverage': {'weight': 25, 'description': 'Breadth across testing types and scenarios'},
                'Tool Selection': {'weight': 20, 'description': 'Appropriate tools with justification'},
                'CI/CD Integration': {'weight': 20, 'description': 'Pipeline design, gates, and automation'},
                'Practical Implementation': {'weight': 20, 'description': 'Realistic rollout plan and team adoption'},
                'Communication': {'weight': 15, 'description': 'Clear documentation and standards'},
            },
        },
        {
            'title': 'Handle a PR Crisis',
            'domain': 'Marketing',
            'difficulty': 'advanced',
            'time_limit_minutes': 45,
            'brief': 'Your company customer data was breached affecting 100K Indian users. Draft your crisis communication plan including immediate response, stakeholder comms, and recovery plan.',
            'rubric': {
                'Speed & Decisiveness': {'weight': 25, 'description': 'Immediate response plan and decision framework'},
                'Stakeholder Communication': {'weight': 25, 'description': 'Tailored messaging for each audience'},
                'Legal & Compliance': {'weight': 20, 'description': 'DPDP Act awareness, regulatory notification'},
                'Recovery Plan': {'weight': 15, 'description': 'Trust rebuilding and long-term measures'},
                'Tone & Empathy': {'weight': 15, 'description': 'Appropriate language and genuine concern'},
            },
        },
        {
            'title': 'Build a Sales Enablement Playbook',
            'domain': 'Sales',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'Create a sales enablement playbook for scaling from 5 to 20 reps, covering ICP, discovery calls, demo scripts, objection handling, and competitive battle cards.',
            'rubric': {
                'ICP & Messaging': {'weight': 25, 'description': 'Clear ideal customer profile and value propositions'},
                'Process Design': {'weight': 25, 'description': 'Structured, repeatable sales methodology'},
                'Objection Handling': {'weight': 20, 'description': 'Common objections with specific responses'},
                'Competitive Intel': {'weight': 15, 'description': 'Battle card structure and differentiation'},
                'Scalability': {'weight': 15, 'description': 'Onboarding-ready format for new reps'},
            },
        },
        {
            'title': 'Evaluate a SaaS Acquisition Target',
            'domain': 'Finance',
            'difficulty': 'intermediate',
            'time_limit_minutes': 45,
            'brief': 'Outline due diligence framework, valuation approach, synergy analysis, integration risks, and deal structure for acquiring a smaller SaaS player.',
            'rubric': {
                'Due Diligence': {'weight': 25, 'description': 'Comprehensive checklist across financial, tech, and commercial areas'},
                'Valuation': {'weight': 25, 'description': 'Multiple methodologies with justified multiples'},
                'Synergy Analysis': {'weight': 20, 'description': 'Revenue and cost synergies with realistic timelines'},
                'Risk Assessment': {'weight': 15, 'description': 'Integration risks, customer churn, key-person dependency'},
                'Deal Structure': {'weight': 15, 'description': 'Payment terms, earnouts, and protection mechanisms'},
            },
        },
        {
            'title': 'Design an Accessibility Audit Process',
            'domain': 'Design',
            'difficulty': 'advanced',
            'time_limit_minutes': 45,
            'brief': 'Design an audit framework, remediation prioritization, and ongoing accessibility maintenance plan aligned with WCAG 2.1 AA standards.',
            'rubric': {
                'Audit Framework': {'weight': 25, 'description': 'Comprehensive testing methodology and tools'},
                'WCAG Knowledge': {'weight': 25, 'description': 'Understanding of success criteria and conformance levels'},
                'Prioritization': {'weight': 20, 'description': 'Severity-based remediation approach'},
                'Process Integration': {'weight': 15, 'description': 'Design/dev workflow changes for ongoing compliance'},
                'Advocacy': {'weight': 15, 'description': 'Organizational buy-in and culture shift strategy'},
            },
        },
        {
            'title': 'Implement a Supply Chain Resilience Plan',
            'domain': 'Operations',
            'difficulty': 'advanced',
            'time_limit_minutes': 60,
            'brief': 'Propose a multi-sourcing strategy, inventory optimization, risk monitoring, and business continuity plan for a company with single-region sourcing.',
            'rubric': {
                'Risk Assessment': {'weight': 25, 'description': 'Comprehensive identification of supply chain vulnerabilities'},
                'Strategy Design': {'weight': 25, 'description': 'Multi-sourcing, nearshoring, and buffer stock approach'},
                'Technology & Monitoring': {'weight': 20, 'description': 'Real-time risk monitoring and early warning systems'},
                'Financial Impact': {'weight': 15, 'description': 'Cost analysis and ROI of resilience investments'},
                'Implementation': {'weight': 15, 'description': 'Phased plan with timeline and milestones'},
            },
        },
    ]

    count = 0
    for ch_data in CHALLENGES:
        existing = WorkChallenge.query.filter_by(title=ch_data['title']).first()
        if not existing:
            challenge = WorkChallenge(
                title=ch_data['title'],
                domain=ch_data['domain'],
                challenge_type='scenario',
                difficulty=ch_data['difficulty'],
                brief_text=ch_data['brief'],
                instructions_text=ch_data['brief'],
                evaluation_rubric=ch_data['rubric'],
                time_limit_minutes=ch_data['time_limit_minutes'],
                is_published=True,
                is_sponsored=False,
            )
            db.session.add(challenge)
            count += 1

    if count > 0:
        db.session.commit()
        logger.info('Seeded %d new challenges (total: %d)', count, WorkChallenge.query.count())
    else:
        logger.info('Challenges already seeded — skipped.')
