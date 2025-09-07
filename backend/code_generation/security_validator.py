"""
Security Validator - テストを通すための最小実装（Green段階）
セキュリティリスク検知システム
"""

import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum

from .response_parser import CodeBlock


class RiskSeverity(Enum):
    """リスク重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityRisk:
    """セキュリティリスク情報"""
    risk_type: str
    severity: str
    description: str
    filename: str
    line: int = 0
    column: int = 0
    recommendation: str = ""
    
    def __post_init__(self):
        # severity文字列を正規化
        if isinstance(self.severity, RiskSeverity):
            self.severity = self.severity.value


class SecurityValidator:
    """
    セキュリティリスク検証システム
    """
    
    def __init__(self):
        # 危険なパターン定義
        self.dangerous_patterns = {
            "xss": {
                "patterns": [
                    r"dangerouslySetInnerHTML\s*=\s*\{\{\s*__html:",
                    r"innerHTML\s*=",
                    r"outerHTML\s*=",
                ],
                "severity": RiskSeverity.HIGH,
                "description": "Potential XSS vulnerability through unsafe HTML rendering"
            },
            "code_injection": {
                "patterns": [
                    r"\beval\s*\(",
                    r"\bnew\s+Function\s*\(",
                    r"setTimeout\s*\(\s*['\"]",
                    r"setInterval\s*\(\s*['\"]",
                ],
                "severity": RiskSeverity.CRITICAL,
                "description": "Code injection vulnerability through dynamic code execution"
            },
            "sql_injection": {
                "patterns": [
                    r"SELECT\s+.*\s+FROM\s+.*\$\{",
                    r"INSERT\s+INTO\s+.*\$\{",
                    r"UPDATE\s+.*\s+SET\s+.*\$\{",
                    r"DELETE\s+FROM\s+.*\$\{",
                    r"query\s*\(\s*`.*\$\{.*\}.*`",
                ],
                "severity": RiskSeverity.CRITICAL,
                "description": "SQL injection vulnerability through string interpolation in queries"
            },
            "path_traversal": {
                "patterns": [
                    r"\.\.\/",
                    r"\.\.\\\\",
                    r"path.*\+.*req\.",
                    r"fs\.readFile.*req\.",
                ],
                "severity": RiskSeverity.HIGH,
                "description": "Path traversal vulnerability"
            },
            "unsafe_redirect": {
                "patterns": [
                    r"window\.location\s*=\s*.*req\.",
                    r"location\.href\s*=\s*.*req\.",
                    r"redirect\s*\(\s*req\.",
                ],
                "severity": RiskSeverity.MEDIUM,
                "description": "Unsafe redirect using user input"
            }
        }
        
        # セキュアなパターン（除外対象）
        self.safe_patterns = [
            r"dangerouslySetInnerHTML.*DOMPurify\.sanitize",
            r"eval\s*\(\s*['\"]test['\"]",  # テストコード内
        ]
    
    def scan_security_risks(self, block: CodeBlock) -> List[SecurityRisk]:
        """
        セキュリティリスクスキャン
        
        Args:
            block: 検証対象コードブロック
            
        Returns:
            検出されたセキュリティリスクのリスト
        """
        risks = []
        
        # 各リスクタイプをチェック
        for risk_type, config in self.dangerous_patterns.items():
            detected_risks = self._detect_risk_pattern(block, risk_type, config)
            risks.extend(detected_risks)
        
        # 偽陽性除去
        risks = self._filter_false_positives(risks, block)
        
        return risks
    
    def _detect_risk_pattern(self, block: CodeBlock, risk_type: str, config: Dict[str, Any]) -> List[SecurityRisk]:
        """特定リスクパターンの検出"""
        risks = []
        lines = block.content.split('\n')
        
        for pattern in config["patterns"]:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            
            for i, line in enumerate(lines, 1):
                matches = regex.finditer(line)
                
                for match in matches:
                    risk = SecurityRisk(
                        risk_type=risk_type,
                        severity=config["severity"].value,
                        description=config["description"],
                        filename=block.filename,
                        line=i,
                        column=match.start(),
                        recommendation=self._get_recommendation(risk_type)
                    )
                    risks.append(risk)
        
        return risks
    
    def _filter_false_positives(self, risks: List[SecurityRisk], block: CodeBlock) -> List[SecurityRisk]:
        """偽陽性フィルタリング"""
        filtered_risks = []
        
        for risk in risks:
            is_false_positive = False
            
            # セーフパターンチェック
            for safe_pattern in self.safe_patterns:
                if re.search(safe_pattern, block.content, re.IGNORECASE):
                    is_false_positive = True
                    break
            
            # コメント内かチェック
            lines = block.content.split('\n')
            if risk.line <= len(lines):
                line = lines[risk.line - 1]
                if '//' in line:
                    comment_start = line.find('//')
                    if risk.column >= comment_start:
                        is_false_positive = True
            
            if not is_false_positive:
                filtered_risks.append(risk)
        
        return filtered_risks
    
    def _get_recommendation(self, risk_type: str) -> str:
        """リスクタイプに応じた推奨対策"""
        recommendations = {
            "xss": "Use React's default JSX rendering or sanitize HTML with DOMPurify before using dangerouslySetInnerHTML",
            "code_injection": "Avoid dynamic code execution. Use safer alternatives like JSON parsing or predefined function maps",
            "sql_injection": "Use parameterized queries or prepared statements instead of string interpolation",
            "path_traversal": "Validate and sanitize file paths. Use path.resolve() and check against allowed directories",
            "unsafe_redirect": "Validate redirect URLs against a whitelist of allowed domains"
        }
        
        return recommendations.get(risk_type, "Review code for potential security implications")
    
    def get_risk_summary(self, risks: List[SecurityRisk]) -> Dict[str, Any]:
        """リスクサマリー生成"""
        summary = {
            "total_risks": len(risks),
            "by_severity": {
                "critical": len([r for r in risks if r.severity == "critical"]),
                "high": len([r for r in risks if r.severity == "high"]),
                "medium": len([r for r in risks if r.severity == "medium"]),
                "low": len([r for r in risks if r.severity == "low"])
            },
            "by_type": {}
        }
        
        # タイプ別集計
        for risk in risks:
            if risk.risk_type not in summary["by_type"]:
                summary["by_type"][risk.risk_type] = 0
            summary["by_type"][risk.risk_type] += 1
        
        return summary
    
    def validate_security_compliance(self, blocks: List[CodeBlock]) -> Dict[str, Any]:
        """セキュリティ準拠性検証"""
        all_risks = []
        
        for block in blocks:
            risks = self.scan_security_risks(block)
            all_risks.extend(risks)
        
        # 準拠性判定
        critical_risks = [r for r in all_risks if r.severity == "critical"]
        high_risks = [r for r in all_risks if r.severity == "high"]
        
        compliance_level = "compliant"
        if critical_risks:
            compliance_level = "non_compliant"
        elif high_risks:
            compliance_level = "partially_compliant"
        
        return {
            "compliance_level": compliance_level,
            "total_risks": len(all_risks),
            "critical_risks": len(critical_risks),
            "high_risks": len(high_risks),
            "risks": all_risks,
            "summary": self.get_risk_summary(all_risks)
        }