import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

def split_tables(lines):
    tables = []
    current_table = []

    for line in lines:
        # Split lines with commas.
        elements = line.strip().split(',')
        # Check whether all elements are empty.
        if all(e.strip() == '' for e in elements):
            if current_table:  # Add if the current table is not empty.
                tables.append(current_table)
                current_table = []
        else:
            current_table.append(elements)

    # Add last table if there is no blank line at the end of the file.
    if current_table:
        tables.append(current_table)

    return tables

def extract_matching_tables(tables, extract_columns):
    matching_tables = []
    
    for table in tables:
        for column in zip(*table):
            column = list(column)
            if column[0] == extract_columns:
                matching_tables.append(column[1:])
    return matching_tables

def extract_spectre(file_path, extract_columns):
    # load csv file
    with open(file_path, 'r', encoding='shift_jis') as file:
        lines = file.readlines()

    # Split by table with blank rows.
    tables = split_tables(lines)

    # Extract data name list.
    data_name_list = tables[0][1][1:]

    # Extract specified columns.
    matching_tables = extract_matching_tables(tables, extract_columns)

    # Converted to numpy array.
    spectre_datas = np.array(matching_tables, dtype=float)
    np.set_printoptions(suppress=True)
    return data_name_list, spectre_datas

def main(args):
    dir_path = args.dir
    extract_columns = args.columns
    is_plot = not args.no_plot

    # Check file path
    check_csv_dir = glob(f'{dir_path}/csv')
    if not check_csv_dir:
        print('csv directory does not exist.')
        return
    
    # Get csv file path list
    csv_path_list = glob(f'{dir_path}/csv/*.csv')
    if not csv_path_list:
        print('csv file does not exist.')
        return
    
    # Create save directory
    npy_dir = f'{dir_path}/npy'
    spectre_dir = f'{dir_path}/spectre'
    os.makedirs(npy_dir, exist_ok=True)
    os.makedirs(spectre_dir, exist_ok=True)
    
    # Extract spectre data fron csv file
    for csv_path in csv_path_list:
        data_name_list, spectre_datas = extract_spectre(csv_path, extract_columns)

        # Extract file name from csv_path
        file_name = os.path.basename(csv_path)
        x = range(350,1001)
        for spectre_data, data_name in zip(spectre_datas, data_name_list):
            np.save(f'{npy_dir}/{file_name[:-4]}_{data_name}.npy', spectre_data)

            # Plot spectre data
            if is_plot:
                plt.figure(figsize=(10, 6))
                plt.plot(x, spectre_data, label=data_name)
                plt.legend()
                plt.grid()
                plt.xlabel('Wavelength (nm)')
                plt.ylabel('radiance')
                plt.title(f'{data_name}')
                plt.savefig(f'{spectre_dir}/{file_name[:-4]}_{data_name}.png')
                plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', type=str, default='./data', help='Path to the data directory')
    parser.add_argument('-c', '--columns', type=str, default='Le [W/(sr*sqm*nm)]', help='Columns to extract')
    parser.add_argument('-p', '--no-plot', action='store_true', help='Disable plotting of spectre data')
    args = parser.parse_args()
    main(args)