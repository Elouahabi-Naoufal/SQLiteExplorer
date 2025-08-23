"""Data export/import utilities"""

import csv
import json
import os
from typing import List, Dict, Any, Optional
from .logger import Logger

class ExportManager:
    """Manages data export and import operations"""
    
    def __init__(self):
        self.logger = Logger()
    
    def export_to_csv(self, data: List[Dict[str, Any]], file_path: str, 
                     columns: Optional[List[str]] = None) -> bool:
        """Export data to CSV file"""
        try:
            if not data:
                self.logger.log("No data to export", "WARNING")
                return False
            
            # Use provided columns or extract from first record
            if not columns:
                columns = list(data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                
                for record in data:
                    # Filter record to only include specified columns
                    filtered_record = {col: record.get(col, '') for col in columns}
                    writer.writerow(filtered_record)
            
            self.logger.log(f"Data exported to CSV: {file_path} ({len(data)} records)")
            return True
            
        except Exception as e:
            self.logger.log(f"CSV export failed: {str(e)}", "ERROR")
            return False
    
    def export_to_json(self, data: List[Dict[str, Any]], file_path: str, 
                      pretty: bool = True) -> bool:
        """Export data to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                if pretty:
                    json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
                else:
                    json.dump(data, jsonfile, ensure_ascii=False, default=str)
            
            self.logger.log(f"Data exported to JSON: {file_path} ({len(data)} records)")
            return True
            
        except Exception as e:
            self.logger.log(f"JSON export failed: {str(e)}", "ERROR")
            return False
    
    def import_from_csv(self, file_path: str, column_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Import data from CSV file"""
        try:
            if not os.path.exists(file_path):
                self.logger.log(f"CSV file not found: {file_path}", "ERROR")
                return []
            
            data = []
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row in reader:
                    # Apply column mapping if provided
                    if column_mapping:
                        mapped_row = {}
                        for csv_col, db_col in column_mapping.items():
                            if csv_col in row:
                                mapped_row[db_col] = row[csv_col]
                        data.append(mapped_row)
                    else:
                        data.append(dict(row))
            
            self.logger.log(f"Data imported from CSV: {file_path} ({len(data)} records)")
            return data
            
        except Exception as e:
            self.logger.log(f"CSV import failed: {str(e)}", "ERROR")
            return []
    
    def import_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Import data from JSON file"""
        try:
            if not os.path.exists(file_path):
                self.logger.log(f"JSON file not found: {file_path}", "ERROR")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)
            
            # Ensure data is a list of dictionaries
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                self.logger.log("Invalid JSON format: expected list or object", "ERROR")
                return []
            
            self.logger.log(f"Data imported from JSON: {file_path} ({len(data)} records)")
            return data
            
        except Exception as e:
            self.logger.log(f"JSON import failed: {str(e)}", "ERROR")
            return []
    
    def export_table_structure(self, table_schema: List[Dict[str, Any]], file_path: str) -> bool:
        """Export table structure to JSON"""
        try:
            structure = {
                'table_schema': table_schema,
                'export_timestamp': self.logger.get_timestamp()
            }
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(structure, jsonfile, indent=2, ensure_ascii=False)
            
            self.logger.log(f"Table structure exported: {file_path}")
            return True
            
        except Exception as e:
            self.logger.log(f"Structure export failed: {str(e)}", "ERROR")
            return False
    
    def get_csv_preview(self, file_path: str, max_rows: int = 10) -> tuple[List[str], List[Dict[str, Any]]]:
        """Get preview of CSV file"""
        try:
            if not os.path.exists(file_path):
                return [], []
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                columns = reader.fieldnames or []
                data = []
                
                for i, row in enumerate(reader):
                    if i >= max_rows:
                        break
                    data.append(dict(row))
            
            return columns, data
            
        except Exception as e:
            self.logger.log(f"CSV preview failed: {str(e)}", "ERROR")
            return [], []
    
    def validate_import_data(self, data: List[Dict[str, Any]], 
                           table_schema: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """Validate imported data against table schema"""
        errors = []
        
        if not data:
            errors.append("No data to validate")
            return False, errors
        
        # Get required columns
        required_columns = [col['name'] for col in table_schema if col['notnull'] and not col['pk']]
        available_columns = list(data[0].keys())
        
        # Check for missing required columns
        missing_columns = set(required_columns) - set(available_columns)
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Validate data types (basic validation)
        for i, record in enumerate(data[:100]):  # Check first 100 records
            for column in table_schema:
                col_name = column['name']
                if col_name not in record:
                    continue
                
                value = record[col_name]
                if value is None or value == '':
                    continue
                
                col_type = column['type'].upper()
                
                try:
                    if 'INT' in col_type:
                        int(value)
                    elif 'REAL' in col_type or 'FLOAT' in col_type:
                        float(value)
                    elif 'BOOL' in col_type:
                        if str(value).lower() not in ['0', '1', 'true', 'false', 'yes', 'no']:
                            errors.append(f"Row {i+1}: Invalid boolean value for {col_name}: {value}")
                except ValueError:
                    errors.append(f"Row {i+1}: Invalid {col_type} value for {col_name}: {value}")
        
        return len(errors) == 0, errors