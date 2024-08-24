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
from bs4 import BeautifulSoup

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

# First, check if the environment variable is defined
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    openai_api_key = get_openai_key()

openai.api_key = openai_api_key
input_prompt = get_prompt()


@app.route("/")
def index():
        return render_template("tutor_builder.html")


#################
# TUTOR BUILDER #
#################


def process_element(element, processed=None):
    if processed is None:
        processed = set()
    if element in processed:
        return ''
    processed.add(element)
    class_list = element.get('class', [])
    if 'btn-tutor-title' in class_list:
        title = element.find('p', class_='page-item')
        return f"title[{title.get_text(strip=True)}]" if title else ''
    elif 'btn-row' in class_list or 'btn-column' in class_list:
        container_type = 'row' if 'btn-row' in class_list else 'column'
        return process_container(element, container_type, processed)
    elif 'btn-label' in class_list:
        label = element.find('p', class_='page-item')
        return f"label[{label.get_text(strip=True)}]" if label else ''
    elif 'btn-input-box-t' in class_list:
        input_element = element.find('input')
        input_placeholder = input_element.get('placeholder', 'Text Box') if input_element else 'Text Box'
        return f"input[{input_placeholder}]"
    return ''

def process_container(element, container_type, processed):
    ul_element = element.find('ul', recursive=False)
    if ul_element:
        children = ul_element.find_all('div', recursive=False)
        if children:
            child_elements = [process_element(child, processed) for child in children]
            child_elements = [elem for elem in child_elements if elem]  # Remove empty strings
            return f"{container_type}{{{', '.join(child_elements)}}}"
    return f"{container_type}{{}}"

def compact_html_representation(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    
    if soup:
        elements = soup.find_all('div', recursive=False)
        processed = set()
        representation = ', '.join(filter(None, (process_element(elem, processed) for elem in elements)))
        return representation
    else:
        return "No top-level container found"


#################
# DSL TO HTML #
#################

item_count = 0

def create_element(tag, class_name=None, placeholder=None, data_type=None, content="",style = None):
    global item_count
    attributes = []
    if class_name:
        attributes.append(f'class="{class_name}"')
    if placeholder:
        attributes.append(f'placeholder="{placeholder}"')
    if data_type:
        item_id = f"newItem_{item_count}"
        attributes.extend([f'data-type="{data_type}"', 'draggable="true"', 'type="button"', f'id="{item_id}"'])
        item_count += 1
    if style:
        attributes.append('style="'+style+'"')
    return f"<{tag} {' '.join(attributes)}>{content}</{tag}>"

def process_compact_rep(compact_string, is_child=False):
    regex = re.compile(r'(\w+)\[([^\]]+)\]|\w+\s*{')
    match = None
    html = []

    while True:
        match = regex.search(compact_string)
        if match:
            matched_string, type_, content = match.group(), match.group(1), match.group(2)
            if type_ and content:
                if type_ == "title" or type_ == "label":
                    div_class = "btn-primary btn-tutor-title" if type_ == "title" else "btn-success btn-label row"
                    dt = "page-items" if type_ == "title" else "page-row"
                    p = create_element("p", "page-item", None, None, content) + create_element("p", "removeFromDom", None, None, "Tutor Title")
                    q = create_element("p", "page-item align-self-center", None, None, content) + create_element("p", "removeFromDom", None, None, "Label")
                    f = p if type_ == "title" else q
                    html.append(create_element("div", f"btn {div_class} rounded-button", None, dt, f))
                elif type_ == "input":
                    input_element_style = "border: none;box-shadow: none;text-align: center;"
                    input_element = create_element("input", "form-control", content, None, None, input_element_style)
                    html.append(create_element("div", "btn btn-light btn-input-box-t rounded-button", None, "page-row", input_element))
            elif matched_string.strip().endswith("{"):
                element_type = matched_string.strip().replace("{", "").strip()
                div_type = "page-row" if element_type == "row" else "page-items"
                div_class = "btn-warning btn-row btn-row-item grid" if element_type == "row" else "btn-info btn-column"
                p_remove = create_element("p", "removeFromDom", None, None, element_type.capitalize())
                ul_class = "list one page-item-ul grid grid-flow-col gap-1" if element_type == "row" else "list one d-flex flex-column gap-2 page-item-rl-row"
                ul_id = "page-item-ul" if element_type == "row" else "page-item-rl-row"
                close_index = find_closing_index(compact_string, match.end())
                inner_content = compact_string[match.end():close_index]
                ul_content = process_compact_rep(inner_content, True)
                ul = f'<ul class="{ul_class}" data-type="page-row">{ul_content}</ul>'
                html.append(create_element("div", f"btn {div_class} drop-box rounded-button", None, div_type, p_remove + ul))
                compact_string = compact_string[close_index + 1:]
                continue
            compact_string = compact_string[match.end():]
        else:
            break

    if is_child:
        return ''.join(html)
    else:
        page_div = create_element("div", None, None, "page-items", ''.join(html))
        final_container_div = create_element("div", "container mx-auto flex flex-col py-1 justify-center items-center", None, None, "")
        return ''.join(html) + final_container_div

def find_closing_index(string, open_index):
    stack = 1
    for i in range(open_index, len(string)):
        if string[i] == "{":
            stack += 1
        elif string[i] == "}":
            stack -= 1

        if stack == 0:
            return i
    return -1  # Handle malformed strings gracefully

def append_elements_from_compact_rep(compact_rep, is_child=False):
    html = process_compact_rep(compact_rep, is_child)
    return html.replace("None", "")



#################
# HTML TO DSL #
#################


def process_pointed_element(element, processed=None):
    if processed is None:
        processed = set()
    if element in processed:
        return ''
    processed.add(element)
    class_list = element.get('class', [])
    pointed_value = element.get('pointed', '')
    pointed_suffix = f"({pointed_value})" if pointed_value else ''
    if 'btn-tutor-title' in class_list:
        title = element.find('p', class_='page-item')
        return f"title[{title.get_text(strip=True)}]{pointed_suffix}" if title else ''
    elif 'btn-row' in class_list or 'btn-column' in class_list:
        container_type = 'row' if 'btn-row' in class_list else 'column'
        return process_pointed_container(element, container_type, processed)
    elif 'btn-label' in class_list:
        label = element.find('p', class_='page-item')
        return f"label[{label.get_text(strip=True)}]{pointed_suffix}" if label else ''
    elif 'btn-input-box-t' in class_list:
        input_element = element.find('input')
        input_placeholder = input_element.get('placeholder', 'Text Box') if input_element else 'Text Box'
        return f"input[{input_placeholder}]{pointed_suffix}"
    return ''

def process_pointed_container(element, container_type, processed):
    ul_element = element.find('ul', recursive=False)
    if ul_element:
        children = ul_element.find_all('div', recursive=False)
        if children:
            child_elements = [process_pointed_element(child, processed) for child in children]
            child_elements = [elem for elem in child_elements if elem]  # Remove empty strings
            return f"{container_type}{{{', '.join(child_elements)}}}"
    return f"{container_type}{{}}"

def compact_html_representation_pointed(html):
    soup = BeautifulSoup(html, 'html.parser')    
    if soup:
        elements = soup.find_all('div', recursive=False)
        processed = set()
        representation = ', '.join(filter(None, (process_pointed_element(elem, processed) for elem in elements)))
        return representation
    else:
        return "No top-level container found"

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
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Put the coefficient and solve for the x 3. Solve the equation"
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
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Reorder the coefficients to solve for the x 3. Solve the equation"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}. Steps: 1. Rewrite under the same radical 2. Solve the argument of the radical 3. Solve the argument of the radical"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight 2. Enter the recommended dosage per kg (in mg) 3. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees 2. Enter the number of hours worked 3. Enter the number of average tasks completed 4. Calculate the current workflow efficiency, 5. Enter the suggested changes to optimize the workflow 6. Calculate the optimized workflow efficiency"
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
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. Steps: 1. Enter the numerators and denominators of the first fraction member, 2. Enter the numerators and denominators of the second fraction member, 3. Enter the result \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Reorder the coefficients to solve for the x 3. Solve the equation"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}. Steps: 1. Rewrite under the same radical 2. Solve the argument of the radical 3. Solve the argument of the radical"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight 2. Enter the recommended dosage per kg (in mg) 3. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees 2. Enter the number of hours worked 3. Enter the number of average tasks completed 4. Calculate the current workflow efficiency, 5. Enter the suggested changes to optimize the workflow 6. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"

    steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(refined_steps))
    instruction = f"\nDetailed Description:\n{detailed_description}\n\ Steps:\n{steps_text}\n"
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
        
@app.route('/generateFromPreferences', methods=['POST'])
def generateFromPreferences():
    data = request.get_json()
    drafts = data.get('drafts')
    layouts = [compact_html_representation_pointed(draft) for draft in drafts ] 
    
    prompt_system = """Create a dynamic and interactive tutor interface layout specifically crafted for problem-solving exercises. The layout should be based on input requirements, a specified number of steps for the tutor design to respect, and a set of preferences over initial draft layouts. The final layout should combine these drafts while respecting the requirements, steps, and preferences.

    The representation of layouts and preferences is as follows:
    - Preferences are expressed in parentheses after the element on which they are expressed.
    - Preferences can be of type 'fix', where the fixed element must be mandatory present in the final remixed interface.
    - Preferences can be of type 'pref', where the element should be present in the final layout if the fixed elements, steps, or requirements allow.

    Example: 
    title[Rational Equation Solver](fix), column{label[Solve the equation], row{column{input[Numerator 1], label[___](pref), input[Denominator 1](pref)}, label[=](fix), input[Result](fix)}}

    The interface should facilitate a clear, step-by-step resolution pathway, commencing with an explicit problem statement and progressing through a structured series of steps. Each step should include text inputs that are directly linked to data sources, ensuring their correctness can be validated through an HTN (Hierarchical Task Network) process. This setup should lead to the revealing of the final solution, all while adhering to pedagogical best practices that logically sequence problem-solving elements and enforce the understanding of the educational content."""

    prompt_introduction = """Generate a compact representation layout string for a tutor interface based on the given requirements, number of steps, and preferences over initial draft layouts. The final layout should combine these elements according to the specified format."""

    prompt_format = "The format uses: title[Title], row{{...}}, column{{...}} with each element stacked vertically over the other within the column, label[Label], and input[Placeholder]. Elements within rows and columns are enclosed in curly braces {{}}, and attributes are in square brackets []."

    prompt_design_instructions = """Design principles require that each input element be separate, for example, in an equation, there should be one input element per digit. A single equation must be on a single row. Elements within a row are arranged horizontally. Rows cannot be directly nested within other rows, nor can columns be nested within other columns. Ensure each input element is separate, such as digits in an equation, and a single equation appears on a single line. There are no interactive buttons like 'Click to solve' within the layout."""

    prompt_task = """Transform the given requirements, number of steps, and preferences into a final compact representation layout string according to the instructions. Ensure that the final layout respects the fixed elements, incorporates preferred elements where possible, and adheres to the specified number of steps."""


    prompt_examples = "Example 0: A fraction is always of the form column{input[Numerator], label[____], input[Denominator]} and is never row{input[Numerator], label[/], input[Denominator]}. "
    prompt_examples += "Example 1: Equation row with two fraction members should be represented as a row with multiple columns inside for the members. Each column contains stacked numerator, operand (division symbol), and denominator. Include labels for operators in the main row. For a fraction equation like 1/2 + 3/4, the layout should be row{column{input[Numerator], label[____], input[Denominator]}, label[+], column{input[Numerator], label[____], input[Denominator]}, label[=], input[Result]}. This format ensures that each part of the fraction equation is clearly defined and separated for input. Steps: 1. Enter the numerators and denominators of the fractions, 2. Add the fractions and enter the result \
    "
    # Examples of the prompt format
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Reorder the coefficients to solve for the x 3. Solve the equation"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}. Steps: 1. Rewrite under the same radical 2. Solve the argument of the radical 3. Solve the argument of the radical"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight 2. Enter the recommended dosage per kg (in mg) 3. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees 2. Enter the number of hours worked 3. Enter the number of average tasks completed 4. Calculate the current workflow efficiency, 5. Enter the suggested changes to optimize the workflow 6. Calculate the optimized workflow efficiency"
    prompt_examples += ", Example 8: For an English article selection tutor, the representation would be title[English Article Selection Tutor], column{label[Instructions], label[Select the most appropriate article ('a', 'an', 'the' or 'no article') for each blank in the sentences below], row{label[Sentence 1], input[Sentence 1 Article Choice]}, row{label[Sentence 2], input[Sentence 2 Article Choice]}, row{label[Sentence 3], input[Sentence 3 Article Choice]}}. Steps: 1. Select the appropriate article for the first sentence, 2. Select the appropriate article for the second sentence, 3. Select the appropriate article for the third sentence"
    prompt_examples += ", Example 9: For a tutor for conducting a cash flow analysis of a business, the representation would be title[Cash Flow Analysis Tutor], column{label[Instructions], label[Enter the relevant business data in the fields below to begin your cash flow analysis conversion], row{label[Enter the total revenue of the business for the chosen period], input[Total Revenue]}, row{label[Enter the total cost of goods sold (COGS) during the same period], input[Cost of Goods Sold]}, label[Gross Profit], row{input[Gross Profit], label[]}, row{label[Enter the total operating expenses during the same period], input[Operating Expenses]}, label[Net Profit], row{input[Net Profit], label[]}, row{label[Enter the total cash flows from investing activities (e.g. purchase of assets, investments)], input[Investing Cash Flows]}, row{label[Enter the total cash flows from financing activities (e.g. loans, dividends, repayable)], input[Financing Cash Flows]}, label[Net Cash Flow], row{input[Net Cash Flow], label[]}}. Steps: 1. Enter the total revenue and cost of goods sold, 2. Calculate the gross profit, 3. Enter the total operating expenses, 4. Calculate the net profit, 5. Enter the cash flows from investing activities, 6. Enter the cash flows from financing activities, 7. Calculate the net cash flow"
    prompt_examples += ", Example 10: For a tutor for a three members rational equation, the representation would be title[Rational Equations], column{label[Solve the rational equation], row{column{input[Numerator 1], label[___], input[Denominator 1]}, label[+], column{input[Numerator 2], label[___], input[Denominator 2]}, label[=], column{input[Numerator 3], label[___], input[Denominator 3]}}}. Steps: 1. Enter the numerators and denominators of the three fractions, 2. Solve the rational equation"

    

    prompt = f"{prompt_system}\n{prompt_introduction}\n\n{prompt_format}\n\n{prompt_design_instructions}\n\n{prompt_examples}\n\n{prompt_task}"
    layouts_string = '\n'.join(layouts)
    instruction = f"\Layouts to mix:\n{layouts_string}\n Reply with only the resulting layout, nothing else, also, the overall goal is to make a nice strucure, referring to examples. Avoid inserting the fix or pref indication in the result. Use the format provided in the examples."

    try:
        
        response = openai.chat.completions.create(
            model="gpt-4", # Adjusted to use GPT-4
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": instruction }]
        )
        generated_text = response.choices[0].message.content.strip()
    # Return the layouts generated by OpenAI
        return jsonify({"text": generated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  # Return the high-level steps generated by OpenAI



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
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Reorder the coefficients to solve for the x 3. Solve the equation"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}. Steps: 1. Rewrite under the same radical 2. Solve the argument of the radical 3. Solve the argument of the radical"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight 2. Enter the recommended dosage per kg (in mg) 3. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees 2. Enter the number of hours worked 3. Enter the number of average tasks completed 4. Calculate the current workflow efficiency, 5. Enter the suggested changes to optimize the workflow 6. Calculate the optimized workflow efficiency"
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
    prompt_examples += ", Example 2: A one variable equation solver should be represented as 'column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'. Steps: 1. Enter the coefficients and variables of the first equation, 2. Reorder the coefficients to solve for the x 3. Solve the equation"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}. Steps: 1. Rewrite under the same radical 2. Solve the argument of the radical 3. Solve the argument of the radical"
    prompt_examples += ", Example 4: For a Squared Tutor interface, the representation would be title[Squared Tutor], column{label[Enter the number you wish to square], row{input[Number], label[=], input[Result]}}. This configuration places the label and input for the number and the result all in a single horizontal row, maintaining a clear and concise layout. Steps: 1. Enter the number to be squared, 2. Calculate the square of the number"
    prompt_examples += ", Example 5: For a Tutor for missionaries and cannibals, the representation would be title[Missionaries and Cannibals Tutor], column{label[Instructions], row{label[Enter the number of missionaries], input[Missionaries]}, row{label[Enter the number of cannibals], input[Cannibals]}, label[Solution], row{input[First Move], label[->], input[Second Move]}, row{input[Third Move], label[->], input[Fourth Move]}}. As in This case, make sure to scaffold all the resolution steps. Steps: 1. Enter the number of missionaries and cannibals, 2. Determine the first move, 3. Determine the second move, 4. Determine the third move, 5. Determine the fourth move"
    prompt_examples += ", Example 6: For a tutor for calculating proper drug dosage levels for a nurse to administer to a patient, the representation would be title[Drug Dosage Tutor], column{label[Calculation Instructions], row{label[Enter the weight of the patient (in kg)], input[Patient Weight]}, row{label[Enter the recommended dosage per kg (in mg)], input[Dosage per kg]}, label[Calculated Dosage], row{input[Dosage Total], label[mg]}}. Steps: 1. Enter the patient's weight 2. Enter the recommended dosage per kg (in mg) 3. Calculate the total dosage"
    prompt_examples += ", Example 7: For A tutor for optimizing a business workflow, the representation would be title[Business Workflow Optimization Tutor], column{label[Instructions], row{label[Enter the number of employees], input[Number of Employees]}, row{label[Enter the number of hours worked by each employee per week], input[Hours Worked]}, row{label[Enter the average number of tasks completed by an employee per hour], input[Average Tasks Completed]}, label[Optimization Solution], row{input[Current Workflow Efficiency], label[%]}, row{label[Enter the changes you wish to make], input[Suggested Changes]}, label[Calculated Optimized Efficiency], row{input[Optimized Workflow Efficiency], label[%]}}. Steps: 1. Enter the number of employees 2. Enter the number of hours worked 3. Enter the number of average tasks completed 4. Calculate the current workflow efficiency, 5. Enter the suggested changes to optimize the workflow 6. Calculate the optimized workflow efficiency"
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
    prompt_examples += ", Example 2: A one variable equation solver should be represented as column{label[Equation], row{input[Equation Coefficient 1], label[x], label[+], input[Equation Coefficient 2], label[=], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}, row{label[x], label[=], input[Equation Coefficient 2], input[Equation Result]}}'"
    prompt_examples += ", Example 3: For a radicals tutor interface, the representation would be title[Radicals Tutor], column{label[Solve the following radicals multiplication problem below], row{label[What is √2 * √2], input[Result]}, row{label[Rewrite under the same radical], input[Result]}, row{label[Solve the argument of the radical], input[Result]}, row{label[Simplify the radical], input[Result]}}"
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


