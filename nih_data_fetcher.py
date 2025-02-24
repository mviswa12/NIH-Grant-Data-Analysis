# nih_data_fetcher.py

import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from tqdm import tqdm

class NIHDataFetcher:
    def __init__(self, category_handler):
        """Initialize with category handler for dynamic category processing"""
        self.base_url = "https://api.reporter.nih.gov/v2"
        self.search_endpoint = f"{self.base_url}/projects/search"
        self.project_endpoint = f"{self.base_url}/projects"
        self.category_handler = category_handler
        
    def create_search_criteria(self, fiscal_years=None, keywords=None, org_names=None):
        """Create enhanced search criteria for the NIH RePORTER API"""
        criteria = {
            "criteria": {
                "fiscal_years": fiscal_years or [datetime.now().year - 1],
                "include_active_projects": True,
                "exclude_inherited_projects": False,
                "limit": 500,
                "offset": 0,
                "include_fields": [
                    "ActivityCode",
                    "ApplicationId",
                    "ProjectTitle",
                    "AbstractText",
                    "ProjectStartDate",
                    "ProjectEndDate",
                    "AwardAmount",
                    "Organization",
                    "FiscalYear",
                    "FundingOpportunityNumber",
                    "ClinicalTrialsRequired",
                    "ProgramOfficers",
                    "ProjectDetails",
                    "StudySection",
                    "DirectCostAmt",
                    "IndirectCostAmt",
                    "ContactPiName",
                    "AwardType",
                    "BudgetDates",
                    "ProjectTerms",
                    "ClinicalTrials",
                    "Keywords"
                ]
            }
        }
        
        if keywords:
            criteria["criteria"]["text_search_parameters"] = {
                "operator": "and",
                "search_fields": [{"field": "project_title"}, {"field": "abstract"}],
                "search_text": " ".join(keywords)
            }
            
        if org_names:
            criteria["criteria"]["organization_names"] = org_names
            
        return criteria

    def fetch_data(self, search_criteria, max_requests=10):
        """Fetch data from NIH RePORTER API with progress tracking"""
        all_projects = []
        offset = 0
        total_count = None
        
        for request_num in tqdm(range(max_requests), desc="Fetching data batches"):
            search_criteria["criteria"]["offset"] = offset
            
            try:
                response = requests.post(
                    self.search_endpoint,
                    json=search_criteria,
                    timeout=30
                )
                response.raise_for_status()
                
                data = response.json()
                
                if total_count is None:
                    total_count = data.get("meta", {}).get("total", 0)
                    print(f"\nTotal projects found: {total_count}")
                
                projects = data.get("results", [])
                all_projects.extend(projects)
                
                if len(all_projects) >= total_count:
                    break
                
                offset += len(projects)
                time.sleep(1)  # Respect API rate limits
                
            except requests.exceptions.RequestException as e:
                print(f"\nError fetching data: {str(e)}")
                break
        
        return all_projects

    def _calculate_project_duration(self, start_date, end_date):
        """Calculate project duration category using category handler"""
        if not start_date or not end_date:
            return 'Unknown'
        
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            duration_years = (end - start).days / 365
            
            return self.category_handler.get_duration_category(duration_years)
        except:
            return 'Unknown'

    def process_projects(self, projects):
        """Convert project data to DataFrame with dynamic category processing"""
        print("Processing project data...")
        processed_data = []
        
        for project in tqdm(projects, desc="Processing projects"):
            # Get organization details
            org_details = project.get('organization', {})
            if not org_details:
                org_details = project.get('org_details', {})
            
            # Calculate durations and categories
            duration_category = self._calculate_project_duration(
                project.get('project_start_date'),
                project.get('project_end_date')
            )
            
            award_size = self.category_handler.get_award_size_category(
                project.get('award_amount', 0)
            )
            
            processed_project = {
                # Basic identification
                'application_id': (
                    project.get('appl_id') or 
                    project.get('application_id') or 
                    project.get('project_id')
                ),
                
                # Project details
                'project_title': project.get('project_title', 'No Title'),
                'abstract_text': project.get('abstract_text', 'No Abstract'),
                'project_start_date': pd.to_datetime(
                    project.get('project_start_date')
                ).strftime('%Y-%m-%d') if project.get('project_start_date') else None,
                'project_end_date': pd.to_datetime(
                    project.get('project_end_date')
                ).strftime('%Y-%m-%d') if project.get('project_end_date') else None,
                'project_duration_category': duration_category,
                
                # Financial information
                'award_amount': project.get('award_amount', 0),
                'award_size_category': award_size,
                'direct_cost_amount': project.get('direct_cost_amt', 0),
                'indirect_cost_amount': project.get('indirect_cost_amt', 0),
                
                # Organization information
                'org_name': org_details.get('org_name', 'Unknown Organization'),
                'org_city': org_details.get('org_city', 'Unknown City'),
                'org_state': org_details.get('org_state', 'Unknown State'),
                'org_type': org_details.get('org_type', 'Unknown Type'),
                
                # Administrative details
                'fiscal_year': project.get('fiscal_year', datetime.now().year),
                'activity_code': project.get('activity_code', 'Unknown'),
                'funding_opportunity_number': (
                    project.get('funding_opportunity_number') or 
                    project.get('foa_details', {}).get('funding_opportunity_number') or 
                    'Not Available'
                ),
                
                # Additional metadata
                'clinical_trials_required': project.get('clinical_trials_required', False),
                'program_officers': ', '.join([
                    po.get('full_name', '') 
                    for po in project.get('program_officers', [])
                ]),
                'study_section': project.get('study_section', 'Not Available'),
                'keywords': ', '.join(project.get('keywords', [])),
                'project_terms': ', '.join(project.get('project_terms', []))
            }
            
            processed_data.append(processed_project)
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Apply data cleaning
        df = self._clean_data(df)
        
        return df

    def _clean_data(self, df):
        """Clean and validate the data"""
        # Fill missing values
        df['award_amount'] = df['award_amount'].fillna(0)
        df['direct_cost_amount'] = df['direct_cost_amount'].fillna(0)
        df['indirect_cost_amount'] = df['indirect_cost_amount'].fillna(0)
        
        # Convert dates to datetime
        date_columns = ['project_start_date', 'project_end_date']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean text fields
        text_columns = ['project_title', 'abstract_text', 'program_officers', 'study_section']
        for col in text_columns:
            df[col] = df[col].fillna('Not Available')
            df[col] = df[col].astype(str).str.strip()
        
        # Ensure numeric fields are correct type
        numeric_columns = ['award_amount', 'direct_cost_amount', 'indirect_cost_amount']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df

    def save_data(self, df, output_path):
        """Save the processed data with proper formatting"""
        try:
            print(f"Saving data to {output_path}")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Grant_Data', index=False)
                
                # Summary sheet
                summary_stats = pd.DataFrame({
                    'Metric': [
                        'Total Grants',
                        'Total Funding',
                        'Average Award',
                        'Median Award',
                        'Total Organizations',
                        'Unique Activity Codes'
                    ],
                    'Value': [
                        len(df),
                        f"${df['award_amount'].sum():,.2f}",
                        f"${df['award_amount'].mean():,.2f}",
                        f"${df['award_amount'].median():,.2f}",
                        df['org_name'].nunique(),
                        df['activity_code'].nunique()
                    ]
                })
                summary_stats.to_excel(writer, sheet_name='Summary', index=False)
                
            print("Data saved successfully!")
            
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            # Save as CSV as backup
            backup_path = output_path.replace('.xlsx', '.csv')
            df.to_csv(backup_path, index=False)
            print(f"Saved backup to: {backup_path}")