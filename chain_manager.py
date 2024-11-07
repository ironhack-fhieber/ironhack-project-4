class ChainManager:
    def __init__(self):
        self.llm_list = []

    def add_chain(self, id, title, qa_chain, ex_chain, examples):
        """
        Adds a new entry to llm_list if the given ID

        Parameters:
            id (int): The ID of the video.
            title (str): The title of the video.
            qa_chain: The QARetrieval chain instance to associate with the ID.
            ex_chain: The ConversationalRetrievalChain instance for examples.
            examples: A list of example questions.
        """

        self.llm_list.append({'id': id, 'qa_chain': qa_chain, 'ex_chain': ex_chain, 'title': title, 'examples': examples})
        print(f"Added new entry with ID {id}.")

    def get_chain(self, id):
        """
        Retrieves the ChainManger object instance associated with the given video ID.

        Parameters:
            id (int): The ID to look up.

        Returns:
            The llm instance if found, else None.
        """

        for entry in self.llm_list:
            if entry['id'] == id:
                return entry

        print(f"No entry found with ID {id}.")
        return None

    def update_examples(self, id, new_examples):
        """
        Updates the 'examples' list for the entry with the given ID.

        Parameters:
            id (int): The ID of the entry to update.
            new_examples: The new list of examples to set.
        """
        for entry in self.llm_list:
            if entry['id'] == id:
                entry['examples'] = new_examples
                return

        print(f"No entry found with ID {id}.")

    def is_new(self, id):
        """Checks if a given ID is new (not already present) in the llm_list.

        Args:
            id: The ID to check for novelty.

        Returns:
            True if the ID is not found in the llm_list (i.e., it's new),
            False otherwise.
        """

        return any(entry['id'] == id for entry in self.llm_list)
