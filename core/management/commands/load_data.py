from django.core.management.base import BaseCommand, CommandError

from core.models import Scene
from data.scene.power_plant import scene as power_plant_scene


class Command(BaseCommand):
    """Command class for load_data."""

    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        """Handle command."""
        try:
            scene: Scene = Scene.objects.initialize_scene(power_plant_scene)
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise CommandError(e)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully initialized scene "%s"' % scene.name
            )
        )
