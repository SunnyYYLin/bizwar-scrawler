from bs4 import BeautifulSoup
from .const import PARTS, SUBMIT_VALUES
import numpy as np
import pandas as pd
import re

class InfoParser:
    def __init__(self, soups: BeautifulSoup):
        self.soups = soups
        
    def parse(self) -> pd.DataFrame|None:
        for table in self.soups.find_all('table'):
            info = self.parse_info(table)
            match len(info):
                case 0:
                    continue
                case 1:
                    return info[0]
                case _:
                    merged_info = pd.concat(info, axis=1).loc[:, ~pd.concat(info, axis=1).columns.duplicated()]
                    return merged_info
        return None
    
    def parse_info(self, table) -> pd.DataFrame:
        trs = table.find_all('tr')
        header = trs[0]
        rows = trs[1:]
        columns = [cell.get_text(strip=True) for cell in header.find_all("td")]
        
        # Iterate over the rows to separate sections
        dataframes: list[pd.DataFrame] = []
        current_df_data = []
        for row in rows:
            cells = row.find_all('td')
            cell_text = [self.str2num(cell.get_text(strip=True)) for cell in cells]
            
            if columns[0] in cell_text:
                # When a header row is encountered (i.e., a new section starts)
                if current_df_data:  # if there's data collected, convert it to a DataFrame
                    df = pd.DataFrame(current_df_data, columns=columns)
                    dataframes.append(df)
                    current_df_data = []
                columns = cell_text  # Update headers for the new section
            elif cell_text and len(cell_text) == len(columns):
                # Ensure it's a row with the right number of cells
                current_df_data.append(cell_text)

        # Append the final DataFrame after the loop
        if current_df_data:
            df = pd.DataFrame(current_df_data, columns=columns)
            dataframes.append(df)
                
        return dataframes

    def parse_table(self, table: BeautifulSoup) -> np.ndarray:
        data: list[list[str]] = []
        max_col = 0
        trs = table.find_all('tr')
        for i, tr in enumerate(trs):
            data.append([])
            tds = tr.find_all('td')
            for j, td in enumerate(tds):
                data[i].append(td.text)
                max_col = max(max_col, j)

        for i in range(len(data)):
            if len(data[i]) < max_col:
                data[i] += [''] * (max_col - len(data[i]))
        
        return np.array(data)
    
    def input_parser(self, table: BeautifulSoup) -> dict[str, dict[str, ]]:
        inputs: dict[str, dict[str, ]] = {}
        pattern = re.compile(r'(.*?)\[(.*?)\]')
        for input_ in table.find_all('input'):
            topic_name = re.search(pattern, input_['name'])
            if topic_name:
                topic = topic_name.group(1)
                name = topic_name.group(2)
                if topic not in inputs:
                    inputs[topic] = {}
                value = self.str2num(input_['value'])
                inputs[topic][name] = value
        return inputs

    @staticmethod
    def str2num(s: str) -> int|float|str:
        s = s.strip().replace(',', '')
        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s