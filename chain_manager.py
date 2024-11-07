"""
ChainManager handles the persisted saving of trained chains for each video
"""

class ChainManager:
    def __init__(self):
        self.llm_list = []

    def add_chain(self, video_id, title, chains, examples):
        """
        Adds a new entry to llm_list if the given ID

        Parameters:
            video_id (int): The ID of the video.
            title (str): The title of the video.
            chains: (dict) The QARetrieval and ConversationalRetrievalChain chain instances.
            examples: A list of example questions.
        """

        self.llm_list.append({'id': video_id, 'title': title, 'examples': examples,
                              'qa_chain': chains['questions'], 'ex_chain': chains['examples']})
        print(f"Added new entry with ID {video_id}.")

    def get_chain(self, video_id):
        """
        Retrieves the ChainManger object instance associated with the given video ID.

        Parameters:
            video_id (int): The ID to look up.

        Returns:
            The llm instance if found, else None.
        """

        for entry in self.llm_list:
            if entry['id'] == video_id:
                return entry

        print(f"No entry found with ID {video_id}.")
        return None

    def update_examples(self, video_id, new_examples):
        """
        Updates the 'examples' list for the entry with the given ID.

        Parameters:
            video_id (int): The ID of the entry to update.
            new_examples: The new list of examples to set.
        """

        for entry in self.llm_list:
            if entry['id'] == video_id:
                entry['examples'] = new_examples
                return

        print(f"No entry found with ID {video_id}.")

    def is_new(self, video_id):
        """Checks if a given ID is new (not already present) in the llm_list.

        Args:
            video_id: The ID to check for novelty.

        Returns:
            True if the ID is not found in the llm_list (i.e., it's new),
            False otherwise.
        """

        return any(entry['id'] == video_id for entry in self.llm_list)
