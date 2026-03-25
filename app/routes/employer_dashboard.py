from flask import Blueprint, render_template
from flask_login import current_user
from app.decorators import employer_required
from app.models.employer import EmployerAccount, TalentList, TalentListMember
from app.models.connection import ContactRequest

employer_dashboard_bp = Blueprint('employer_dashboard', __name__)


@employer_dashboard_bp.route('/employer/dashboard')
@employer_required
def employer_dashboard():
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    lists = TalentList.query.filter_by(employer_account_id=employer.id).all() if employer else []
    recent_contacts = ContactRequest.query.filter_by(
        employer_user_id=current_user.id
    ).order_by(ContactRequest.created_at.desc()).limit(10).all()
    return render_template(
        'employer/dashboard.html',
        employer=employer,
        talent_lists=lists,
        recent_contacts=recent_contacts,
    )


@employer_dashboard_bp.route('/employer/pipeline')
@employer_required
def candidate_pipeline():
    employer = EmployerAccount.query.filter_by(owner_user_id=current_user.id).first()
    lists = TalentList.query.filter_by(employer_account_id=employer.id).all() if employer else []
    stages = ['shortlisted', 'contacted', 'interviewing', 'offer', 'declined']
    pipeline = {}
    for stage in stages:
        pipeline[stage] = TalentListMember.query.join(TalentList).filter(
            TalentList.employer_account_id == employer.id,
            TalentListMember.pipeline_stage == stage
        ).all() if employer else []
    return render_template(
        'employer/pipeline.html',
        employer=employer,
        pipeline=pipeline,
        stages=stages,
        talent_lists=lists,
    )
