from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models.challenge import WorkChallenge

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    challenges = WorkChallenge.query.filter_by(is_published=True).limit(3).all()
    return render_template('main/index.html', challenges=challenges)


@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')


@main_bp.route('/for-employers')
def for_employers():
    return render_template('main/for_employers.html')


@main_bp.route('/pricing')
def pricing():
    return render_template('main/pricing.html')


@main_bp.route('/challenges')
def challenges_public():
    page = request.args.get('page', 1, type=int)
    domain = request.args.get('domain', '')
    difficulty = request.args.get('difficulty', '')
    query = WorkChallenge.query.filter_by(is_published=True)
    if domain:
        query = query.filter_by(domain=domain)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    challenges = query.order_by(WorkChallenge.created_at.desc()).paginate(page=page, per_page=12, error_out=False)
    return render_template('challenges/library.html', challenges=challenges, domain=domain, difficulty=difficulty)


@main_bp.route('/challenges/<int:id>')
def challenge_preview(id):
    challenge = WorkChallenge.query.get_or_404(id)
    return render_template('challenges/detail.html', challenge=challenge)


@main_bp.route('/blog')
def blog_index():
    return render_template('main/blog_index.html')


@main_bp.route('/blog/<slug>')
def blog_post(slug):
    return render_template('main/blog_post.html', slug=slug)


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your message. We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('main/contact.html')


@main_bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html')


@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html')
