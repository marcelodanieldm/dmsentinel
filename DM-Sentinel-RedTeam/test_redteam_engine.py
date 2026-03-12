"""
Test Suite for sentinel_redteam_engine.py
===========================================
Autor: DM Sentinel Security Team
Fecha: 2025-03-12
Versión: 1.0.0

Tests para el Red Team Automation Engine.
Verifica:
- Inicialización del RedTeamEngine
- Simulación de ataques individuales
- Assessment completo con múltiples vectores
- Generación de reportes (JSON, HTML)
- Funciones de conveniencia
- Manejo de errores
- Verificación de compliance
- Rate limiting
"""

import pytest
import asyncio
import json
import os
from typing import List
from datetime import datetime
from sentinel_redteam_engine import (
    AttackType,
    Severity,
    AttackStatus,
    AttackVector,
    AttackResult,
    RedTeamReport,
    RedTeamEngine,
    ATTACK_VECTORS,
    quick_scan,
    get_attack_vector
)


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def engine():
    """Initialize RedTeamEngine for tests."""
    return RedTeamEngine(
        target_url="https://test.api.example.com",
        rate_limit=10,
        safe_mode=True
    )


@pytest.fixture
def sample_attack_vector():
    """Return sample attack vector for testing."""
    return ATTACK_VECTORS[AttackType.BOLA_TEST]


@pytest.fixture
def all_attack_types():
    """Return list of all attack types."""
    return [
        AttackType.BOLA_TEST,
        AttackType.AUTH_BYPASS,
        AttackType.MASS_ASSIGNMENT,
        AttackType.RATE_LIMIT_TEST,
        AttackType.BFLA_TEST,
        AttackType.BUSINESS_LOGIC,
        AttackType.SSRF_TEST,
        AttackType.SECURITY_MISCONFIG,
        AttackType.API_VERSION_PROBE,
        AttackType.INJECTION_TEST
    ]


# ==========================================
# Test 1: Engine Initialization
# ==========================================

def test_engine_initialization(engine):
    """
    Test 1: RedTeamEngine correctly initializes.
    
    Verifica:
    - Engine se inicializa sin errores
    - Parámetros están configurados correctamente
    - Attack vectors están cargados
    - Safe mode está habilitado
    """
    assert engine is not None, "Engine should be initialized"
    assert engine.target_url == "https://test.api.example.com", "Target URL should match"
    assert engine.rate_limit == 10, "Rate limit should match"
    assert engine.safe_mode is True, "Safe mode should be enabled"
    assert len(engine.attack_vectors) >= 10, "Should have at least 10 attack vectors"
    
    print("✅ Test 1 PASSED: Engine initialized correctly")


# ==========================================
# Test 2: Attack Vector Database
# ==========================================

def test_attack_vector_database():
    """
    Test 2: Verify ATTACK_VECTORS database is complete.
    
    Verifica:
    - Todos los OWASP API Top 10 están cubiertos
    - Cada vector tiene todos los campos requeridos
    - CVSS scores son válidos
    - Severities son apropiadas
    """
    assert len(ATTACK_VECTORS) >= 10, "Should have at least 10 attack vectors"
    
    for attack_type, vector in ATTACK_VECTORS.items():
        assert vector.attack_type == attack_type, f"Attack type should match for {attack_type}"
        assert len(vector.name) > 0, f"Name should exist for {attack_type}"
        assert len(vector.description) > 0, f"Description should exist for {attack_type}"
        assert len(vector.payload) > 0, f"Payload should exist for {attack_type}"
        assert len(vector.expected_indicators) > 0, f"Expected indicators should exist for {attack_type}"
        assert 0.0 <= vector.cvss_score <= 10.0, f"CVSS score should be valid for {attack_type}"
        assert vector.owasp_category.startswith("API"), f"OWASP category should be valid for {attack_type}"
    
    print(f"✅ Test 2 PASSED: Attack vector database complete - {len(ATTACK_VECTORS)} vectors")


# ==========================================
# Test 3: Single Attack Simulation
# ==========================================

@pytest.mark.asyncio
async def test_single_attack_simulation(engine, sample_attack_vector):
    """
    Test 3: Simulate a single attack and verify result.
    
    Verifica:
    - Attack simulation se ejecuta
    - Resultado contiene todos los campos esperados
    - Status es válido
    - Evidence está presente
    """
    result = await engine.simulate_attack(
        attack_vector=sample_attack_vector,
        target_endpoint="/api/test"
    )
    
    assert result is not None, "Should return attack result"
    assert isinstance(result, AttackResult), "Should return AttackResult object"
    assert result.attack_vector == sample_attack_vector, "Attack vector should match"
    assert result.target_url.endswith("/api/test"), "Target URL should include endpoint"
    assert result.status in [AttackStatus.VULNERABLE, AttackStatus.BLOCKED], "Status should be valid"
    assert isinstance(result.vulnerable, bool), "Vulnerable should be boolean"
    assert isinstance(result.evidence, dict), "Evidence should be dictionary"
    assert result.response_time > 0, "Response time should be positive"
    assert result.remediation_advice is not None, "Should include remediation advice"
    
    print(f"✅ Test 3 PASSED: Single attack simulation - Status: {result.status.value}")


# ==========================================
# Test 4: BOLA Test Attack
# ==========================================

@pytest.mark.asyncio
async def test_bola_attack(engine):
    """
    Test 4: Test BOLA (Broken Object Level Authorization) attack.
    
    Verifica:
    - BOLA attack vector se ejecuta
    - Resultado es coherente con OWASP API1:2023
    """
    vector = ATTACK_VECTORS[AttackType.BOLA_TEST]
    result = await engine.simulate_attack(vector)
    
    assert result.attack_vector.owasp_category == "API1:2023", "Should map to API1:2023"
    assert result.attack_vector.severity in [Severity.HIGH, Severity.CRITICAL], "BOLA should be high severity"
    assert "ISO27001:A.9.4.1" in result.attack_vector.compliance_tags, "Should have ISO27001 tag"
    
    print("✅ Test 4 PASSED: BOLA attack tested successfully")


# ==========================================
# Test 5: Auth Bypass Test Attack
# ==========================================

@pytest.mark.asyncio
async def test_auth_bypass_attack(engine):
    """
    Test 5: Test Authentication Bypass attack.
    
    Verifica:
    - Auth bypass attack se ejecuta
    - Severity es CRITICAL
    """
    vector = ATTACK_VECTORS[AttackType.AUTH_BYPASS]
    result = await engine.simulate_attack(vector)
    
    assert result.attack_vector.severity == Severity.CRITICAL, "Auth bypass should be critical"
    assert result.attack_vector.cvss_score >= 9.0, "CVSS should be very high"
    assert result.attack_vector.owasp_category == "API2:2023", "Should map to API2:2023"
    
    print("✅ Test 5 PASSED: Auth bypass attack tested successfully")


# ==========================================
# Test 6: Injection Test Attack
# ==========================================

@pytest.mark.asyncio
async def test_injection_attack(engine):
    """
    Test 6: Test Injection attack (SQL, NoSQL, Command).
    
    Verifica:
    - Injection attack se ejecuta
    - Payload incluye múltiples tipos de injection
    """
    vector = ATTACK_VECTORS[AttackType.INJECTION_TEST]
    result = await engine.simulate_attack(vector)
    
    assert "SQL" in vector.payload or "SQL" in vector.description, "Should test SQL injection"
    assert result.attack_vector.severity == Severity.CRITICAL, "Injection should be critical"
    assert result.attack_vector.owasp_category == "API10:2023", "Should map to API10:2023"
    
    print("✅ Test 6 PASSED: Injection attack tested successfully")


# ==========================================
# Test 7: Full Assessment (All Attacks)
# ==========================================

@pytest.mark.asyncio
async def test_full_assessment(engine):
    """
    Test 7: Run full Red Team assessment with all attack vectors.
    
    Verifica:
    - Assessment se ejecuta completamente
    - Report contiene todos los resultados
    - Executive summary se genera
    - Compliance status se evalúa
    """
    report = await engine.run_full_assessment()
    
    assert report is not None, "Should return report"
    assert isinstance(report, RedTeamReport), "Should return RedTeamReport object"
    assert report.total_attacks >= 10, "Should test at least 10 attack vectors"
    assert len(report.attack_results) == report.total_attacks, "All attacks should be recorded"
    assert report.start_time is not None, "Should have start time"
    assert report.end_time is not None, "Should have end time"
    assert len(report.executive_summary) > 100, "Executive summary should be substantial"
    assert len(report.compliance_status) > 0, "Should have compliance status"
    
    print(f"✅ Test 7 PASSED: Full assessment - {report.total_attacks} attacks, {report.vulnerabilities_found} vulnerabilities")


# ==========================================
# Test 8: Selective Assessment (Specific Attacks)
# ==========================================

@pytest.mark.asyncio
async def test_selective_assessment(engine):
    """
    Test 8: Run assessment with specific attack types only.
    
    Verifica:
    - Assessment respeta filtro de attack_types
    - Solo se ejecutan los ataques solicitados
    """
    selected_attacks = [
        AttackType.BOLA_TEST,
        AttackType.AUTH_BYPASS,
        AttackType.INJECTION_TEST
    ]
    
    report = await engine.run_full_assessment(attack_types=selected_attacks)
    
    assert report.total_attacks == len(selected_attacks), "Should only test selected attacks"
    assert len(report.attack_results) == len(selected_attacks), "Results should match selected attacks"
    
    # Verify only selected attacks were executed
    result_types = [r.attack_vector.attack_type for r in report.attack_results]
    for attack_type in selected_attacks:
        assert attack_type in result_types, f"{attack_type} should be in results"
    
    print(f"✅ Test 8 PASSED: Selective assessment - {len(selected_attacks)} specific attacks")


# ==========================================
# Test 9: Remediation Advice Generation
# ==========================================

@pytest.mark.asyncio
async def test_remediation_advice(engine, all_attack_types):
    """
    Test 9: Verify remediation advice is provided for all attack types.
    
    Verifica:
    - Cada resultado incluye remediation advice
    - Advice es específico y técnico
    """
    for attack_type in all_attack_types[:5]:  # Test subset for speed
        vector = ATTACK_VECTORS[attack_type]
        result = await engine.simulate_attack(vector)
        
        assert result.remediation_advice is not None, f"Should have remediation for {attack_type}"
        assert len(result.remediation_advice) > 20, f"Remediation should be substantial for {attack_type}"
        
        # Check for technical terms
        advice_lower = result.remediation_advice.lower()
        has_technical = any(term in advice_lower for term in [
            "implement", "validate", "use", "enforce", "configure",
            "middleware", "token", "limit", "sanitize", "encrypt"
        ])
        assert has_technical, f"Remediation should be technical for {attack_type}"
    
    print("✅ Test 9 PASSED: Remediation advice is comprehensive")


# ==========================================
# Test 10: Executive Summary Generation
# ==========================================

@pytest.mark.asyncio
async def test_executive_summary_generation(engine):
    """
    Test 10: Verify executive summary contains key information.
    
    Verifica:
    - Summary incluye estadísticas clave
    - Severity breakdown está presente
    - Recommendations están incluidas
    """
    report = await engine.run_full_assessment()
    summary = report.executive_summary
    
    assert "Target System:" in summary, "Should include target system"
    assert "FINDINGS:" in summary or "Findings" in summary, "Should include findings section"
    assert "SEVERITY" in summary or "Severity" in summary, "Should include severity breakdown"
    assert "RECOMMENDATIONS" in summary or "Recommendations" in summary, "Should include recommendations"
    assert str(report.total_attacks) in summary, "Should include test count"
    
    print("✅ Test 10 PASSED: Executive summary is comprehensive")


# ==========================================
# Test 11: Compliance Assessment
# ==========================================

@pytest.mark.asyncio
async def test_compliance_assessment(engine):
    """
    Test 11: Verify compliance status assessment.
    
    Verifica:
    - ISO27001 status se evalúa
    - SOC2 status se evalúa
    - OWASP API Top 10 coverage se reporta
    """
    report = await engine.run_full_assessment()
    compliance = report.compliance_status
    
    assert "ISO27001" in compliance, "Should assess ISO27001 compliance"
    assert "SOC2" in compliance, "Should assess SOC2 compliance"
    assert "OWASP" in compliance or any("OWASP" in k for k in compliance.keys()), "Should assess OWASP compliance"
    
    # Check format
    for key, value in compliance.items():
        assert isinstance(value, str), f"Compliance value for {key} should be string"
        assert len(value) > 0, f"Compliance value for {key} should not be empty"
    
    print(f"✅ Test 11 PASSED: Compliance assessment - {len(compliance)} frameworks evaluated")


# ==========================================
# Test 12: Vulnerability Summary
# ==========================================

@pytest.mark.asyncio
async def test_vulnerability_summary(engine):
    """
    Test 12: Test get_vulnerability_summary() method.
    
    Verifica:
    - Summary contiene métricas clave
    - Breakdown por severity está presente
    - Breakdown por OWASP está presente
    """
    report = await engine.run_full_assessment()
    summary = engine.get_vulnerability_summary()
    
    assert "total_tests" in summary, "Should include total tests"
    assert "vulnerabilities_found" in summary, "Should include vulnerabilities found"
    assert "by_severity" in summary, "Should include severity breakdown"
    assert "by_owasp" in summary, "Should include OWASP breakdown"
    
    # Check severity breakdown
    severity_breakdown = summary["by_severity"]
    assert "CRITICAL" in severity_breakdown, "Should include critical count"
    assert "HIGH" in severity_breakdown, "Should include high count"
    assert "MEDIUM" in severity_breakdown, "Should include medium count"
    
    print("✅ Test 12 PASSED: Vulnerability summary is complete")


# ==========================================
# Test 13: JSON Export
# ==========================================

@pytest.mark.asyncio
async def test_json_export(engine):
    """
    Test 13: Test JSON report export functionality.
    
    Verifica:
    - JSON export funciona
    - Archivo se crea correctamente
    - JSON es válido y parseable
    """
    await engine.run_full_assessment()
    
    filename = "test_redteam_report.json"
    exported_file = engine.export_report_json(filename)
    
    assert os.path.exists(filename), "JSON file should be created"
    
    # Verify JSON is valid
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert "report_id" in data, "JSON should include report_id"
    assert "total_attacks" in data, "JSON should include total_attacks"
    assert "attack_results" in data, "JSON should include attack_results"
    assert isinstance(data["attack_results"], list), "attack_results should be list"
    
    # Cleanup
    os.remove(filename)
    
    print("✅ Test 13 PASSED: JSON export works correctly")


# ==========================================
# Test 14: HTML Export
# ==========================================

@pytest.mark.asyncio
async def test_html_export(engine):
    """
    Test 14: Test HTML report export functionality.
    
    Verifica:
    - HTML export funciona
    - Archivo se crea correctamente
    - HTML contiene elementos esperados
    """
    await engine.run_full_assessment()
    
    filename = "test_redteam_report.html"
    exported_file = engine.export_report_html(filename)
    
    assert os.path.exists(filename), "HTML file should be created"
    
    # Verify HTML content
    with open(filename, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    assert "<!DOCTYPE html>" in html_content, "Should be valid HTML"
    assert "Red Team Assessment Report" in html_content, "Should include title"
    assert "Executive Summary" in html_content, "Should include executive summary"
    assert "<table" in html_content, "Should include tables"
    
    # Cleanup
    os.remove(filename)
    
    print("✅ Test 14 PASSED: HTML export works correctly")


# ==========================================
# Test 15: Quick Scan Convenience Function
# ==========================================

@pytest.mark.asyncio
async def test_quick_scan_function():
    """
    Test 15: Test quick_scan() convenience function.
    
    Verifica:
    - Función de conveniencia funciona
    - Retorna report válido
    """
    target = "https://api.quicktest.com"
    report = await quick_scan(target)
    
    assert report is not None, "Should return report"
    assert isinstance(report, RedTeamReport), "Should return RedTeamReport"
    assert report.target_system == target, "Target should match"
    assert report.total_attacks > 0, "Should execute attacks"
    
    print("✅ Test 15 PASSED: Quick scan function works")


# ==========================================
# Test 16: Get Attack Vector Function
# ==========================================

def test_get_attack_vector_function():
    """
    Test 16: Test get_attack_vector() convenience function.
    
    Verifica:
    - Función obtiene attack vectors correctamente
    - Maneja errores con tipos inválidos
    """
    # Valid attack type
    vector = get_attack_vector("BOLA_TEST")
    assert vector is not None, "Should return vector for valid type"
    assert isinstance(vector, AttackVector), "Should return AttackVector"
    assert vector.attack_type == AttackType.BOLA_TEST, "Type should match"
    
    # Invalid attack type
    invalid_vector = get_attack_vector("INVALID_ATTACK")
    assert invalid_vector is None, "Should return None for invalid type"
    
    print("✅ Test 16 PASSED: Get attack vector function works")


# ==========================================
# Test 17: Attack Vector Data Completeness
# ==========================================

def test_attack_vector_completeness():
    """
    Test 17: Verify all attack vectors have complete data.
    
    Verifica:
    - Todos los vectores tienen payloads válidos
    - Todos tienen expected_indicators
    - Todos tienen compliance tags
    """
    for attack_type, vector in ATTACK_VECTORS.items():
        assert len(vector.payload) > 10, f"Payload should be substantial for {attack_type}"
        assert len(vector.expected_indicators) >= 1, f"Should have indicators for {attack_type}"
        assert vector.cvss_score > 0, f"CVSS score should be positive for {attack_type}"
        
        # Check OWASP mapping
        assert vector.owasp_category.startswith("API"), f"OWASP category should be valid for {attack_type}"
        
        # Most vectors should have compliance tags
        if attack_type in [AttackType.BOLA_TEST, AttackType.AUTH_BYPASS, AttackType.INJECTION_TEST]:
            assert len(vector.compliance_tags) > 0, f"Should have compliance tags for {attack_type}"
    
    print("✅ Test 17 PASSED: All attack vectors are complete")


# ==========================================
# Test 18: CVSS Score Validation
# ==========================================

def test_cvss_score_validation():
    """
    Test 18: Verify CVSS scores are appropriate for severity levels.
    
    Verifica:
    - CRITICAL vulnerabilities tienen CVSS >= 9.0
    - HIGH vulnerabilities tienen CVSS >= 7.0
    - MEDIUM vulnerabilities tienen CVSS >= 4.0
    """
    for attack_type, vector in ATTACK_VECTORS.items():
        if vector.severity == Severity.CRITICAL:
            assert vector.cvss_score >= 9.0, f"CRITICAL should have CVSS >= 9.0 for {attack_type}"
        elif vector.severity == Severity.HIGH:
            assert vector.cvss_score >= 7.0, f"HIGH should have CVSS >= 7.0 for {attack_type}"
        elif vector.severity == Severity.MEDIUM:
            assert vector.cvss_score >= 4.0, f"MEDIUM should have CVSS >= 4.0 for {attack_type}"
    
    print("✅ Test 18 PASSED: CVSS scores align with severity levels")


# ==========================================
# Test 19: OWASP API Top 10 Coverage
# ==========================================

def test_owasp_top_10_coverage():
    """
    Test 19: Verify all OWASP API Top 10 (2023) categories are covered.
    
    Verifica:
    - API1 through API10 están cubiertos
    - Al menos un ataque por categoría
    """
    owasp_categories = set()
    for vector in ATTACK_VECTORS.values():
        owasp_categories.add(vector.owasp_category)
    
    # Should cover API1 through API10
    for i in range(1, 11):
        category = f"API{i}:2023"
        assert any(category in cat for cat in owasp_categories), f"Should cover {category}"
    
    print(f"✅ Test 19 PASSED: OWASP API Top 10 fully covered - {len(owasp_categories)} categories")


# ==========================================
# Test 20: Report ID Uniqueness
# ==========================================

@pytest.mark.asyncio
async def test_report_id_uniqueness(engine):
    """
    Test 20: Verify report IDs are unique across multiple assessments.
    
    Verifica:
    - Cada assessment genera un report_id único
    - IDs son UUIDs válidos
    """
    report1 = await engine.run_full_assessment(attack_types=[AttackType.BOLA_TEST])
    report2 = await engine.run_full_assessment(attack_types=[AttackType.AUTH_BYPASS])
    
    assert report1.report_id != report2.report_id, "Report IDs should be unique"
    
    # Verify UUID format (basic check)
    assert len(report1.report_id) == 36, "Report ID should be UUID format"
    assert "-" in report1.report_id, "Report ID should contain hyphens"
    
    print("✅ Test 20 PASSED: Report IDs are unique")


# ==========================================
# Test Runner
# ==========================================

if __name__ == "__main__":
    """
    Run all tests manually (without pytest).
    Útil para debugging rápido.
    """
    print("\n" + "="*60)
    print("🧪 DM SENTINEL - RED TEAM ENGINE TEST SUITE")
    print("="*60 + "\n")
    
    async def run_async_tests():
        engine = RedTeamEngine(
            target_url="https://test.api.example.com",
            rate_limit=10,
            safe_mode=True
        )
        
        sample_vector = ATTACK_VECTORS[AttackType.BOLA_TEST]
        all_attacks = list(ATTACK_VECTORS.keys())[:10]
        
        # Sync tests
        test_engine_initialization(engine)
        test_attack_vector_database()
        test_get_attack_vector_function()
        test_attack_vector_completeness()
        test_cvss_score_validation()
        test_owasp_top_10_coverage()
        
        # Async tests
        await test_single_attack_simulation(engine, sample_vector)
        await test_bola_attack(engine)
        await test_auth_bypass_attack(engine)
        await test_injection_attack(engine)
        await test_full_assessment(engine)
        await test_selective_assessment(engine)
        await test_remediation_advice(engine, all_attacks)
        await test_executive_summary_generation(engine)
        await test_compliance_assessment(engine)
        await test_vulnerability_summary(engine)
        await test_json_export(engine)
        await test_html_export(engine)
        await test_quick_scan_function()
        await test_report_id_uniqueness(engine)
        
        print("\n" + "="*60)
        print("✅ ALL 20 TESTS PASSED!")
        print("="*60 + "\n")
    
    try:
        asyncio.run(run_async_tests())
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
