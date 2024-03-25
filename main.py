#IMPORTS
from bitcoin_data import btc_decision_making, btc_exchange_concentration, btc_hosting_concentration, btc_geo_index, btc_improvement_protocol, btc_owner_control, btc_reference_client_concentration
from ethererum_data import eth_decision_making, eth_exchange_concentration, eth_geo_index, eth_improvement_protocol, eth_hosting_concentration, eth_owner_control, eth_reference_client_concentration
from cardano_data import ada_exchange_concentration, ada_improvement_protocol, ada_owner_control, ada_reference_client_concentration, ada_decision_making, ada_geo_hosting
from solana_data import sol_exchange_concentration, sol_geo_index, sol_improvement_protocol, sol_owner_control, sol_reference_client_concentration, sol_hosting_concentration, sol_decision_making
from avalanche_data import ava_decision_making, ava_exchange_concentration, ava_geo_diversity_hosting_concentration, ava_improvement_protocol, ava_owner_control, ava_reference_client_concentration
from shannon_index import calculate_shannon_index
from fractional_owner_index import calculate_fractional_owner_index
from geo_index import normalize_geographical_diversity_index
from gini_coefficient import calculate_gini
import csv
import time
import mysql.connector
from mysql.connector import Error
from app import socketio
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
db_host = os.environ.get("DB_HOST")
db_database = os.environ.get("DB_DATABASE")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


# ==========================================
# DATA SCRAPING ALGORITHM
# ==========================================
        
# Connect to the MySQL database
try:
    
    while True: 

        connection = mysql.connector.connect(
            host=db_host,
            database=db_database,
            user=db_user,
            password=db_password
        )

        if connection.is_connected():
            print("Connected to MySQL database")
            cursor = connection.cursor()

            
            # ==========================================
            # BITCOIN KPI CALCULATIONS
            # ==========================================
            btc_shannon_hosting = calculate_shannon_index(btc_hosting_concentration())
            btc_index_geo_diversity = normalize_geographical_diversity_index(btc_geo_index())
            btc_gini_exchange_concentration = calculate_gini(btc_exchange_concentration())
            btc_gini_reference_client_concentration = calculate_gini(btc_reference_client_concentration())
            btc_fractional_owner_control = calculate_fractional_owner_index(btc_owner_control())
            btc_gini_improvement_protocol = calculate_gini(btc_improvement_protocol())
            btc_gini_hash_power = calculate_gini(btc_decision_making())

            
            cursor.execute("""
                INSERT INTO bitcoin_kpis (
                    hosting_concentration,
                    geographical_diversity,
                    exchange_concentration,
                    reference_client_contribution,
                    owner_control,
                    improvement_protocol,
                    decision_making
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                btc_shannon_hosting,
                btc_index_geo_diversity,
                btc_gini_exchange_concentration,
                btc_gini_reference_client_concentration,
                btc_fractional_owner_control,
                btc_gini_improvement_protocol,
                btc_gini_hash_power
            ))

            print("Bitcoin KPIs have been written to the MySQL database")


            # ==========================================
            # ETHEREUM KPI CALCULATIONS
            # ==========================================
            eth_shannon_hosting = calculate_shannon_index(eth_hosting_concentration())
            eth_index_geo_diversity = normalize_geographical_diversity_index(eth_geo_index())
            eth_gini_exchange_concentration = calculate_gini(eth_exchange_concentration())
            eth_gini_reference_client_concentration = calculate_gini(eth_reference_client_concentration())
            eth_fractional_owner_control = calculate_fractional_owner_index(eth_owner_control())
            eth_gini_improvement_protocol = calculate_gini(eth_improvement_protocol())
            eth_gini_stake_distribution = calculate_gini(eth_decision_making())


            cursor.execute("""
                INSERT INTO ethereum_kpis (
                    hosting_concentration,
                    geographical_diversity,
                    exchange_concentration,
                    reference_client_contribution,
                    owner_control,
                    improvement_protocol,
                    decision_making
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                eth_shannon_hosting,
                eth_index_geo_diversity,
                eth_gini_exchange_concentration,
                eth_gini_reference_client_concentration,
                eth_fractional_owner_control,
                eth_gini_improvement_protocol,
                eth_gini_stake_distribution
            ))

            print("Ethereum KPIs have been written to the MySQL database")


            # ==========================================
            # CARDANO KPI CALCULATIONS
            # ==========================================
            ada_geo_list, ada_hosting_list = ada_geo_hosting()
            ada_shannon_hosting = calculate_shannon_index(ada_hosting_list)
            ada_index_geo_diversity = normalize_geographical_diversity_index(ada_geo_list)
            ada_gini_exchange_concentration = calculate_gini(ada_exchange_concentration())
            ada_gini_reference_client_concentration = calculate_gini(ada_reference_client_concentration())
            ada_fractional_owner_control = calculate_fractional_owner_index(ada_owner_control())
            ada_gini_improvement_protocol = calculate_gini(ada_improvement_protocol())
            ada_gini_stake_distribution = calculate_gini(ada_decision_making())


            cursor.execute("""
                INSERT INTO cardano_kpis (
                    hosting_concentration,
                    geographical_diversity,
                    exchange_concentration,
                    reference_client_contribution,
                    owner_control,
                    improvement_protocol,
                    decision_making
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                ada_shannon_hosting,
                ada_index_geo_diversity,
                ada_gini_exchange_concentration,
                ada_gini_reference_client_concentration,
                ada_fractional_owner_control,
                ada_gini_improvement_protocol,
                ada_gini_stake_distribution
            ))

            print("Cardano KPIs have been written to the MySQL database")


            # ==========================================
            # SOLANA KPI CALCULATIONS
            # ==========================================
            sol_shannon_hosting = calculate_shannon_index(sol_hosting_concentration())
            sol_index_geo_diversity = normalize_geographical_diversity_index(sol_geo_index())
            sol_gini_exchange_concentration = calculate_gini(sol_exchange_concentration())
            sol_gini_reference_client_concentration = calculate_gini(sol_reference_client_concentration())
            sol_fractional_owner_control = calculate_fractional_owner_index(sol_owner_control())
            sol_gini_improvement_protocol = calculate_gini(sol_improvement_protocol())
            sol_gini_stake_distribution = calculate_gini(sol_decision_making())


            cursor.execute("""
                INSERT INTO solana_kpis (
                    hosting_concentration,
                    geographical_diversity,
                    exchange_concentration,
                    reference_client_contribution,
                    owner_control,
                    improvement_protocol,
                    decision_making
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                sol_shannon_hosting,
                sol_index_geo_diversity,
                sol_gini_exchange_concentration,
                sol_gini_reference_client_concentration,
                sol_fractional_owner_control,
                sol_gini_improvement_protocol,
                sol_gini_stake_distribution
            ))

            print("Solana KPIs have been written to the MySQL database")


            # ==========================================
            # AVALANCHE KPI CALCULATIONS
            # ==========================================
            ava_geo_list, ava_hosting_list = ava_geo_diversity_hosting_concentration()
            ava_shannon_hosting = calculate_shannon_index(ava_hosting_list)
            ava_index_geo_diversity = normalize_geographical_diversity_index(ava_geo_list)
            ava_gini_exchange_concentration = calculate_gini(ava_exchange_concentration())
            ava_gini_reference_client_concentration = calculate_gini(ava_reference_client_concentration())
            ava_fractional_owner_control = calculate_fractional_owner_index(ava_owner_control())
            ava_gini_improvement_protocol = calculate_gini(ava_improvement_protocol())
            ava_stake_distribution = calculate_gini(ava_decision_making())


            cursor.execute("""
                INSERT INTO avalanche_kpis (
                    hosting_concentration,
                    geographical_diversity,
                    exchange_concentration,
                    reference_client_contribution,
                    owner_control,
                    improvement_protocol,
                    decision_making
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                ava_shannon_hosting,
                ava_index_geo_diversity,
                ava_gini_exchange_concentration,
                ava_gini_reference_client_concentration,
                ava_fractional_owner_control,
                ava_gini_improvement_protocol,
                ava_stake_distribution
            ))

            print("Avalanche KPIs have been written to the MySQL database")


            connection.commit()
            print("All data has been written to the MySQL database successfully. The program will now sleep for 18 hours.")            
            socketio.emit('update_notification', {'data': 'New data added to the database'})

            time.sleep(64800)

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
