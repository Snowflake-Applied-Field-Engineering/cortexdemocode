"""
Cortex Guard - AI Security Guardrails
Protects LLM applications from prompt injection, jailbreaks, and other threats
"""

import re
import yaml
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ThreatType(Enum):
    SAFE = "safe"
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    PII = "pii"
    TOXICITY = "toxicity"
    CUSTOM_RULE = "custom_rule"


class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GuardResult:
    """Result of a Cortex Guard check"""
    is_safe: bool
    threat_type: ThreatType
    severity: Severity
    confidence: float
    message: str
    details: Optional[Dict] = None


class CortexGuard:
    """Main Cortex Guard class for protecting LLM applications"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize Cortex Guard with configuration"""
        self.config = self._load_config(config_path)
        self._init_patterns()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Return default config if file not found
            return {
                'thresholds': {
                    'prompt_injection': 0.7,
                    'jailbreak': 0.8,
                    'pii': 0.6,
                    'toxicity': 0.75
                },
                'checks': {
                    'prompt_injection': True,
                    'jailbreak': True,
                    'pii_detection': True,
                    'toxicity': True,
                    'custom_rules': True
                }
            }
    
    def _init_patterns(self):
        """Initialize detection patterns"""
        # Prompt injection patterns
        self.injection_patterns = [
            r"ignore (all )?previous (instructions|prompts|commands)",
            r"disregard (all )?(previous|above|prior) (instructions|prompts)",
            r"forget (all )?(previous|above|prior) (instructions|prompts)",
            r"new (instructions|prompt|task):",
            r"system:?\s*(override|reset|clear)",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]
        
        # Jailbreak patterns
        self.jailbreak_patterns = [
            r"you are now (in )?(DAN|developer|god) mode",
            r"pretend (you are|to be) (evil|unethical|harmful)",
            r"act as if you (have no|don't have) (restrictions|limitations|rules)",
            r"bypass (your|all) (safety|ethical) (guidelines|rules|filters)",
            r"from now on,? you (will|must|should) (ignore|disregard)",
        ]
        
        # PII patterns
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        }
        
        # Toxic content patterns
        self.toxic_patterns = [
            r'\b(kill|murder|harm|hurt|attack)\s+(yourself|myself|themselves)',
            r'\b(hate|despise|detest)\s+(you|them|everyone)',
            r'\b(stupid|idiot|moron|dumb)\b',
        ]
    
    def check(self, text: str) -> GuardResult:
        """
        Main check method - analyzes text for security threats
        
        Args:
            text: User input to analyze
            
        Returns:
            GuardResult with safety assessment
        """
        text_lower = text.lower()
        
        # Check prompt injection
        if self.config['checks'].get('prompt_injection', True):
            result = self._check_prompt_injection(text_lower)
            if not result.is_safe:
                return result
        
        # Check jailbreak attempts
        if self.config['checks'].get('jailbreak', True):
            result = self._check_jailbreak(text_lower)
            if not result.is_safe:
                return result
        
        # Check PII
        if self.config['checks'].get('pii_detection', True):
            result = self._check_pii(text)
            if not result.is_safe:
                return result
        
        # Check toxicity
        if self.config['checks'].get('toxicity', True):
            result = self._check_toxicity(text_lower)
            if not result.is_safe:
                return result
        
        # Check custom rules
        if self.config['checks'].get('custom_rules', True):
            result = self._check_custom_rules(text_lower)
            if not result.is_safe:
                return result
        
        # All checks passed
        return GuardResult(
            is_safe=True,
            threat_type=ThreatType.SAFE,
            severity=Severity.LOW,
            confidence=1.0,
            message="Input passed all security checks"
        )
    
    def _check_prompt_injection(self, text: str) -> GuardResult:
        """Check for prompt injection attempts"""
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardResult(
                    is_safe=False,
                    threat_type=ThreatType.PROMPT_INJECTION,
                    severity=Severity.HIGH,
                    confidence=0.9,
                    message="Potential prompt injection detected",
                    details={'pattern': pattern}
                )
        return GuardResult(True, ThreatType.SAFE, Severity.LOW, 1.0, "OK")
    
    def _check_jailbreak(self, text: str) -> GuardResult:
        """Check for jailbreak attempts"""
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardResult(
                    is_safe=False,
                    threat_type=ThreatType.JAILBREAK,
                    severity=Severity.CRITICAL,
                    confidence=0.95,
                    message="Jailbreak attempt detected",
                    details={'pattern': pattern}
                )
        return GuardResult(True, ThreatType.SAFE, Severity.LOW, 1.0, "OK")
    
    def _check_pii(self, text: str) -> GuardResult:
        """Check for personally identifiable information"""
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                return GuardResult(
                    is_safe=False,
                    threat_type=ThreatType.PII,
                    severity=Severity.HIGH,
                    confidence=0.85,
                    message=f"PII detected: {pii_type}",
                    details={'pii_type': pii_type, 'count': len(matches)}
                )
        return GuardResult(True, ThreatType.SAFE, Severity.LOW, 1.0, "OK")
    
    def _check_toxicity(self, text: str) -> GuardResult:
        """Check for toxic content"""
        for pattern in self.toxic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardResult(
                    is_safe=False,
                    threat_type=ThreatType.TOXICITY,
                    severity=Severity.MEDIUM,
                    confidence=0.75,
                    message="Toxic content detected",
                    details={'pattern': pattern}
                )
        return GuardResult(True, ThreatType.SAFE, Severity.LOW, 1.0, "OK")
    
    def _check_custom_rules(self, text: str) -> GuardResult:
        """Check custom rules from config"""
        custom_rules = self.config.get('custom_rules', [])
        for rule in custom_rules:
            pattern = rule.get('pattern', '')
            if re.search(pattern, text, re.IGNORECASE):
                return GuardResult(
                    is_safe=False,
                    threat_type=ThreatType.CUSTOM_RULE,
                    severity=Severity[rule.get('severity', 'MEDIUM').upper()],
                    confidence=0.8,
                    message=f"Custom rule violated: {rule.get('threat_type', 'unknown')}",
                    details={'rule': rule}
                )
        return GuardResult(True, ThreatType.SAFE, Severity.LOW, 1.0, "OK")
    
    def batch_check(self, texts: List[str]) -> List[GuardResult]:
        """Check multiple texts at once"""
        return [self.check(text) for text in texts]

