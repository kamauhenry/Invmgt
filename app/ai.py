import os
import requests
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configuration
GPT4V_KEY = "f549c621241c4ae693bfef95c58127be"
headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

# Your prompt
prompt = "Please provide a detailed feasibility report for the project with the following details: Project Name: {project_name}, Project Owner: {project_owner}, Start Date: {start_date}, End Date: {end_date}, Project Type: {project_type}, Location: {location}, Description: {description}, Building Area: {building_area} square meters, Number of Floors: {number_of_floors}, Materials: {materials}, Building Codes: {building_codes}, Site Conditions: {site_conditions}, Drawings: {drawings}, Project Requirements: {project_requirements}, Sustainability Considerations: {sustainability_considerations}, External Factors: {external_factors}, Estimated Completion Time: {estimated_completion_time} days, Required Employees: {required_employees}, Detailed Materials List: {detailed_materials_list}. Assess the project's feasibility, identify potential challenges or risks, provide an estimate of project costs, evaluate the estimated completion time and suggest adjustments if necessary, review building codes and site conditions for compliance with local regulations, analyze sustainability considerations and recommend improvements, assess the adequacy of required employees and materials, evaluate external factors that might influence the project's feasibility and suggest mitigation strategies, and include any additional observations or recommendations relevant to the project's success."

# Payload for the request
payload = {
  "messages": [
    {"role": "user", "content": prompt}
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

GPT4V_ENDPOINT = "https://ai-service-proj.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"

def make_request_with_retries(endpoint, headers, payload, max_retries=5, delay=5):
    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if e.response and e.response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise SystemExit(f"Failed to make the request. Error: {e}")

# Make the request
result = make_request_with_retries(GPT4V_ENDPOINT, headers, payload)

# Print the result
print(result)

# Extract the response content
content = result['choices'][0]['message']['content']

# Path to save the PDF
pdf_path = "feasibility_report.pdf"

# Create the PDF
c = canvas.Canvas(pdf_path, pagesize=letter)
width, height = letter
text = c.beginText(40, height - 40)
text.setFont("Helvetica", 12)

# Add response content to the PDF
for line in content.split('\n'):
    text.textLine(line)

c.drawText(text)
c.showPage()
c.save()

print(f"PDF saved at {pdf_path}")
