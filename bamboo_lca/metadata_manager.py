class MetadataManager:
    """
    This class is used to manage metadata of this library, the metadata is designed for handling ununiformly uncertainty analysis.

    The metadata with uncertainty information follows the following structure:

        self.metadata: save activity information, including: 
                activity index(the index in the datapackage), 
                uncertainty type, 
                activity name, 
                itemwise uncertainty value,
                and columnwise uncertainty value. (Here the uncertainy value means the mu value.)

        metadata = {
            index1: {
                "type": 1,
                "act": act1,
                "specific": [specific1, specific2, specific3, ...],
                "gsd": 0,
            },
            index2: {
                "type": 2,
                "act": act2,
                "specific": [],
                "gsd": gsd2,
            },
            ...
        }
        """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "metadata"):
            self.metadata = {}

    def _update_metadata(self, key, value):
        self.metadata[key] = value

    def _get_metadata(self):
        return self.metadata
    
metadata_manager = MetadataManager()