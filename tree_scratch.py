class ExpressionTree:
    _id = 0
    def __init__(self):
        self.tree = Node(None)
        self.current_node = ExpressionTree._id

    def set_active_node(self, node_id):
        self.current_node = node_id

    def set_value(self, node_id):
        self

    def get_current_node(self):
        return self.current_node

    def add_leaf(self, item):