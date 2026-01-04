# app/routes.py
from flask import render_template, request, abort, render_template_string
from app import app
from ortools.linear_solver import pywraplp

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
    return render_template('index.html')

@app.route('/submit/<string:string_activities>', methods=['POST']) 
def submit(string_activities):
    if request.method == 'POST':
        # get form data
        budget = int(request.form['budget'])
        time = int(request.form['time'])
        activities = {}

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
                # Updated HTML structure to match new CSS
                return render_template_string("""
                    <div class="box">
                        <h2 class="title">Optimized Plan</h2>
                        <p>Based on your budget and time constraints, here are the recommended activities:</p>
                        <table style="margin-top: 1rem;">
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
                """, activities=result)

            else:
                return """
                <div class="box" style="border-left: 4px solid var(--danger-color);">
                    <h3 style="color: var(--danger-color);">No Solution Found</h3>
                    <p>The problem does not have an optimal solution within the given constraints.</p>
                </div>
                """
