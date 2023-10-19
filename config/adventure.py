from pydantic import Field

from . import BaseConfig


class AdventureConfig(BaseConfig):
    """Configurations for Adventure"""

    system_message: str = Field(
        "You are a DnD Dungeon Master. You are creating a new adventure for"
        " your user. You either respond to the user's action or create a new"
        " event or action for user if the user is not sure what to do next. "
        " Give only 2 to 3 sentences, do not list actions for user to choose"
        " from."
    )
    start_message: str = Field("You may start the story however you like.")
    base_summary_system_message: str = Field(
        "You are an assistant to summarize a JSON list of messages between an"
        " assistant and a user. Make sure to include any factual information"
        " and name in the conversation messages, don't make up anything not"
        " mentioned in the conversation messages. Each sentence consists of"
        " about 10 to 30 words. You should always refer to the assistant in"
        " second person perspective, as 'you'."
    )
    prev_summary_system_message: str = Field(
        "Describe the previous summary using 1 sentence."
    )
    env_summary_system_message: str = Field(
        "Describe the conversation messages using 3 sentences."
    )
    knowledge_system_message: str = Field(
        "You are an assistant to analyze a JSON list of conversation messages"
        " between an assistant and a user. You should help the assistant in"
        " the converstaion decide which of his/her own knowledge to use to"
        " respond to the user's message. You must call the function"
        " `get_knowledge` and provide the arguments to indicate the knowledge"
        " to use, each argument is a boolean value and True indicates the"
        " knowledge should be used, False otherwise. Depends on user's"
        " message, you may need to use multiple knowledge, you may also use no"
        " knowledge at all if you think none of the knowledge is related to"
        " the user's message."
    )
    default_choice_index: int = Field(0)

    @property
    def summary_system_message(self) -> str:
        """Get the summary system message"""
        return (
            self.base_summary_system_message
            + " "
            + self.prev_summary_system_message
            + " "
            + self.env_summary_system_message
        )

    @property
    def summary_system_message_no_prev(self) -> str:
        """Get the summary system message without previous summary"""
        return (
            self.base_summary_system_message
            + " "
            + self.env_summary_system_message
        )

    class Config:
        env_prefix = "ADVENTURE_"
        env_file = ".env"


adventure_config = AdventureConfig()
