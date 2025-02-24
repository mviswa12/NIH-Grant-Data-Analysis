# category_handler.py

import pandas as pd
from datetime import datetime

class CategoryHandler:
    def __init__(self, categories_config):
        """Initialize with category configuration"""
        self.config = categories_config
        self.validate_config()
        
    def validate_config(self):
        """Validate category configuration structure"""
        required_sections = ['Research_Areas', 'Award_Size', 'Technology_Platform', 'Study_Design']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required section: {section}")
        
        # Validate Research Areas
        for area, details in self.config['Research_Areas'].items():
            if not isinstance(details, dict):
                raise ValueError(f"Invalid structure for area: {area}")
            if 'keywords' not in details:
                raise ValueError(f"Missing 'keywords' in {area}")
            if 'subtypes' not in details:
                raise ValueError(f"Missing 'subtypes' in {area}")
            if not isinstance(details['keywords'], list):
                raise ValueError(f"'keywords' must be a list in {area}")
            if not isinstance(details['subtypes'], dict):
                raise ValueError(f"'subtypes' must be a dictionary in {area}")
    
    def get_all_category_columns(self):
        """Get all possible category column names"""
        columns = []
        
        # Main research areas
        for area in self.config['Research_Areas'].keys():
            columns.append(f"is_{area}")
            # Subtypes
            for subtype in self.config['Research_Areas'][area]['subtypes'].keys():
                columns.append(f"is_{area}_{subtype}")
        
        # Technology platforms
        for platform in self.config['Technology_Platform'].keys():
            columns.append(f"uses_{platform}")
            
        # Study designs
        for design_type, subtypes in self.config['Study_Design'].items():
            for subtype in subtypes.keys():
                columns.append(f"study_design_{design_type}_{subtype}")
                
        return columns
    
    def get_award_size_category(self, amount):
        """Determine award size category for any amount"""
        if pd.isna(amount):
            return 'Unknown'
            
        for category, limits in self.config['Award_Size'].items():
            if 'max_amount' in limits and amount <= limits['max_amount']:
                return category
            elif 'min_amount' in limits and amount > limits['min_amount']:
                return category
        
        return 'Large'  # Default for amounts above all thresholds
    
    def get_keywords_for_area(self, area):
        """Get all keywords for a research area"""
        if area not in self.config['Research_Areas']:
            raise ValueError(f"Unknown research area: {area}")
            
        keywords = self.config['Research_Areas'][area]['keywords'].copy()
        
        # Add subtype keywords
        for subtype_keywords in self.config['Research_Areas'][area]['subtypes'].values():
            keywords.extend(subtype_keywords)
            
        return list(set(keywords))  # Remove duplicates
    
    def clean_category_name(self, name):
        """Clean category names for display"""
        return name.replace('is_', '').replace('uses_', '').replace('study_design_', '').replace('_', ' ').title()
    
    def get_category_structure(self):
        """Get complete category structure for reporting"""
        structure = {
            'Research_Areas': {
                area: {
                    'keyword_count': len(details['keywords']),
                    'subtypes': list(details['subtypes'].keys())
                }
                for area, details in self.config['Research_Areas'].items()
            },
            'Technology_Platforms': list(self.config['Technology_Platform'].keys()),
            'Study_Designs': {
                design: list(subtypes.keys())
                for design, subtypes in self.config['Study_Design'].items()
            },
            'Award_Sizes': list(self.config['Award_Size'].keys())
        }
        return structure
    
    def check_text_for_category(self, text, area_name, include_subtypes=True):
        """Check if text matches any keywords for a given category"""
        if area_name not in self.config['Research_Areas']:
            raise ValueError(f"Unknown research area: {area_name}")
            
        area = self.config['Research_Areas'][area_name]
        text = str(text).lower()
        
        # Check main keywords
        if any(kw in text for kw in area['keywords']):
            return True
            
        # Check subtype keywords if requested
        if include_subtypes:
            for subtype_keywords in area['subtypes'].values():
                if any(kw in text for kw in subtype_keywords):
                    return True
                    
        return False
    
    def get_matching_categories(self, text):
        """Get all categories that match given text"""
        matches = []
        text = str(text).lower()
        
        # Check research areas
        for area in self.config['Research_Areas'].keys():
            if self.check_text_for_category(text, area):
                matches.append(area)
                
        return matches