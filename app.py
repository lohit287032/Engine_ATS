from flask import Flask, request, render_template, jsonify
from ast_module import create_rule, combine_rules, evaluate_rule
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY, rule_string TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    data = request.get_json()
    rule_string = data['rule_string']
    rule_ast = create_rule(rule_string)
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO rules (rule_string) VALUES (?)", (rule_string,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Rule created successfully"}), 201

@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rule_string FROM rules")
    rules = [row[0] for row in c.fetchall()]
    conn.close()

    combined_rule_ast = combine_rules(rules)
    return jsonify({"message": "Rules combined successfully"}), 200

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    data = request.get_json()
    user_data = data.get('user_data')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT rule_string FROM rules")
    rules = [create_rule(row[0]) for row in c.fetchall()]
    conn.close()

    combined_rule_ast = combine_rules(rules)
    result = evaluate_rule(combined_rule_ast, user_data)
    
    return jsonify({"eligible": result}), 200

if __name__ == '__main__':
    app.run(debug=True)
