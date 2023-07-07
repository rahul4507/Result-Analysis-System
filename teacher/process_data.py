import csv
from io import StringIO


def generate_csv(result_data):
    # Create a string buffer to store the CSV data
    csv_buffer = StringIO()

    # Define the CSV fields
    field_names = ['Name', 'PRN', 'Marks', 'TAG']

    # Create a CSV writer using the string buffer
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=field_names)

    # Write the header row
    csv_writer.writeheader()

    # Write the data rows
    for result in result_data:
        csv_writer.writerow({
            'Name': result.student_id.name,
            'PRN': result.student_id.prn,
            'Marks': result.obtained_marks,
            'TAG': result.TAG,
        })

    # Get the CSV data from the string buffer
    csv_data = csv_buffer.getvalue()

    # Close the string buffer
    csv_buffer.close()

    return csv_data


def generate_comparison_csv(result_data):
    # Create a string buffer to store the CSV data
    csv_buffer = StringIO()

    # Define the CSV fields
    field_names = ['Name', 'PRN', 'Marks', 'TAG']

    # Create a CSV writer using the string buffer
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=field_names)

    # Write the header row
    csv_writer.writeheader()

    # Write the data rows
    for result in result_data:
        csv_writer.writerow({
            'Name': result.student_id.name,
            'PRN': result.student_id.prn,
            'Marks': result.obtained_marks,
            'TAG': result.TAG,
        })

    # Get the CSV data from the string buffer
    csv_data = csv_buffer.getvalue()

    # Close the string buffer
    csv_buffer.close()

    return csv_data

