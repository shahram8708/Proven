"""Seed script: Populate work challenges with rubrics.

Can be run standalone:  python -m app.seed_challenges
Also runs automatically on app startup via run.py
"""

from app import create_app
from app.extensions import db
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
        'brief': 'Design a notification system for a platform with 10M users that supports email, push, SMS, and in-app notifications. Address delivery guarantees, user preferences, rate limiting, and template management. Include a high-level architecture diagram description.',
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
        'brief': 'You are given a SaaS company\'s customer data with features like usage metrics, support tickets, contract type, and churn labels. Describe your approach to building a churn prediction model, including EDA, feature engineering, model selection, evaluation metrics, and actionable business recommendations.',
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
        'brief': 'You\'re the PM for a B2B SaaS tool with 500 customers. You have 12 feature requests, 3 critical bugs, and a tech debt item. Your engineering team has capacity for 6 items this quarter. Describe your prioritization framework, the items you\'d select, and how you\'d communicate this to stakeholders.',
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
        'brief': 'An e-commerce platform has a 68% cart abandonment rate. Their current checkout is a single long form. Describe your redesign approach, including user research methods, UX principles, wireframe descriptions, and how you\'d measure success.',
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
        'brief': 'A fintech startup is launching a UPI-based micro-investment app for Tier 2/3 cities in India. Budget: ₹50 lakhs for 6 months. Define your target segments, positioning, channel strategy, content plan, and KPIs.',
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
        'brief': 'You\'re selling a ₹75L/year enterprise SaaS platform to a large Indian bank. The CISO loves it, the CTO is neutral, the CFO is skeptical about ROI, and procurement wants a 40% discount. Describe your strategy to close this deal in the current quarter.',
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
        'brief': 'A Series A SaaS startup (₹8Cr ARR, 15% MoM growth, 70% gross margins) needs a 3-year financial model for fundraising. Describe your model structure, key assumptions, revenue drivers, cost categories, and the key metrics investors will scrutinize.',
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
        'brief': 'A D2C brand\'s warehouse handles 2,000 orders/day with a 4% error rate and 36-hour avg fulfillment time. Identify bottlenecks, propose process improvements, and define an implementation plan to achieve <1% error rate and <24hr fulfillment.',
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
        'brief': 'A 500-person tech company has seen engagement scores drop from 78% to 61% over 12 months. Exit interviews cite "lack of growth" and "poor management." Design a comprehensive engagement improvement program with measurable outcomes.',
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
        'brief': 'Your team needs to migrate from a monolithic architecture to microservices for the user authentication module. Write an RFC (Request for Comments) that includes the problem statement, proposed solution, alternatives considered, migration plan, and risks.',
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
        'brief': 'You\'re building a project management tool competing with Asana, Monday.com, and ClickUp. Conduct a competitive analysis covering positioning, pricing, features, strengths/weaknesses, and identify 3 differentiation opportunities.',
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
        'brief': 'An otherwise strong employee has been underperforming for 3 months. Their manager has given informal feedback twice. Design a fair, structured performance improvement plan (PIP) that balances support with accountability.',
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
        'brief': 'A B2B cybersecurity startup wants to generate 50 qualified leads/month through content marketing. Define your content pillars, formats, distribution channels, editorial calendar structure, and measurement approach.',
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
        'brief': 'Your team maintains 40+ REST API endpoints with growing reliability issues. Design a comprehensive API testing strategy covering unit, integration, contract, performance, and security testing. Include tooling recommendations and CI/CD integration.',
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
        'brief': 'Your company\'s customer data was breached, affecting 100K Indian users. The news is on Twitter. Draft your crisis communication plan including initial response (first 2 hours), stakeholder communications, media statement, customer notification, and 30-day recovery plan.',
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
        'brief': 'Your SaaS company is scaling from 5 to 20 sales reps. Create a sales enablement playbook covering ICP definition, discovery call framework, demo script outline, objection handling guide, and competitive battle cards structure.',
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
        'brief': 'Your company (₹200Cr ARR) is considering acquiring a smaller SaaS player (₹30Cr ARR, ₹5Cr EBITDA). Outline your due diligence framework, valuation approach, synergy analysis, integration risks, and deal structure recommendation.',
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
        'brief': 'Your product has 500K users but no formal accessibility program. Design an audit framework, remediation prioritization process, and ongoing accessibility maintenance plan aligned with WCAG 2.1 AA standards.',
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
        'brief': 'A consumer electronics company sources 70% of components from a single region. After recent disruptions, leadership wants a resilience plan. Propose a multi-sourcing strategy, inventory optimization, risk monitoring system, and business continuity plan.',
        'rubric': {
            'Risk Assessment': {'weight': 25, 'description': 'Comprehensive identification of supply chain vulnerabilities'},
            'Strategy Design': {'weight': 25, 'description': 'Multi-sourcing, nearshoring, and buffer stock approach'},
            'Technology & Monitoring': {'weight': 20, 'description': 'Real-time risk monitoring and early warning systems'},
            'Financial Impact': {'weight': 15, 'description': 'Cost analysis and ROI of resilience investments'},
            'Implementation': {'weight': 15, 'description': 'Phased plan with timeline and milestones'},
        },
    },
]


def seed_challenges():
    app = create_app()
    with app.app_context():
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

        db.session.commit()
        print(f'Seeded {count} new challenges (total: {WorkChallenge.query.count()})')


if __name__ == '__main__':
    seed_challenges()
