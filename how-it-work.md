## Phase 0: Environment Setup & First Run

Before testing any feature, you must verify your environment is correctly configured.

**Step 1: Check Python version**
```bash
python --version
```
Expected output: `Python 3.10.x` or higher. If lower, upgrade Python first.

**Step 2: Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```
You should see `(venv)` at the start of your terminal line after activation.

**Step 3: Install all dependencies**
```bash
pip install -r requirements.txt
```
Wait for all packages to install. If any error appears, note the package name and install it separately:
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf flask-mail flask-limiter flask-migrate google-genai razorpay boto3 python-magic pillow gunicorn psycopg2-binary python-dotenv itsdangerous werkzeug wtforms email-validator
```

**Step 4: Create your `.env` file**
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Now open `.env` in a text editor and fill in these values for local testing:
```env
FLASK_ENV=development
SECRET_KEY=myproventestkey1234567890abcdef
DATABASE_URL=sqlite:///proven_dev.db
GEMINI_API_KEY=your-actual-gemini-api-key-here
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your-razorpay-test-secret
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_DEFAULT_SENDER=noreply@proven.work
BASE_URL=http://localhost:5000
MAX_EVIDENCE_FILES=5
MAX_FILE_SIZE_MB=5
```
For local testing, use **SQLite** (no PostgreSQL setup needed). Use Mailtrap.io for email — it's free and captures all emails without sending them.

**Step 5: Initialize the database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```
Expected output: `INFO  [alembic.runtime.migration] Running upgrade -> xxxxxxx`

**Step 6: Seed the database**
```bash
python seed/seed_skills.py
python seed/seed_challenges.py
```
Expected output: `Seeded 300 skills successfully` and `Seeded 20 challenges successfully`

**Step 7: Run the app**
```bash
python run.py
```
Expected output:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```
Open `http://localhost:5000` in your browser. You should see the Proven homepage.

---

Here is a visual map of all testing phases:---

## Phase 1: Public Pages Testing

Open browser at `http://localhost:5000` and test each page manually.

**Homepage (`/`)**
- Visit `http://localhost:5000`
- Check: Hero headline visible ("Your skills are real. Now prove it.")
- Check: Two buttons visible — "Build Your Profile — Free" and "Find Verified Talent"
- Check: Navigation bar has Logo, How It Works, For Employers, Pricing, Blog links
- Check: Footer has Privacy, Terms, Contact links
- Click "How It Works" — should go to `/how-it-works`
- Click "For Employers" — should go to `/for-employers`
- Click "Pricing" — should go to `/pricing` and show ₹ prices in Indian Rupees

**Challenge Library (`/challenges`)**
- Visit `http://localhost:5000/challenges`
- You should see challenge cards (seeded from `seed_challenges.py`)
- Click any challenge card — should go to `/challenges/<id>` with the brief visible
- A "Login to Take This Challenge" button should appear if you are not logged in

**Contact Page (`/contact`)**
- Visit `http://localhost:5000/contact`
- Fill in: Name = `Ravi Sharma`, Email = `ravi@example.com`, Message = `I want to know more about Proven`
- Click Submit
- Expected: Green flash message "Your message has been sent."

---

## Phase 2: Authentication System Testing

**Test 1: Talent User Registration**
- Go to `http://localhost:5000/signup`
- Select account type: **Talent**
- Fill the form:
  - First Name: `Ravi`
  - Last Name: `Sharma`
  - Email: `ravi.sharma@testmail.com`
  - Password: `TestPass@2024Secure`
  - Confirm Password: `TestPass@2024Secure`
- Click "Create Account"
- Expected: Redirect to a page saying "Check your email to verify your account"
- Go to **Mailtrap.io** → inbox → find email from `noreply@proven.work` → click the verification link
- Expected: Redirect to login page with flash "Email verified successfully!"

**Test 2: Login**
- Go to `http://localhost:5000/login`
- Email: `ravi.sharma@testmail.com`
- Password: `TestPass@2024Secure`
- Click Login
- Expected: Redirect to `/onboarding` (since onboarding is not complete)

**Test 3: Wrong Password**
- Go to `/login`
- Email: `ravi.sharma@testmail.com`
- Password: `WrongPassword123`
- Expected: Red flash message "Invalid email or password"

**Test 4: Forgot Password**
- Go to `/forgot-password`
- Email: `ravi.sharma@testmail.com`
- Click "Send Reset Link"
- Go to Mailtrap → find the reset email → click the link
- Enter new password: `NewPass@2024Secure`
- Confirm: `NewPass@2024Secure`
- Expected: "Password reset successful. Please log in."

**Test 5: Employer Registration**
- Logout first: go to `/logout`
- Go to `/signup`
- Select account type: **Employer**
- Fill:
  - First Name: `Elena`
  - Last Name: `Mukherjee`
  - Email: `elena@techstartup.in`
  - Company Name: `TechStartup India`
  - Password: `EmployerPass@2024`
- Complete email verification from Mailtrap
- Expected: Redirect to employer onboarding

---

## Phase 3: Onboarding Flow Testing

Log in as `ravi.sharma@testmail.com`. After login you should land on `/onboarding`.

**Step 1 — Primary Domain:**
- Select: `Technology`
- Click Next

**Step 2 — Years of Experience:**
- Enter: `4`
- Click Next

**Step 3 — Goals:**
- Select: `Freelance clients`
- Also select: `Full-time opportunities`
- Click Finish
- Expected: Redirect to `/dashboard` with Profile Strength at about 5-10%

---

## Phase 4: Evidence Submission Testing

Log in as `ravi.sharma@testmail.com`. Go to `/evidence/new`.

**Fill the full 6-step form with these REAL inputs:**

**Step 1 — Title and Type:**
- Evidence Title: `Built a Multi-Tenant SaaS Dashboard for an Indian Fintech Client`
- Evidence Type: `Project Delivery`
- Click Next Step

**Step 2 — Context & Situation:**
```
The client was a Pune-based lending startup with 12,000 active borrowers. Their 
loan officers were tracking repayments using three separate Excel sheets, causing 
data reconciliation errors that delayed loan approvals by 3-4 days per cycle. 
They needed a unified web dashboard that all 8 loan officers could use simultaneously, 
with real-time data and role-based access.
```
- Click Next Step

**Step 3 — Your Approach:**
```
I started with a 2-hour discovery call to understand the existing Excel workflow 
and identify which data fields were most critical. I chose React for the frontend 
and Node.js + PostgreSQL for the backend to support concurrent users. I proposed 
a 3-week delivery timeline: Week 1 for backend API and database schema, Week 2 for 
the React dashboard UI, Week 3 for data migration and testing. I communicated 
progress daily via WhatsApp and held a mid-project demo at the end of Week 2 to 
course-correct before final delivery.
```
- Click Next Step

**Step 4 — Key Decisions and Reasoning:**
```
The most critical decision was whether to migrate the existing Excel data into 
PostgreSQL or keep Excel as a source of truth with the dashboard as a read-only 
view. I chose full migration because read-only integration would not solve the 
concurrent-editing problem. I also chose not to use a no-code tool like Airtable 
because the client needed custom repayment calculation logic that no-code tools 
could not support. I used JWT authentication instead of session-based auth because 
the client later wanted a mobile app and JWTs are mobile-friendly.
```
- Click Next Step

**Step 5 — Outcome:**
```
Delivered the dashboard on day 19 of the 21-day timeline. The loan approval cycle 
dropped from 3-4 days to 6 hours. Data reconciliation errors dropped to zero in 
the first month. All 8 loan officers adopted the system within the first week with 
no training needed beyond a 30-minute demo. The client extended the contract for 
3 additional months to add an analytics module.
```
- Click Next Step

**Step 6 — Skills and Reflection:**
```
Skills demonstrated: React, Node.js, PostgreSQL, REST API design, project management, 
client communication, requirements gathering, database schema design, user authentication.

Reflection: I underestimated the complexity of migrating 2 years of Excel data into a 
normalized database schema. It took 6 hours instead of the estimated 2. In future 
projects I will build a data audit step into the project timeline before the migration 
sprint begins. I also learned that showing working software in a mid-project demo 
builds far more client trust than status update emails.
```
- Team Size: `Solo`
- Project Scale: `Team`
- Click Submit Evidence

**After submission:**
- Expected: Loading spinner → Screen showing AI-extracted skill tags
- You should see tags like: `React`, `Node.js`, `PostgreSQL`, `Project Management`, `Client Communication`
- Review each tag. If any is wrong, remove it. Confirm the correct ones.
- Click "Confirm Skills"
- Expected: Redirect to verification request page

**Auto-save test:** Start filling a new evidence form. Fill Step 1 only. Close the browser tab. Log in again → go to Dashboard. Under "Drafts" you should see the partially filled evidence saved automatically.

---

## Phase 5: AI Skill Extraction Testing

After confirming skills in Phase 4, go to your dashboard at `/dashboard`.

**Check these things:**
- Under "My Evidence" you should see the evidence card with Title, Evidence Type badge, and Verification Status = "Unverified"
- Click on the evidence card → go to `/evidence/<id>`
- You should see the full 6-field submission, the quality score (should be around 55-70 out of 100), and the confirmed skill tags
- Go to `/profile/ravisharma` (your public profile URL)
- You should see the Capability Radar Chart with scores in Technical Skills, Process Skills, and Communication dimensions

**Test with minimal input (edge case):**
Create another evidence submission with very short answers:
- Situation: `Fixed a bug`
- Approach: `I looked at the code`
- Decisions: `Used a fix`
- Outcome: `Bug was fixed`
- Skills: `Coding`
- Reflection: `Learned something`
- Expected: Quality Score should be low (around 10-20). The AI should extract very few skill tags. This confirms the quality scoring engine works.

---

## Phase 6: Verification System Testing

You need two different email accounts for this test.

**From talent account (`ravi.sharma@testmail.com`):**
- Go to your published evidence at `/evidence/<id>`
- Click "Request Verification"
- Enter verifier email: `client@another-test.com` (use a second Mailtrap inbox)
- Specific claim: `I am asking you to confirm that Ravi independently built the dashboard described, delivered it within the 21-day timeline, and that loan approval times improved as stated.`
- Click "Send Verification Request"
- Expected: Flash "Verification request sent to client@another-test.com"

**From the verifier's side:**
- Go to Mailtrap → second inbox → open the verification request email
- Click the verification link in the email
- You should land on `/verify/respond/<token>` WITHOUT needing to log in
- You should see Ravi's evidence card and the specific claim he asked about
- Select: `I confirm this is accurate`
- Fill: Verifier Name = `Priya Kapoor`, Role = `CTO`, Company = `LendFast India`
- Click "Submit Verification"
- Expected: Thank you screen with soft CTA to create a free Proven account

**Back on talent account:**
- Refresh the evidence card at `/evidence/<id>`
- You should now see: "Verified by 1 witness — Priya Kapoor, CTO at LendFast India"
- Quality Score should have increased (verification adds 15 points)
- Go to public profile: `/profile/ravisharma` — Verification badge should now show "1 Verified"

**Edge cases to test:**
- Try to visit an expired token URL: manually change the token in the URL → Expected: "This verification link has expired or is invalid"
- Try to respond to the same token a second time → Expected: "You have already responded to this verification request"

---

## Phase 7: Work Challenges Testing

**Browse challenges (logged out):**
- Log out → go to `/challenges`
- You should see challenge cards from the seed data
- Click any challenge → should show brief preview
- Click "Take This Challenge" → should redirect to `/login`

**Take a challenge (logged in as talent):**
- Log in as `ravi.sharma@testmail.com`
- Go to `/challenges`
- Click the challenge: "Analyze a SaaS Churn Problem" (from seed data)
- Go to `/challenges/take/<id>`
- You should see: challenge brief, timer countdown, text submission area
- Write a real response:
```
Based on the data provided showing 15% monthly churn, I would start by segmenting 
churn by customer cohort to identify whether it is concentrated in new users 
(first 30 days) or long-term users. If churn is early-stage, the problem is 
onboarding. If it is long-term, the problem is product-market fit or competitive 
displacement.

My first action would be to run a 10-user exit interview study specifically 
targeting churned users from the last 30 days. I would ask: What was the primary 
reason you stopped using the product? What were you trying to do that the product 
did not support? What did you switch to and why?

Based on typical SaaS patterns, I would hypothesize that early churn is caused by 
the product failing to deliver value in the first session. My retention recommendation 
would be a structured onboarding checklist with a milestone-based email sequence 
triggered by specific in-app actions, not just time-based drip emails.

Success metric: Reduce 30-day churn from 15% to below 8% within 2 quarters.
```
- Click "Submit Challenge"
- Expected: AI scoring loading screen → Score displayed (e.g. 74/100) with feedback
- Expected: Challenge completion card visible on your public profile

---

## Phase 8: Employer Account & Discovery Testing

**Create an employer account:**
- Use the employer account: `elena@techstartup.in` (created in Phase 2)
- Log in as Elena
- Complete employer onboarding:
  - Company Name: `TechStartup India`
  - Industry: `Technology`
  - Company Size: `11-50`
  - Click Finish
- Expected: Redirect to `/employer/dashboard`

**Talent Discovery (`/discover`):**
- Go to `/discover`
- You should see the 3-column layout: filters | results | preview drawer
- In the filter panel, select:
  - Domain: `Technology`
  - Minimum Verification Rate: `50%` (drag slider)
  - Challenge Completion: check the box
- Click Search / Apply Filters
- You should see Ravi Sharma's card in the results (because he has verified evidence and a challenge submission)
- Click Ravi's card → Profile preview drawer should slide in from the right
- Inside the drawer: evidence summaries, capability radar chart, top skill tags
- Click "View Full Profile" → Opens `/profile/ravisharma`

**Saved Talent Lists:**
- In the discovery drawer, click "Save to List" → "Create New List"
- List Name: `Senior Backend — Q1 2025`
- Click Save
- Go to `/discover/lists` → You should see the list with Ravi's name
- Click the list → Go to list detail
- Change pipeline stage for Ravi: from `Shortlisted` → `Contacted`
- Add employer note (private): `Strong fintech background. Schedule call for Jan 15.`
- This note must NEVER appear if you log in as Ravi and view your own profile

**Verify privacy of employer notes:**
- Log out → Log in as `ravi.sharma@testmail.com`
- Go to `/profile/ravisharma` or `/dashboard`
- The employer note "Strong fintech background..." must NOT appear anywhere
- This is a critical security test — if this note is visible, there is a bug

---

## Phase 9: Razorpay Payment Testing

**Important:** Use Razorpay test mode only. Never use real card details.

**Get test card details from Razorpay:**
- Card Number: `4111 1111 1111 1111`
- Expiry: `12/26`
- CVV: `123`
- Name: `Test User`

**Test employer subscription:**
- Log in as `elena@techstartup.in`
- Go to `/settings/billing`
- You should see three plan cards with prices in ₹: Starter ₹8,299/mo, Team ₹29,199/mo
- Click "Subscribe" on the Starter plan
- The Razorpay checkout modal should open
- Fill in the test card details above
- Click Pay
- Expected: Modal closes → Flash "Subscription activated successfully"
- Go to dashboard → you should now have "Starter" plan active
- Profile features that were locked should now be accessible (50 profile views, advanced filters)

**Test failed payment:**
- Go to `/settings/billing`
- Click Subscribe on Team plan
- In the Razorpay modal, use a declined card: `4000 0000 0000 0002`
- Expected: Payment failure message from Razorpay — "Your payment was declined"
- Your subscription tier should remain unchanged

**Test talent pro subscription:**
- Log in as `ravi.sharma@testmail.com`
- Go to `/settings/billing`
- Click "Upgrade to Talent Pro — ₹749/month"
- Complete test payment
- Expected: "Profile view analytics" section appears on dashboard

---

## Phase 10: Fraud Detection Testing

These tests verify the fraud system catches bad actors.

**Test 1: Duplicate submission detection**
- Log in as `ravi.sharma@testmail.com`
- Create a second evidence submission
- Copy-paste the exact same text from your first submission into all 6 fields
- Change only the title
- Submit it
- Expected: Evidence should be flagged (check the admin panel — it should appear in the fraud queue with "medium" or "high" suspicion level)

**Test 2: Velocity check**
- Try to submit more than 10 evidence items within 24 hours
- After the 10th submission, the 11th should be blocked
- Expected: Flash message "You have reached the daily evidence submission limit"

**Test 3: Short, vague submission**
- Create a new evidence submission with very generic text:
  - Title: `Did some work`
  - Situation: `There was a problem at work`
  - Approach: `I helped solve it`
  - Decisions: `Made good decisions`
  - Outcome: `Everything went well`
  - Reflection: `Learned a lot`
- Expected: AI consistency check gives low score. Quality score should be under 20. It should still allow submission (it's low suspicion, not automatic ban), but the quality badge should show "Low Quality" in a grey/red indicator.

---

## Phase 11: Admin Panel Testing

**Create an admin user directly in the database:**
```bash
# Open Python shell
flask shell

# Inside the shell
from app.models.user import User
from app import db
admin = User.query.filter_by(email='ravi.sharma@testmail.com').first()
admin.is_admin = True
db.session.commit()
print("Admin access granted")
exit()
```

**Test admin panel:**
- Log in as `ravi.sharma@testmail.com`
- Go to `http://localhost:5000/admin`
- Expected: Admin dashboard showing:
  - Total users count (should be 2 or more)
  - Evidence submissions count
  - Verifications count
  - Challenge completions count

**Test admin user list:**
- Go to `/admin/users`
- You should see all registered users in a table
- Search by email: type `elena` → should filter to Elena's account
- Click "Suspend Account" on a test user → Expected: That user can no longer log in

**Test fraud queue:**
- Go to `/admin/fraud`
- The duplicate submission from Phase 10 Test 1 should appear here
- Click "Review" on the flagged evidence
- Read the fraud reason
- Click "Approve" to clear it or "Ban User" to take action

**Test access control:**
- Log out → Log in with a non-admin account
- Try to visit `http://localhost:5000/admin`
- Expected: 403 Forbidden error page

---

## Phase 12: Security Testing

**Test 1: CSRF protection**
- Open browser developer tools (F12) → Network tab
- Try to submit a form
- Check the POST request headers — you should see `X-CSRFToken` in the request
- If you remove the CSRF token from a form and submit it manually using a tool like Postman, you should get a 400 Bad Request error

**Test 2: Rate limiting**
- Go to `/login`
- Enter wrong password 11 times in a row
- Expected: After 10 failed attempts, you should see "Too many login attempts. Please try again in 15 minutes."

**Test 3: Unauthorized access**
- While logged out, try to visit `http://localhost:5000/evidence/new`
- Expected: Redirect to `/login`
- While logged in as talent, try to visit `http://localhost:5000/discover`
- Expected: 403 Forbidden (discovery is employer-only)
- While logged in as employer, try to visit `http://localhost:5000/evidence/new`
- Expected: 403 Forbidden (evidence submission is talent-only)

**Test 4: Mobile responsiveness**
- Open Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)
- Test on these 3 sizes:
  - 320px width (iPhone SE)
  - 768px width (iPad)
  - 1280px width (laptop)
- On 320px: Navigation should collapse to a hamburger menu. Evidence cards should stack vertically. Discovery filter panel should collapse.
- On 768px: Two-column layouts should become single column.
- On 1280px: Full 3-column discovery layout should show.

**Test 5: SQL injection attempt**
- Go to the talent discovery search
- In the keyword search box, type: `'; DROP TABLE users; --`
- Click Search
- Expected: The query runs normally with no results — it does NOT crash, does NOT delete data. SQLAlchemy's parameterized queries protect against this.

---

## Phase 13: Full End-to-End Flow Test

This final test simulates the complete real-world user journey from start to finish.

**The scenario:** A self-taught developer (Ravi) builds his verified profile, and an employer (Elena) finds and contacts him.

1. Log in as Ravi → Submit 3 evidence items with full detail (use the Phase 4 input as a template, create 3 variations with different projects)
2. Request verification for each evidence item (use different verifier emails)
3. Respond to all 3 verification requests (from Mailtrap)
4. Complete 2 work challenges
5. Check public profile `/profile/ravisharma` — Verification Score should be above 60%, Profile Strength above 50%, Radar chart should show data in at least 3 dimensions
6. Log out → Log in as Elena
7. Go to `/discover` → Filter by `Technology` domain, min verification rate `50%`
8. Find Ravi's card in results
9. Open profile preview drawer → Click "View Full Profile"
10. Save Ravi to a talent list → Set pipeline stage to "Shortlisted"
11. Elena has Starter plan (from Phase 9) → Click "Request to Connect"
12. Check Mailtrap → Ravi should have received a contact request notification email
13. Log in as Ravi → Go to dashboard → Accept the contact request
14. Expected: Pipeline stage for Elena's list should update to "Contacted"

If all 14 steps complete without errors, your platform is working end-to-end.

---

## Quick Reference: Test Accounts Summary

| Account | Email | Password | Type | Purpose |
|---|---|---|---|---|
| Talent | `ravi.sharma@testmail.com` | `TestPass@2024Secure` | Talent | Main talent user testing |
| Employer | `elena@techstartup.in` | `EmployerPass@2024` | Employer | Discovery & payment testing |
| Verifier | `client@another-test.com` | n/a (no login needed) | External | Verification response testing |
| Admin | (same as Ravi, after db upgrade) | same | Admin | Admin panel testing |

---

## Common Errors and Fixes

**"500 Internal Server Error" on any page:**
- Check your terminal where Flask is running — the full error traceback is there
- Most common cause: a missing `.env` variable or a database table not created

**"Import Error: No module named google.genai":**
```bash
pip install google-genai
```

**"Import Error: No module named razorpay":**
```bash
pip install razorpay
```

**Email not arriving in Mailtrap:**
- Check that `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` in `.env` match your Mailtrap SMTP credentials exactly
- Go to Mailtrap.io → My Inbox → SMTP Settings → copy the values from there

**Razorpay modal not opening:**
- Make sure `RAZORPAY_KEY_ID` in `.env` starts with `rzp_test_` (not `rzp_live_`)
- Open browser console (F12) — any JS error will tell you what's wrong

**Database migration error:**
```bash
flask db stamp head
flask db migrate
flask db upgrade
```

Work through the phases in order. Once all 13 phases pass, your platform is ready for production deployment.