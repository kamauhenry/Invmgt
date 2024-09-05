INVGMT 
CONSTRUCTION PROJECT MANAGEMENT WEBAPP

This Web Application combines robust **Construction Project Management** features with an **Inventory Management** system. It helps manage construction projects efficiently by tracking tasks, inventory, employee performance, project progress, and more. With this app, you can oversee construction activities while managing inventory items, their quantities, costs, and usage.

## Table of Contents

- [About](#about)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## About

The **Construction & Inventory Management Web App** is a comprehensive solution for businesses in the construction industry, designed to streamline project management while also offering seamless inventory control. The app helps you keep track of ongoing projects, resources, employee tasks, and material usage, ensuring that both construction operations and inventory remain aligned and optimized.

## Features

### Construction Management Features:
- **Project Management**: Track the status, start and end dates, location, and owner of construction projects.
- **Task Management**: Assign tasks to employees, monitor progress, and track time allocation.
- **AI-Driven Feasibility Analysis**: Leverage AI tools for accurate material estimation and project feasibility assessments.
- **Employee Management**: Monitor employee performance, manage wages, and assign roles.
- **Reporting**: Generate detailed feasibility reports, task reports, and progress updates using AI.

### Inventory Management Features:
- **Add, Update, and Delete Items**: Manage inventory items with details on quantities, costs, and purchase dates.
- **Track Issuance & Return**: Track the issuance, return, and usage of equipment and materials for construction tasks.
- **Real-time Monitoring**: Monitor inventory levels, equipment usage, and costs in real time.
- **Generate Reports**: View inventory usage trends and generate detailed reports on costs and item usage.

### General Features:
- **User Authentication**: Secure access with role-based permissions for admins, project managers, and other users.
- **User-Friendly Interface**: Intuitive UI for easy navigation and smooth interaction with the system.
- **Real-Time Collaboration**: Ensure teams can collaborate on project details and material allocation in real time.
- **Sustainability Considerations**: Integrated sustainability tracking for ensuring compliance with environmental standards and regulations.
- **Comprehensive Integration**: Seamless integration of construction project data and inventory for a unified workflow.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11
- Django 4.2.5
- Database system (MSSQL or PostgreSQL recommended for scalability)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kamauhenry/InventoryMngt.git
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   ```bash
   # Windows
   venv\Scripts\activate

   # macOS and Linux
   source venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Create a superuser for admin access:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Usage

1. **Log In**: Use admin credentials to access the system dashboard.
2. **Project Management**: Add new construction projects, assign tasks, and monitor progress.
3. **Inventory Management**: Add inventory items and track their usage for construction tasks.
4. **Generate Reports**: Produce detailed reports on inventory trends and project feasibility using AI-driven tools.
5. **Secure Access**: Ensure users can access relevant features based on their roles.
6. **User-Friendly Interface**: Navigate through projects and inventory with an intuitive design.

## Contributing

We welcome contributions to improve the app further! Here's how to contribute:

1. Fork the repository on GitHub.
2. Clone the forked repository.
3. Create a branch for your feature or bug fix: `git checkout -b feature-name`.
4. Make your changes and commit them: `git commit -m 'Add feature XYZ'`.
5. Push changes to your fork: `git push origin feature-name`.
6. Open a pull request to the main repository.
7. Your contribution will be reviewed, and feedback will be provided.

Please ensure your contributions follow the coding standards and code of conduct.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

We would like to express our gratitude to the following:

- [Django](https://www.djangoproject.com/): The web framework used for this application.
- [Bootstrap](https://getbootstrap.com/): For sleek and responsive UI components.
- The open-source community for their contributions and inspiration.
- The AI research community for the insights into material estimation and feasibility analysis tools integrated into the system.

--- 

This README now reflects the combined functionality of **Construction** and **Inventory Management** systems, highlighting features such as AI-driven project feasibility and material estimation alongside core inventory tracking capabilities.
