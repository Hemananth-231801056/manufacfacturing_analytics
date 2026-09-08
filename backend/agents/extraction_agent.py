"""
Extraction Agent
================
Agent 2 of 9 in the Agentic AI Pipeline.

Extracts structured tables or key-value parameters from raw text or DataFrames
into a standard list of row dictionaries. Includes an Ollama LLM fallback for 
complex unstructured text.
"""

import pandas as pd
import re
import httpx
import json

class ExtractionAgent:
    """Agent responsible for structured information extraction."""

    def __init__(self, ollama_url="http://localhost:11434/api/generate", model_name="llama3"):
        self.ollama_url = ollama_url
        self.model_name = model_name

    def extract(self, read_result: dict) -> list[dict]:
        """
        Extract structured rows from the raw file reader results.
        """
        if not read_result.get("success"):
            return []

        fmt = read_result["format"]
        content = read_result["raw_content"]

        if fmt in ["csv", "xlsx"]:
            if isinstance(content, pd.DataFrame):
                df = content.copy()
                df = df.where(pd.notnull(df), None)
                return df.to_dict(orient="records")
            return []

        elif fmt in ["pdf", "docx"]:
            text = str(content)
            batches = self._extract_from_text(text)
            
            # If regex extraction fails, fallback to Ollama LLM
            if not batches:
                batches = self._extract_via_ollama(text)
                
            return batches

        return []

    def _extract_from_text(self, text: str) -> list[dict]:
        """
        Extract structured variables from free-text using regular expressions.
        """
        batches = []
        
        # 1. Look for text table rows (e.g. "BATCH-001 | 25 | 1.5 ...")
        lines = text.split('\n')
        table_rows = []
        for line in lines:
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                # Relaxed from > 5 to >= 2 to support smaller tables
                if len(parts) >= 2:
                    table_rows.append(parts)
        
        if table_rows:
            header = [self._normalize_col_name(h) for h in table_rows[0]]
            if any(k in header for k in ['batch_id', 'code', 'api_water', 'purity']):
                for row in table_rows[1:]:
                    if len(row) == len(header):
                        batch_data = {}
                        for col, val in zip(header, row):
                            batch_data[col] = self._parse_val(val)
                        if 'batch_id' in batch_data or 'code' in batch_data:
                            batches.append(batch_data)
                if batches:
                    return batches

        # 2. Look for JSON-like or Key-Value patterns
        sections = re.split(r'(?i)batch\s*(?:id)?\s*[:#-]\s*(\w+)', text)
        if len(sections) > 1:
            for i in range(1, len(sections), 2):
                batch_id = sections[i]
                section_text = sections[i+1] if i+1 < len(sections) else ""
                batch_data = {"batch_id": batch_id}
                
                pairs = re.findall(r'([\w\s()-]+)\s*[:=]\s*([\d\w.,]+)', section_text)
                for key, val in pairs:
                    norm_key = self._normalize_col_name(key)
                    batch_data[norm_key] = self._parse_val(val)
                
                if len(batch_data) > 1:
                    batches.append(batch_data)
                    
            if batches:
                return batches

        # 3. Fallback: parse entire text for single batch key-values
        batch_data = {}
        pairs = re.findall(r'([\w\s()-]+)\s*[:=]\s*([\d\w.,]+)', text)
        for key, val in pairs:
            norm_key = self._normalize_col_name(key)
            batch_data[norm_key] = self._parse_val(val)
        if len(batch_data) > 1:
            if 'batch_id' not in batch_data:
                batch_data['batch_id'] = 'BATCH-EXTRACTED'
            batches.append(batch_data)

        return batches

    def _extract_via_ollama(self, text: str) -> list[dict]:
        """Use Ollama LLM to extract batch data from unstructured text."""
        prompt = f"""You are a Pharmaceutical Data Extraction AI.
Extract all manufacturing batch records from the following raw document text.
You MUST format your response as a valid JSON array of objects.
Map all extracted parameters to numerical values where possible.
Ensure 'batch_id' is included in each object.

Raw Text:
{text[:2000]}

Respond ONLY with raw JSON. Do not include markdown blocks.
Example format:
[
  {{"batch_id": "BATCH-01", "code": 15, "api_water": 1.2, "purity": 96.5}}
]
"""
        try:
            response = httpx.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                llm_text = data.get("response", "").strip()
                try:
                    extracted = json.loads(llm_text)
                    if isinstance(extracted, list):
                        # Normalize keys and values
                        cleaned = []
                        for b in extracted:
                            if isinstance(b, dict):
                                cb = {self._normalize_col_name(k): self._parse_val(str(v)) for k, v in b.items()}
                                if 'batch_id' not in cb:
                                    cb['batch_id'] = 'OLLAMA-EXTRACTED'
                                cleaned.append(cb)
                        return cleaned
                except json.JSONDecodeError:
                    print("[Extraction Agent] Ollama JSON parsing failed.")
        except Exception as e:
            print(f"[Extraction Agent] Ollama request failed: {e}")
            
        return []

    def _normalize_col_name(self, name: str) -> str:
        s = name.lower().strip()
        s = re.sub(r'[^a-z0-9_\s]', '', s)
        s = re.sub(r'\s+', '_', s)
        
        mappings = {
            'purity': 'api_content',
            'api_purity': 'api_content',
            'impurities': 'api_total_impurities',
            'api_impurities': 'api_total_impurities',
            'water': 'api_water',
            'moisture': 'api_water',
            'compression_force': 'main_compforce_mean',
            'hardness': 'tbl_av_hardness',
            'thickness': 'tbl_min_thickness',
            'fill_depth': 'tbl_fill_mean',
            'speed': 'tbl_speed_mean',
            'turret_speed': 'tbl_speed_mean',
            'yield': 'batch_yield',
            'waste': 'total_waste'
        }
        return mappings.get(s, s)

    def _parse_val(self, val: str):
        val = val.strip()
        if val.lower() in ['yes', 'true']:
            return 1
        if val.lower() in ['no', 'false']:
            return 0
        try:
            val_clean = val.replace(',', '.')
            if '.' in val_clean:
                return float(val_clean)
            return int(val_clean)
        except ValueError:
            return val
