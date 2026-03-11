"""
DM Sentinel - Multi-Gateway Pricing Configuration
Centralized configuration for all pricing tiers and payment gateways.

Supports:
- Stripe (One-time + Subscriptions)
- Mercado Pago (One-time + PIX)
- USDC Crypto Payments

Author: Marcelo Daniel DM
Version: 3.0.0
Date: 2026-03-11
"""

import os
from typing import Dict, List, Any

# ==================== ENVIRONMENT VARIABLES ====================
# Stripe Keys
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_...')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_...')

# Mercado Pago Keys
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY', '')

# USDC Crypto (Coinbase Commerce or similar)
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY', '')
USDC_WALLET_ADDRESS = os.getenv('USDC_WALLET_ADDRESS', '')

# Application URLs
FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://dmsentinel.com')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL', 'https://api.dmsentinel.com')

# ==================== PRICING TIERS ====================
PRICING_TIERS = {
    'checkup': {
        'id': 'checkup',
        'name': {
            'es': 'Check-up Único',
            'en': 'One-Time Check-up',
            'pt': 'Check-up Único',
            'fr': 'Check-up Unique',
            'eo': 'Unufoja Kontrolo'
        },
        'description': {
            'es': 'Auditoría completa por evento con reporte PDF profesional',
            'en': 'Complete one-time audit with professional PDF report',
            'pt': 'Auditoria completa por evento com relatório PDF profissional',
            'fr': 'Audit complet ponctuel avec rapport PDF professionnel',
            'eo': 'Kompleta unufoja kontrolo kun profesia PDF raporto'
        },
        'price_usd': 49,
        'price_brl': 249,  # ~5.08 BRL/USD conversion
        'mode': 'payment',  # One-time payment
        'features': {
            'es': [
                'Escaneo completo CMS/LMS',
                'Reporte PDF profesional',
                'Plan de mitigación detallado',
                'Entrega en < 2 minutos',
                'Detección de vulnerabilidades CVE',
                'Color-coded severity levels'
            ],
            'en': [
                'Complete CMS/LMS scan',
                'Professional PDF report',
                'Detailed mitigation plan',
                'Delivery in < 2 minutes',
                'CVE vulnerability detection',
                'Color-coded severity levels'
            ],
            'pt': [
                'Escaneamento completo CMS/LMS',
                'Relatório PDF profissional',
                'Plano de mitigação detalhado',
                'Entrega em < 2 minutos',
                'Detecção de vulnerabilidades CVE',
                'Níveis de severidade com código de cores'
            ],
            'fr': [
                'Scan complet CMS/LMS',
                'Rapport PDF professionnel',
                'Plan de mitigation détaillé',
                'Livraison en < 2 minutes',
                'Détection de vulnérabilités CVE',
                'Niveaux de séverité codés par couleur'
            ],
            'eo': [
                'Kompleta CMS/LMS skano',
                'Profesia PDF raporto',
                'Detala milda plano',
                'Liverado en < 2 minutoj',
                'CVE-vundebleco detekto',
                'Kolorkodaj severecniveloj'
            ]
        },
        'limitations': {
            'es': ['Sin monitoreo continuo', 'Sin alertas Telegram', 'Sin historial'],
            'en': ['No continuous monitoring', 'No Telegram alerts', 'No history'],
            'pt': ['Sem monitoramento contínuo', 'Sem alertas do Telegram', 'Sem histórico'],
            'fr': ['Pas de surveillance continue', 'Pas d\'alertes Telegram', 'Pas d\'historique'],
            'eo': ['Sen kontinua monitoro', 'Sen Telegram-avertoj', 'Sen historio']
        },
        'stripe': {
            'price_id': os.getenv('STRIPE_PRICE_CHECKUP', 'price_checkup_49usd'),
            'product_id': 'prod_checkup'
        },
        'mercadopago': {
            'title': 'DM Sentinel - Check-up Único',
            'unit_price': 49,
            'currency_id': 'USD'
        },
        'usdc': {
            'amount': 49,
            'network': 'ethereum'  # or 'polygon' for lower fees
        }
    },
    
    'sentinel': {
        'id': 'sentinel',
        'name': {
            'es': 'Sentinel',
            'en': 'Sentinel',
            'pt': 'Sentinel',
            'fr': 'Sentinel',
            'eo': 'Sentinel'
        },
        'description': {
            'es': 'Monitoreo mensual con alertas críticas y reportes automatizados',
            'en': 'Monthly monitoring with critical alerts and automated reports',
            'pt': 'Monitoramento mensal com alertas críticos e relatórios automatizados',
            'fr': 'Surveillance mensuelle avec alertes critiques et rapports automatisés',
            'eo': 'Monata monitoro kun kritikaj avertoj kaj aŭtomataj raportoj'
        },
        'price_usd': 19,
        'price_brl': 97,  # ~5.08 BRL/USD conversion
        'mode': 'subscription',  # Recurring subscription
        'interval': 'month',
        'features': {
            'es': [
                'Todo lo del Check-up',
                'Escaneo mensual automatizado',
                'Alertas críticas por Telegram',
                'Historial de auditorías',
                'Soporte por email',
                'Dashboard web básico'
            ],
            'en': [
                'Everything in Check-up',
                'Automated monthly scanning',
                'Critical Telegram alerts',
                'Audit history',
                'Email support',
                'Basic web dashboard'
            ],
            'pt': [
                'Tudo do Check-up',
                'Escaneamento mensal automatizado',
                'Alertas críticos do Telegram',
                'Histórico de auditorias',
                'Suporte por email',
                'Dashboard web básico'
            ],
            'fr': [
                'Tout du Check-up',
                'Scan mensuel automatisé',
                'Alertes Telegram critiques',
                'Historique d\'audits',
                'Support par email',
                'Tableau de bord web basique'
            ],
            'eo': [
                'Ĉio de Check-up',
                'Aŭtomata monata skanado',
                'Kritikaj Telegram-avertoj',
                'Kontrolhistorio',
                'Helpdesko per retpoŝto',
                'Baza reta panelo'
            ]
        },
        'stripe': {
            'price_id': os.getenv('STRIPE_PRICE_SENTINEL', 'price_sentinel_19usd_monthly'),
            'product_id': 'prod_sentinel'
        },
        'mercadopago': {
            'title': 'DM Sentinel - Suscripción Mensual',
            'unit_price': 19,
            'currency_id': 'USD',
            'frequency': 1,
            'frequency_type': 'months'
        },
        'usdc': {
            'amount': 19,
            'network': 'polygon',  # Lower fees for recurring
            'note': 'Manual renewal required each month'
        }
    },
    
    'pro': {
        'id': 'pro',
        'name': {
            'es': 'Sentinel Pro Full',
            'en': 'Sentinel Pro Full',
            'pt': 'Sentinel Pro Full',
            'fr': 'Sentinel Pro Full',
            'eo': 'Sentinel Pro Plena'
        },
        'description': {
            'es': 'Monitoreo continuo 24/7 con todas las herramientas v2.0',
            'en': 'Continuous 24/7 monitoring with all v2.0 tools',
            'pt': 'Monitoramento contínuo 24/7 com todas as ferramentas v2.0',
            'fr': 'Surveillance continue 24/7 avec tous les outils v2.0',
            'eo': 'Kontinua 24/7 monitoro kun ĉiuj v2.0 iloj'
        },
        'price_usd': 99,
        'price_brl': 503,  # ~5.08 BRL/USD conversion
        'mode': 'subscription',  # Recurring subscription
        'interval': 'month',
        'features': {
            'es': [
                'Todo lo de Sentinel',
                'Monitoreo en tiempo real 24/7',
                'Port Scanner completo',
                'DNS Health Check',
                'Secret Scanning (API keys)',
                'Soporte prioritario 24/7',
                'Dashboard Power BI',
                'API REST completa',
                'Integraciones personalizadas'
            ],
            'en': [
                'Everything in Sentinel',
                'Real-time 24/7 monitoring',
                'Complete port scanner',
                'DNS health check',
                'Secret scanning (API keys)',
                'Priority 24/7 support',
                'Power BI dashboard',
                'Full REST API',
                'Custom integrations'
            ],
            'pt': [
                'Tudo do Sentinel',
                'Monitoramento em tempo real 24/7',
                'Port Scanner completo',
                'Verificação de integridade DNS',
                'Escaneamento de segredos (chaves API)',
                'Suporte prioritário 24/7',
                'Dashboard Power BI',
                'API REST completa',
                'Integrações personalizadas'
            ],
            'fr': [
                'Tout de Sentinel',
                'Surveillance en temps réel 24/7',
                'Scan de ports complet',
                'Vérification de santé DNS',
                'Scan de secrets (clés API)',
                'Support prioritaire 24/7',
                'Tableau de bord Power BI',
                'API REST complète',
                'Intégrations personnalisées'
            ],
            'eo': [
                'Ĉio de Sentinel',
                'Realtempa 24/7 monitoro',
                'Kompleta porda skanilo',
                'DNS sano-kontrolo',
                'Sekreta skanado (API-ŝlosiloj)',
                'Priorita 24/7 helpdesko',
                'Power BI panelo',
                'Kompleta REST API',
                'Personigitaj integrigoj'
            ]
        },
        'stripe': {
            'price_id': os.getenv('STRIPE_PRICE_PRO', 'price_pro_99usd_monthly'),
            'product_id': 'prod_pro'
        },
        'mercadopago': {
            'title': 'DM Sentinel Pro - Suscripción Premium',
            'unit_price': 99,
            'currency_id': 'USD',
            'frequency': 1,
            'frequency_type': 'months'
        },
        'usdc': {
            'amount': 99,
            'network': 'polygon',
            'note': 'Manual renewal required each month'
        }
    }
}

# ==================== PAYMENT GATEWAY CONFIGURATIONS ====================
GATEWAY_CONFIG = {
    'stripe': {
        'enabled': True,
        'name': 'Stripe',
        'icon': 'credit-card',
        'supported_currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
        'supported_modes': ['payment', 'subscription'],
        'webhook_path': '/webhook',
        'success_url': f'{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
        'cancel_url': f'{FRONTEND_URL}/cancel',
        'display_order': 1
    },
    
    'pix': {
        'enabled': True,
        'name': 'PIX',
        'icon': 'smartphone',
        'supported_currencies': ['BRL'],
        'supported_modes': ['payment'],  # One-time only for now
        'webhook_path': '/webhook/mercadopago',
        'display_order': 2,
        'region': 'Brazil',
        'instant_approval': True
    },
    
    'mercadopago': {
        'enabled': True,
        'name': 'Mercado Pago',
        'icon': 'wallet',
        'supported_currencies': ['USD', 'BRL', 'ARS', 'MXN', 'CLP', 'COP'],
        'supported_modes': ['payment', 'subscription'],
        'webhook_path': '/webhook/mercadopago',
        'success_url': f'{FRONTEND_URL}/success',
        'failure_url': f'{FRONTEND_URL}/failure',
        'pending_url': f'{FRONTEND_URL}/pending',
        'display_order': 3,
        'region': 'Latin America'
    },
    
    'usdc': {
        'enabled': True,
        'name': 'USDC',
        'icon': 'coins',
        'supported_currencies': ['USDC'],
        'supported_modes': ['payment'],  # Manual renewal for subscriptions
        'webhook_path': '/webhook/crypto',
        'display_order': 4,
        'networks': ['ethereum', 'polygon'],
        'confirmation_blocks': 12,  # Required confirmations
        'note': 'Stablecoin payments on blockchain'
    }
}

# ==================== HELPER FUNCTIONS ====================

def get_plan_config(plan_id: str) -> Dict[str, Any]:
    """Get configuration for a specific pricing plan."""
    return PRICING_TIERS.get(plan_id)


def get_gateway_config(gateway: str) -> Dict[str, Any]:
    """Get configuration for a specific payment gateway."""
    return GATEWAY_CONFIG.get(gateway)


def get_localized_plan_name(plan_id: str, language: str = 'es') -> str:
    """Get localized plan name."""
    plan = get_plan_config(plan_id)
    if not plan:
        return plan_id
    return plan['name'].get(language, plan['name']['es'])


def get_localized_features(plan_id: str, language: str = 'es') -> List[str]:
    """Get localized feature list for a plan."""
    plan = get_plan_config(plan_id)
    if not plan:
        return []
    return plan['features'].get(language, plan['features']['es'])


def get_plan_price(plan_id: str, currency: str = 'USD') -> float:
    """Get plan price in specified currency."""
    plan = get_plan_config(plan_id)
    if not plan:
        return 0
    
    if currency == 'USD':
        return plan['price_usd']
    elif currency == 'BRL':
        return plan['price_brl']
    else:
        # Default to USD
        return plan['price_usd']


def is_subscription_plan(plan_id: str) -> bool:
    """Check if plan is a subscription (vs one-time payment)."""
    plan = get_plan_config(plan_id)
    if not plan:
        return False
    return plan['mode'] == 'subscription'


def get_stripe_price_id(plan_id: str) -> str:
    """Get Stripe Price ID for a plan."""
    plan = get_plan_config(plan_id)
    if not plan or 'stripe' not in plan:
        return ''
    return plan['stripe'].get('price_id', '')


def get_available_gateways_for_plan(plan_id: str, currency: str = 'USD') -> List[str]:
    """Get list of available payment gateways for a specific plan."""
    plan = get_plan_config(plan_id)
    if not plan:
        return []
    
    available = []
    
    for gateway_id, gateway_config in GATEWAY_CONFIG.items():
        if not gateway_config['enabled']:
            continue
        
        # Check if gateway supports the plan mode
        if plan['mode'] not in gateway_config['supported_modes']:
            continue
        
        # Check if gateway supports the currency
        if currency not in gateway_config['supported_currencies'] and currency != 'USDC':
            continue
        
        available.append(gateway_id)
    
    # Sort by display order
    available.sort(key=lambda x: GATEWAY_CONFIG[x]['display_order'])
    
    return available


def validate_checkout_data(plan_id: str, gateway: str, target_url: str, email: str) -> tuple[bool, str]:
    """
    Validate checkout data before processing payment.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check plan exists
    if plan_id not in PRICING_TIERS:
        return False, f"Invalid plan ID: {plan_id}"
    
    # Check gateway exists and is enabled
    gateway_config = get_gateway_config(gateway)
    if not gateway_config or not gateway_config['enabled']:
        return False, f"Invalid or disabled gateway: {gateway}"
    
    # Check gateway supports this plan type
    plan = get_plan_config(plan_id)
    if plan['mode'] not in gateway_config['supported_modes']:
        return False, f"Gateway {gateway} does not support {plan['mode']} mode"
    
    # Validate target URL
    if not target_url or not (target_url.startswith('http://') or target_url.startswith('https://')):
        return False, "Invalid target URL"
    
    # Validate email
    if not email or '@' not in email:
        return False, "Invalid email address"
    
    return True, ""


# ==================== EXPORTS ====================
__all__ = [
    'PRICING_TIERS',
    'GATEWAY_CONFIG',
    'get_plan_config',
    'get_gateway_config',
    'get_localized_plan_name',
    'get_localized_features',
    'get_plan_price',
    'is_subscription_plan',
    'get_stripe_price_id',
    'get_available_gateways_for_plan',
    'validate_checkout_data',
    'STRIPE_SECRET_KEY',
    'STRIPE_WEBHOOK_SECRET',
    'MERCADOPAGO_ACCESS_TOKEN',
    'COINBASE_API_KEY'
]
