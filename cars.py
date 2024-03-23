import pandas as pd

# Load the CSV file
file_path = '/mnt/data/filtered_sorted_co2_emissions.csv'
data = pd.read_csv(file_path)

# Constants
CO2_OFFSET_PER_TREE_PER_YEAR = 48  # in pounds
GRAMS_PER_POUND = 454

# Function to calculate emissions and trees required for offset
def calculate_emissions_and_trees(car_name, miles):
    # Find the car in the dataset
    car_data = data[data['Car Name'].str.lower() == car_name.lower()]
    
    if car_data.empty:
        print("Car not found in the dataset.")
        return
    
    # Get CO2 emissions per mile for the car
    co2_per_mile = car_data.iloc[0]['Co2 Fuel Type1']
    
    # Calculate total emissions for the entered miles
    total_emissions_grams = co2_per_mile * miles
    total_emissions_pounds = total_emissions_grams / GRAMS_PER_POUND
    
    # Calculate the number of trees needed to offset the total emissions
    trees_required = total_emissions_pounds / CO2_OFFSET_PER_TREE_PER_YEAR
    trees_required_rounded_up = int(trees_required) if trees_required.is_integer() else int(trees_required) + 1  # Round up to the nearest whole number
    
    print(f"Total estimated CO2 emissions for driving {miles} miles in a {car_name}: {total_emissions_grams} grams.")
    print(f"To offset these emissions, you would need to plant approximately {trees_required_rounded_up} tree(s).")

# User input
car_name = input("Enter the name of the car you're driving: ")
miles = float(input("How many miles do you plan on driving? "))

# Calculate and display the emissions and trees required
calculate_emissions_and_trees(car_name, miles)
