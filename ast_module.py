import re

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type  # "operator" or "operand"
        self.value = value
        self.left = left
        self.right = right

def parse_condition(condition):
    match = re.match(r"(\w+)\s*(>|>=|<|<=|==|!=)\s*([0-9]+|'[a-zA-Z]+')", condition.strip())
    if match:
        field, operator, value = match.groups()
        return Node("operand", {"field": field, "operator": operator, "value": eval(value)})
    else:
        raise ValueError("Invalid condition format")

def create_rule(rule_string):
    stack = []
    tokens = re.split(r"(\(|\)|AND|OR)", rule_string)
    for token in tokens:
        token = token.strip()
        if token in ("AND", "OR"):
            right = stack.pop()
            left = stack.pop()
            node = Node("operator", value=token, left=left, right=right)
            stack.append(node)
        elif token in ("(", ")"):
            continue
        elif token:
            stack.append(parse_condition(token))
    return stack[0] if stack else None

def combine_rules(rules):
    combined_root = None
    for rule in rules:
        rule_ast = create_rule(rule)
        if combined_root:
            combined_root = Node("operator", "AND", left=combined_root, right=rule_ast)
        else:
            combined_root = rule_ast
    return combined_root

def evaluate_condition(condition, data):
    field = condition["field"]
    operator = condition["operator"]
    value = condition["value"]
    return {
        ">": lambda x, y: x > y,
        "<": lambda x, y: x < y,
        "==": lambda x, y: x == y,
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y,
        "!=": lambda x, y: x != y,
    }[operator](data.get(field), value)

def evaluate_rule(node, data):
    if node.type == "operand":
        return evaluate_condition(node.value, data)
    elif node.type == "operator":
        left_eval = evaluate_rule(node.left, data)
        right_eval = evaluate_rule(node.right, data)
        return left_eval and right_eval if node.value == "AND" else left_eval or right_eval
