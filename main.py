# Flask
import flash
import flask
from flask import Flask
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
# Other Python Modules
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from json import loads
import jwt
import os
import re
from sqlite3 import Error
import sqlite3
import sys
# User-Defined Modules
from app_setup import *
import database
import helpers
import tutor
import openai
import csv 
sys.setrecursionlimit(10000)

########
# AUTH #
########
def get_openai_key():
    # Check if the file exists
    if not os.path.isfile('openai_key.txt'):
        # Create the file if it does not exist and write a default value or leave it blank
        with open('openai_key.txt', 'w') as file:
            file.write('')  # You could prompt the user for a key or leave it blank
    # Read the key from the file
    with open('openai_key.txt', 'r') as file:
        return file.read().strip()

def get_prompt():
    # Check if the prompt file exists
    if not os.path.isfile('prompt.txt'):
        # Create the file if it does not exist and write a default value or leave it blank
        with open('prompt.txt', 'w') as file:
            file.write('')  # You could provide a default prompt or leave it blank
    # Read the prompt from the file
    with open('prompt.txt', 'r') as file:
        return file.read().strip()

# Usage
openai.api_key = get_openai_key()
input_prompt = get_prompt()



@app.route("/")
def index():
        return render_template("tutor_builder.html")


#################
# TUTOR BUILDER #
#################



###########
# GENERAL #
###########






@app.route("/tutor_builder", methods=["GET", 'POST'])
def tutor_builder():

    return render_template("tutor_builder.html")




@app.route("/profile", methods=["GET", 'POST'])
def profile():
    api_key_exists = False
    api_key_value = ''
    try:
        with open('openai_key.txt', 'r') as file:
            api_key_value = file.read().strip()
            if api_key_value:
                api_key_exists = True
    except FileNotFoundError:
        pass  # It's okay if the file doesn't exist; treat as if no key has been saved yet.

    if request.method == 'POST':
        api_key_value = request.form['api_key']  # Assuming the input for the key has name='first_name'

        # Save the key to a file
        with open('openai_key.txt', 'w') as file:
            file.write(api_key_value)

        openai.api_key = api_key_value
        api_key_exists = True

        # Redirect or respond accordingly after sav
    
    # # print("************* : ", data.first_name)
    return render_template("profile.html",  api_key_value=api_key_value, api_key_exists=api_key_exists)


@app.route('/generateComponentLayout', methods=['POST'])
def generate_component_layout():
    data = request.get_json()
    text_specification = data.get('text')
    detailed_description = data.get('text')
    # Introduction to the task
    prompt_introduction = """Generate a compact representation layout string for a tutor interface component based on a specific format. This format includes elements such as rows, columns, labels, and inputs."""
# Explanation of the format
    prompt_format = "The format uses: row{{...}}, column{{...}} with each element stacked vertically over the other within the column, label[Label], and input[Placeholder]. Elements within rows and columns are enclosed in curly braces {{}}, and attributes are in square brackets []."
# Design instructions for the layout
    prompt_design_instructions = """Design principles require that each input element be separate, for example, in an equation, there should be one input element per digit. A single equation must be on a single row. Elements within a row are arranged horizontally. Rows cannot be directly nested within other rows, nor can columns be nested within other columns. Ensure each input element is separate, such as digits in an equation, and a single equation appears on a single line. There are no interactive buttons like 'Click to solve' within the component."""
    # Instruction to transform the description into the layout string
    prompt_task = """Transform the detailed description into the compact representation layout string according to the instructions."""
    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: An equations solver should be represented as column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}}."
    prompt_examples += ", Example 3: For a radicals tutor compoenent, the representation would be column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}"
    prompt_examples += ", Example 4: For a Squared Tutor component, the representation would be column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout."

    # Combining all the parts to form the complete prompt
    prompt = f"\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"
    instruction = f"\nYou always MUST GENERATE A LAYOUT CORRECTLY FORMATTED EVEN IF THE DESCRIPTION IS UNDER SPECIFIED!!! Description:\n{detailed_description}\n"
    # Format the prompt with the detailed description from the request
    #prompt = f"""Given a detailed description of a tutor interface, generate a compact representation layout string in a specific format. The format includes titles, rows, columns, labels, and inputs, represented as follows: title[Title], row {{ ... }}, column {{ ... }}, label[Label], and input[Placeholder]. Elements inside rows and columns should be enclosed in curly braces {{}}, and element attributes should be enclosed in square brackets []. Ensure the output is precise and adheres to this structure for easy parsing.
    #Design instructions: Given that the intelligent tutor will utilize an AI algorithm to learn from the teacher interaction what the problem solution is; each input element should be separate, for example in an equation there should be one input element per digit. Respect design principles; for example, a single equation must be in a single line. 
    #Detailed Description:
    #{detailed_description}
    #Transform this description into the compact representation layout string according to the instructions. Respond in one line."""

    try:
        response = openai.chat.completions.create(
          model="gpt-4", # Adjusted to use GPT-4
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction }]
        )
        generated_text = response.choices[0].message.content.strip()
        print(generated_text)
        # Return the compact layout generated by OpenAI
        return jsonify({"compactLayout": generated_text})
    except Exception as e:
        return jsonify({"error": "Instert Valid OpenAI key"}), 500
    
@app.route('/generateTutorSteps', methods=['POST'])
def generate_tutor_steps():
    
    data = request.get_json()
    detailed_description = data.get('text')
    prompt_system = "Create a series of high-level steps for solving a problem in a tutor interface. Each step should be a clear, concise description of an action the user needs to take. The steps should logically progress from the initial problem statement to the final solution, adhering to pedagogical best practices."
    prompt_introduction = """Generate a series of high-level steps for solving a problem in a tutor interface based on a detailed description."""
    prompt_format = "The steps should be numbered and separated by commas. Each step should be a short, actionable phrase that guides the user through the problem-solving process."
    prompt_design_instructions = """Design principles require that each step be focused on a single action or concept. Steps should be ordered logically and build upon each other. Avoid using technical jargon or complex language. Each step should be clear and easily understandable for the user."""
    # Instruction to transform the description into the steps
    prompt_task = """Transform the detailed description into a series of high-level steps according to the instructions."""
    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}. Steps: 1. Enter the numerator and denominator"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. Steps: 1. Enter the numerators and denominators of the fractions, 2. Add the fractions and enter the result \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A two equations solver should be represented as title[2 Equation Solver], column{label[First Equation], row{input[First Equation Coefficient 1], label[x], label[+], input[First Equation Coefficient 2], label[=], input[First Equation Result]}, label[Second Equation], row{input[Second Equation Coefficient 1], label[x], label[+], input[Second Equation Coefficient 2], label[y], label[=], input[Second Equation Result]}}. Steps: 1. Enter the coefficients and variables of the first equation, 2. Enter the coefficients and variables of the second equation, 3. Solve the system of equations"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}. Steps: 1. Multiply the radicals, 2. Simplify the expression"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight and recommended dosage per kg, 2. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees, hours worked, and average tasks completed, 2. Calculate the current workflow efficiency, 3. Enter the suggested changes to optimize the workflow, 4. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"


    # Combining all the parts to form the complete prompt
    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"
    instruction = f"\nDetailed Description:\n{detailed_description}\n"

    try:
        response = openai.chat.completions.create(
        model="gpt-4", # Adjusted to use GPT-4
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction }]
        )
        generated_text = response.choices[0].message.content.strip()
        print(generated_text)
        # Return the high-level steps generated by OpenAI
        return jsonify({"steps": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/generateTutorLayoutsFromSteps', methods=['POST'])
def generate_tutor_layouts_from_steps():
    data = request.get_json()
    detailed_description = data.get('text')
    refined_steps = data.get('steps', [])
    num_layouts = 6  # Set the number of layouts to generate
    prompt_system = "Create a compact representation layout string for a tutor interface based on the given requirements and refined steps. The layout should facilitate the problem-solving process described in the steps."
    prompt_introduction = """Generate a compact representation layout string for a tutor interface component based on a specific format. This format includes elements such as rows, columns, labels, and inputs."""
    prompt_format = "The format uses: row{{...}}, column{{...}} with each element stacked vertically over the other within the column, label[Label], and input[Placeholder]. Elements within rows and columns are enclosed in curly braces {{}}, and attributes are in square brackets []."
    prompt_design_instructions = """Design principles require that each input element be separate, for example, in an equation, there should be one input element per digit. A single equation must be on a single row. Elements within a row are arranged horizontally. Rows cannot be directly nested within other rows, nor can columns be nested within other columns. Ensure each input element is separate, such as digits in an equation, and a single equation appears on a single line."""
    prompt_task = f"""Transform the detailed description and refined steps into {num_layouts} different compact representation layout strings according to the instructions. Each layout should be on a new line, preceded by 'Layout X:', where X is the layout number."""


    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}. Steps: 1. Enter the numerator and denominator"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. Steps: 1. Enter the numerators and denominators of the fractions, 2. Add the fractions and enter the result \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A two equations solver should be represented as title[2 Equation Solver], column{label[First Equation], row{input[First Equation Coefficient 1], label[x], label[+], input[First Equation Coefficient 2], label[=], input[First Equation Result]}, label[Second Equation], row{input[Second Equation Coefficient 1], label[x], label[+], input[Second Equation Coefficient 2], label[y], label[=], input[Second Equation Result]}}. Steps: 1. Enter the coefficients and variables of the first equation, 2. Enter the coefficients and variables of the second equation, 3. Solve the system of equations"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}. Steps: 1. Multiply the radicals, 2. Simplify the expression"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight and recommended dosage per kg, 2. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees, hours worked, and average tasks completed, 2. Calculate the current workflow efficiency, 3. Enter the suggested changes to optimize the workflow, 4. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"

    steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(refined_steps))
    instruction = f"\nDetailed Description:\n{detailed_description}\n\nRefined Steps:\n{steps_text}\n"
    # Combining all the parts to form the complete prompt
    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction}]
        )
        generated_text = response.choices[0].message.content.strip()
        
        # Split the generated text into individual layouts
        layouts = generated_text.split('\n')
        layouts = [layout.strip() for layout in layouts if layout.strip().startswith('Layout')]
        
        print(generated_text)
        # Return the layouts generated by OpenAI
        return jsonify({"layouts": layouts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/generateTutorLayoutFromSteps', methods=['POST'])
def generate_tutor_layout_from_steps():
    data = request.get_json()
    detailed_description = data.get('text')
    refined_steps = data.get('steps', [])
    prompt_system = "Create a compact representation layout string for a tutor interface based on the given requirements and refined steps. The layout should facilitate the problem-solving process described in the steps."
    prompt_introduction = """Generate a compact representation layout string for a tutor interface component based on a specific format. This format includes elements such as rows, columns, labels, and inputs."""
    prompt_format = "The format uses: row{{...}}, column{{...}} with each element stacked vertically over the other within the column, label[Label], and input[Placeholder]. Elements within rows and columns are enclosed in curly braces {{}}, and attributes are in square brackets []."
    prompt_design_instructions = """Design principles require that each input element be separate, for example, in an equation, there should be one input element per digit. A single equation must be on a single row. Elements within a row are arranged horizontally. Rows cannot be directly nested within other rows, nor can columns be nested within other columns. Ensure each input element is separate, such as digits in an equation, and a single equation appears on a single line."""
    prompt_task = """Transform the detailed description and refined steps into a compact representation layout string according to the instructions."""

    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}. Steps: 1. Enter the numerator and denominator"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. Steps: 1. Enter the numerators and denominators of the fractions, 2. Add the fractions and enter the result \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A two equations solver should be represented as title[2 Equation Solver], column{label[First Equation], row{input[First Equation Coefficient 1], label[x], label[+], input[First Equation Coefficient 2], label[=], input[First Equation Result]}, label[Second Equation], row{input[Second Equation Coefficient 1], label[x], label[+], input[Second Equation Coefficient 2], label[y], label[=], input[Second Equation Result]}}. Steps: 1. Enter the coefficients and variables of the first equation, 2. Enter the coefficients and variables of the second equation, 3. Solve the system of equations"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}. Steps: 1. Multiply the radicals, 2. Simplify the expression"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight and recommended dosage per kg, 2. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees, hours worked, and average tasks completed, 2. Calculate the current workflow efficiency, 3. Enter the suggested changes to optimize the workflow, 4. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"

    prompt_task = """Transform the detailed description and refined steps into a compact representation layout string according to the instructions."""
    steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(refined_steps))
    instruction = f"\nDetailed Description:\n{detailed_description}\n\nRefined Steps:\n{steps_text}\n"
    # Combining all the parts to form the complete prompt
    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"

    try:
        response = openai.chat.completions.create(
        model="gpt-4", # Adjusted to use GPT-4
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction }]
        )
        generated_text = response.choices[0].message.content.strip()
        print(generated_text)
        # Return the high-level steps generated by OpenAI
        return jsonify({"steps": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generateLockedSteps', methods=['POST'])
def generate_locked_steps():
    data = request.get_json()
    detailed_description = data.get('text')
    locked_steps = data.get('lockedSteps', [])  # Get locked steps from the request
    prompt_system = "Create a series of high-level steps for solving a problem in a tutor interface, taking into account any locked steps that must remain unchanged. Each step should be a clear, concise description of an action the user needs to take. The steps should logically progress from the initial problem statement to the final solution, adhering to pedagogical best practices."

    prompt_introduction = """Generate a series of high-level steps for solving a problem in a tutor interface based on a detailed description, preserving any locked steps provided."""

    prompt_format = "The steps should be numbered and separated by commas. Each step should be a short, actionable phrase that guides the user through the problem-solving process. Locked steps must remain in their original position and content."

    prompt_design_instructions = """Design principles require that each step be focused on a single action or concept. Steps should be ordered logically and build upon each other. Avoid using technical jargon or complex language. Each step should be clear and easily understandable for the user."""
    # Instruction to transform the description into the steps
    prompt_task = """Transform the detailed description into a series of high-level steps according to the instructions, preserving the locked steps in their original positions and generating new or modified steps around them. Don't highlight in anyway the locked steps (DO NOT use parenthesis to specify the locked step). They must be formatted exactly as the others. The locked steps in the regenerated must be also in other positions, but they must preserve the succession specified before, if one before was the five, and the other is the seven, the second also in the regenerated version must go after the first."""
    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. \
    "
    prompt_examples += ", Example 2: A two equations solver should be represented as title[2 Equation Solver], column{label[First Equation], row{input[First Equation Coefficient 1], label[x], label[+], input[First Equation Coefficient 2], label[=], input[First Equation Result]}, label[Second Equation], row{input[Second Equation Coefficient 1], label[x], label[+], input[Second Equation Coefficient 2], label[y], label[=], input[Second Equation Result]}}. Steps: 1. Enter the coefficients and variables of the first equation, 2. Enter the coefficients and variables of the second equation, 3. Solve the system of equations"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}. Steps: 1. Multiply the radicals, 2. Simplify the expression"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight and recommended dosage per kg, 2. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees, hours worked, and average tasks completed, 2. Calculate the current workflow efficiency, 3. Enter the suggested changes to optimize the workflow, 4. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"



    # Combining all the parts to form the complete prompt
    locked_steps_info = "\nLocked steps (must be preserved):\n"
    for i, step in enumerate(locked_steps, 1):
        locked_steps_info += f"{i}. {step}\n"

    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"
    instruction = f"\nDetailed Description:\n{detailed_description}\n{locked_steps_info}"


    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": instruction}
            ]
        )
        generated_text = response.choices[0].message.content.strip()
        print(generated_text)
        return jsonify({"steps": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generateTutorLayout', methods=['POST'])
def generate_tutor_layout():
    data = request.get_json()
    text_specification = data.get('text')
    detailed_description = data.get('text')
    # Introduction to the task
    prompt_system = "Create a dynamic and interactive tutor interface layout specifically crafted for problem-solving exercises, which commences with the precise definition of variables that are essential for the problem at hand. Each interface is to facilitate a clear, step-by-step resolution pathway, commencing with an explicit problem statement and progressing through a structured series of steps. Each step is to include text inputs that are directly linked to data sources, ensuring their correctness can be validated through an HTN (Hierarchical Task Network) process. This setup should lead to the revealing of the final solution, all while adhering to pedagogical best practices that logically sequence problem-solving elements and enforce the understanding of the educational content."

    prompt_introduction = """Generate a compact representation layout string for a tutor interface based on a specific format. This format includes elements such as titles, rows, columns, labels, and inputs."""
# Explanation of the format
    prompt_format = "The format uses: title[Title], row{{...}}, column{{...}} with each element stacked vertically over the other within the column, label[Label], and input[Placeholder]. Elements within rows and columns are enclosed in curly braces {{}}, and attributes are in square brackets []."
# Design instructions for the layout
    prompt_design_instructions = """Design principles require that each input element be separate, for example, in an equation, there should be one input element per digit. A single equation must be on a single row. Elements within a row are arranged horizontally. Rows cannot be directly nested within other rows, nor can columns be nested within other columns. Ensure each input element is separate, such as digits in an equation, and a single equation appears on a single line. There are no interactive buttons like 'Click to solve' within the layout."""
    # Instruction to transform the description into the layout string
    prompt_task = """Transform the detailed description into the compact representation layout string according to the instructions."""
    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}"
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A two equations solver should be represented as title[2 Equation Solver], column{label[First Equation], row{input[First Equation Coefficient 1], label[x], label[+], input[First Equation Coefficient 2], label[=], input[First Equation Result]}, label[Second Equation], row{input[Second Equation Coefficient 1], label[x], label[+], input[Second Equation Coefficient 2], label[y], label[=], input[Second Equation Result]}}."
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, input{label[Simplify the expression]}}"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout."
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps."
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}"
    prompt_examples += ", Example 9: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}"


    # Combining all the parts to form the complete prompt
    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"
    instruction = f"\nDetailed Description:\n{detailed_description}\n"

    # Format the prompt with the detailed description from the request
    #prompt = f"""Given a detailed description of a tutor interface, generate a compact representation layout string in a specific format. The format includes titles, rows, columns, labels, and inputs, represented as follows: title[Title], row {{ ... }}, column {{ ... }}, label[Label], and input[Placeholder]. Elements inside rows and columns should be enclosed in curly braces {{}}, and element attributes should be enclosed in square brackets []. Ensure the output is precise and adheres to this structure for easy parsing.
    #Design instructions: Given that the intelligent tutor will utilize an AI algorithm to learn from the teacher interaction what the problem solution is; each input element should be separate, for example in an equation there should be one input element per digit. Respect design principles; for example, a single equation must be in a single line. 
    #Detailed Description:
    #{detailed_description}
    #Transform this description into the compact representation layout string according to the instructions. Respond in one line."""

    try:
        response = openai.chat.completions.create(
          model="gpt-4", # Adjusted to use GPT-4
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction }]
        )
        generated_text = response.choices[0].message.content.strip()
        print(generated_text)
        # Return the compact layout generated by OpenAI
        return jsonify({"compactLayout": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    







###################################################
###################################################

if __name__ == "__main__":
    app.run()


