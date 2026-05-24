"""Seed WealthNest with admin, categories, and achievements."""
from django.core.management.base import BaseCommand
from accounts.models import Login
from chores.models import ChoreCategory
from admin_panel.models import ExpenseCategory, ChoreCategoryAdmin, GoalCategory
from achievements.models import Achievement


class Command(BaseCommand):
    help = "Seed WealthNest with initial data (admin, categories, achievements)."

    def handle(self, *args, **options):
        # Admin
        if not Login.objects.filter(username='admin').exists():
            admin = Login(username='admin', email='admin@wealthnest.app',
                          user_type='admin', user_phone='9999999999')
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin created — username: admin / password: admin123'))
        else:
            self.stdout.write('✓ Admin already exists')

        # Chore Categories (used in Chore form)
        chore_cats = [
            ('Cleaning', '🧹', '#10B981'),
            ('Kitchen', '🍽️', '#F6C90E'),
            ('Pets', '🐶', '#8B5CF6'),
            ('Garden', '🌱', '#10B981'),
            ('Laundry', '🧺', '#1E1B4B'),
            ('Study', '📚', '#F6C90E'),
            ('Outdoor', '🚴', '#FF6B6B'),
            ('Helping', '🤝', '#8B5CF6'),
            ('Errand', '🛒', '#06B6D4'),
            ('Other', '✨', '#1E1B4B'),
        ]
        for name, icon, color in chore_cats:
            ChoreCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})
            ChoreCategoryAdmin.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})

        # Expense Categories
        exp_cats = [
            ('Food & Snacks', '🍔', '#FF6B6B'),
            ('Toys', '🧸', '#F6C90E'),
            ('Books', '📚', '#1E1B4B'),
            ('Games', '🎮', '#8B5CF6'),
            ('Clothing', '👕', '#10B981'),
            ('Stationery', '✏️', '#06B6D4'),
            ('Sports', '⚽', '#10B981'),
            ('Tech', '💻', '#1E1B4B'),
            ('Gifts', '🎁', '#FF6B6B'),
            ('Other', '🛒', '#6B7280'),
        ]
        for name, icon, color in exp_cats:
            ExpenseCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})

        # Goal Categories
        goal_cats = [
            ('Bicycle', '🚲', '#10B981'),
            ('Toy', '🧸', '#F6C90E'),
            ('Tech', '📱', '#1E1B4B'),
            ('Books', '📚', '#06B6D4'),
            ('Sports Gear', '⚽', '#10B981'),
            ('Trip', '✈️', '#8B5CF6'),
            ('Donation', '❤️', '#FF6B6B'),
            ('Investment', '📈', '#10B981'),
        ]
        for name, icon, color in goal_cats:
            GoalCategory.objects.get_or_create(name=name, defaults={'icon': icon, 'color': color})

        # Achievements
        achs = [
            ('First Chore!', 'Complete your first chore', '🌟', 50, 'bronze', 'first_chore', 1, 'Complete any chore to unlock'),
            ('Chore Champion', 'Complete 10 chores', '🏆', 100, 'silver', 'chores_completed', 10, 'Complete 10 chores'),
            ('Chore Master', 'Complete 50 chores', '👑', 250, 'gold', 'chores_completed', 50, 'Complete 50 chores'),
            ('Week Warrior', '7-day activity streak', '🔥', 75, 'silver', 'streak_days', 7, 'Stay active 7 days in a row'),
            ('Month Master', '30-day activity streak', '⚡', 200, 'gold', 'streak_days', 30, 'Stay active 30 days in a row'),
            ('First Goal!', 'Complete your first savings goal', '🎯', 100, 'bronze', 'first_goal', 1, 'Complete any savings goal'),
            ('Saver Starter', 'Save your first ₹1000', '💰', 100, 'bronze', 'savings_amount', 1000, 'Save ₹1000 in goals'),
            ('Big Saver', 'Save ₹5000 across goals', '💎', 250, 'gold', 'savings_amount', 5000, 'Save ₹5000 in goals'),
            ('Wealth Builder', 'Save ₹10,000', '🏰', 500, 'platinum', 'savings_amount', 10000, 'Save ₹10,000 in goals'),
            ('Goal Crusher', 'Complete 5 goals', '🚀', 300, 'gold', 'goals_reached', 5, 'Complete 5 savings goals'),
        ]
        for name, desc, icon, xp, badge, trigger, val, hint in achs:
            Achievement.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc, 'icon': icon, 'xp_reward': xp,
                    'badge_type': badge, 'trigger_type': trigger,
                    'trigger_value': val, 'hint': hint,
                }
            )

        # Subscription Plans
        try:
            from subscriptions.models import Plan
            plans = [
                {
                    'name': 'Free', 'slug': 'free',
                    'tagline': 'Get started for your family — forever free.',
                    'price_monthly': 0, 'price_yearly': 0,
                    'max_dependents': 2, 'max_chores': 10, 'max_goals': 3,
                    'has_ai': False, 'has_analytics': False, 'has_export': False,
                    'has_achievements': True, 'has_priority_support': False,
                    'color': '#6B7280', 'icon': '🌱', 'sort_order': 1,
                    'is_popular': False,
                    'features': '✅ Up to 2 dependents\n✅ 10 active chores\n✅ 3 savings goals\n✅ Achievement badges\n✅ Family dashboard\n❌ AI Money Coach\n❌ Advanced analytics\n❌ CSV / PDF exports',
                },
                {
                    'name': 'Pro', 'slug': 'pro',
                    'tagline': 'Best for active families — most popular.',
                    'price_monthly': 299, 'price_yearly': 2999,
                    'max_dependents': 5, 'max_chores': 9999, 'max_goals': 9999,
                    'has_ai': True, 'has_analytics': True, 'has_export': False,
                    'has_achievements': True, 'has_priority_support': False,
                    'color': '#F6C90E', 'icon': '⭐', 'sort_order': 2,
                    'is_popular': True,
                    'features': '✅ Up to 5 dependents\n✅ Unlimited chores\n✅ Unlimited savings goals\n✅ AI Money Coach (Gemini)\n✅ Family analytics dashboards\n✅ Achievement badges & XP\n✅ Spending category insights\n❌ CSV / PDF exports',
                },
                {
                    'name': 'Premium', 'slug': 'premium',
                    'tagline': 'Everything for big families — premium support.',
                    'price_monthly': 499, 'price_yearly': 4999,
                    'max_dependents': 9999, 'max_chores': 9999, 'max_goals': 9999,
                    'has_ai': True, 'has_analytics': True, 'has_export': True,
                    'has_achievements': True, 'has_priority_support': True,
                    'color': '#8B5CF6', 'icon': '💎', 'sort_order': 3,
                    'is_popular': False,
                    'features': '✅ Unlimited dependents\n✅ Unlimited chores & goals\n✅ AI Money Coach (Gemini)\n✅ Advanced family analytics\n✅ CSV / PDF report exports\n✅ Custom achievement badges\n✅ Priority email support\n✅ Early access to new features',
                },
            ]
            for p in plans:
                Plan.objects.update_or_create(slug=p['slug'], defaults=p)
            self.stdout.write(self.style.SUCCESS(f'✓ Seeded {len(plans)} subscription plans'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Plans not seeded: {e}'))

        self.stdout.write(self.style.SUCCESS('✅ Seed complete!'))
        self.stdout.write(self.style.WARNING('Admin login: username=admin, password=admin123'))
