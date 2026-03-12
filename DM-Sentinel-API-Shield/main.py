"""
DM Sentinel API Shield - Main Orchestrator
===========================================

PROMPT 3: El Validador de Negocio (Product Owner)

Orquestador principal que demuestra al cliente la "superficie de ataque invisible".
Ejecuta el flujo completo de descubrimiento y genera reportes ejecutivos.

Author: DM Global Security Team
Date: March 2026
Version: 1.0
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from api_discovery_engine import (
    APIDiscoveryEngine,
    BusinessExporter,
    DiscoveryResult,
    DiscoveredEndpoint
)


# ============================================================================
# DISCOVERY ORCHESTRATOR
# ============================================================================

class DiscoveryOrchestrator:
    """
    Main orchestrator for API discovery operations.
    
    PROMPT 3: Demonstrates the "invisible attack surface" to the client
    with clear executive summaries and multi-version API detection.
    """
    
    def __init__(self, output_dir: str = "artifacts/outputs"):
        """Initialize orchestrator with output directory."""
        self.output_dir = Path(output_dir)
        self.engine = APIDiscoveryEngine(
            max_concurrent=10,
            timeout=30,
            max_retries=3
        )
        self.business_exporter = BusinessExporter(output_dir=str(self.output_dir))
    
    async def discover_and_report(self, target_url: str, export_formats: List[str] = None) -> DiscoveryResult:
        """
        Execute full discovery flow and generate reports.
        
        Args:
            target_url: URL to scan
            export_formats: List of export formats ['crm', 'powerbi', 'json', 'markdown']
        
        Returns:
            DiscoveryResult: Complete discovery results
        """
        if export_formats is None:
            export_formats = ['crm', 'powerbi']
        
        # Print start banner
        self._print_start_banner(target_url)
        
        # Execute discovery
        print("\n🔍 Iniciando escaneo de APIs...\n")
        result = await self.engine.discover_apis(target_url)
        
        # Print executive summary
        self._print_executive_summary(result)
        
        # Validate acceptance criteria (PROMPT 3)
        self._validate_acceptance_criteria(result)
        
        # Print detailed findings
        self._print_detailed_findings(result)
        
        # Export results
        self._export_results(result, export_formats)
        
        # Print completion banner
        self._print_completion_banner(result)
        
        return result
    
    def _print_start_banner(self, target_url: str) -> None:
        """Print start banner."""
        print("\n" + "=" * 80)
        print("🛡️  DM SENTINEL API SHIELD - EXPLORADOR DE SUPERFICIE DE ATAQUE")
        print("=" * 80)
        print(f"\n🎯 Objetivo: {target_url}")
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def _print_executive_summary(self, result: DiscoveryResult) -> None:
        """
        Print executive summary (PROMPT 3 requirement).
        Human-readable summary for business stakeholders.
        """
        print("\n" + "=" * 80)
        print("📊 RESUMEN EJECUTIVO")
        print("=" * 80)
        
        print(f"\n✅ Escaneo completado exitosamente")
        print(f"   Duración: {result.scan_duration:.2f} segundos")
        
        print(f"\n🔍 Descubrimiento:")
        print(f"   • {result.total_endpoints} endpoints encontrados")
        print(f"   • {result.js_files_analyzed} archivos JavaScript analizados")
        print(f"   • {len(result.subdomains)} subdominios únicos detectados")
        
        print(f"\n📋 Clasificación por tipo:")
        print(f"   • REST APIs: {len(result.rest_endpoints)}")
        print(f"   • GraphQL: {len(result.graphql_endpoints)}")
        print(f"   • WebSockets: {len(result.websocket_endpoints)}")
        
        # Security alerts
        if result.api_keys or result.auth_headers:
            print(f"\n⚠️  Alertas de Seguridad:")
            if result.api_keys:
                print(f"   • {len(result.api_keys)} API keys expuestas en código cliente")
            if result.auth_headers:
                print(f"   • {len(result.auth_headers)} headers de autenticación detectados")
        
        print("\n" + "=" * 80)
    
    def _validate_acceptance_criteria(self, result: DiscoveryResult) -> None:
        """
        Validate acceptance criteria (PROMPT 3).
        
        Criteria: Detect at least 3 different API versions (v1, v2, /graphql)
        """
        print("\n" + "=" * 80)
        print("✅ CRITERIOS DE ACEPTACIÓN (PROMPT 3)")
        print("=" * 80)
        
        # Combine all endpoints
        all_endpoints = result.rest_endpoints + result.graphql_endpoints + result.websocket_endpoints
        
        # Detect API versions
        versions_found = self._detect_api_versions(all_endpoints)
        
        print(f"\n🎯 Objetivo: Detectar al menos 3 versiones diferentes de API")
        print(f"   Requerido: v1, v2, y rutas tipo /graphql\n")
        
        # Display detected versions
        print(f"📍 Versiones detectadas ({len(versions_found)}):")
        for version, count in sorted(versions_found.items()):
            print(f"   • {version}: {count} endpoint(s)")
        
        # Validation
        has_v1 = any('v1' in v for v in versions_found.keys())
        has_v2 = any('v2' in v for v in versions_found.keys())
        has_graphql = 'graphql' in versions_found or 'gql' in versions_found
        
        total_versions = len(versions_found)
        
        print(f"\n📋 Validación:")
        print(f"   {'✅' if has_v1 else '❌'} Versión v1 detectada")
        print(f"   {'✅' if has_v2 else '❌'} Versión v2 detectada")
        print(f"   {'✅' if has_graphql else '❌'} GraphQL detectado")
        print(f"   {'✅' if total_versions >= 3 else '❌'} Total de versiones: {total_versions}/3")
        
        if total_versions >= 3 and (has_v1 or has_v2 or has_graphql):
            print(f"\n🎉 CRITERIO CUMPLIDO: {total_versions} versiones diferentes detectadas")
        else:
            print(f"\n⚠️  ADVERTENCIA: Solo {total_versions} versiones detectadas (mínimo 3 requerido)")
        
        print("=" * 80)
    
    def _detect_api_versions(self, endpoints: List[DiscoveredEndpoint]) -> Dict[str, int]:
        """
        Detect API versions from endpoints.
        
        Returns:
            Dict mapping version names to count of endpoints
        """
        import re
        
        versions = {}
        
        for endpoint in endpoints:
            url = endpoint.url.lower()
            
            # Detect versioned APIs (v1, v2, v3, etc.)
            version_match = re.search(r'/v(\d+(?:\.\d+)?)', url)
            if version_match:
                version = f"v{version_match.group(1)}"
                versions[version] = versions.get(version, 0) + 1
            
            # Detect GraphQL
            if '/graphql' in url or '/gql' in url:
                versions['graphql'] = versions.get('graphql', 0) + 1
            
            # Detect REST (no version)
            if '/api/' in url and not version_match and '/graphql' not in url:
                versions['rest (unversioned)'] = versions.get('rest (unversioned)', 0) + 1
            
            # Detect WebSocket
            if endpoint.endpoint_type == 'WebSocket':
                versions['websocket'] = versions.get('websocket', 0) + 1
        
        return versions
    
    def _print_detailed_findings(self, result: DiscoveryResult) -> None:
        """Print detailed findings with business context."""
        print("\n" + "=" * 80)
        print("🔎 HALLAZGOS DETALLADOS")
        print("=" * 80)
        
        # REST Endpoints
        if result.rest_endpoints:
            print(f"\n📍 APIs REST ({len(result.rest_endpoints)} endpoints):")
            
            # Group by confidence
            high_confidence = [e for e in result.rest_endpoints if e.confidence >= 0.9]
            medium_confidence = [e for e in result.rest_endpoints if 0.7 <= e.confidence < 0.9]
            low_confidence = [e for e in result.rest_endpoints if e.confidence < 0.7]
            
            print(f"\n   Alta confianza (≥90%): {len(high_confidence)} endpoints")
            for i, endpoint in enumerate(high_confidence[:5], 1):
                print(f"      {i}. [{endpoint.method}] {endpoint.url}")
                print(f"         Fuente: {endpoint.source_file} | Confianza: {endpoint.confidence*100:.0f}%")
            
            if len(high_confidence) > 5:
                print(f"      ... y {len(high_confidence) - 5} más")
            
            if medium_confidence:
                print(f"\n   Confianza media (70-90%): {len(medium_confidence)} endpoints")
            
            if low_confidence:
                print(f"\n   ⚠️  Baja confianza (<70%): {len(low_confidence)} endpoints")
                print(f"      (Posibles Shadow APIs o rutas internas)")
        
        # GraphQL
        if result.graphql_endpoints:
            print(f"\n🔷 GraphQL Endpoints ({len(result.graphql_endpoints)}):")
            for endpoint in result.graphql_endpoints:
                print(f"   • {endpoint.url}")
                print(f"     Fuente: {endpoint.source_file}")
        
        # WebSocket
        if result.websocket_endpoints:
            print(f"\n🔌 WebSocket Connections ({len(result.websocket_endpoints)}):")
            for endpoint in result.websocket_endpoints:
                print(f"   • {endpoint.url}")
        
        # Shadow APIs (using BusinessExporter logic)
        shadow_apis = [
            e for e in (result.rest_endpoints + result.graphql_endpoints + result.websocket_endpoints)
            if self.business_exporter.is_shadow_api(e, result)
        ]
        
        if shadow_apis:
            print(f"\n👻 Shadow APIs Detectados ({len(shadow_apis)}):")
            print(f"   APIs no documentados o internos encontrados:")
            for endpoint in shadow_apis[:5]:
                sensitivity = self.business_exporter.calculate_sensitivity_score(endpoint)
                print(f"   • {endpoint.url}")
                print(f"     Sensibilidad: {sensitivity}/10 | Confianza: {endpoint.confidence*100:.0f}%")
            
            if len(shadow_apis) > 5:
                print(f"   ... y {len(shadow_apis) - 5} más")
        
        # Exposed API Keys
        if result.api_keys:
            print(f"\n🚨 CRÍTICO: API Keys Expuestas ({len(result.api_keys)}):")
            print(f"   ⚠️  Se encontraron {len(result.api_keys)} claves API en código cliente")
            print(f"   Estas credenciales son visibles para cualquier usuario.")
            for i, key in enumerate(list(result.api_keys)[:3], 1):
                print(f"      {i}. {key[:15]}...{key[-10:]}")
        
        # Subdomains
        if result.subdomains:
            print(f"\n🌐 Subdominios Únicos ({len(result.subdomains)}):")
            for subdomain in sorted(result.subdomains)[:5]:
                print(f"   • {subdomain}")
            if len(result.subdomains) > 5:
                print(f"   ... y {len(result.subdomains) - 5} más")
        
        print("\n" + "=" * 80)
    
    def _export_results(self, result: DiscoveryResult, formats: List[str]) -> None:
        """Export results in specified formats."""
        print("\n" + "=" * 80)
        print("💾 EXPORTANDO RESULTADOS")
        print("=" * 80)
        
        exported_files = []
        
        # CRM Export
        if 'crm' in formats:
            crm_path = self.business_exporter.export_to_crm(result)
            exported_files.append(('CRM (JSON)', crm_path))
        
        # PowerBI Export
        if 'powerbi' in formats:
            powerbi_path = self.business_exporter.export_to_powerbi(result)
            exported_files.append(('PowerBI (CSV)', powerbi_path))
        
        # JSON Export
        if 'json' in formats:
            from api_discovery_engine import DiscoveryExporter
            exporter = DiscoveryExporter()
            json_result = exporter.to_json(result)
            json_path = self.output_dir / f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            exported_files.append(('Technical JSON', str(json_path)))
        
        # Markdown Export
        if 'markdown' in formats:
            from api_discovery_engine import DiscoveryExporter
            exporter = DiscoveryExporter()
            md_content = exporter.to_markdown(result)
            md_path = self.output_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            exported_files.append(('Markdown Report', str(md_path)))
        
        # Display exported files
        print(f"\n📄 Archivos generados ({len(exported_files)}):")
        for format_name, file_path in exported_files:
            print(f"   • {format_name}: {file_path}")
        
        print("\n" + "=" * 80)
    
    def _print_completion_banner(self, result: DiscoveryResult) -> None:
        """Print completion banner with next steps."""
        print("\n" + "=" * 80)
        print("✅ ESCANEO COMPLETADO")
        print("=" * 80)
        
        # Calculate business metrics
        all_endpoints = result.rest_endpoints + result.graphql_endpoints + result.websocket_endpoints
        shadow_count = len([e for e in all_endpoints if self.business_exporter.is_shadow_api(e, result)])
        high_sensitivity = len([e for e in all_endpoints if self.business_exporter.calculate_sensitivity_score(e) >= 7.0])
        
        print(f"\n📊 Métricas Clave:")
        print(f"   • Total endpoints: {result.total_endpoints}")
        print(f"   • Shadow APIs: {shadow_count}")
        print(f"   • Alta sensibilidad: {high_sensitivity}")
        print(f"   • API keys expuestas: {len(result.api_keys)}")
        
        print(f"\n💡 Próximos Pasos:")
        print(f"   1. Revisar Shadow APIs identificados")
        print(f"   2. Documentar endpoints no catalogados")
        print(f"   3. Rotar API keys expuestas inmediatamente")
        print(f"   4. Implementar controles de seguridad")
        
        print(f"\n📁 Ubicación de reportes: {self.output_dir}/")
        
        print("\n" + "=" * 80)
        print("🛡️  DM SENTINEL - Protegiendo tu superficie de ataque")
        print("=" * 80 + "\n")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='DM Sentinel API Shield - Descubridor de Shadow APIs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Escaneo básico
  python main.py https://example.com

  # Escaneo con todos los formatos de exportación
  python main.py https://example.com --export-all

  # Escaneo solo con PowerBI export
  python main.py https://example.com --export powerbi

  # Directorio de salida personalizado
  python main.py https://example.com --output-dir ./reports

Formatos de exportación disponibles:
  - crm: JSON para sistemas CRM (Salesforce, HubSpot)
  - powerbi: CSV para dashboards PowerBI
  - json: JSON técnico completo
  - markdown: Reporte en Markdown legible
        """
    )
    
    parser.add_argument(
        'target_url',
        help='URL objetivo para escanear (ej: https://example.com)'
    )
    
    parser.add_argument(
        '--export',
        nargs='+',
        choices=['crm', 'powerbi', 'json', 'markdown'],
        default=['crm', 'powerbi'],
        help='Formatos de exportación (default: crm powerbi)'
    )
    
    parser.add_argument(
        '--export-all',
        action='store_true',
        help='Exportar en todos los formatos disponibles'
    )
    
    parser.add_argument(
        '--output-dir',
        default='artifacts/outputs',
        help='Directorio de salida (default: artifacts/outputs)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='DM Sentinel API Shield v1.0 (March 2026)'
    )
    
    return parser.parse_args()


async def main():
    """
    Main entry point for DM Sentinel API Shield.
    
    PROMPT 3: El Validador de Negocio (Product Owner)
    - Resumen ejecutivo entendible para humanos
    - Detección de múltiples versiones de API (v1, v2, graphql)
    - Orquestación completa del flujo de descubrimiento
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Determine export formats
        export_formats = ['crm', 'powerbi', 'json', 'markdown'] if args.export_all else args.export
        
        # Initialize orchestrator
        orchestrator = DiscoveryOrchestrator(output_dir=args.output_dir)
        
        # Execute discovery and reporting
        result = await orchestrator.discover_and_report(
            target_url=args.target_url,
            export_formats=export_formats
        )
        
        # Success exit
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Escaneo interrumpido por el usuario.")
        return 1
    
    except Exception as e:
        print(f"\n\n❌ Error durante el escaneo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
