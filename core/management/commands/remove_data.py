from django.core.management.base import BaseCommand, CommandError

from core.models import Knowledge, Scene, SceneNpc, SceneNpcAdventurePair


class Command(BaseCommand):
    """Command class for load_data."""

    help = "Remove scene data from the database."

    def add_arguments(self, parser):
        """Add arguments to the command."""
        parser.add_argument("id", type=str)

    def handle(self, *args, **options):
        """Handle command."""
        try:
            id = options["id"]
            self.stdout.write(self.style.SUCCESS("Removing %s" % id))
            scene: Scene = Scene.objects.get(id=id)

            # Remove scene npcs
            scene_npcs: SceneNpc = SceneNpc.objects.filter(scene=scene)
            scene_npcs.delete()

            # Remove redundant knowledge
            knowledge: Knowledge = Knowledge.objects.filter(npcs=None)
            knowledge.delete()

            # Remove scene npcs adventure pairs
            scene_npc_adventure_pairs: SceneNpcAdventurePair = (
                SceneNpcAdventurePair.objects.filter(npc=None)
            )
            scene_npc_adventure_pairs.delete()

            # Remove scene
            scene.delete()
        except Exception as e:
            import traceback

            traceback.print_exc()
            raise CommandError(e)

        self.stdout.write(
            self.style.SUCCESS("Successfully removed scene %s" % id)
        )
