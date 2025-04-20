from django.core.management.base import BaseCommand
from django.utils import timezone
from community.models import (
    Challenge, ChallengeRequirement, ChallengeReward, Badge
)

class Command(BaseCommand):
    help = 'Updates the Couch to 5K challenge with requirements and rewards'

    def handle(self, *args, **kwargs):
        # Get or create the challenge
        challenge, created = Challenge.objects.get_or_create(
            title="Couch to 5K Challenge",
            defaults={
                'description': """Join our 9-week Couch to 5K program! This beginner-friendly challenge will help you go from no running experience to completing a 5K run.
                
                What to expect:
                - 3 workouts per week
                - Gradual progression from walking to running
                - Supportive community
                - Weekly progress tracking
                - Achievement badges for milestones
                """,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(weeks=9),
                'points': 500,
                'is_active': True
            }
        )

        # Clear existing requirements and rewards
        challenge.requirements.clear()
        challenge.rewards.clear()

        # Create requirements
        requirements = [
            "Complete 3 workouts per week",
            "Follow the weekly training schedule",
            "Track your progress in the app",
            "Share your journey in the community (optional)",
            "Complete the final 5K run"
        ]
        
        for i, req in enumerate(requirements):
            requirement = ChallengeRequirement.objects.create(
                description=req,
                is_mandatory=(i != 3),  # Only the community sharing is optional
                order=i
            )
            challenge.requirements.add(requirement)

        # Create rewards
        rewards = [
            {
                "description": "Complete Week 1",
                "points_value": 50,
                "badge": None
            },
            {
                "description": "Complete Week 4",
                "points_value": 100,
                "badge": None
            },
            {
                "description": "Complete the 5K Challenge",
                "points_value": 350,
                "badge": Badge.objects.get_or_create(
                    name="5K Runner",
                    defaults={
                        'description': 'Completed the Couch to 5K Challenge',
                        'badge_type': 'achievement',
                        'required_points': 500
                    }
                )[0]
            }
        ]
        
        for reward_data in rewards:
            reward = ChallengeReward.objects.create(
                description=reward_data["description"],
                points_value=reward_data["points_value"],
                badge=reward_data["badge"]
            )
            challenge.rewards.add(reward)

        self.stdout.write(self.style.SUCCESS('Successfully updated Couch to 5K challenge with requirements and rewards')) 