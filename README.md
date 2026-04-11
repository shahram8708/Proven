# Proven 🏅

### *Your skills are real. Now prove it.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-Not%20Specified-lightgrey)](#license)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-orange?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Payments](https://img.shields.io/badge/Payments-Razorpay-02042B?logo=razorpay&logoColor=white)](https://razorpay.com)
[![Storage](https://img.shields.io/badge/Storage-AWS%20S3-FF9900?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Project](#running-the-project)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact / Author](#contact--author)

---

## About the Project

The hiring market is full of résumés — polished PDFs that claim everything and prove nothing. Proven flips that script. It's a **skills verification platform** where talent professionals build portfolios of *demonstrated* work, backed by real verifiers and scored by AI, and where employers can search and assess candidates based on what they've actually done, not what they've written about themselves.

Professionals write structured work evidence using a STAR-adjacent format (Situation, Approach, Decisions, Outcome, Skills, Reflection), upload supporting files, and request verification from former colleagues or managers. Google Gemini AI reads each submission and extracts the skills it actually demonstrates — not the ones the author hoped to mention. A fraud detection engine runs in parallel, flagging plagiarism, submission velocity anomalies, and potential verification rings.

On the employer side, companies subscribe to search the talent pool with powerful filters: domain, skills, experience, evidence count, verification rate, and challenge completions. They can build curated talent lists, move candidates through a hiring pipeline, and send contact requests that land in a talent's inbox — not a black hole.

It's built for the Indian market (Razorpay payments, INR pricing) but the architecture is solid enough to deploy anywhere.

---

## Key Features ✨

- **Structured Work Evidence** — Talent submits evidence using a six-section narrative format (Situation → Approach → Decisions → Outcome → Skills → Reflection) that forces specificity and makes AI extraction reliable.
- **AI Skill Extraction** — Google Gemini 2.5 Flash reads each evidence submission and maps demonstrated skills to a curated taxonomy of 300+ skills across five dimensions (technical, process, communication, leadership, problem-solving).
- **Peer Verification System** — Talent can request email-based verification from former colleagues; verifiers respond via a token-protected URL with one of: confirmed, confirmed with qualification, or denied.
- **Evidence Quality Scoring** — A multi-factor scoring engine (0–100) evaluates completeness, specificity via AI, measurability (looks for numbers and percentages in outcomes), verification count, recency, and fraud status.
- **Fraud Detection Engine** — Automatically checks for text plagiarism via n-gram similarity, velocity abuse, AI-assessed internal consistency, free-email-domain verifier misuse, and verification ring patterns.
- **Work Challenges Library** — A seeded library of structured challenges that talent can take; AI scores each submission against a per-challenge rubric and delivers feedback across four dimensions (clarity, depth, practicality, reasoning).
- **Employer Discovery** — Advanced talent search with filters for domain, skills, country, experience range, minimum evidence count, minimum verification rate, and whether the candidate has completed a work challenge.
- **Talent Pipeline Management** — Employers can save candidates to named lists, attach private notes, and track pipeline stage (shortlisted, interviewing, offered, etc.).
- **Sponsored Challenges** — Employers can post branded work challenges that appear in the challenge library, giving them early signal on candidates who self-select in.
- **Profile Strength Score** — A dynamic 0–100 score computed from evidence count, verification rate, challenge completions, profile completeness, and skill tag density.
- **Radar Chart Skill Visualisation** — A five-axis radar chart on every talent profile showing relative strength across all skill dimensions.
- **Razorpay Subscriptions** — Three billing plans (Talent Pro at ₹749/mo, Employer Starter at ₹8,299/mo, Employer Team at ₹29,199/mo) with webhook-based subscription lifecycle management.
- **Admin Dashboard** — A password-protected admin panel with platform statistics, user management, and a fraud review queue.
- **Dual File Storage** — Switchable between local disk (development) and AWS S3 (production) for evidence file uploads.

---

## Tech Stack 🛠️

**Backend**
- Python 3.10+
- Flask (application framework, factory pattern)
- Flask-SQLAlchemy (ORM)
- Flask-Migrate (Alembic database migrations)
- Flask-Login (session management)
- Flask-WTF + WTForms (form handling and CSRF protection)
- Flask-Mail (transactional email)
- Flask-Limiter (rate limiting)
- Gunicorn (production WSGI server)
- Werkzeug (password hashing, utilities)
- itsdangerous (signed tokens for email verification and password reset)

**AI**
- Google Generative AI SDK (`google-genai`) — Gemini 2.5 Flash for skill extraction, evidence specificity scoring, consistency checking, and challenge scoring

**Payments**
- Razorpay Python SDK — order creation, payment verification (HMAC-SHA256 signature), and webhook event handling

**Database**
- SQLite (development)
- PostgreSQL via `psycopg2-binary` (production)

**File Storage**
- Local filesystem (development)
- AWS S3 via `boto3` (production) — with `python-magic` and `Pillow` for file type validation and image handling

**Frontend**
- Jinja2 templating
- Custom CSS (component, dashboard, discover, profile, and main stylesheets)
- Vanilla JavaScript (chart rendering, discover filters, evidence form, profile drawer, Razorpay checkout)
- Chart.js (radar charts, skill visualisations)

**DevOps / Infrastructure**
- `python-dotenv` for environment management
- `email-validator` for signup form validation
- Gunicorn + `wsgi.py` entrypoint for production

---

## Project Structure

```
Proven-main/
├── run.py                        # Development entrypoint — creates app, inits DB, seeds data
├── wsgi.py                       # Production WSGI entrypoint for Gunicorn
├── requirements.txt              # All Python dependencies
├── .gitignore                    # Ignores .env, uploads/, *.db, venv/, etc.
├── Proven_PRD.docx               # Product Requirements Document
├── how-it-work.md                # Manual testing guide (phase-by-phase walkthrough)
│
└── app/
    ├── __init__.py               # App factory (create_app), blueprints, Jinja2 filters, error handlers
    ├── config.py                 # DevelopmentConfig, ProductionConfig, TestingConfig
    ├── extensions.py             # Flask extensions (db, migrate, login_manager, mail, limiter, csrf)
    ├── decorators.py             # @admin_required, @employer_required, @premium_required
    ├── seed_skills.py            # Seeds 300+ skills into skill_taxonomy table
    ├── seed_challenges.py        # Seeds 20+ work challenges into work_challenges table
    │
    ├── models/
    │   ├── user.py               # User model — auth, subscription, profile fields
    │   ├── evidence.py           # EvidenceSubmission + EvidenceFile models
    │   ├── skill.py              # SkillTaxonomy + UserSkillTag models
    │   ├── challenge.py          # WorkChallenge + ChallengeSubmission models
    │   ├── verification.py       # Verification model — token-based peer verification
    │   ├── employer.py           # EmployerAccount + TalentList + TalentListMember
    │   └── connection.py         # ContactRequest model
    │
    ├── routes/
    │   ├── main.py               # Public pages: home, how-it-works, for-employers, pricing, blog
    │   ├── auth.py               # Signup, login, logout, email verification, password reset
    │   ├── onboarding.py         # 3-step onboarding flow (domain, experience, goals)
    │   ├── talent_dashboard.py   # Talent home dashboard
    │   ├── employer_dashboard.py # Employer home dashboard + pipeline
    │   ├── evidence.py           # Evidence CRUD, file upload, AI skill review, publish
    │   ├── verification.py       # Send verification requests, respond via token link
    │   ├── challenges.py         # Challenge library, take challenge, submit, AI score
    │   ├── discover.py           # Employer talent search, talent lists, profile drawer
    │   ├── profile.py            # Public profile, edit profile
    │   ├── settings.py           # Account, notifications, billing settings pages
    │   ├── billing.py            # Razorpay order creation, payment verification, webhook
    │   └── admin.py              # Admin dashboard, user management, fraud queue
    │
    ├── forms/
    │   ├── auth_forms.py         # SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
    │   ├── evidence_forms.py     # EvidenceSubmissionForm
    │   ├── profile_forms.py      # ProfileEditForm
    │   ├── challenge_forms.py    # ChallengeSubmissionForm
    │   ├── discover_forms.py     # EmployerSearchFilterForm
    │   └── verification_forms.py # VerificationResponseForm
    │
    ├── services/
    │   ├── ai_skill_extractor.py       # Gemini-powered skill extraction from evidence text
    │   ├── evidence_quality_scorer.py  # Multi-factor quality score (0–100)
    │   ├── fraud_detector.py           # Plagiarism, velocity, consistency, ring detection
    │   ├── challenge_scorer.py         # Gemini-powered rubric scoring for challenge submissions
    │   ├── profile_strength.py         # Profile strength score computation
    │   ├── skill_aggregator.py         # Rebuilds UserSkillTag records from published evidence
    │   ├── search_engine.py            # SQLAlchemy talent search with multi-filter support
    │   ├── file_handler.py             # Upload handling — local or S3 backend
    │   ├── email_service.py            # Email templates for verification, password reset, contact
    │   └── verification_token.py       # itsdangerous token generation and validation
    │
    ├── static/
    │   ├── css/
    │   │   ├── proven_main.css         # Global styles, design tokens, typography
    │   │   ├── components.css          # Cards, badges, buttons, form elements
    │   │   ├── dashboard.css           # Talent and employer dashboard layouts
    │   │   ├── discover.css            # Talent search and filter UI
    │   │   └── profile.css             # Public profile page styles
    │   ├── js/
    │   │   ├── main.js                 # Global JS — mobile nav, flash messages, tooltips
    │   │   ├── charts.js               # Chart.js radar and bar chart initialisation
    │   │   ├── discover_filters.js     # Real-time search filter interactions
    │   │   ├── evidence_form.js        # Multi-step evidence form, file upload previews
    │   │   ├── profile_drawer.js       # Slide-in talent profile drawer for employers
    │   │   └── razorpay_checkout.js    # Razorpay payment flow integration
    │   └── img/
    │       └── proven_logo.svg         # SVG logo
    │
    └── templates/
        ├── base.html                   # Talent-facing base layout
        ├── talent_base.html            # Talent dashboard base
        ├── employer_base.html          # Employer dashboard base
        ├── admin/                      # Admin panel templates
        ├── auth/                       # Login, signup, email verification, password reset
        ├── challenges/                 # Challenge library, detail, take, review
        ├── components/                 # Reusable partials (cards, badges, pagination, drawer)
        ├── discover/                   # Employer talent search index and lists
        ├── emails/                     # HTML email templates
        ├── employer/                   # Employer dashboard and pipeline
        ├── errors/                     # 403, 404, 500 error pages
        ├── evidence/                   # Evidence new, edit, detail, skills review
        ├── main/                       # Public pages (home, pricing, blog, contact, legal)
        ├── onboarding/                 # 3-step onboarding wizard
        ├── profile/                    # Public profile, edit profile
        ├── settings/                   # Account, billing, notifications settings
        ├── talent/                     # Talent dashboard
        └── verification/               # Request and respond to verifications
```

---

## Getting Started

### Prerequisites

Make sure you have these installed before you begin:

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** — comes bundled with Python 3.10+
- **Git** — [git-scm.com](https://git-scm.com/)
- **PostgreSQL** (production only) — [postgresql.org/download](https://www.postgresql.org/download/) — SQLite works fine for local development
- A **Google Gemini API key** — [aistudio.google.com](https://aistudio.google.com/) (free tier available)
- A **Razorpay account** (test mode works) — [razorpay.com](https://razorpay.com)
- A **Mailtrap account** for local email testing — [mailtrap.io](https://mailtrap.io) (free tier available)
- An **AWS account** (production S3 only) — [aws.amazon.com](https://aws.amazon.com)

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/shahram8708/proven.git
cd proven
```

**2. Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

**3. Install all dependencies**

```bash
pip install -r requirements.txt
```

**4. Create your `.env` file**

There is no `.env.example` in the repository, so create a `.env` file in the project root manually:

```bash
touch .env   # macOS / Linux
# or just create the file in your editor
```

Populate it with the variables described in the [Environment Variables](#environment-variables) section below.

**5. Initialise the database**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

> **Note:** On first run, `run.py` also calls `init_database()` and `seed_data()` automatically, so the explicit migration step is only needed if you want to manage schema changes with Alembic.

**6. Run the application**

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000). The database tables are created, skills are seeded, and a default admin account is created on startup.

---

### Environment Variables

Create a `.env` file in the project root with the following variables:

| Variable | Description | Example |
|---|---|---|
| `FLASK_ENV` | Runtime environment — `development`, `production`, or `testing` | `development` |
| `SECRET_KEY` | Flask secret key for session signing (use a long random string in production) | `my-super-secret-key-change-me` |
| `DATABASE_URL` | Database connection URI. Defaults to SQLite in development | `sqlite:///proven_dev.db` |
| `GEMINI_API_KEY` | Google Gemini API key for AI skill extraction, scoring, and fraud detection | `AIza...` |
| `RAZORPAY_KEY_ID` | Razorpay API key ID (use test key `rzp_test_...` in development) | `rzp_test_xxxxxxxxxxxxxxxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret | `your_razorpay_secret` |
| `RAZORPAY_WEBHOOK_SECRET` | Razorpay webhook secret for HMAC signature verification | `your_webhook_secret` |
| `MAIL_SERVER` | SMTP server hostname | `smtp.mailtrap.io` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | Enable TLS for SMTP | `True` |
| `MAIL_USERNAME` | SMTP username | `your_mailtrap_username` |
| `MAIL_PASSWORD` | SMTP password | `your_mailtrap_password` |
| `MAIL_DEFAULT_SENDER` | From address for all outbound email | `noreply@proven.work` |
| `BASE_URL` | Full base URL of the app — used in email links | `http://localhost:5000` |
| `STORAGE_BACKEND` | File storage backend: `local` or `s3` | `local` |
| `AWS_ACCESS_KEY_ID` | AWS access key (required when `STORAGE_BACKEND=s3`) | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `your_aws_secret` |
| `AWS_S3_BUCKET` | S3 bucket name | `proven-evidence-files` |
| `AWS_S3_REGION` | AWS region | `ap-south-1` |
| `MAX_FILE_SIZE_MB` | Maximum upload size per file in megabytes | `5` |
| `MAX_EVIDENCE_FILES` | Maximum number of files per evidence submission | `5` |
| `DAILY_EVIDENCE_LIMIT` | Maximum evidence submissions per user per day | `10` |
| `ADMIN_EMAIL` | Default admin account email (created on first run) | `admin@proven.work` |
| `ADMIN_PASSWORD` | Default admin account password | `ProvenAdmin@2026` |
| `ADMIN_USERNAME` | Default admin account username | `provenadmin` |
| `ADMIN_FIRST_NAME` | Admin first name | `Proven` |
| `ADMIN_LAST_NAME` | Admin last name | `Admin` |

---

### Running the Project

**Development mode**

```bash
python run.py
```

Flask runs with `debug=True` and `use_reloader=False` (reloader is disabled to avoid double-seeding). The app is available at [http://localhost:5000](http://localhost:5000).

**Production mode with Gunicorn**

```bash
gunicorn wsgi:app --workers 4 --bind 0.0.0.0:8000
```

Set `FLASK_ENV=production` in your environment before running in production. This switches to `ProductionConfig`, which enforces `SESSION_COOKIE_SECURE=True`, requires a PostgreSQL `DATABASE_URL`, and defaults `STORAGE_BACKEND` to `s3`.

---

## Usage

### For Talent

1. Sign up at `/signup` and choose "Talent" as your account type.
2. Verify your email via the link sent to your inbox.
3. Complete the 3-step onboarding: choose your primary domain, set your experience level, and select your career goals.
4. From your dashboard, click **Add Evidence** to write your first work story.
5. Fill in all six sections — the more specific you are about what you did and what measurably changed, the higher your quality score.
6. On the Skills Review page, review and confirm the skills Gemini extracted from your evidence.
7. Publish your evidence, then request verifications from former colleagues using the **Request Verification** button.
8. Browse the **Challenge Library** and complete a challenge to boost your profile with an AI-scored demonstration.

### For Employers

1. Sign up at `/signup` and choose "Employer" as your account type.
2. Verify your email and complete onboarding.
3. Navigate to **Discover** to search the talent pool using domain, skills, experience, evidence count, verification rate, and challenge filters.
4. Click any talent card to open a slide-in drawer with their full profile — evidence, skills radar, verification badges, and challenge scores.
5. Save interesting candidates to a **Talent List** for later review.
6. Use **Contact Credits** (included in your subscription) to send a contact request directly to a talent's email.
7. Move candidates through your **Pipeline** — shortlisted → interviewing → offered → hired.
8. Post a **Sponsored Challenge** on the Employer Dashboard to attract self-motivated candidates in your domain.

---

## API Documentation

Proven is a server-rendered web application. The only JSON API endpoints are for the Razorpay payment flow.

### POST `/billing/create-order`

Creates a Razorpay order for a given subscription plan.

**Authentication:** Login required.

**Request body (JSON):**
```json
{ "plan_id": "talent_pro" }
```

Valid `plan_id` values: `talent_pro`, `employer_starter`, `employer_team`.

**Response:**
```json
{
  "order_id": "order_xxxxxxxxxxxxxxxxx",
  "amount": 74900,
  "currency": "INR",
  "key": "rzp_test_xxxxxxxxxxxxxxxx"
}
```

---

### POST `/billing/verify-payment`

Verifies a Razorpay payment signature and activates the user's subscription.

**Authentication:** Login required.

**Request body (JSON):**
```json
{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "xxxxx",
  "plan_id": "talent_pro"
}
```

**Response:**
```json
{ "success": true, "message": "Subscription activated successfully" }
```

---

### POST `/billing/webhook`

Razorpay webhook endpoint for subscription lifecycle events (`subscription.activated`, `subscription.cancelled`). CSRF exempt. Signature verified via `HMAC-SHA256` using `RAZORPAY_WEBHOOK_SECRET`.

---

### POST `/discover/contact/<talent_user_id>`

Sends a contact request email to a talent user. Deducts one contact credit from the employer's account.

**Authentication:** Login required (employer + premium).

---

### POST `/discover/list/add`

Adds a talent user to an employer's named list.

**Authentication:** Login required (employer).

**Request body (JSON):**
```json
{ "talent_id": 42, "list_id": 7 }
```

---

## Configuration

Configuration is class-based in `app/config.py`. Three classes are available:

- `DevelopmentConfig` — SQLite database, local file storage, `DEBUG=True`, no secure cookies.
- `ProductionConfig` — Requires a PostgreSQL `DATABASE_URL`, enforces `SESSION_COOKIE_SECURE=True`, defaults to S3 file storage.
- `TestingConfig` — In-memory SQLite, CSRF disabled, local file storage.

Select the config by setting `FLASK_ENV` in your environment to `development`, `production`, or `testing`. The app factory reads this variable at startup.

Key configurable defaults:

| Setting | Default | Description |
|---|---|---|
| `MAX_CONTENT_LENGTH` | `5 MB` | Max file upload size (controlled by `MAX_FILE_SIZE_MB`) |
| `MAX_EVIDENCE_FILES` | `5` | Files per evidence submission |
| `DAILY_EVIDENCE_LIMIT` | `10` | Submissions per user per 24 hours |
| `PERMANENT_SESSION_LIFETIME` | `365 days` | How long login sessions persist |
| `RATELIMIT_STORAGE_URI` | `memory://` | Rate limit backend (use Redis in production for multi-worker) |

---

## Testing

The project does not currently include an automated test suite. No test files, pytest configuration, or test fixtures are present in the repository.

The `how-it-work.md` file serves as a comprehensive manual testing guide, walking through every feature phase by phase — from environment setup and public pages through talent and employer flows, billing, admin tools, and edge cases.

A `TestingConfig` class is defined in `config.py` (in-memory SQLite, CSRF off) and is ready to be used with pytest + Flask's test client when tests are added.

---

## Deployment

### Gunicorn (any Linux server / VPS)

**1. Set environment variables** (via `.env` or your server's environment management):
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:password@host:5432/proven
export SECRET_KEY=your-production-secret-key
# ... all other variables from the Environment Variables table
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run database migrations:**
```bash
flask db upgrade
```

**4. Start with Gunicorn:**
```bash
gunicorn wsgi:app --workers 4 --bind 0.0.0.0:8000 --timeout 120
```

Proxy this through Nginx and add an SSL certificate (e.g., via Let's Encrypt / Certbot) for production.

---

### Heroku / Railway / Render

The app is Gunicorn-ready. Add a `Procfile` in the project root:

```
web: gunicorn wsgi:app
```

Set all environment variables via the platform's dashboard. Make sure `DATABASE_URL` points to the platform's PostgreSQL add-on and that `FLASK_ENV=production`.

---

### AWS / Cloud (General Notes)

- **File uploads:** Set `STORAGE_BACKEND=s3` and configure your S3 bucket with appropriate IAM permissions for `PutObject`, `GetObject`, and `DeleteObject`. The default bucket is `proven-evidence-files` in `ap-south-1`.
- **Email:** Use SES or your SMTP provider of choice; configure `MAIL_*` variables accordingly.
- **Rate limiting:** The default `RATELIMIT_STORAGE_URI=memory://` won't work correctly across multiple Gunicorn workers. Switch to a Redis URI: `redis://your-redis-host:6379/0`.

---

## Contributing

Pull requests are welcome. Here's how to get involved:

**1. Fork the repository** and create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

**2. Make your changes.** Keep commits focused — one logical change per commit.

**3. Follow the code style:**
- Python: PEP 8. Blueprint functions are lowercase with underscores.
- Templates: Jinja2 with consistent 4-space indentation.
- Services are pure functions where possible — keep business logic out of route handlers.

**4. Open a Pull Request** with a clear description of what changed and why.

**Reporting bugs:**
Open a GitHub Issue with: Python version, OS, steps to reproduce, expected behaviour, and actual behaviour (including any traceback).

**Requesting features:**
Open a GitHub Issue with: the use case you're trying to solve, the proposed solution, and any alternative approaches you considered.

---

## Roadmap

Based on the codebase structure, TODOs, and feature completeness, here's what's shipped and what's in the wings:

- [x] Talent evidence submission with six-section narrative structure
- [x] AI-powered skill extraction (Gemini 2.5 Flash)
- [x] Peer verification via token-protected email links
- [x] Evidence quality scoring (multi-factor, 0–100)
- [x] Fraud detection engine (plagiarism, velocity, AI consistency, ring detection)
- [x] Employer talent search with advanced filters
- [x] Talent lists and hiring pipeline
- [x] Work challenge library with AI rubric scoring
- [x] Sponsored challenges for employers
- [x] Razorpay subscription billing (INR, three tiers)
- [x] AWS S3 file storage backend
- [x] Admin dashboard and fraud review queue
- [x] Profile strength score and radar chart visualisation
- [ ] LinkedIn OAuth signup / profile import
- [ ] Automated test suite (pytest + Flask test client)
- [ ] Redis-backed rate limiting for multi-worker production
- [ ] Background job queue (Celery or RQ) for async AI scoring
- [ ] Notification centre (in-app, not just email)
- [ ] Employer company profiles with public-facing branded pages
- [ ] API endpoints for mobile app consumption
- [ ] International payment gateway support (Stripe)

---

## License

No license file was found in the repository. All rights are reserved by default until a license is added. If you intend to use, modify, or distribute this code, contact the author for permission.

---

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/) and the Pallets team for a framework that gets out of your way.
- [Google Gemini](https://deepmind.google/technologies/gemini/) for making it genuinely easy to put a capable LLM inside an application — the AI scoring and extraction in Proven would have taken weeks to build with older approaches.
- [Razorpay](https://razorpay.com) for a payment API that actually works well in the Indian market.
- [Chart.js](https://www.chartjs.org/) for the radar charts that make skill profiles feel visual and alive.
- [Mailtrap](https://mailtrap.io) for making local email development painless.
- [SQLAlchemy](https://www.sqlalchemy.org/) for an ORM that handles complex joins without complaining.

---

## Contact / Author

Author information was not found in `package.json`, git config, or any project file. Based on domain references in the config (`proven.work`), this project belongs to the **Proven** team.

- 🌐 Website: [proven.work](https://proven.work) *(referenced in config)*
- 📧 Default sender: `noreply@proven.work`
- 🛡️ Admin contact: `admin@proven.work`

If you found a bug, have a question, or just want to say the fraud detection ring analysis is genuinely impressive — open an issue or send an email. This project is worth building on.