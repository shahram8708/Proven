"""Seed script: Populate skills across 5 dimensions and 9 domains.

Can be run standalone:  python -m app.seed_skills
Also runs automatically on app startup via run.py
"""

from app import create_app
from app.extensions import db
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


def seed_skills():
    app = create_app()
    with app.app_context():
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

        db.session.commit()
        print(f'Seeded {count} new skills (total: {SkillTaxonomy.query.count()})')


if __name__ == '__main__':
    seed_skills()
