# app/routes.py
from flask import render_template, request, abort, render_template_string, jsonify
from app import app
from ortools.linear_solver import pywraplp
import openai
import google.generativeai as genai
import requests
import json
import os

def create_linear_programming_model(activities, budget_constraint, time_constraint):
    solver = pywraplp.Solver.CreateSolver('CBC_MIXED_INTEGER_PROGRAMMING')
    
    # Create variables
    vars_dict = {}
    activities_list = list(activities)  # Convert activities dictionary into a list
    
    for i, activity in enumerate(activities_list):
        vars_dict[f'activity_{i}'] = solver.IntVar(0, 1, f'activity_{i}')

    #Budget constraint
    budget_constraint_expr = solver.Sum([activities[i]['cost'] * vars_dict[f'activity_{i}'] for i in range(len(activities))])
    solver.Add(budget_constraint_expr <= budget_constraint)

    #Time constraint
    time_constraint_expr = solver.Sum([activities[i]['time'] * vars_dict[f'activity_{i}'] for i in range(len(activities))])
    solver.Add(time_constraint_expr <= time_constraint)

    # Objective function
    objective_expr = solver.Sum([activities[i]['value'] * vars_dict[f'activity_{i}'] for i in range(len(activities))])
    solver.Maximize(objective_expr)

    
    # Invoke solver
    status = solver.Solve()
    
    # Check solution
    if status == pywraplp.Solver.OPTIMAL:
        # Collect the list of activities that the user can do
        optimal_activities = [activities[i]['name'] for i in range(len(activities)) if vars_dict[f'activity_{i}'].solution_value() == 1]
        return optimal_activities
    else:
        return None

@app.route('/')
def index():
    try:
        with open('templates/index.html', 'r') as f:
            template_content = f.read()
        return template_content
    except FileNotFoundError:
        abort(404)

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    data = request.json
    api_key = data.get('apiKey')
    provider = data.get('provider')
    user_prompt = data.get('prompt')

    if not api_key or not provider or not user_prompt:
        return jsonify({'error': 'Missing required fields'}), 400

    system_prompt = """
    You are a travel assistant. Generate a day trip plan based on the user's request.
    You must return a valid JSON object with the following structure:
    {
        "budget": <number>,
        "time": <number (hours)>,
        "activities": [
            {
                "name": <string>,
                "cost": <number>,
                "time": <number (hours)>,
                "value": <number (0-10 preference score)>
            }
        ]
    }
    Ensure the JSON is valid and contains no other text.
    """

    try:
        if provider == 'openai':
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.choices[0].message.content

        elif provider == 'gemini':
            # Use REST API directly to avoid global state issues with the python library
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\nUser Request: {user_prompt}"
                    }]
                }]
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            gemini_data = response.json()
            try:
                content = gemini_data['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return jsonify({'error': 'Invalid response from Gemini'}), 500

        else:
            return jsonify({'error': 'Invalid provider'}), 400

        # Robust JSON extraction
        import re
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            json_str = match.group(0)
            plan_data = json.loads(json_str)
        else:
            # Fallback to direct parsing if no braces found (unlikely for valid JSON)
            plan_data = json.loads(content)
        return jsonify(plan_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit/<string:string_activities>', methods=['POST']) 
def submit(string_activities):
    if request.method == 'POST':
        # get form data
        if not request.form['budget'] or not request.form['time']:
             return "Please fill out all the fields."
        budget = int(request.form['budget'])
        time = int(request.form['time'])
        activities = {}

        # # Loop through the range of activity indices
        # for i in range(num_activities):
        #     activity_name = request.form.getlist('activityName[]')[i]
        #     activity_cost = int(request.form.getlist('activityCost[]')[i])
        #     activity_time = int(request.form.getlist('activityTime[]')[i])
        #     activity_value = int(request.form.getlist('activityValue[]')[i])
        #     activities[i] = {
        #         'name': activity_name,
        #         'cost': activity_cost,
        #         'time': activity_time,
        #         'value': activity_value
        #     }

        #StringActivity store the data of the table where it's seperate by , for the columns and ; for the rows
        print("string_activities: ", string_activities)
        
        stringActivities = []
        stringActivities = string_activities.split(';')

        for i in range(len(stringActivities) - 1):
            activity = stringActivities[i].split(',')
            activities[i] = {
                'name': activity[0],
                'cost': int(activity[1]),
                'time': int(activity[2]),
                'value': int(activity[3])
            }

        # Check if any of the required fields are empty
        if not budget or not time or not activities:
            print("Budget: ", budget)
            print("Time: ", time)
            print("Activities: ", activities)
            return "Please fill out all the fields."
        else:
            # create linear programming model

            result = create_linear_programming_model(activities, budget, time)
            if result is not None:
                return render_template_string("""
                    <section class="section">
                        <div class="container">
                            <h2 class="title">The Activities within your Budget and Time:</h2>
                            <table class="table is-bordered is-fullwidth">
                                <thead>
                                    <tr>
                                        <th>Activity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for activity in activities %}
                                    <tr>
                                        <td>{{ activity }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </section>
                """, activities=result)

            else:
                return "The problem does not have an optimal solution."