#!/usr/bin/env python3
"""
Script to generate example Excel files for xlsx2md documentation.
"""

import pandas as pd


def create_sample_data():
    """Create sample data for Excel files."""
    # Sample data for multiple sheets
    employees_data = {
        "Name": [
            "John Doe",
            "Jane Smith",
            "Bob Johnson",
            "Alice Brown",
            "Charlie Wilson",
        ],
        "Department": ["Engineering", "Marketing", "Sales", "Engineering", "Marketing"],
        "Salary": [75000, 65000, 70000, 72000, 68000],
        "StartDate": [
            "2020-01-15",
            "2019-03-22",
            "2018-11-08",
            "2021-02-14",
            "2020-07-30",
        ],
        "Performance": [4.2, 3.8, 4.5, 4.1, 3.9],
    }
    sales_data = {
        "Product": ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones"],
        "Q1_Sales": [120, 450, 200, 80, 300],
        "Q2_Sales": [135, 480, 220, 85, 320],
        "Q3_Sales": [110, 420, 180, 75, 280],
        "Q4_Sales": [150, 500, 250, 90, 350],
        "Revenue": [45000, 6750, 12000, 13500, 18750],
    }
    inventory_data = {
        "Item": ["Widget A", "Widget B", "Widget C", "", "Widget D"],
        "Quantity": [100, 50, 75, None, 200],
        "Price": [10.50, 25.00, 15.75, 0, 8.25],
        "Category": ["Electronics", "Tools", "Electronics", "", "Tools"],
        "LastUpdated": ["2024-01-15", "2024-01-10", "2024-01-12", "", "2024-01-08"],
    }
    return employees_data, sales_data, inventory_data


def create_excel_files():
    """Create example Excel files."""
    employees_data, sales_data, inventory_data = create_sample_data()
    # Create sample_data.xlsx with multiple sheets
    with pd.ExcelWriter("docs/examples/sample_data.xlsx", engine="openpyxl") as writer:
        pd.DataFrame(employees_data).to_excel(
            writer, sheet_name="Employees", index=False
        )
        pd.DataFrame(sales_data).to_excel(writer, sheet_name="Sales", index=False)
        pd.DataFrame(inventory_data).to_excel(
            writer, sheet_name="Inventory", index=False
        )
    # Create sales_report.xlsx with formatting
    sales_report_data = {
        "Region": ["North", "South", "East", "West", "Central"],
        "Sales_2023": [1250000, 980000, 1450000, 1120000, 890000],
        "Sales_2024": [1350000, 1050000, 1550000, 1200000, 950000],
        "Growth_%": [8.0, 7.1, 6.9, 7.1, 6.7],
        "Target": [1300000, 1000000, 1500000, 1150000, 900000],
        "Status": ["On Track", "Behind", "Ahead", "On Track", "Behind"],
    }
    with pd.ExcelWriter("docs/examples/sales_report.xlsx", engine="openpyxl") as writer:
        pd.DataFrame(sales_report_data).to_excel(
            writer, sheet_name="Regional_Sales", index=False
        )
    # Create inventory.xlsx with empty cells and long text
    inventory_detailed = {
        "Product_ID": ["P001", "P002", "P003", "", "P004", "P005"],
        "Product_Name": [
            "Laptop Pro",
            "Wireless Mouse",
            "Office Chair",
            "",
            "Coffee Maker",
            "Desk Lamp",
        ],
        "Category": [
            "Electronics",
            "Electronics",
            "Furniture",
            "",
            "Appliances",
            "Furniture",
        ],
        "Quantity": [45, 120, 23, None, 67, 89],
        "Price": [1299.99, 29.99, 199.99, 0, 89.99, 49.99],
        "Description": [
            "High-performance laptop for professionals with 16GB RAM and 512GB SSD",
            "Ergonomic wireless mouse with precision tracking and long battery life",
            "Comfortable office chair with lumbar support and adjustable height",
            "",
            "Programmable coffee maker with thermal carafe and auto-shutoff feature",
            "LED desk lamp with adjustable brightness and color temperature",
        ],
        "Last_Updated": [
            "2024-01-15",
            "2024-01-10",
            "2024-01-12",
            "",
            "2024-01-08",
            "2024-01-14",
        ],
    }
    with pd.ExcelWriter("docs/examples/inventory.xlsx", engine="openpyxl") as writer:
        pd.DataFrame(inventory_detailed).to_excel(
            writer, sheet_name="Inventory", index=False
        )


def main():
    """Main function to generate all example files."""
    print("Generating example Excel files...")
    try:
        create_excel_files()
        print("✅ Successfully created example Excel files:")
        print("  - docs/examples/sample_data.xlsx")
        print("  - docs/examples/sales_report.xlsx")
        print("  - docs/examples/inventory.xlsx")
        print("\nCSV files are already created:")
        print("  - docs/examples/users.csv")
        print("  - docs/examples/products.csv")
        print("  - docs/examples/data_utf8.csv")
    except Exception as e:
        print(f"❌ Error creating example files: {e}")


if __name__ == "__main__":
    main()
