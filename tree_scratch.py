from graphviz import Digraph
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'


class Node:
    def __init__(self, uid=None, value=None):
        if uid is None:
            self._id = ExpressionTree._id
            ExpressionTree._id += 1
        else:
            self._id = uid
        self.value = value


class ExpressionTree:
    _id = 0

    def __init__(self, structure=None):
        if structure is None:
            i = ExpressionTree._id
            self.current_node = i
            self._relations = [i]
            self.nodes = {i: Node(uid=i)}
            ExpressionTree._id += 1
        else:
            self.nodes = {}
            self._relations = structure
            f = self.flatten_list(structure)
            for i in f:
                self.nodes[i] = Node(uid=i)
            ExpressionTree._id = max(f)

    def set_active_node(self, node_id):
        self.current_node = node_id

    def flatten_list(self, l):
        f = []
        for i in l:
            if type(i) is list:
                f.extend(self.flatten_list(i))
            else:
                f.append(i)
        return f

    def set_value(self, value, node_id=None):
        if node_id is None:
            node_id = self.current_node
        self.nodes[node_id].value = value

    def get_current_node(self):
        return self.current_node

    def add_leaf(self, val=None):
        o_path = self._build_path_to()
        path = str(o_path)[:-1]
        path = self._format_path(path)
        o_path = self._format_path(int(o_path) + 1)
        n = Node(value=val)
        i = ExpressionTree._id
        self.nodes[i] = n
        loc = locals()
        exec('l = self._relations{}'.format(path), globals(), loc)
        l = loc['l']
        position = l.index(self.current_node)
        # item is is at the end of its level and has no children
        if position + 1 == len(l):
            exec('self._relations{}.append([i])'.format(path))
        # item has no children
        elif type(l[position + 1]) is not list:
            exec('self._relations{}.insert(position + 1, [i])'.format(path))
        # item already has child(ren)
        else:
            exec('self._relations{}.append(i)'.format(o_path))

    def get_num_leaves(self, uid=None):
        path = self._build_path_to()
        path = str(path)[:-1]
        path = self._format_path(path)
        loc = locals()
        exec('l = self._relations{}'.format(path), globals(), loc)
        l = loc['l']
        position = l.index(self.current_node)
        if position + 1 == len(l):
            return 0
        elif type(l[position + 1]) is not list:
            return 0
        else:
            return len(l[position + 1])

    def _build_path_to(self, target_list=None, uid=None):
        if target_list is None:
            target_list = self._relations
        if uid is None:
            uid = self.current_node
        #     we've found the value we want
        for i in target_list:
            if uid == i:
                return target_list.index(uid)
        # otherwise check an underlying list
        for i in range(0, len(target_list)):
            if type(target_list[i]) is list:
                b = self._build_path_to(target_list[i], uid)
                if b != '' and b is not None:
                    return '{}{}'.format(i, b)

    def _format_path(self, path_str):
        a = ''
        for i in str(path_str):
            a += '[{}]'.format(i)
        return a

    def insert_parent(self, val=None):
        o_path = self._build_path_to()
        n = Node(value=val)
        i = ExpressionTree._id
        self.nodes[i] = n
        parent = [i]
        if len(str(o_path)) < 2:
            parent.append(self._relations)
            self._relations = parent
            return
        path = str(o_path)[:-2]
        c_path = int(o_path) + 1
        c_path = self._format_path(c_path)
        children = None
        loc = locals()
        if self.get_num_leaves() > 0:
            exec('children = self._relations{}'.format(c_path), globals(), loc)
        children = loc['children']
        loc = locals()
        # if node is not terminal
        if children is not None:
            exec('self._relations{}'.format(
                self._format_path(int(o_path) + 1)) + ' = [self.current_node, children]', globals(), loc)
        else:
            exec('self._relations{}'.format(
                self._format_path(str(o_path)[:-1])) + '.append([self.current_node])', globals(), loc)
        exec('self._relations{}'.format(
            self._format_path(o_path)) + ' = i', globals(), loc)

    def draw_tree(self, tree=None, target=None, parent=0):
        previous = parent
        if tree is None:
            tree = Digraph()
        if target is None:
            target = self._relations
        for n in target:
            if type(n) is list:
                tree = self.draw_tree(tree, n, previous)
            else:
                # tree.node(str(n), self.nodes[n].__str__())
                tree.node(str(n), str(n))
                previous = n
                if parent != 0:
                    tree.edge(str(parent), str(n))
        return tree

    def render_tree(self, t):
        t.render('parse_tree.gv', view=True)


if __name__ == '__main__':
    tree = [1,[2,[3,4]]]
    t = ExpressionTree(tree)
    t.set_active_node(4)
    t.get_num_leaves()
    c = t._build_path_to()
    d = t._format_path(c)
    # print(eval("t._relations"+d))
    t.add_leaf()
    # print(t.get_num_leaves())
    t.add_leaf()
    t.set_active_node(1)
    t.add_leaf()
    t.set_active_node(7)
    t.add_leaf()
    t.add_leaf()
    t.set_active_node(8)
    j = t._build_path_to()
    j = int(j) + 1
    j = t._format_path(j)
    t.set_active_node(5)
    t.add_leaf()
    t.set_active_node(10)
    t.add_leaf()
    t.add_leaf()
    # print(j)
    # exec('print(t._relations{})'.format(j))
    t.set_active_node(4)
    t.insert_parent()

    print(t._relations)
    p = t.draw_tree()
    t.render_tree(p)





