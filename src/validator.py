"""Input validation for SPU Processing Tool.

Validates CDD input data before processing to catch errors early
and provide clear, actionable error messages.
"""

import json
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pydantic import BaseModel, ValidationError, field_validator
from src.logger import get_logger


class ValidationResult(BaseModel):
    """Result of a validation check."""
    level: str  # 'error' or 'warning'
    sheet: str
    row: Optional[int] = None
    column: Optional[str] = None
    message: str

    def __str__(self):
        location = f"[{self.sheet}]"
        if self.row is not None:
            location += f" Row {self.row}"
        if self.column:
            location += f" Column '{self.column}'"
        return f"{location}: {self.message}"


class CDDValidator:
    """Validator for CDD input data."""

    REQUIRED_SHEETS = ["IP", "Radio 4G"]
    OPTIONAL_SHEETS = ["Radio 2G", "Radio 3G", "Radio 5G", "2G-2G", "2G-3G", "2G-4G",
                       "3G-2G", "3G-3G", "3G-4G", "RET", "Mapping"]

    IP_REQUIRED_COLUMNS = ["NE_Name", "eNBId", "OAM_IP", "OAM_Gateway", "LTE_IP", "LTE_Gateway"]
    IP_OPTIONAL_COLUMNS = ["gNBId", "NR_IP", "NR_Gateway", "MME", "AMF", "Baseband config"]

    RADIO_4G_REQUIRED_COLUMNS = ["NE_Name", "CellName", "cellId", "PCI", "TAC", "arfcndl",
                                  "dlChannelBandwidth", "RRU", "RRUname", "rruPort"]
    RADIO_4G_OPTIONAL_COLUMNS = ["arfcnul", "ulChannelBandwidth", "RSI", "cpSpeRefSigPwr",
                                  "MIMO", "CellType", "RiPort Baseband", "RiPort RRU", "Relation 5G"]

    RADIO_5G_REQUIRED_COLUMNS = ["NE_Name", "nRCell", "gNBId", "cellLocalId", "nRPCI", "nRTAC",
                                  "arfcnDL", "bSChannelBwDL", "RRU", "RRUname", "rruPort"]

    def __init__(self, data: Dict[str, pd.DataFrame], config_path: str):
        """Initialize validator.

        Args:
            data: Dictionary of sheet name to DataFrame
            config_path: Path to config.json
        """
        self.data = data
        self.config = self._load_config(config_path)
        self.errors: List[ValidationResult] = []
        self.warnings: List[ValidationResult] = []

    def _load_config(self, config_path: str) -> dict:
        """Load configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.errors.append(ValidationResult(
                level='error',
                sheet='config',
                message=f"Failed to load config.json: {e}"
            ))
            return {}

    def validate(self) -> Tuple[List[str], List[str]]:
        """Run all validations.

        Returns:
            Tuple of (errors, warnings) as lists of strings
        """
        logger = get_logger()
        logger.info("Starting CDD validation")

        # Clear previous results
        self.errors = []
        self.warnings = []

        # Run validations
        self._validate_required_sheets()
        self._validate_ip_sheet()
        self._validate_radio_4g_sheet()
        self._validate_radio_5g_sheet()
        self._validate_mapping_sheet()
        self._validate_config_references()

        # Convert to strings
        errors = [str(e) for e in self.errors]
        warnings = [str(w) for w in self.warnings]

        logger.info(f"Validation complete: {len(errors)} errors, {len(warnings)} warnings")

        return errors, warnings

    def _validate_required_sheets(self):
        """Check that required sheets exist and are not empty."""
        for sheet_name in self.REQUIRED_SHEETS:
            if sheet_name not in self.data:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet=sheet_name,
                    message=f"Required sheet '{sheet_name}' is missing"
                ))
            elif self.data[sheet_name].empty:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet=sheet_name,
                    message=f"Required sheet '{sheet_name}' is empty"
                ))

        # Check optional sheets
        for sheet_name in self.OPTIONAL_SHEETS:
            if sheet_name not in self.data or self.data[sheet_name].empty:
                self.warnings.append(ValidationResult(
                    level='warning',
                    sheet=sheet_name,
                    message=f"Optional sheet '{sheet_name}' is missing or empty"
                ))

    def _validate_ip_sheet(self):
        """Validate IP sheet data."""
        if "IP" not in self.data or self.data["IP"].empty:
            return

        df = self.data["IP"]

        # Check required columns
        for col in self.IP_REQUIRED_COLUMNS:
            if col not in df.columns:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet='IP',
                    column=col,
                    message=f"Required column '{col}' is missing"
                ))

        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row number (1-indexed + header)

            # Check NE_Name format
            ne_name = str(row.get("NE_Name", ""))
            if ne_name and not self._is_valid_ne_name(ne_name):
                self.warnings.append(ValidationResult(
                    level='warning',
                    sheet='IP',
                    row=row_num,
                    column='NE_Name',
                    message=f"NE_Name '{ne_name}' doesn't match expected format (e.g., gCM00025Z, eBL00123Z)"
                ))

            # Check IP address format
            for ip_col in ["OAM_IP", "LTE_IP", "NR_IP"]:
                if ip_col in df.columns:
                    ip_value = str(row.get(ip_col, ""))
                    if ip_value and ip_value != "nan" and not self._is_valid_ip(ip_value):
                        self.errors.append(ValidationResult(
                            level='error',
                            sheet='IP',
                            row=row_num,
                            column=ip_col,
                            message=f"Invalid IP address: '{ip_value}'"
                        ))

            # Check eNBId is numeric
            enb_id = row.get("eNBId", "")
            if pd.notna(enb_id):
                try:
                    int(float(enb_id))
                except (ValueError, TypeError):
                    self.errors.append(ValidationResult(
                        level='error',
                        sheet='IP',
                        row=row_num,
                        column='eNBId',
                        message=f"eNBId '{enb_id}' must be numeric"
                    ))

            # Check MME references
            mme_str = str(row.get("MME", ""))
            if mme_str and mme_str != "nan":
                mme_names = mme_str.split()
                mme_config = self.config.get("mme", {})
                for mme_name in mme_names:
                    if mme_name not in mme_config:
                        self.warnings.append(ValidationResult(
                            level='warning',
                            sheet='IP',
                            row=row_num,
                            column='MME',
                            message=f"MME '{mme_name}' not found in config.json"
                        ))

            # Check AMF references
            amf_str = str(row.get("AMF", ""))
            if amf_str and amf_str != "nan":
                amf_names = amf_str.split()
                amf_config = self.config.get("amf", {})
                for amf_name in amf_names:
                    if amf_name not in amf_config:
                        self.warnings.append(ValidationResult(
                            level='warning',
                            sheet='IP',
                            row=row_num,
                            column='AMF',
                            message=f"AMF '{amf_name}' not found in config.json"
                        ))

    def _validate_radio_4g_sheet(self):
        """Validate Radio 4G sheet data."""
        if "Radio 4G" not in self.data or self.data["Radio 4G"].empty:
            return

        df = self.data["Radio 4G"]

        # Check required columns
        for col in self.RADIO_4G_REQUIRED_COLUMNS:
            if col not in df.columns:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet='Radio 4G',
                    column=col,
                    message=f"Required column '{col}' is missing"
                ))

        # Get config mappings
        spu_config = self.config.get("SPU", {}).get("V1.70.26", {})
        bandwidth_mapping = spu_config.get("bandwidth_mapping", {})
        band_indicator_mapping = spu_config.get("bandIndicator_mapping", {})
        hw_mapping = spu_config.get("hwWorkScence_mapping", {})

        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2

            # Check NE_Name exists in IP sheet
            ne_name = str(row.get("NE_Name", ""))
            if ne_name and "IP" in self.data:
                ip_df = self.data["IP"]
                if "NE_Name" in ip_df.columns:
                    if ne_name not in ip_df["NE_Name"].values:
                        self.errors.append(ValidationResult(
                            level='error',
                            sheet='Radio 4G',
                            row=row_num,
                            column='NE_Name',
                            message=f"NE_Name '{ne_name}' not found in IP sheet"
                        ))

            # Check PCI range (0-503)
            pci = row.get("PCI", "")
            if pd.notna(pci):
                try:
                    pci_int = int(float(pci))
                    if pci_int < 0 or pci_int > 503:
                        self.errors.append(ValidationResult(
                            level='error',
                            sheet='Radio 4G',
                            row=row_num,
                            column='PCI',
                            message=f"PCI {pci_int} is out of range (0-503)"
                        ))
                except (ValueError, TypeError):
                    self.errors.append(ValidationResult(
                        level='error',
                        sheet='Radio 4G',
                        row=row_num,
                        column='PCI',
                        message=f"PCI '{pci}' must be numeric"
                    ))

            # Check arfcndl exists in config
            arfcn_dl = row.get("arfcndl", "")
            if pd.notna(arfcn_dl):
                arfcn_str = str(int(float(arfcn_dl)))
                if arfcn_str not in band_indicator_mapping:
                    self.warnings.append(ValidationResult(
                        level='warning',
                        sheet='Radio 4G',
                        row=row_num,
                        column='arfcndl',
                        message=f"EARFCN {arfcn_str} not found in bandIndicator_mapping"
                    ))

            # Check RRUname exists in config
            rru_name = str(row.get("RRUname", ""))
            if rru_name and rru_name != "nan":
                if rru_name not in hw_mapping:
                    self.warnings.append(ValidationResult(
                        level='warning',
                        sheet='Radio 4G',
                        row=row_num,
                        column='RRUname',
                        message=f"RRU type '{rru_name}' not found in hwWorkScence_mapping"
                    ))

            # Check bandwidth
            dl_bw = row.get("dlChannelBandwidth", "")
            if pd.notna(dl_bw):
                bw_str = str(float(dl_bw))
                if bw_str not in bandwidth_mapping:
                    self.warnings.append(ValidationResult(
                        level='warning',
                        sheet='Radio 4G',
                        row=row_num,
                        column='dlChannelBandwidth',
                        message=f"Bandwidth {bw_str} not found in bandwidth_mapping"
                    ))

    def _validate_radio_5g_sheet(self):
        """Validate Radio 5G sheet data."""
        if "Radio 5G" not in self.data or self.data["Radio 5G"].empty:
            return

        df = self.data["Radio 5G"]

        # Check required columns
        for col in self.RADIO_5G_REQUIRED_COLUMNS:
            if col not in df.columns:
                self.warnings.append(ValidationResult(
                    level='warning',
                    sheet='Radio 5G',
                    column=col,
                    message=f"Expected column '{col}' is missing"
                ))

        # Validate each row
        for idx, row in df.iterrows():
            row_num = idx + 2

            # Check NE_Name exists in IP sheet
            ne_name = str(row.get("NE_Name", ""))
            if ne_name and "IP" in self.data:
                ip_df = self.data["IP"]
                if "NE_Name" in ip_df.columns:
                    if ne_name not in ip_df["NE_Name"].values:
                        self.errors.append(ValidationResult(
                            level='error',
                            sheet='Radio 5G',
                            row=row_num,
                            column='NE_Name',
                            message=f"NE_Name '{ne_name}' not found in IP sheet"
                        ))

            # Check nRPCI range (0-1007)
            nr_pci = row.get("nRPCI", "")
            if pd.notna(nr_pci):
                try:
                    pci_int = int(float(nr_pci))
                    if pci_int < 0 or pci_int > 1007:
                        self.errors.append(ValidationResult(
                            level='error',
                            sheet='Radio 5G',
                            row=row_num,
                            column='nRPCI',
                            message=f"nRPCI {pci_int} is out of range (0-1007)"
                        ))
                except (ValueError, TypeError):
                    self.errors.append(ValidationResult(
                        level='error',
                        sheet='Radio 5G',
                        row=row_num,
                        column='nRPCI',
                        message=f"nRPCI '{nr_pci}' must be numeric"
                    ))

    def _validate_mapping_sheet(self):
        """Validate Mapping sheet."""
        if "Mapping" not in self.data or self.data["Mapping"].empty:
            self.warnings.append(ValidationResult(
                level='warning',
                sheet='Mapping',
                message="Mapping sheet is missing or empty. Using default mappings."
            ))
            return

        df = self.data["Mapping"]
        required_cols = ["Version", "Sheet", "Column"]

        for col in required_cols:
            if col not in df.columns:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet='Mapping',
                    column=col,
                    message=f"Required column '{col}' is missing from Mapping sheet"
                ))

    def _validate_config_references(self):
        """Validate that config.json has required sections."""
        required_sections = ["mcc", "mnc", "province", "mme", "SPU"]

        for section in required_sections:
            if section not in self.config:
                self.errors.append(ValidationResult(
                    level='error',
                    sheet='config.json',
                    message=f"Required section '{section}' is missing from config.json"
                ))

        # Check SPU version
        spu = self.config.get("SPU", {})
        if "V1.70.26" not in spu:
            self.warnings.append(ValidationResult(
                level='warning',
                sheet='config.json',
                message="SPU version V1.70.26 not found. Available versions: " +
                        ", ".join(spu.keys())
            ))

    def _is_valid_ne_name(self, ne_name: str) -> bool:
        """Check if NE_Name matches expected format (e.g., gCM00025Z, eBL00123Z)."""
        import re
        # Pattern: starts with g or e, followed by 2 uppercase letters,
        # followed by digits, optionally ending with a letter
        pattern = r'^[ge][A-Z]{2}\d+[A-Z]?$'
        return bool(re.match(pattern, ne_name))

    def _is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid."""
        import re
        # Simple IPv4 pattern
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        # Check each octet is 0-255
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
