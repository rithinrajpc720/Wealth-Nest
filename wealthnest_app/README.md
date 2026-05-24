# 🪙 WealthNest

> Build wealth habits as a family. Together.

A complete family financial literacy platform — chores, allowances, savings goals, achievement badges, and an AI money coach — built with Django + SQLite + Google Gemini. **BCA Final Year Project.**

![Tech](https://img.shields.io/badge/Django-4.2-092E20?logo=django) ![Tech](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![Tech](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite) ![AI](https://img.shields.io/badge/AI-Gemini%201.5-F6C90E)

---

## ✨ Features

### 👨‍👩‍👧‍👦 Three Roles
- **Admin** — Platform oversight, family enrollment control, telemetry, taxonomies, complaint handling
- **Household Head** — Manage chores, approve submissions, set allowances, view family analytics
- **Family Dependent (Child / Teen / Young Adult)** — Complete chores, log spending, save toward goals, earn badges

### 🎯 Core Modules
| Module | Description |
|--------|-------------|
| 🪙 Chore Reward System | Assign → Submit → Approve → Auto-credit reward |
| 📅 Allowance Manager | Weekly / monthly recurring allowance schedules |
| 🎯 Savings Goals | Visual progress bars with milestone celebrations |
| 💸 Expense Tracking | Categorized spending with budget validation |
| 📈 Family Analytics | Chart.js dashboards for parents and kids |
| 🏆 Achievements | XP, levels, streaks, unlockable badges |
| 🤖 AI Money Coach | Gemini 1.5 Flash with role-aware prompting |
| 📮 Complaints + 💬 Feedback | Two-way platform communication |
| 💳 Payment System (Demo) | Subscription plans + simulated card / UPI / netbanking flow |

### 🎨 Design System — "Warm Prosperity"
- Deep Indigo `#1E1B4B` + Prosperity Gold `#F6C90E` palette
- Poppins (headings) + Manrope (body)
- Confetti celebrations, coin-stack animations, achievement medals
- Full dark/light mode with localStorage persistence
- Responsive (Bootstrap 5) + AOS scroll reveals + GSAP hero animations

---

## 🛠️ Tech Stack

**Frontend:** HTML5 · CSS3 · Vanilla JS (ES6+) · Bootstrap 5 · Chart.js · DataTables · AOS · GSAP · Google Fonts

**Backend:** Python 3.11+ · Django 4.2 · SQLite3 · *(no DRF — pure Django views/forms/templates/ORM)*

**AI:** Google Gemini API (`google-generativeai`, model `gemini-1.5-flash`)

**Auth:** Custom role-based session authentication (no `django.contrib.auth.User` for end users)

---

## 🚀 Quick Start

```bash
# 1. Clone & enter the project folder
git clone <your-repo> WealthNest
cd WealthNest/wealthnest_app

# 2. Create virtual env (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional — chatbot falls back to canned replies)

# 5. Migrate DB & seed data
python manage.py migrate
python manage.py seed_data

# 6. Run!
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) and you're live!

### 🔑 Default Credentials

| Role | URL | Username | Password |
|------|-----|----------|----------|
| Admin | `/accounts/admin/login/` | `admin` | `admin123` |
| Parent | `/accounts/head/register/` | *create* | *create* |
| Kid/Teen | `/accounts/dependent/register/` | *(use parent's family PIN)* | *create* |

---

## 📁 Project Structure

```
wealthnest_app/
├── wealthnest/              # Django project (settings, root urls)
├── accounts/                # Login, password reset, decorators
│   └── management/commands/ # seed_data
├── admin_panel/             # Admin dashboard, enrollment, taxonomies
├── families/                # Family + join PIN
├── heads/                   # HouseholdHead, family management
├── dependents/              # FamilyDependent, kid views
├── chores/                  # Chore + ChoreSubmission
├── transactions/            # Transaction + AllowanceSchedule
├── goals/                   # SavingsGoal + GoalContribution
├── achievements/            # Achievement + UserAchievement + utils
├── complaints/              # Complaint
├── feedback/                # Feedback
├── chatbot/                 # ChatSession + ChatMessage + Gemini
├── templates/
│   ├── base.html
│   ├── partials/            # navbar, sidebars
│   ├── public/              # landing, login/register, OTP
│   ├── admin/               # admin pages
│   ├── head/                # parent pages
│   ├── dependent/           # kid pages
│   ├── chatbot/
│   └── errors/              # 404
├── static/
│   ├── css/style.css        # Warm Prosperity design system
│   └── js/main.js           # confetti, count-up, modals, theme
├── fixtures/                # initial categories + admin
├── requirements.txt
├── .env.example
└── manage.py
```

---

## 🔄 Business Logic Overview

### Chore Reward Flow
```
Head assigns chore → status='active'
  ↓
Dependent marks complete + notes → ChoreSubmission created → status='pending_approval'
  ↓
Head approves → Transaction(reward) auto-created
                wallet_balance += reward_amount
                xp_points += {easy:10, medium:25, hard:50}
                check_achievements() runs → badges unlocked
                If recurring → new chore auto-generated
  ↓
(Or) Head rejects with reason → status back to 'active'
```

### Achievement Triggers
After every relevant action, `achievements.utils.check_achievements(dep)` runs and compares
the dependent's stats against `Achievement.trigger_value`. Newly earned badges return to
the frontend for confetti celebration.

### Savings Goal
Dependent contributes from wallet → wallet decreases, goal increases. At 100%,
`is_completed=True`, achievement check runs, confetti fires.

### AI Chatbot
Detects role from session and switches system prompt:
- **Parents** get advisor-style guidance (chore amounts, allowance, family budgeting)
- **Kids/Teens** get a friendly money coach (saving, smart spending, goals — emoji-friendly)

If `GEMINI_API_KEY` is unset, falls back to handcrafted canned responses.

---

## 💳 Subscription & Demo Payment System

### Plans (all under ₹5,000)

| Plan | Monthly | Yearly | Limits | Features |
|------|---------|--------|--------|----------|
| 🌱 **Free** | ₹0 | ₹0 | 2 dependents · 10 chores · 3 goals | Basic dashboard, achievement badges |
| ⭐ **Pro** *(popular)* | ₹299 | ₹3,588 | 5 dependents · unlimited chores & goals | + AI Coach, family analytics |
| 💎 **Premium** | ₹399 | ₹4,788 | Unlimited everything | + CSV/PDF exports, priority support |

> Yearly = 12 × monthly (no hidden discount math). All plans under ₹5,000.

### Demo Payment Flow

1. Pricing page (`/subscriptions/pricing/`) — toggle monthly/yearly (yearly is exactly 12× monthly)
2. Pick a plan → redirected to checkout (free plan auto-subscribes)
3. Choose payment method: **Card** · **UPI** · **Net Banking**
4. Submit any data — payment always succeeds (it's a demo)
5. Receipt page with confetti, invoice number, transaction ID
6. **Download invoice as a real PDF** (generated on the fly with ReportLab)
7. Manage subscription dashboard with usage meters and cancel option
8. Payment history with downloadable PDF invoices for every transaction

> ⚠️ **No real charges.** All payments are simulated for the BCA project demo.
> Card numbers, UPI IDs, and bank info are not validated against real services.

### Subscription URLs

- `/subscriptions/pricing/` — pricing tiers
- `/subscriptions/checkout/<plan>/<cycle>/` — checkout form
- `/subscriptions/manage/` — current subscription dashboard
- `/subscriptions/history/` — payment list
- `/subscriptions/invoice/<id>/` — printable invoice page
- `/subscriptions/invoice/<id>/pdf/` — **download PDF** (ReportLab)
- `/subscriptions/admin/subscriptions/` — admin: all family subscriptions
- `/subscriptions/admin/payments/` — admin: revenue + payment list

---

## 🧪 Verified Flows

The smoke test (run during development) verified:
- ✅ **All 43 routes** (public, admin, head, dependent, chatbot, subscriptions) return 200
- ✅ Head register → login → dashboard
- ✅ Dependent register (with PIN) → login → dashboard
- ✅ Chore create → submit → approve → reward credited → XP gained → achievement unlocked
- ✅ Savings goal create → contribute → 100% complete → achievement unlocked
- ✅ Expense logging with balance validation
- ✅ Admin login → dashboard, enrollment, telemetry, complaints, feedback, categories
- ✅ Subscription: free auto-subscribe, pro/premium card payment, UPI payment, netbanking, invoice rendering, cancel auto-renewal, invalid card rejection

---

## 🎨 Design Tokens (CSS variables)

```css
--indigo: #1E1B4B    /* primary */
--gold:   #F6C90E    /* accent  */
--green:  #10B981    /* growth  */
--coral:  #FF6B6B    /* warning */
--reward: #8B5CF6    /* purple  */
--bg:     #FAFAF8    /* warm white */
--surface:#FFF8DC    /* soft cream */
```

Dark mode toggles via `data-theme="dark"` on `<html>` (persisted in `localStorage`).

---

## 📜 License

Built for educational purposes — BCA Final Year Project, 2026.

---

> Made with 🪙 by a final year student.
