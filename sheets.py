"""Google Sheets integration for reading and writing DSA problems."""

import random
from typing import List, Optional, Set

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config
from models import Problem


class SheetsService:
    """Service for interacting with Google Sheets."""
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        """Initialize Google Sheets service."""
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_CREDENTIALS_FILE,
            scopes=self.SCOPES
        )
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet_id = Config.GOOGLE_SHEETS_ID
        self.range_name = Config.GOOGLE_SHEETS_RANGE
    
    def get_all_problems(self) -> List[Problem]:
        """Fetch all problems from Google Sheets."""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            problems = []
            
            for row in values:
                # Ensure row has at least 5 columns (id, title, difficulty, topic, url)
                if len(row) >= 5:
                    problems.append(Problem(
                        id=row[0].strip() if row[0] else "",
                        title=row[1].strip() if row[1] else "",
                        difficulty=row[2].strip().lower() if row[2] else "",
                        topic=row[3].strip() if row[3] else "",
                        url=row[4].strip() if row[4] else ""
                    ))
            
            return problems
        except HttpError as error:
            raise Exception(f"Error fetching problems from Google Sheets: {error}")
    
    def get_random_problem(self, difficulty: Optional[str] = None, exclude_ids: Optional[Set[str]] = None) -> Optional[Problem]:
        """Get a random problem, optionally filtered by difficulty and excluding certain IDs.
        
        Args:
            difficulty: Optional difficulty filter ('easy', 'medium', 'hard')
            exclude_ids: Set of problem IDs to exclude from selection
        """
        problems = self.get_all_problems()
        
        if not problems:
            return None
        
        # Filter out excluded problems
        if exclude_ids:
            problems = [p for p in problems if p.id not in exclude_ids]
        
        if not problems:
            return None
        
        # Filter by difficulty if specified
        if difficulty:
            difficulty = difficulty.lower()
            filtered = [p for p in problems if p.difficulty == difficulty]
            if filtered:
                return random.choice(filtered)
            # If no problems found for difficulty, return random from all (excluding excluded)
            if problems:
                return random.choice(problems)
            return None
        
        return random.choice(problems)
    
    def add_problem(self, problem: Problem) -> bool:
        """Add a new problem to Google Sheets."""
        try:
            # Get the next available row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=self.range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 2  # +2 because range starts at row 2 (skip header)
            
            # Prepare the row data
            row_data = [
                problem.id,
                problem.title,
                problem.difficulty,
                problem.topic,
                problem.url
            ]
            
            # Append the row
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheet_id,
                range=f'Sheet1!A{next_row}:E{next_row}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except HttpError as error:
            raise Exception(f"Error adding problem to Google Sheets: {error}")
