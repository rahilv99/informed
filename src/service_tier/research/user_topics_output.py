import common.s3

class UserTopicsOutput:
    def __init__(self, user_id):
        data = common.s3.restore_serialized(user_id, "USER_TOPICS")
        self.expanded_embeddings= data["expanded_embeddings"]
        self.user_input_embeddings = data["user_input_embeddings"]
        self.all_input = data["all_input"]