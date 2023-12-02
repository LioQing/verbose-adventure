from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    CorsOptions,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
)
from django.core.management.base import BaseCommand

from config.azure_ai_search import azure_ai_search_config
from data.scene.power_plant import scene as power_plant_scene


class Command(BaseCommand):
    """Command class for azure_ai_search."""

    help = "Export the data as Azure AI Search Index and Data."

    def handle(self, *args, **options):
        """Handle command."""
        self.stdout.write(self.style.SUCCESS("Exporting data to AI Search"))

        service_name = azure_ai_search_config.service_name
        admin_key = azure_ai_search_config.admin_key

        for npc in power_plant_scene.npcs:
            index_name = f"verbose-adventure-power-plant-{npc.id}"

            # Create an SDK client
            endpoint = "https://{}.search.windows.net/".format(service_name)
            admin_client = SearchIndexClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(admin_key),
            )

            search_client = SearchClient(
                endpoint=endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(admin_key),
            )

            try:
                result = admin_client.delete_index(index_name)
                print(self.style.SUCCESS(f"Index {index_name} Deleted"))
            except Exception as ex:
                print(self.style.ERROR(ex))

            # Specify the index schema
            name = index_name
            fields = [
                SimpleField(
                    name="id", type=SearchFieldDataType.String, key=True
                ),
                SearchableField(
                    name="name",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True,
                ),
                SearchableField(
                    name="description",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True,
                ),
                SearchableField(
                    name="knowledge",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True,
                ),
            ]
            cors_options = CorsOptions(
                allowed_origins=["*"], max_age_in_seconds=60
            )
            scoring_profiles = []
            suggester = [
                {
                    "name": "sg",
                    "source_fields": ["name", "description", "knowledge"],
                }
            ]

            index = SearchIndex(
                name=name,
                fields=fields,
                scoring_profiles=scoring_profiles,
                suggesters=suggester,
                cors_options=cors_options,
            )

            try:
                result = admin_client.create_index(index)
                print(self.style.SUCCESS(f"Index {result.name} created"))
            except Exception as ex:
                print(self.style.ERROR(ex))

            documents = [
                {
                    "@search.action": "upload",
                    "id": knowledge.id,
                    "name": knowledge.name,
                    "description": knowledge.description,
                    "knowledge": knowledge.knowledge,
                }
                for knowledge in npc.knowledges
            ]

            try:
                result = search_client.upload_documents(documents=documents)
                print(
                    self.style.SUCCESS(
                        "Upload of new document succeeded:"
                        f" {[str(r) for r in result]}"
                    )
                )
            except Exception as ex:
                print(self.style.ERROR(ex.message))
