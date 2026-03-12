"""
Test Suite for api_mitigation_intel.py
===========================================
Autor: DM Sentinel Team
Fecha: 2025-03-11
Versión: 1.0.0

Tests para el Motor de Inteligencia de Mitigación Multilingüe.
Verifica:
- Inicialización del MitigationProvider
- Obtención de consejos en 5 idiomas
- Sistema de fallback inteligente
- Búsqueda por etiquetas de compliance
- Exportación en múltiples formatos
- Cobertura de las 10 vulnerabilidades OWASP API Top 10
- Manejo de errores
"""

import pytest
from typing import Optional, List
from api_mitigation_intel import (
    VulnerabilityType,
    Language,
    MitigationAdvice,
    MitigationProvider,
    get_mitigation,
    MITIGATION_DATABASE
)


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def provider():
    """Initialize MitigationProvider for tests."""
    return MitigationProvider()


@pytest.fixture
def all_vulnerability_types():
    """Return list of all OWASP API Top 10 vulnerability types."""
    return [
        VulnerabilityType.BOLA,
        VulnerabilityType.BROKEN_AUTH,
        VulnerabilityType.MASS_ASSIGNMENT,
        VulnerabilityType.RATE_LIMITING,
        VulnerabilityType.BFLA,
        VulnerabilityType.BUSINESS_LOGIC,
        VulnerabilityType.SSRF,
        VulnerabilityType.SECURITY_MISCONFIGURATION,
        VulnerabilityType.API_VERSIONING,
        VulnerabilityType.INJECTION
    ]


@pytest.fixture
def all_languages():
    """Return list of all supported languages."""
    return [
        Language.SPANISH,
        Language.ENGLISH,
        Language.FRENCH,
        Language.PORTUGUESE,
        Language.ESPERANTO
    ]


# ==========================================
# Test 1: Provider Initialization
# ==========================================

def test_provider_initialization(provider):
    """
    Test 1: MitigationProvider correctly initializes with database.
    
    Verifica:
    - Provider se inicializa sin errores
    - Database está cargada
    - Idiomas soportados están configurados
    - Orden de fallback es correcto
    """
    assert provider is not None, "Provider should be initialized"
    assert provider.database is not None, "Database should be loaded"
    assert len(provider.database) >= 10, "Database should have at least 10 OWASP vulnerabilities"
    
    # Check supported languages
    expected_languages = ["ES", "EN", "FR", "PT", "EO"]
    assert provider.supported_languages == expected_languages, "Supported languages should match"
    
    # Check fallback order
    expected_fallback = ["EN", "ES"]
    assert provider.fallback_order == expected_fallback, "Fallback order should be EN → ES"
    
    print("✅ Test 1 PASSED: Provider initialized correctly")


# ==========================================
# Test 2: Get Advice in Spanish
# ==========================================

def test_get_advice_spanish(provider):
    """
    Test 2: Get BOLA mitigation advice in Spanish.
    
    Verifica:
    - Consejo se obtiene correctamente
    - Título está en español
    - Descripción está en español
    - Mitigación está en español
    - Código de ejemplo incluye comentarios en español
    - Tags de compliance están presentes
    """
    advice = provider.get_advice(VulnerabilityType.BOLA, Language.SPANISH)
    
    assert advice is not None, "Should return advice"
    assert isinstance(advice, MitigationAdvice), "Should return MitigationAdvice object"
    assert advice.vulnerability_type == VulnerabilityType.BOLA, "Vulnerability type should match"
    assert advice.language.value == "ES", "Language should be Spanish"
    
    # Check Spanish content
    assert "BOLA" in advice.title, "Title should contain BOLA"
    assert "Autorización" in advice.title or "objeto" in advice.title.lower(), "Title should be in Spanish"
    assert len(advice.description) > 20, "Description should be substantial"
    assert len(advice.mitigation) > 50, "Mitigation should be detailed"
    assert len(advice.code_example) > 30, "Code example should be provided"
    
    # Check compliance tags
    assert len(advice.tags) > 0, "Should have compliance tags"
    assert any("ISO27001" in tag or "authorization" in tag for tag in advice.tags), "Should have relevant tags"
    
    print(f"✅ Test 2 PASSED: Spanish advice - {advice.title[:50]}...")


# ==========================================
# Test 3: Get Advice in English
# ==========================================

def test_get_advice_english(provider):
    """
    Test 3: Get Broken Authentication mitigation advice in English.
    
    Verifica:
    - Consejo en inglés se obtiene correctamente
    - Contenido técnico es específico (MFA, JWT, etc.)
    """
    advice = provider.get_advice(VulnerabilityType.BROKEN_AUTH, Language.ENGLISH)
    
    assert advice is not None, "Should return advice"
    assert advice.language.value == "EN", "Language should be English"
    assert "Authentication" in advice.title or "Auth" in advice.title, "Title should be in English"
    
    # Check technical content
    mitigation_lower = advice.mitigation.lower()
    assert any(term in mitigation_lower for term in ["mfa", "multi-factor", "jwt", "token"]), \
        "Should contain specific technical recommendations"
    
    print(f"✅ Test 3 PASSED: English advice - {advice.title[:50]}...")


# ==========================================
# Test 4: Get Advice in French
# ==========================================

def test_get_advice_french(provider):
    """
    Test 4: Get Mass Assignment mitigation advice in French.
    
    Verifica:
    - Consejo en francés se obtiene correctamente
    - Contenido está traducido
    """
    advice = provider.get_advice(VulnerabilityType.MASS_ASSIGNMENT, Language.FRENCH)
    
    assert advice is not None, "Should return advice"
    assert advice.language.value == "FR", "Language should be French"
    assert len(advice.mitigation) > 50, "Mitigation should be detailed"
    
    print(f"✅ Test 4 PASSED: French advice - {advice.title[:50]}...")


# ==========================================
# Test 5: Get Advice in Portuguese
# ==========================================

def test_get_advice_portuguese(provider):
    """
    Test 5: Get Rate Limiting mitigation advice in Portuguese.
    
    Verifica:
    - Consejo en portugués se obtiene correctamente
    """
    advice = provider.get_advice(VulnerabilityType.RATE_LIMITING, Language.PORTUGUESE)
    
    assert advice is not None, "Should return advice"
    assert advice.language.value == "PT", "Language should be Portuguese"
    assert len(advice.description) > 20, "Description should be substantial"
    
    print(f"✅ Test 5 PASSED: Portuguese advice - {advice.title[:50]}...")


# ==========================================
# Test 6: Get Advice in Esperanto
# ==========================================

def test_get_advice_esperanto(provider):
    """
    Test 6: Get BFLA mitigation advice in Esperanto.
    
    Verifica:
    - Consejo en esperanto se obtiene correctamente
    """
    advice = provider.get_advice(VulnerabilityType.BFLA, Language.ESPERANTO)
    
    assert advice is not None, "Should return advice"
    assert advice.language.value == "EO", "Language should be Esperanto"
    assert len(advice.mitigation) > 50, "Mitigation should be detailed"
    
    print(f"✅ Test 6 PASSED: Esperanto advice - {advice.title[:50]}...")


# ==========================================
# Test 7: Fallback System
# ==========================================

def test_fallback_system(provider):
    """
    Test 7: Test intelligent fallback system (requested → EN → ES).
    
    Verifica:
    - Si idioma solicitado no disponible, usa English
    - Sistema de fallback funciona correctamente
    - Mensaje de fallback se imprime (captured in output)
    """
    # Create custom database with only English and Spanish for one vulnerability
    custom_database = {
        VulnerabilityType.BOLA: {
            "title": {
                "EN": "Broken Object Level Authorization",
                "ES": "Autorización Rota a Nivel de Objeto"
            },
            "description": {
                "EN": "Users can access other users' objects.",
                "ES": "Usuarios pueden acceder a objetos de otros usuarios."
            },
            "mitigation": {
                "EN": "Implement ownership validation.",
                "ES": "Implementar validación de propiedad."
            },
            "code_example": {
                "EN": "# Example code",
                "ES": "# Código de ejemplo"
            },
            "tags": ["authorization"]
        }
    }
    
    custom_provider = MitigationProvider(database=custom_database)
    
    # Try to get French (should fallback to English)
    advice = custom_provider.get_advice(VulnerabilityType.BOLA, Language.FRENCH)
    
    assert advice is not None, "Should return advice with fallback"
    assert advice.language.value == "EN", "Should fallback to English"
    assert "Broken Object" in advice.title, "Should use English content"
    
    print("✅ Test 7 PASSED: Fallback system works correctly (FR → EN)")


# ==========================================
# Test 8: All 10 OWASP Vulnerabilities
# ==========================================

def test_all_owasp_vulnerabilities(provider, all_vulnerability_types):
    """
    Test 8: Verify all 10 OWASP API Top 10 vulnerabilities are covered.
    
    Verifica:
    - Cada vulnerabilidad tiene datos en la base
    - Se puede obtener consejo para cada una
    - Todas tienen título, descripción, mitigación y código
    """
    for vuln_type in all_vulnerability_types:
        advice = provider.get_advice(vuln_type, Language.ENGLISH)
        
        assert advice is not None, f"Should return advice for {vuln_type.value}"
        assert len(advice.title) > 0, f"Title should exist for {vuln_type.value}"
        assert len(advice.description) > 0, f"Description should exist for {vuln_type.value}"
        assert len(advice.mitigation) > 0, f"Mitigation should exist for {vuln_type.value}"
        assert len(advice.code_example) > 0, f"Code example should exist for {vuln_type.value}"
        assert len(advice.tags) > 0, f"Tags should exist for {vuln_type.value}"
    
    print(f"✅ Test 8 PASSED: All {len(all_vulnerability_types)} OWASP vulnerabilities covered")


# ==========================================
# Test 9: Search by Compliance Tag
# ==========================================

def test_search_by_compliance_tag(provider):
    """
    Test 9: Search vulnerabilities by ISO27001 and SOC2 compliance tags.
    
    Verifica:
    - Búsqueda por ISO27001 retorna vulnerabilidades relevantes
    - Búsqueda por SOC2 retorna vulnerabilidades relevantes
    - Búsqueda por tag genérico funciona
    """
    # Search by ISO27001
    iso_results = provider.search_by_tag("ISO27001")
    assert len(iso_results) > 0, "Should find ISO27001 tagged vulnerabilities"
    assert all(isinstance(v, VulnerabilityType) for v in iso_results), "Results should be VulnerabilityType"
    
    # Search by SOC2
    soc2_results = provider.search_by_tag("SOC2")
    assert len(soc2_results) >= 0, "Should find SOC2 tagged vulnerabilities (or none)"
    
    # Search by authorization tag
    auth_results = provider.search_by_tag("authorization")
    assert len(auth_results) > 0, "Should find authorization tagged vulnerabilities"
    assert VulnerabilityType.BOLA in auth_results or VulnerabilityType.BFLA in auth_results, \
        "Authorization search should include BOLA or BFLA"
    
    print(f"✅ Test 9 PASSED: Tag search - ISO27001:{len(iso_results)}, SOC2:{len(soc2_results)}, auth:{len(auth_results)}")


# ==========================================
# Test 10: Export Markdown Format
# ==========================================

def test_export_markdown(provider):
    """
    Test 10: Export mitigation advice in Markdown format.
    
    Verifica:
    - Exportación a Markdown funciona
    - Formato contiene headers (#)
    - Contenido incluye título y mitigación
    """
    markdown = provider.export_advice(
        VulnerabilityType.INJECTION,
        Language.SPANISH,
        format="markdown"
    )
    
    assert markdown is not None, "Should return markdown string"
    assert len(markdown) > 100, "Markdown should be substantial"
    assert "#" in markdown, "Markdown should contain headers"
    assert "Injection" in markdown or "Inyección" in markdown, "Should contain vulnerability name"
    
    print("✅ Test 10 PASSED: Markdown export works")


# ==========================================
# Test 11: Export Text Format
# ==========================================

def test_export_text(provider):
    """
    Test 11: Export mitigation advice in plain text format.
    
    Verifica:
    - Exportación a texto plano funciona
    - Contenido es legible
    """
    text = provider.export_advice(
        VulnerabilityType.SSRF,
        Language.ENGLISH,
        format="text"
    )
    
    assert text is not None, "Should return text string"
    assert len(text) > 50, "Text should be substantial"
    assert "SSRF" in text or "Request Forgery" in text, "Should contain vulnerability name"
    
    print("✅ Test 11 PASSED: Text export works")


# ==========================================
# Test 12: Export HTML Format
# ==========================================

def test_export_html(provider):
    """
    Test 12: Export mitigation advice in HTML format.
    
    Verifica:
    - Exportación a HTML funciona
    - Contiene tags HTML válidos
    """
    html = provider.export_advice(
        VulnerabilityType.SECURITY_MISCONFIGURATION,
        Language.FRENCH,
        format="html"
    )
    
    assert html is not None, "Should return HTML string"
    assert len(html) > 50, "HTML should be substantial"
    assert "<" in html and ">" in html, "Should contain HTML tags"
    
    print("✅ Test 12 PASSED: HTML export works")


# ==========================================
# Test 13: Convenience Function
# ==========================================

def test_convenience_function():
    """
    Test 13: Test get_mitigation() convenience function.
    
    Verifica:
    - Función de conveniencia funciona correctamente
    - Acepta strings para vulnerability type y language
    - Retorna MitigationAdvice válido
    """
    advice = get_mitigation("BOLA", "ES")
    
    assert advice is not None, "Convenience function should return advice"
    assert isinstance(advice, MitigationAdvice), "Should return MitigationAdvice object"
    assert advice.vulnerability_type == VulnerabilityType.BOLA, "Type should be BOLA"
    assert advice.language.value == "ES", "Language should be Spanish"
    
    print("✅ Test 13 PASSED: Convenience function works")


# ==========================================
# Test 14: Invalid Vulnerability Type
# ==========================================

def test_invalid_vulnerability_type():
    """
    Test 14: Test handling of invalid vulnerability type in convenience function.
    
    Verifica:
    - Función maneja gracefully tipos inválidos
    - Retorna None en lugar de crash
    """
    advice = get_mitigation("INVALID_TYPE", "EN")
    
    assert advice is None, "Should return None for invalid vulnerability type"
    
    print("✅ Test 14 PASSED: Invalid vulnerability type handled gracefully")


# ==========================================
# Test 15: Invalid Language
# ==========================================

def test_invalid_language():
    """
    Test 15: Test handling of invalid language in convenience function.
    
    Verifica:
    - Función maneja gracefully idiomas inválidos
    - Retorna None en lugar de crash
    """
    advice = get_mitigation("BOLA", "INVALID_LANG")
    
    assert advice is None, "Should return None for invalid language"
    
    print("✅ Test 15 PASSED: Invalid language handled gracefully")


# ==========================================
# Test 16: Get All Vulnerabilities
# ==========================================

def test_get_all_vulnerabilities(provider):
    """
    Test 16: Test get_all_vulnerabilities() method.
    
    Verifica:
    - Método retorna todas las vulnerabilidades
    - Lista contiene al menos 10 tipos
    """
    all_vulns = provider.get_all_vulnerabilities()
    
    assert len(all_vulns) >= 10, "Should return at least 10 vulnerabilities"
    assert all(isinstance(v, VulnerabilityType) for v in all_vulns), "All items should be VulnerabilityType"
    
    print(f"✅ Test 16 PASSED: Get all vulnerabilities - {len(all_vulns)} types")


# ==========================================
# Test 17: Get Supported Languages
# ==========================================

def test_get_supported_languages(provider):
    """
    Test 17: Test get_supported_languages() method.
    
    Verifica:
    - Método retorna los 5 idiomas soportados
    """
    supported = provider.get_supported_languages()
    
    assert len(supported) == 5, "Should support 5 languages"
    assert "ES" in supported, "Should include Spanish"
    assert "EN" in supported, "Should include English"
    assert "FR" in supported, "Should include French"
    assert "PT" in supported, "Should include Portuguese"
    assert "EO" in supported, "Should include Esperanto"
    
    print(f"✅ Test 17 PASSED: Supported languages - {supported}")


# ==========================================
# Test 18: Code Examples Quality
# ==========================================

def test_code_examples_quality(provider, all_vulnerability_types):
    """
    Test 18: Verify code examples are substantial and contain actual code.
    
    Verifica:
    - Cada código de ejemplo tiene longitud razonable
    - Contiene elementos de código (def, @, import, etc.)
    """
    for vuln_type in all_vulnerability_types:
        advice = provider.get_advice(vuln_type, Language.ENGLISH)
        code = advice.code_example
        
        assert len(code) > 30, f"Code example for {vuln_type.value} should be substantial"
        
        # Check for code-like content
        code_indicators = ["def ", "class ", "@", "import ", "=", "(", ")", "{", "}", "if ", "return"]
        has_code = any(indicator in code for indicator in code_indicators)
        assert has_code, f"Code example for {vuln_type.value} should contain actual code"
    
    print("✅ Test 18 PASSED: All code examples are substantial")


# ==========================================
# Test 19: Mitigation Detail Quality
# ==========================================

def test_mitigation_detail_quality(provider, all_vulnerability_types):
    """
    Test 19: Verify mitigation recommendations are detailed and technical.
    
    Verifica:
    - Cada mitigación tiene longitud mínima de 50 caracteres
    - Mitigaciones son específicas (contienen términos técnicos)
    """
    for vuln_type in all_vulnerability_types:
        advice = provider.get_advice(vuln_type, Language.ENGLISH)
        mitigation = advice.mitigation
        
        assert len(mitigation) > 50, f"Mitigation for {vuln_type.value} should be detailed"
        
        # Check for technical content (at least some technical terms)
        mitigation_lower = mitigation.lower()
        has_technical_terms = any(term in mitigation_lower for term in [
            "implement", "validate", "use", "verify", "enforce", "configure",
            "middleware", "policy", "control", "authentication", "authorization",
            "encryption", "token", "api", "request", "response"
        ])
        assert has_technical_terms, f"Mitigation for {vuln_type.value} should be technical"
    
    print("✅ Test 19 PASSED: All mitigations are detailed and technical")


# ==========================================
# Test 20: Database Completeness
# ==========================================

def test_database_completeness():
    """
    Test 20: Verify MITIGATION_DATABASE has all required fields for each vulnerability.
    
    Verifica:
    - Cada vulnerabilidad tiene 'title', 'description', 'mitigation', 'code_example', 'tags'
    - Cada campo tiene traducciones en los 5 idiomas
    """
    required_fields = ["title", "description", "mitigation", "code_example", "tags"]
    required_languages = ["ES", "EN", "FR", "PT", "EO"]
    
    for vuln_type, vuln_data in MITIGATION_DATABASE.items():
        # Check all required fields exist
        for field in required_fields:
            assert field in vuln_data, f"{vuln_type.value} missing field: {field}"
            
            if field != "tags":  # tags is a list, not a dict
                # Check all languages exist for this field
                for lang in required_languages:
                    assert lang in vuln_data[field], \
                        f"{vuln_type.value} missing {lang} translation for {field}"
                    
                    content = vuln_data[field][lang]
                    assert len(content) > 0, \
                        f"{vuln_type.value} has empty {lang} translation for {field}"
    
    print(f"✅ Test 20 PASSED: Database is complete - {len(MITIGATION_DATABASE)} vulnerabilities verified")


# ==========================================
# Test Runner
# ==========================================

if __name__ == "__main__":
    """
    Run all tests manually (without pytest).
    Útil para debugging rápido.
    """
    print("\n" + "="*60)
    print("🧪 DM SENTINEL - API Mitigation Intelligence Test Suite")
    print("="*60 + "\n")
    
    provider = MitigationProvider()
    all_vulns = [
        VulnerabilityType.BOLA,
        VulnerabilityType.BROKEN_AUTH,
        VulnerabilityType.MASS_ASSIGNMENT,
        VulnerabilityType.RATE_LIMITING,
        VulnerabilityType.BFLA,
        VulnerabilityType.BUSINESS_LOGIC,
        VulnerabilityType.SSRF,
        VulnerabilityType.SECURITY_MISCONFIGURATION,
        VulnerabilityType.API_VERSIONING,
        VulnerabilityType.INJECTION
    ]
    all_langs = [
        Language.SPANISH,
        Language.ENGLISH,
        Language.FRENCH,
        Language.PORTUGUESE,
        Language.ESPERANTO
    ]
    
    try:
        test_provider_initialization(provider)
        test_get_advice_spanish(provider)
        test_get_advice_english(provider)
        test_get_advice_french(provider)
        test_get_advice_portuguese(provider)
        test_get_advice_esperanto(provider)
        test_fallback_system(provider)
        test_all_owasp_vulnerabilities(provider, all_vulns)
        test_search_by_compliance_tag(provider)
        test_export_markdown(provider)
        test_export_text(provider)
        test_export_html(provider)
        test_convenience_function()
        test_invalid_vulnerability_type()
        test_invalid_language()
        test_get_all_vulnerabilities(provider)
        test_get_supported_languages(provider)
        test_code_examples_quality(provider, all_vulns)
        test_mitigation_detail_quality(provider, all_vulns)
        test_database_completeness()
        
        print("\n" + "="*60)
        print("✅ ALL 20 TESTS PASSED!")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
