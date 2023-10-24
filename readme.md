# Inventory Management Web App

Inventory Management Web App is a web application designed to help you manage your inventory efficiently. It allows you to keep track of inventory items, their quantities, unit costs, and usage. With this app, you can easily monitor your stock levels and generate reports to make informed decisions.

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

Inventory Management Web App is a user-friendly solution for businesses and organizations of all sizes to streamline their inventory management processes. It helps you save time, reduce costs, and minimize errors associated with manual inventory tracking.

## Features

- Add, update, and delete inventory items.
- Record item quantities, unit costs, and dates.
- Generate reports to view inventory usage and trends.
- User authentication for secure access to the application.
- Intuitive user interface for easy navigation.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.11
- Django 4.2.5
- Database system ( mssql )

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/kamauhenry/InventoryMngt.git

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate

# macOS and Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser

# Start the development server
python manage.py runserver

## Usage

1. **Log In:** Use your admin credentials to access the application.
2. **Add Inventory Items:** Specify item names, quantities, unit costs, and purchase dates.
3. **View, Update, or Delete:** Manage existing inventory records with ease.
4. **Generate Reports:** Analyze inventory usage and trends with the report generation feature.
5. **Secure Access:** User authentication ensures secure access to the application.
6. **User-Friendly Interface:** The intuitive user interface simplifies navigation.

## Contributing

We welcome contributions from the community to make this project even better! To contribute, please follow these steps:

1. Fork the repository on GitHub.
2. Clone the forked repository to your local machine.
3. Create a new branch for your feature or bug fix: `git checkout -b feature-name`.
4. Make your changes and commit them: `git commit -m 'Add feature XYZ'`.
5. Push your changes to your fork on GitHub: `git push origin feature-name`.
6. Open a pull request from your fork to the main repository.
7. I will review your pull request and provide feedback.

Please ensure your contributions adhere to our code of conduct and coding standards. We appreciate your help in making this project better for everyone!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

We would like to express our gratitude to the following individuals and projects for their contributions and inspiration:

- [Django](https://www.djangoproject.com/): The web framework that powers this application.
- [Bootstrap](https://getbootstrap.com/): For the responsive and sleek UI components.
- The open-source community for their continuous support and contributions.


