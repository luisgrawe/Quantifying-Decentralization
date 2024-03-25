# IMPORTS
from flask import Flask, render_template, Response, request
import mysql.connector
from mysql.connector import Error
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO
from io import StringIO
import csv




load_dotenv()  # Load environment variables from .env file
db_host = os.environ.get("DB_HOST")
db_database = os.environ.get("DB_DATABASE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


# Define Blockchains for the HTML files
blockchains = ['Bitcoin', 'Ethereum', 'Cardano', 'Solana', 'Avalanche']

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def fetch_last_row_from_database(selected_blockchain):
    """This function fetches the last row from the database for the specified blockchain to display the current decentralization degree."""

    try:
        connection = mysql.connector.connect(
            host = db_host,
            database = db_database,
            user = db_user,
            password = db_password
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Construct the table name based on the selected blockchain
            table_name = f'{selected_blockchain.lower()}_kpis'

            # Execute a query to get the last row from the specified table
            query = f'SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1'
            cursor.execute(query)

            # Fetch the last row
            last_row = cursor.fetchone()

            cursor.close()
            return last_row

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close()

    return None


def fetch_historical_data(selected_blockchain):
    """This function fetches all historical data from the database for the specified blockchain to generate the plots."""
    try:
        connection = mysql.connector.connect(
            host = db_host ,
            database = db_database,
            user = db_user,
            password = db_password
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Construct the table name based on the selected blockchain
            table_name = f'{selected_blockchain.lower()}_kpis'

            # Execute a query to get all columns for historical data
            query = f'SELECT * FROM {table_name} ORDER BY id'
            cursor.execute(query)

            # Fetch all rows
            historical_data = cursor.fetchall()

            cursor.close()
            return historical_data

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            connection.close()

    return None


def generate_plots(selected_blockchain):
    """This function generates plots for each KPI based on historical data."""

    # Fetch historical data from the database
    historical_data = fetch_historical_data(selected_blockchain)

    # Mapping from database column names to display names
    kpi_display_names = {
        'hosting_concentration': 'Hosting Concentration',
        'geographical_diversity': 'Geographical Diversity',
        'exchange_concentration': 'Exchange Concentration',
        'reference_client_contribution': 'Reference Client Contribution',
        'owner_control': 'Owner Control',
        'improvement_protocol': 'Improvement Protocol',
        'decision_making': 'Decision Making'
    }

    plots = {}

    for kpi in kpi_display_names:
        timestamps = [entry['timestamp'] for entry in historical_data] # Extract x-axis values
        kpi_values = [entry[kpi] for entry in historical_data] # Extract y-axis values

        # Creating a line plot for each KPI
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=kpi_values, mode='lines', name=kpi_display_names[kpi]))
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title=kpi_display_names[kpi],
            xaxis=dict(
                tickformat="%Y-%m-%d",  # Format to display only year-month-day
            ),
            yaxis=dict(
                range=[0, 1]  # Fix the range of the y-axis to be between 0 and 1
            )
        )
        # Convert the figure to a JSON string
        plots[kpi] = fig.to_json()

    return plots, kpi_display_names


def fetch_data_for_blockchain(selected_blockchain):
    """This function fetches all historical data from the database for the specified blockchain to download as a CSV file."""
    try:
        connection = mysql.connector.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=db_password
        )

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Construct the table name based on the selected blockchain
            table_name = f'{selected_blockchain.lower()}_kpis'

            # Execute a query to get all columns for historical data
            query = f'SELECT * FROM {table_name} ORDER BY id'
            cursor.execute(query)

            # Fetch all rows
            data = cursor.fetchall()

            cursor.close()
            return data

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            connection.close()

    return None


@app.route('/download_data')
def download_data():
    """This function downloads the historical data for the selected blockchain as a CSV file."""

    selected_blockchain = request.args.get('blockchain')
    data = fetch_data_for_blockchain(selected_blockchain)

    if data:
        # Convert data to CSV format
        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(data[0].keys())  # Write header row
        for row in data:
            csv_writer.writerow(row.values())

        # Create a response with the CSV data
        response = Response(
            csv_data.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={selected_blockchain.lower()}_data.csv'}
        )

        return response

    return "Data not found for the selected blockchain."

@app.route('/')
def index():
    """This function renders the home page."""
    return render_template('index.html', blockchains=blockchains)


@app.route('/<selected_blockchain>')
def blockchain(selected_blockchain):
    """This function renders the blockchain page for the selected blockchain."""
    last_row = fetch_last_row_from_database(selected_blockchain)
    plots, kpi_display_names = generate_plots(selected_blockchain)
    timestamp = last_row['timestamp']

    # Exclude the 'timestamp' field
    if last_row and 'timestamp' in last_row:
        del last_row['timestamp']

    if last_row and 'id' in last_row:
        del last_row['id']

    return render_template('blockchain.html', blockchain=selected_blockchain, decentralization_data=[last_row], blockchains=blockchains, plots=plots, timestamp=timestamp, kpi_display_names=kpi_display_names)


if __name__ == '__main__':
    socketio.run(app, port=8000, debug=True)
    
