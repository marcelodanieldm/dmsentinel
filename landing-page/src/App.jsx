import React, { useState, useEffect } from 'react';
import './App.css';

// ============================================================================
// PAYMENT GATEWAY INTEGRATIONS - PROMPT 2
// ============================================================================

// Note: In production, these would come from environment variables
const STRIPE_PUBLIC_KEY = process.env.REACT_APP_STRIPE_PUBLIC_KEY || 'pk_test_...';
const MERCADO_PAGO_PUBLIC_KEY = process.env.REACT_APP_MERCADO_PAGO_PUBLIC_KEY || 'APP_USR-...';
const WEBHOOK_URL = process.env.REACT_APP_WEBHOOK_URL || 'https://api.dmsentinel.com/webhook/payment';

// Payment Gateway APIs (would be loaded from CDN in production)
const loadStripe = async () => {
  // Load Stripe.js from CDN
  if (window.Stripe) return window.Stripe(STRIPE_PUBLIC_KEY);
  
  const script = document.createElement('script');
  script.src = 'https://js.stripe.com/v3/';
  document.head.appendChild(script);
  
  return new Promise((resolve) => {
    script.onload = () => resolve(window.Stripe(STRIPE_PUBLIC_KEY));
  });
};

const loadMercadoPago = async () => {
  // Load Mercado Pago SDK
  if (window.MercadoPago) return new window.MercadoPago(MERCADO_PAGO_PUBLIC_KEY);
  
  const script = document.createElement('script');
  script.src = 'https://sdk.mercadopago.com/js/v2';
  document.head.appendChild(script);
  
  return new Promise((resolve) => {
    script.onload = () => resolve(new window.MercadoPago(MERCADO_PAGO_PUBLIC_KEY));
  });
};

// ============================================================================
// MULTI-LANGUAGE CONTENT - 5 LANGUAGES
// ============================================================================

const TRANSLATIONS = {
  es: {
    lang: 'es',
    name: 'Español',
    hero: {
      title: 'Auditorías Web3 con IA',
      subtitle: 'Protege tu Smart Contract antes del despliegue',
      cta: 'Auditar Ahora',
      price: 'Desde $2,500 USD'
    },
    vulnerability: {
      title: 'Vulnerabilidad Comprobable',
      subtitle: 'Ejemplo real detectado por DM Sentinel',
      issue: 'Reentrancy en función withdraw()',
      severity: 'Crítico',
      description: 'Patrón de reentrancy detectado. Atacante puede drenar fondos.',
      line: 'Línea 42: Llamada externa antes de actualizar balance'
    },
    features: {
      title: 'Tecnología de Punta',
      items: [
        { title: 'IA Potenciada', desc: 'Slither + Mythril + GPT-4 combinados' },
        { title: 'QA Automatizado', desc: 'Playwright testa tu dApp en 50+ escenarios' },
        { title: 'Intel On-Chain', desc: 'TVL, volumen 24h y riesgo financiero real' },
        { title: 'Entrega Power BI', desc: 'Dashboard ejecutivo con 30+ métricas' }
      ]
    },
    pricing: {
      title: 'Precios Transparentes',
      basic: {
        name: 'Básico',
        price: '$2,500',
        features: [
          'Auditoría de 1 contrato',
          'Reporte PDF Cyber-Dark',
          'QA de dApp (50 tests)',
          'Inteligencia de mercado',
          'Entrega en 3-5 días'
        ],
        cta: 'Empezar'
      },
      pro: {
        name: 'Profesional',
        price: '$7,500',
        features: [
          'Hasta 5 contratos',
          'Revisión de código manual',
          'Tests de penetración',
          'Dashboard Power BI',
          'Soporte prioritario 24/7',
          'Entrega en 2-3 días'
        ],
        cta: 'Contratar',
        badge: 'Más Popular'
      },
      enterprise: {
        name: 'Enterprise',
        price: 'Consultar',
        features: [
          'Contratos ilimitados',
          'Auditoría continua (CI/CD)',
          'Bug bounty privado',
          'Retainer mensual',
          'SLA garantizado',
          'Entrega en 24-48h'
        ],
        cta: 'Contactar'
      }
    },
    integrations: {
      title: 'Integraciones Sin Fricciones',
      subtitle: 'Aceptamos pagos en tu moneda local'
    },
    case_studies: {
      title: 'Vulnerabilidades Críticas: Casos Reales',
      subtitle: 'Aprende de $2.3B+ explotados en protocolos DeFi',
      cases: [
        {
          id: 'drainer',
          icon: '🎣',
          title: 'Drainer Attack: $100M Robados en 24 Horas',
          date: 'Octubre 2023 - Pink Drainer',
          impact: '$100M+ robados',
          problem_title: 'El Problema',
          problem_desc: 'Un usuario firma una transacción que parece legítima ("Claim Airdrop"), pero en realidad es un approve() ilimitado. El atacante drena todos los tokens ERC-20 y NFTs de la wallet en segundos.',
          technical: 'Técnicamente: El contrato malicioso utiliza setApprovalForAll() y transferFrom() para vaciar la wallet sin que el usuario lo note hasta que es tarde.',
          stats: [
            '15,000+ wallets comprometidas',
            '$100M+ en tokens robados',
            '80% de víctimas no revisaron el contrato'
          ],
          solution_title: 'Solución DM Sentinel',
          solution_desc: 'Nuestro sistema de Pentesting + Playwright QA simula ataques de phishing y aprobaciones maliciosas. Analizamos cada función approve(), transferFrom() y setApprovalForAll() en busca de permisos excesivos.',
          solution_features: [
            '🔍 Análisis de permisos excesivos (approve ilimitado)',
            '🤖 Playwright: Simula 50+ escenarios de phishing',
            '⚡ Detección de contratos "honeypot" en tiempo real',
            '📊 Auditoría de frontend + backend completo'
          ],
          cta: 'Proteger mi Protocolo Ahora'
        },
        {
          id: 'reentrancy',
          icon: '♻️',
          title: 'The DAO Hack: $60M Perdidos',
          date: 'Junio 2016 - The DAO',
          impact: '$60M robados → Hard Fork de Ethereum',
          problem_title: 'El Problema',
          problem_desc: 'El error más famoso de la historia DeFi. Una función withdraw() actualizaba el balance DESPUÉS de enviar ETH, permitiendo llamadas recursivas que vaciaron el contrato antes de que se actualizara el estado.',
          technical: 'Técnicamente: El atacante llamó a la función withdraw() de forma recursiva (reentrancy) antes de que el balance se actualizara, drenando todo el ETH del contrato. Patrón: call() antes de balances[msg.sender] -= amount.',
          stats: [
            '$60M robados (15% del supply de ETH)',
            'Hard fork de Ethereum (ETH vs ETC)',
            'Pausa de 27 días en la red'
          ],
          solution_title: 'Solución DM Sentinel',
          solution_desc: 'DM Sentinel detecta automáticamente patrones de reentrancy con Slither + Mythril. Verificamos que TODAS las funciones sigan el patrón Checks-Effects-Interactions y utilizamos Playwright para simular ataques de reentrancy en vivo.',
          solution_features: [
            '🛡️ Detección automática de reentrancy con Slither',
            '✅ Verificación de patrón Checks-Effects-Interactions',
            '🔐 ReentrancyGuard de OpenZeppelin integrado',
            '🧪 Playwright: Test de reentrancy multi-llamada'
          ],
          cta: 'Auditar mi Protocolo Ahora'
        },
        {
          id: 'oracle',
          icon: '📡',
          title: 'Oracle Manipulation: Ataques de Flash Loan',
          date: '2020-2023 - Múltiples protocolos',
          impact: '$200M+ robados en ataques de precio',
          problem_title: 'El Problema',
          problem_desc: 'Un atacante toma un flash loan de $10M, manipula el precio del token en un DEX de baja liquidez, y el protocolo víctima usa ese precio falso para liquidar posiciones legítimas, embolsándose las colaterales.',
          technical: 'Técnicamente: Los protocolos confían en un único oráculo de precio (por ejemplo, precio spot de Uniswap V2). El atacante manipula el pool con un trade masivo, el oráculo reporta el precio falso, y el protocolo ejecuta liquidaciones incorrectas.',
          stats: [
            '$200M+ robados en 2020-2023',
            '20+ protocolos DeFi afectados',
            'Flash loans de hasta $1B usados'
          ],
          solution_title: 'Solución DM Sentinel',
          solution_desc: 'DM Sentinel verifica la robustez de tus oráculos con Webscraping de TVL en tiempo real. Comparamos precios de Chainlink, Pyth, y DEXs. Playwright simula ataques de flash loan para verificar que tu protocolo resiste manipulación de precios.',
          solution_features: [
            '📊 Webscraping de TVL de 10+ fuentes',
            '🔗 Verificación de oráculos Chainlink/Pyth',
            '⚡ Playwright: Simula flash loans de $100M+',
            '🛡️ Test de manipulación de liquidez en vivo'
          ],
          cta: 'Asegurar mis Oráculos Ahora'
        }
      ],
      final_cta: {
        title: '¿Tu protocolo está protegido?',
        subtitle: 'No esperes a ser el próximo hack de $100M en las noticias',
        button: 'Solicitar Auditoría One-Shot'
      }
    },
    cta_final: {
      title: '¿Listo para auditar tu protocolo?',
      subtitle: 'Únete a los 150+ proyectos que confían en DM Sentinel',
      button: 'Solicitar Auditoría Gratuita'
    },
    footer: {
      company: '© 2026 DM Sentinel. Todos los derechos reservados.',
      contact: 'Contacto: security@dmsentinel.com'
    },
    payment: {
      modal_title: 'Seleccionar Método de Pago',
      modal_subtitle: 'Elige tu forma de pago preferida',
      plan_selected: 'Plan seleccionado',
      amount: 'Monto',
      methods: {
        card: 'Tarjeta de Crédito',
        card_desc: 'Visa, Mastercard, Amex vía Stripe',
        pix: 'Pix',
        pix_desc: 'Código QR - Pago instantáneo',
        crypto: 'Criptomonedas',
        crypto_desc: 'USDC en Ethereum/Polygon'
      },
      form: {
        contract_url: 'URL del contrato a auditar',
        contract_placeholder: 'https://etherscan.io/address/0x...',
        wallet: 'Tu wallet (opcional)',
        wallet_placeholder: '0x...',
        email: 'Email de contacto',
        email_placeholder: 'tu@email.com',
        pay_button: 'Pagar',
        processing: 'Procesando...',
        cancel: 'Cancelar'
      },
      pix: {
        title: 'Escanea el código QR',
        instructions: 'Abre tu app bancaria y escanea el código',
        copy_code: 'Copiar código Pix',
        waiting: 'Esperando confirmación del pago...'
      },
      crypto: {
        connect: 'Conectar Wallet',
        connected: 'Wallet conectada',
        approve: 'Aprobar USDC',
        pay: 'Pagar con USDC',
        network: 'Red',
        balance: 'Balance'
      },
      success: {
        title: '¡Pago Exitoso!',
        message: 'Tu auditoría será procesada en breve',
        email_sent: 'Te enviamos un email de confirmación'
      },
      error: {
        title: 'Error en el Pago',
        message: 'Hubo un problema procesando tu pago',
        try_again: 'Intentar de nuevo'
      }
    }
  },
  
  en: {
    lang: 'en',
    name: 'English',
    hero: {
      title: 'AI-Powered Web3 Audits',
      subtitle: 'Secure your Smart Contract before deployment',
      cta: 'Audit Now',
      price: 'From $2,500 USD'
    },
    vulnerability: {
      title: 'Verifiable Vulnerability',
      subtitle: 'Real example detected by DM Sentinel',
      issue: 'Reentrancy in withdraw() function',
      severity: 'Critical',
      description: 'Reentrancy pattern detected. Attacker can drain funds.',
      line: 'Line 42: External call before balance update'
    },
    features: {
      title: 'Cutting-Edge Technology',
      items: [
        { title: 'AI-Powered', desc: 'Slither + Mythril + GPT-4 combined' },
        { title: 'Automated QA', desc: 'Playwright tests your dApp in 50+ scenarios' },
        { title: 'On-Chain Intel', desc: 'TVL, 24h volume & real financial risk' },
        { title: 'Power BI Delivery', desc: 'Executive dashboard with 30+ metrics' }
      ]
    },
    pricing: {
      title: 'Transparent Pricing',
      basic: {
        name: 'Basic',
        price: '$2,500',
        features: [
          'Audit of 1 contract',
          'Cyber-Dark PDF Report',
          'dApp QA (50 tests)',
          'Market intelligence',
          'Delivery in 3-5 days'
        ],
        cta: 'Get Started'
      },
      pro: {
        name: 'Professional',
        price: '$7,500',
        features: [
          'Up to 5 contracts',
          'Manual code review',
          'Penetration testing',
          'Power BI Dashboard',
          'Priority support 24/7',
          'Delivery in 2-3 days'
        ],
        cta: 'Hire Now',
        badge: 'Most Popular'
      },
      enterprise: {
        name: 'Enterprise',
        price: 'Contact',
        features: [
          'Unlimited contracts',
          'Continuous audit (CI/CD)',
          'Private bug bounty',
          'Monthly retainer',
          'Guaranteed SLA',
          'Delivery in 24-48h'
        ],
        cta: 'Contact Us'
      }
    },
    integrations: {
      title: 'Frictionless Integrations',
      subtitle: 'We accept payments in your local currency'
    },
    case_studies: {
      title: 'Critical Vulnerabilities: Real Cases',
      subtitle: 'Learn from $2.3B+ exploited in DeFi protocols',
      cases: [
        {
          id: 'drainer',
          icon: '🎣',
          title: 'Drainer Attack: $100M Stolen in 24 Hours',
          date: 'October 2023 - Pink Drainer',
          impact: '$100M+ stolen',
          problem_title: 'The Problem',
          problem_desc: 'A user signs a transaction that looks legitimate ("Claim Airdrop"), but it\'s actually an unlimited approve(). The attacker drains all ERC-20 tokens and NFTs from the wallet in seconds.',
          technical: 'Technically: The malicious contract uses setApprovalForAll() and transferFrom() to empty the wallet without the user noticing until it\'s too late.',
          stats: [
            '15,000+ wallets compromised',
            '$100M+ in stolen tokens',
            '80% of victims didn\'t review the contract'
          ],
          solution_title: 'DM Sentinel Solution',
          solution_desc: 'Our Pentesting + Playwright QA system simulates phishing attacks and malicious approvals. We analyze every approve(), transferFrom() and setApprovalForAll() function for excessive permissions.',
          solution_features: [
            '🔍 Excessive permissions analysis (unlimited approve)',
            '🤖 Playwright: Simulates 50+ phishing scenarios',
            '⚡ Real-time "honeypot" contract detection',
            '📊 Full frontend + backend audit'
          ],
          cta: 'Protect My Protocol Now'
        },
        {
          id: 'reentrancy',
          icon: '♻️',
          title: 'The DAO Hack: $60M Lost',
          date: 'June 2016 - The DAO',
          impact: '$60M stolen → Ethereum Hard Fork',
          problem_title: 'The Problem',
          problem_desc: 'The most famous bug in DeFi history. A withdraw() function updated the balance AFTER sending ETH, allowing recursive calls that drained the contract before the state was updated.',
          technical: 'Technically: The attacker called the withdraw() function recursively (reentrancy) before the balance was updated, draining all ETH from the contract. Pattern: call() before balances[msg.sender] -= amount.',
          stats: [
            '$60M stolen (15% of ETH supply)',
            'Ethereum hard fork (ETH vs ETC)',
            '27-day network pause'
          ],
          solution_title: 'DM Sentinel Solution',
          solution_desc: 'DM Sentinel automatically detects reentrancy patterns with Slither + Mythril. We verify that ALL functions follow the Checks-Effects-Interactions pattern and use Playwright to simulate live reentrancy attacks.',
          solution_features: [
            '🛡️ Automatic reentrancy detection with Slither',
            '✅ Checks-Effects-Interactions pattern verification',
            '🔐 OpenZeppelin ReentrancyGuard integrated',
            '🧪 Playwright: Multi-call reentrancy tests'
          ],
          cta: 'Audit My Protocol Now'
        },
        {
          id: 'oracle',
          icon: '📡',
          title: 'Oracle Manipulation: Flash Loan Attacks',
          date: '2020-2023 - Multiple protocols',
          impact: '$200M+ stolen in price attacks',
          problem_title: 'The Problem',
          problem_desc: 'An attacker takes a $10M flash loan, manipulates the token price on a low-liquidity DEX, and the victim protocol uses that fake price to liquidate legitimate positions, pocketing the collateral.',
          technical: 'Technically: Protocols trust a single price oracle (e.g., Uniswap V2 spot price). The attacker manipulates the pool with a massive trade, the oracle reports the fake price, and the protocol executes incorrect liquidations.',
          stats: [
            '$200M+ stolen in 2020-2023',
            '20+ DeFi protocols affected',
            'Flash loans up to $1B used'
          ],
          solution_title: 'DM Sentinel Solution',
          solution_desc: 'DM Sentinel verifies your oracle robustness with real-time TVL webscraping. We compare prices from Chainlink, Pyth, and DEXs. Playwright simulates flash loan attacks to verify your protocol resists price manipulation.',
          solution_features: [
            '📊 TVL webscraping from 10+ sources',
            '🔗 Chainlink/Pyth oracle verification',
            '⚡ Playwright: Simulates $100M+ flash loans',
            '🛡️ Live liquidity manipulation testing'
          ],
          cta: 'Secure My Oracles Now'
        }
      ],
      final_cta: {
        title: 'Is your protocol protected?',
        subtitle: 'Don\'t wait to be the next $100M hack in the news',
        button: 'Request One-Shot Audit'
      }
    },
    cta_final: {
      title: 'Ready to audit your protocol?',
      subtitle: 'Join 150+ projects that trust DM Sentinel',
      button: 'Request Free Audit'
    },
    footer: {
      company: '© 2026 DM Sentinel. All rights reserved.',
      contact: 'Contact: security@dmsentinel.com'
    },
    payment: {
      modal_title: 'Select Payment Method',
      modal_subtitle: 'Choose your preferred payment method',
      plan_selected: 'Selected plan',
      amount: 'Amount',
      methods: {
        card: 'Credit Card',
        card_desc: 'Visa, Mastercard, Amex via Stripe',
        pix: 'Pix',
        pix_desc: 'QR Code - Instant payment',
        crypto: 'Cryptocurrency',
        crypto_desc: 'USDC on Ethereum/Polygon'
      },
      form: {
        contract_url: 'Contract URL to audit',
        contract_placeholder: 'https://etherscan.io/address/0x...',
        wallet: 'Your wallet (optional)',
        wallet_placeholder: '0x...',
        email: 'Contact email',
        email_placeholder: 'your@email.com',
        pay_button: 'Pay Now',
        processing: 'Processing...',
        cancel: 'Cancel'
      },
      pix: {
        title: 'Scan QR Code',
        instructions: 'Open your banking app and scan the code',
        copy_code: 'Copy Pix code',
        waiting: 'Waiting for payment confirmation...'
      },
      crypto: {
        connect: 'Connect Wallet',
        connected: 'Wallet Connected',
        approve: 'Approve USDC',
        pay: 'Pay with USDC',
        network: 'Network',
        balance: 'Balance'
      },
      success: {
        title: 'Payment Successful!',
        message: 'Your audit will be processed shortly',
        email_sent: 'We sent you a confirmation email'
      },
      error: {
        title: 'Payment Error',
        message: 'There was a problem processing your payment',
        try_again: 'Try again'
      }
    }
  },
  
  fr: {
    lang: 'fr',
    name: 'Français',
    hero: {
      title: 'Audits Web3 alimentés par IA',
      subtitle: 'Sécurisez votre Smart Contract avant le déploiement',
      cta: 'Auditer Maintenant',
      price: 'À partir de $2,500 USD'
    },
    vulnerability: {
      title: 'Vulnérabilité Vérifiable',
      subtitle: 'Exemple réel détecté par DM Sentinel',
      issue: 'Reentrancy dans la fonction withdraw()',
      severity: 'Critique',
      description: 'Modèle de reentrancy détecté. L\'attaquant peut vider les fonds.',
      line: 'Ligne 42: Appel externe avant mise à jour du solde'
    },
    features: {
      title: 'Technologie de Pointe',
      items: [
        { title: 'IA Puissante', desc: 'Slither + Mythril + GPT-4 combinés' },
        { title: 'QA Automatisé', desc: 'Playwright teste votre dApp dans 50+ scénarios' },
        { title: 'Intel On-Chain', desc: 'TVL, volume 24h et risque financier réel' },
        { title: 'Livraison Power BI', desc: 'Tableau de bord exécutif avec 30+ métriques' }
      ]
    },
    pricing: {
      title: 'Prix Transparents',
      basic: {
        name: 'Basique',
        price: '$2,500',
        features: [
          'Audit de 1 contrat',
          'Rapport PDF Cyber-Dark',
          'QA de dApp (50 tests)',
          'Intelligence du marché',
          'Livraison en 3-5 jours'
        ],
        cta: 'Commencer'
      },
      pro: {
        name: 'Professionnel',
        price: '$7,500',
        features: [
          'Jusqu\'à 5 contrats',
          'Révision manuelle du code',
          'Tests de pénétration',
          'Tableau Power BI',
          'Support prioritaire 24/7',
          'Livraison en 2-3 jours'
        ],
        cta: 'Engager',
        badge: 'Plus Populaire'
      },
      enterprise: {
        name: 'Enterprise',
        price: 'Consulter',
        features: [
          'Contrats illimités',
          'Audit continu (CI/CD)',
          'Bug bounty privé',
          'Retainer mensuel',
          'SLA garanti',
          'Livraison en 24-48h'
        ],
        cta: 'Contacter'
      }
    },
    integrations: {
      title: 'Intégrations Sans Friction',
      subtitle: 'Nous acceptons les paiements dans votre devise locale'
    },
    case_studies: {
      title: 'Vulnérabilités Critiques: Cas Réels',
      subtitle: 'Apprenez de $2.3B+ exploités dans les protocoles DeFi',
      cases: [
        {
          id: 'drainer',
          icon: '🎣',
          title: 'Attaque Drainer: $100M Volés en 24 Heures',
          date: 'Octobre 2023 - Pink Drainer',
          impact: '$100M+ volés',
          problem_title: 'Le Problème',
          problem_desc: 'Un utilisateur signe une transaction qui semble légitime ("Claim Airdrop"), mais c\'est en réalité un approve() illimité. L\'attaquant draine tous les tokens ERC-20 et NFTs du wallet en secondes.',
          technical: 'Techniquement: Le contrat malveillant utilise setApprovalForAll() et transferFrom() pour vider le wallet sans que l\'utilisateur ne le remarque jusqu\'à ce qu\'il soit trop tard.',
          stats: [
            '15,000+ wallets compromis',
            '$100M+ de tokens volés',
            '80% des victimes n\'ont pas examiné le contrat'
          ],
          solution_title: 'Solution DM Sentinel',
          solution_desc: 'Notre système Pentesting + Playwright QA simule les attaques de phishing et les approbations malveillantes. Nous analysons chaque fonction approve(), transferFrom() et setApprovalForAll() pour détecter les permissions excessives.',
          solution_features: [
            '🔍 Analyse des permissions excessives (approve illimité)',
            '🤖 Playwright: Simule 50+ scénarios de phishing',
            '⚡ Détection de contrats "honeypot" en temps réel',
            '📊 Audit complet frontend + backend'
          ],
          cta: 'Protéger Mon Protocole Maintenant'
        },
        {
          id: 'reentrancy',
          icon: '♻️',
          title: 'The DAO Hack: $60M Perdus',
          date: 'Juin 2016 - The DAO',
          impact: '$60M volés → Hard Fork d\'Ethereum',
          problem_title: 'Le Problème',
          problem_desc: 'Le bug le plus célèbre de l\'histoire DeFi. Une fonction withdraw() mettait à jour le solde APRÈS avoir envoyé l\'ETH, permettant des appels récursifs qui ont vidé le contrat avant la mise à jour de l\'état.',
          technical: 'Techniquement: L\'attaquant a appelé la fonction withdraw() de manière récursive (reentrancy) avant que le solde ne soit mis à jour, drainant tout l\'ETH du contrat. Pattern: call() avant balances[msg.sender] -= amount.',
          stats: [
            '$60M volés (15% du supply ETH)',
            'Hard fork d\'Ethereum (ETH vs ETC)',
            'Pause réseau de 27 jours'
          ],
          solution_title: 'Solution DM Sentinel',
          solution_desc: 'DM Sentinel détecte automatiquement les patterns de reentrancy avec Slither + Mythril. Nous vérifions que TOUTES les fonctions suivent le pattern Checks-Effects-Interactions et utilisons Playwright pour simuler des attaques de reentrancy en direct.',
          solution_features: [
            '🛡️ Détection automatique de reentrancy avec Slither',
            '✅ Vérification du pattern Checks-Effects-Interactions',
            '🔐 ReentrancyGuard d\'OpenZeppelin intégré',
            '🧪 Playwright: Tests de reentrancy multi-appels'
          ],
          cta: 'Auditer Mon Protocole Maintenant'
        },
        {
          id: 'oracle',
          icon: '📡',
          title: 'Manipulation d\'Oracle: Attaques Flash Loan',
          date: '2020-2023 - Multiples protocoles',
          impact: '$200M+ volés en attaques de prix',
          problem_title: 'Le Problème',
          problem_desc: 'Un attaquant prend un flash loan de $10M, manipule le prix du token sur un DEX à faible liquidité, et le protocole victime utilise ce prix faux pour liquider des positions légitimes, empochant les collatéraux.',
          technical: 'Techniquement: Les protocoles font confiance à un seul oracle de prix (ex: prix spot Uniswap V2). L\'attaquant manipule le pool avec un trade massif, l\'oracle rapporte le prix faux, et le protocole exécute des liquidations incorrectes.',
          stats: [
            '$200M+ volés en 2020-2023',
            '20+ protocoles DeFi affectés',
            'Flash loans jusqu\'à $1B utilisés'
          ],
          solution_title: 'Solution DM Sentinel',
          solution_desc: 'DM Sentinel vérifie la robustesse de vos oracles avec webscraping TVL en temps réel. Nous comparons les prix de Chainlink, Pyth, et DEXs. Playwright simule des attaques flash loan pour vérifier que votre protocole résiste à la manipulation de prix.',
          solution_features: [
            '📊 Webscraping TVL de 10+ sources',
            '🔗 Vérification d\'oracles Chainlink/Pyth',
            '⚡ Playwright: Simule des flash loans de $100M+',
            '🛡️ Test de manipulation de liquidité en direct'
          ],
          cta: 'Sécuriser Mes Oracles Maintenant'
        }
      ],
      final_cta: {
        title: 'Votre protocole est-il protégé?',
        subtitle: 'N\'attendez pas d\'être le prochain hack de $100M dans les news',
        button: 'Demander Audit One-Shot'
      }
    },
    cta_final: {
      title: 'Prêt à auditer votre protocole?',
      subtitle: 'Rejoignez 150+ projets qui font confiance à DM Sentinel',
      button: 'Demander un Audit Gratuit'
    },
    footer: {
      company: '© 2026 DM Sentinel. Tous droits réservés.',
      contact: 'Contact: security@dmsentinel.com'
    },
    payment: {
      modal_title: 'Sélectionner Mode de Paiement',
      modal_subtitle: 'Choisissez votre méthode de paiement préférée',
      plan_selected: 'Plan sélectionné',
      amount: 'Montant',
      methods: {
        card: 'Carte de Crédit',
        card_desc: 'Visa, Mastercard, Amex via Stripe',
        pix: 'Pix',
        pix_desc: 'Code QR - Paiement instantané',
        crypto: 'Cryptomonnaie',
        crypto_desc: 'USDC sur Ethereum/Polygon'
      },
      form: {
        contract_url: 'URL du contrat à auditer',
        contract_placeholder: 'https://etherscan.io/address/0x...',
        wallet: 'Votre wallet (optionnel)',
        wallet_placeholder: '0x...',
        email: 'Email de contact',
        email_placeholder: 'votre@email.com',
        pay_button: 'Payer',
        processing: 'Traitement...',
        cancel: 'Annuler'
      },
      pix: {
        title: 'Scanner le code QR',
        instructions: 'Ouvrez votre app bancaire et scannez le code',
        copy_code: 'Copier code Pix',
        waiting: 'En attente de confirmation du paiement...'
      },
      crypto: {
        connect: 'Connecter Wallet',
        connected: 'Wallet Connecté',
        approve: 'Approuver USDC',
        pay: 'Payer avec USDC',
        network: 'Réseau',
        balance: 'Solde'
      },
      success: {
        title: 'Paiement Réussi!',
        message: 'Votre audit sera traité sous peu',
        email_sent: 'Nous vous avons envoyé un email de confirmation'
      },
      error: {
        title: 'Erreur de Paiement',
        message: 'Un problème est survenu lors du traitement de votre paiement',
        try_again: 'Réessayer'
      }
    }
  },
  
  pt: {
    lang: 'pt',
    name: 'Português',
    hero: {
      title: 'Auditorias Web3 com IA',
      subtitle: 'Proteja seu Smart Contract antes da implantação',
      cta: 'Auditar Agora',
      price: 'A partir de $2,500 USD'
    },
    vulnerability: {
      title: 'Vulnerabilidade Comprovável',
      subtitle: 'Exemplo real detectado pelo DM Sentinel',
      issue: 'Reentrancy na função withdraw()',
      severity: 'Crítico',
      description: 'Padrão de reentrancy detectado. Atacante pode drenar fundos.',
      line: 'Linha 42: Chamada externa antes de atualizar saldo'
    },
    features: {
      title: 'Tecnologia de Ponta',
      items: [
        { title: 'IA Poderosa', desc: 'Slither + Mythril + GPT-4 combinados' },
        { title: 'QA Automatizado', desc: 'Playwright testa sua dApp em 50+ cenários' },
        { title: 'Intel On-Chain', desc: 'TVL, volume 24h e risco financeiro real' },
        { title: 'Entrega Power BI', desc: 'Dashboard executivo com 30+ métricas' }
      ]
    },
    pricing: {
      title: 'Preços Transparentes',
      basic: {
        name: 'Básico',
        price: '$2,500',
        features: [
          'Auditoria de 1 contrato',
          'Relatório PDF Cyber-Dark',
          'QA de dApp (50 testes)',
          'Inteligência de mercado',
          'Entrega em 3-5 dias'
        ],
        cta: 'Começar'
      },
      pro: {
        name: 'Profissional',
        price: '$7,500',
        features: [
          'Até 5 contratos',
          'Revisão manual de código',
          'Testes de penetração',
          'Dashboard Power BI',
          'Suporte prioritário 24/7',
          'Entrega em 2-3 dias'
        ],
        cta: 'Contratar',
        badge: 'Mais Popular'
      },
      enterprise: {
        name: 'Enterprise',
        price: 'Consultar',
        features: [
          'Contratos ilimitados',
          'Auditoria contínua (CI/CD)',
          'Bug bounty privado',
          'Retainer mensal',
          'SLA garantido',
          'Entrega em 24-48h'
        ],
        cta: 'Contatar'
      }
    },
    integrations: {
      title: 'Integrações Sem Fricção',
      subtitle: 'Aceitamos pagamentos na sua moeda local'
    },
    case_studies: {
      title: 'Vulnerabilidades Críticas: Casos Reais',
      subtitle: 'Aprenda com $2.3B+ explorados em protocolos DeFi',
      cases: [
        {
          id: 'drainer',
          icon: '🎣',
          title: 'Ataque Drainer: $100M Roubados em 24 Horas',
          date: 'Outubro 2023 - Pink Drainer',
          impact: '$100M+ roubados',
          problem_title: 'O Problema',
          problem_desc: 'Um usuário assina uma transação que parece legítima ("Claim Airdrop"), mas na verdade é um approve() ilimitado. O atacante drena todos os tokens ERC-20 e NFTs da carteira em segundos.',
          technical: 'Tecnicamente: O contrato malicioso usa setApprovalForAll() e transferFrom() para esvaziar a carteira sem que o usuário perceba até que seja tarde demais.',
          stats: [
            '15,000+ carteiras comprometidas',
            '$100M+ em tokens roubados',
            '80% das vítimas não revisaram o contrato'
          ],
          solution_title: 'Solução DM Sentinel',
          solution_desc: 'Nosso sistema de Pentesting + Playwright QA simula ataques de phishing e aprovações maliciosas. Analisamos cada função approve(), transferFrom() e setApprovalForAll() em busca de permissões excessivas.',
          solution_features: [
            '🔍 Análise de permissões excessivas (approve ilimitado)',
            '🤖 Playwright: Simula 50+ cenários de phishing',
            '⚡ Detecção de contratos "honeypot" em tempo real',
            '📊 Auditoria completa de frontend + backend'
          ],
          cta: 'Proteger Meu Protocolo Agora'
        },
        {
          id: 'reentrancy',
          icon: '♻️',
          title: 'The DAO Hack: $60M Perdidos',
          date: 'Junho 2016 - The DAO',
          impact: '$60M roubados → Hard Fork do Ethereum',
          problem_title: 'O Problema',
          problem_desc: 'O bug mais famoso da história DeFi. Uma função withdraw() atualizava o saldo DEPOIS de enviar ETH, permitindo chamadas recursivas que esvaziaram o contrato antes que o estado fosse atualizado.',
          technical: 'Tecnicamente: O atacante chamou a função withdraw() recursivamente (reentrancy) antes que o saldo fosse atualizado, drenando todo o ETH do contrato. Padrão: call() antes de balances[msg.sender] -= amount.',
          stats: [
            '$60M roubados (15% do supply de ETH)',
            'Hard fork do Ethereum (ETH vs ETC)',
            'Pausa de 27 dias na rede'
          ],
          solution_title: 'Solução DM Sentinel',
          solution_desc: 'DM Sentinel detecta automaticamente padrões de reentrancy com Slither + Mythril. Verificamos que TODAS as funções seguem o padrão Checks-Effects-Interactions e usamos Playwright para simular ataques de reentrancy ao vivo.',
          solution_features: [
            '🛡️ Detecção automática de reentrancy com Slither',
            '✅ Verificação do padrão Checks-Effects-Interactions',
            '🔐 ReentrancyGuard do OpenZeppelin integrado',
            '🧪 Playwright: Testes de reentrancy multi-chamada'
          ],
          cta: 'Auditar Meu Protocolo Agora'
        },
        {
          id: 'oracle',
          icon: '📡',
          title: 'Manipulação de Oracle: Ataques de Flash Loan',
          date: '2020-2023 - Múltiplos protocolos',
          impact: '$200M+ roubados em ataques de preço',
          problem_title: 'O Problema',
          problem_desc: 'Um atacante pega um flash loan de $10M, manipula o preço do token em uma DEX de baixa liquidez, e o protocolo vítima usa esse preço falso para liquidar posições legítimas, embolsando as garantias.',
          technical: 'Tecnicamente: Os protocolos confiam em um único oráculo de preço (ex: preço spot do Uniswap V2). O atacante manipula o pool com um trade massivo, o oráculo reporta o preço falso, e o protocolo executa liquidações incorretas.',
          stats: [
            '$200M+ roubados em 2020-2023',
            '20+ protocolos DeFi afetados',
            'Flash loans de até $1B usados'
          ],
          solution_title: 'Solução DM Sentinel',
          solution_desc: 'DM Sentinel verifica a robustez dos seus oráculos com webscraping de TVL em tempo real. Comparamos preços do Chainlink, Pyth e DEXs. Playwright simula ataques de flash loan para verificar que seu protocolo resiste à manipulação de preços.',
          solution_features: [
            '📊 Webscraping de TVL de 10+ fontes',
            '🔗 Verificação de oráculos Chainlink/Pyth',
            '⚡ Playwright: Simula flash loans de $100M+',
            '🛡️ Teste de manipulação de liquidez ao vivo'
          ],
          cta: 'Proteger Meus Oráculos Agora'
        }
      ],
      final_cta: {
        title: 'Seu protocolo está protegido?',
        subtitle: 'Não espere para ser o próximo hack de $100M nas notícias',
        button: 'Solicitar Auditoria One-Shot'
      }
    },
    cta_final: {
      title: 'Pronto para auditar seu protocolo?',
      subtitle: 'Junte-se aos 150+ projetos que confiam no DM Sentinel',
      button: 'Solicitar Auditoria Gratuita'
    },
    footer: {
      company: '© 2026 DM Sentinel. Todos os direitos reservados.',
      contact: 'Contato: security@dmsentinel.com'
    },
    payment: {
      modal_title: 'Selecionar Método de Pagamento',
      modal_subtitle: 'Escolha seu método de pagamento preferido',
      plan_selected: 'Plano selecionado',
      amount: 'Valor',
      methods: {
        card: 'Cartão de Crédito',
        card_desc: 'Visa, Mastercard, Amex via Stripe',
        pix: 'Pix',
        pix_desc: 'Código QR - Pagamento instantâneo',
        crypto: 'Criptomoeda',
        crypto_desc: 'USDC em Ethereum/Polygon'
      },
      form: {
        contract_url: 'URL do contrato para auditar',
        contract_placeholder: 'https://etherscan.io/address/0x...',
        wallet: 'Sua carteira (opcional)',
        wallet_placeholder: '0x...',
        email: 'Email de contato',
        email_placeholder: 'seu@email.com',
        pay_button: 'Pagar',
        processing: 'Processando...',
        cancel: 'Cancelar'
      },
      pix: {
        title: 'Escaneie o código QR',
        instructions: 'Abra seu app bancário e escaneie o código',
        copy_code: 'Copiar código Pix',
        waiting: 'Aguardando confirmação do pagamento...'
      },
      crypto: {
        connect: 'Conectar Carteira',
        connected: 'Carteira Conectada',
        approve: 'Aprovar USDC',
        pay: 'Pagar com USDC',
        network: 'Rede',
        balance: 'Saldo'
      },
      success: {
        title: 'Pagamento Bem-Sucedido!',
        message: 'Sua auditoria será processada em breve',
        email_sent: 'Enviamos um email de confirmação'
      },
      error: {
        title: 'Erro no Pagamento',
        message: 'Houve um problema ao processar seu pagamento',
        try_again: 'Tentar novamente'
      }
    }
  },
  
  eo: {
    lang: 'eo',
    name: 'Esperanto',
    hero: {
      title: 'AI-povigitaj Web3 Kontroloj',
      subtitle: 'Sekurigu vian Saĝan Kontrakton antaŭ deplojo',
      cta: 'Kontroli Nun',
      price: 'De $2,500 USD'
    },
    vulnerability: {
      title: 'Pruvoebla Vundebleco',
      subtitle: 'Reala ekzemplo detektita de DM Sentinel',
      issue: 'Reentrancy en funkcio withdraw()',
      severity: 'Kritika',
      description: 'Reentrancy ŝablono detektita. Atakanto povas drenigi fondojn.',
      line: 'Linio 42: Ekstera voko antaŭ bilanco ĝisdatigo'
    },
    features: {
      title: 'Avangarda Teknologio',
      items: [
        { title: 'AI-Povigita', desc: 'Slither + Mythril + GPT-4 kombinitaj' },
        { title: 'Aŭtomata QA', desc: 'Playwright testas vian dApp en 50+ scenaroj' },
        { title: 'On-Chain Intel', desc: 'TVL, 24h volumo kaj reala financa risko' },
        { title: 'Power BI Livero', desc: 'Estro panelo kun 30+ metrikoj' }
      ]
    },
    pricing: {
      title: 'Travideblaj Prezoj',
      basic: {
        name: 'Baza',
        price: '$2,500',
        features: [
          'Kontrolo de 1 kontrakto',
          'Cyber-Dark PDF Raporto',
          'dApp QA (50 testoj)',
          'Merkata inteligento',
          'Livero en 3-5 tagoj'
        ],
        cta: 'Komenci'
      },
      pro: {
        name: 'Profesia',
        price: '$7,500',
        features: [
          'Ĝis 5 kontraktoj',
          'Manlibra koda revizio',
          'Penetra testado',
          'Power BI Panelo',
          'Prioritata subteno 24/7',
          'Livero en 2-3 tagoj'
        ],
        cta: 'Dungi',
        badge: 'Plej Populara'
      },
      enterprise: {
        name: 'Entrepreno',
        price: 'Konsulti',
        features: [
          'Senlimaj kontraktoj',
          'Kontinua kontrolo (CI/CD)',
          'Privata cimo premio',
          'Monata reteno',
          'Garantiita SLA',
          'Livero en 24-48h'
        ],
        cta: 'Kontakti'
      }
    },
    integrations: {
      title: 'Senfrikcaj Integriĝoj',
      subtitle: 'Ni akceptas pagojn en via loka valuto'
    },
    case_studies: {
      title: 'Kritikaj Vundeblecoj: Realaj Kazoj',
      subtitle: 'Lernu de $2.3B+ ekspluatitaj en DeFi protokoloj',
      cases: [
        {
          id: 'drainer',
          icon: '🎣',
          title: 'Drainer Atako: $100M Ŝtelitaj en 24 Horoj',
          date: 'Oktobro 2023 - Pink Drainer',
          impact: '$100M+ ŝtelitaj',
          problem_title: 'La Problemo',
          problem_desc: 'Uzanto subskribas transakcion kiu ŝajnas leĝitima ("Claim Airdrop"), sed ĝi fakte estas senlima approve(). La atakanto drenadas ĉiujn ERC-20 ĵetonojn kaj NFT-ojn de la monujo en sekundoj.',
          technical: 'Teknike: La malica kontrakto uzas setApprovalForAll() kaj transferFrom() por malplenigi la monujon sen ke la uzanto rimarkas ĝis tro malfrue.',
          stats: [
            '15,000+ monujoj kompromitigitaj',
            '$100M+ en ŝtelitaj ĵetonoj',
            '80% de viktimoj ne kontrolis la kontrakton'
          ],
          solution_title: 'DM Sentinel Solvo',
          solution_desc: 'Nia Pentesting + Playwright QA sistemo simulas fiŝkaptajn atakojn kaj malicajn aprobojn. Ni analizas ĉiun funkcion approve(), transferFrom() kaj setApprovalForAll() por troaj permesoj.',
          solution_features: [
            '🔍 Analizo de troaj permesoj (senlima approve)',
            '🤖 Playwright: Simulas 50+ fiŝkaptajn scenarojn',
            '⚡ Realtempaj "honeypot" kontrakta detekto',
            '📊 Kompleta antaŭa + malantaŭa kontrolo'
          ],
          cta: 'Protekti Mian Protokolon Nun'
        },
        {
          id: 'reentrancy',
          icon: '♻️',
          title: 'The DAO Hack: $60M Perditaj',
          date: 'Junio 2016 - The DAO',
          impact: '$60M ŝtelitaj → Ethereum Hard Fork',
          problem_title: 'La Problemo',
          problem_desc: 'La plej fama cimo en DeFi historio. Funkcio withdraw() ĝisdatigis la saldon POST sendado de ETH, permesante rikurajn vokojn kiuj drenadas la kontrakton antaŭ ol la stato estis ĝisdatigita.',
          technical: 'Teknike: La atakanto vokis la funkcion withdraw() rikure (reentrancy) antaŭ ol la saldo estis ĝisdatigita, drenante ĉiun ETH de la kontrakto. Ŝablono: call() antaŭ balances[msg.sender] -= amount.',
          stats: [
            '$60M ŝtelitaj (15% de ETH provizo)',
            'Ethereum hard fork (ETH vs ETC)',
            '27-taga reta paŭzo'
          ],
          solution_title: 'DM Sentinel Solvo',
          solution_desc: 'DM Sentinel aŭtomate detektas reentrancy ŝablonojn per Slither + Mythril. Ni kontrolas ke ĈIUJ funkcioj sekvas la Checks-Effects-Interactions ŝablonon kaj uzas Playwright por simuli vivojn reentrancy atakojn.',
          solution_features: [
            '🛡️ Aŭtomata reentrancy detekto per Slither',
            '✅ Checks-Effects-Interactions ŝablona kontrolo',
            '🔐 OpenZeppelin ReentrancyGuard integrita',
            '🧪 Playwright: Multi-voka reentrancy testoj'
          ],
          cta: 'Kontroli Mian Protokolon Nun'
        },
        {
          id: 'oracle',
          icon: '📡',
          title: 'Orakola Manipulado: Flash Loan Atakoj',
          date: '2020-2023 - Multoblaj protokoloj',
          impact: '$200M+ ŝtelitaj en preza atakoj',
          problem_title: 'La Problemo',
          problem_desc: 'Atakanto prenas flash loan de $10M, manipulas la ĵetona prezon en malalta-likvideca DEX, kaj la viktima protokolo uzas tiun falsan prezon por likvidi leĝitimajn poziciojn, poŝigante la kolateralojn.',
          technical: 'Teknike: Protokoloj fidas unu prezan orakolon (ekz: Uniswap V2 spot prezo). La atakanto manipulas la polon kun masiva komerco, la orakolo raportas la falsan prezon, kaj la protokolo ekzekutas malĝustajn likvidojn.',
          stats: [
            '$200M+ ŝtelitaj en 2020-2023',
            '20+ DeFi protokoloj trafitaj',
            'Flash loans ĝis $1B uzitaj'
          ],
          solution_title: 'DM Sentinel Solvo',
          solution_desc: 'DM Sentinel kontrolas viajn orakolajn fortikojn per realtempaj TVL webscraping. Ni komparas prezojn de Chainlink, Pyth, kaj DEX-oj. Playwright simulas flash loan atakojn por kontroli ke via protokolo rezistas prezan manipuladon.',
          solution_features: [
            '📊 TVL webscraping de 10+ fontoj',
            '🔗 Chainlink/Pyth orakola kontrolo',
            '⚡ Playwright: Simulas $100M+ flash loans',
            '🛡️ Viva likvideca manipulada testo'
          ],
          cta: 'Sekurigi Miajn Orakolojn Nun'
        }
      ],
      final_cta: {
        title: 'Ĉu via protokolo estas protektita?',
        subtitle: 'Ne atendu esti la sekva $100M hack en la novaĵoj',
        button: 'Peti One-Shot Kontrolon'
      }
    },
    cta_final: {
      title: 'Ĉu preta kontroli vian protokolon?',
      subtitle: 'Aliĝu al 150+ projektoj kiuj fidas DM Sentinel',
      button: 'Peti Senpagan Kontrolon'
    },
    footer: {
      company: '© 2026 DM Sentinel. Ĉiuj rajtoj rezervitaj.',
      contact: 'Kontakto: security@dmsentinel.com'
    },
    payment: {
      modal_title: 'Elekti Pagmanieron',
      modal_subtitle: 'Elektu vian preferatan pagmanieron',
      plan_selected: 'Plano elektita',
      amount: 'Sumo',
      methods: {
        card: 'Kreditkarto',
        card_desc: 'Visa, Mastercard, Amex per Stripe',
        pix: 'Pix',
        pix_desc: 'QR-kodo - Tuja pago',
        crypto: 'Kriptomonero',
        crypto_desc: 'USDC sur Ethereum/Polygon'
      },
      form: {
        contract_url: 'URL de kontrakto por aŭditi',
        contract_placeholder: 'https://etherscan.io/address/0x...',
        wallet: 'Via monujo (malnepra)',
        wallet_placeholder: '0x...',
        email: 'Kontakta retpoŝto',
        email_placeholder: 'via@retposxto.com',
        pay_button: 'Pagi',
        processing: 'Traktante...',
        cancel: 'Nuligi'
      },
      pix: {
        title: 'Skanu la QR-kodon',
        instructions: 'Malfermu vian bankan aplikon kaj skanu la kodon',
        copy_code: 'Kopii Pix-kodon',
        waiting: 'Atendante konfirmon de pago...'
      },
      crypto: {
        connect: 'Konekti Monujon',
        connected: 'Monujo Konektita',
        approve: 'Aprobi USDC',
        pay: 'Pagi per USDC',
        network: 'Reto',
        balance: 'Saldo'
      },
      success: {
        title: 'Pago Sukcesis!',
        message: 'Via aŭditado estos traktata baldaṷ',
        email_sent: 'Ni sendis retpoŝtan konfirmon'
      },
      error: {
        title: 'Paga Eraro',
        message: 'Okazis problemo traktante vian pagon',
        try_again: 'Provi denove'
      }
    }
  }
};

// ============================================================================
// LANGUAGE DETECTION LOGIC
// ============================================================================

const detectLanguage = () => {
  // 1. Check browser language
  const browserLang = navigator.language || navigator.userLanguage;
  const langCode = browserLang.split('-')[0].toLowerCase();
  
  // 2. Map to supported languages
  const langMap = {
    'es': 'es',
    'en': 'en',
    'fr': 'fr',
    'pt': 'pt',
    'eo': 'eo'
  };
  
  const detectedLang = langMap[langCode] || 'en';
  
  // 3. Simulate IP-based detection (would use API in production)
  // For demo: Check localStorage override
  const savedLang = localStorage.getItem('dmsentinel_lang');
  
  return savedLang || detectedLang;
};

// ============================================================================
// LOGO SVG COMPONENTS
// ============================================================================

const EthereumLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path d="M16 0L15.7188 0.954375V21.7531L16 22.0312L25.5 16.2938L16 0Z" fill="#627EEA"/>
    <path d="M16 0L6.5 16.2938L16 22.0312V0Z" fill="#8A92B2"/>
    <path d="M16 24L15.8594 24.1719V31.6594L16 32L25.5062 18.2656L16 24Z" fill="#627EEA"/>
    <path d="M16 32V24L6.5 18.2656L16 32Z" fill="#8A92B2"/>
    <path d="M16 22.0312L25.5 16.2938L16 11.9375V22.0312Z" fill="#627EEA"/>
    <path d="M6.5 16.2938L16 22.0312V11.9375L6.5 16.2938Z" fill="#8A92B2"/>
  </svg>
);

const PolygonLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path d="M22 10.5C21.4 10.2 20.7 10.2 20.1 10.5L16.8 12.3L14.5 13.7L11.2 15.5C10.6 15.8 9.9 15.8 9.3 15.5L6.8 14C6.2 13.7 5.8 13.1 5.8 12.4V9.5C5.8 8.8 6.1 8.2 6.8 7.9L9.3 6.4C9.9 6.1 10.6 6.1 11.2 6.4L13.7 7.9C14.3 8.2 14.7 8.8 14.7 9.5V11.3L16.8 10V8.2C16.8 7.5 16.5 6.9 15.8 6.6L11.3 4.2C10.7 3.9 10 3.9 9.4 4.2L4.8 6.6C4.1 6.9 3.8 7.5 3.8 8.2V13C3.8 13.7 4.1 14.3 4.8 14.6L9.3 17C9.9 17.3 10.6 17.3 11.2 17L14.5 15.2L16.8 13.8L20.1 12C20.7 11.7 21.4 11.7 22 12L24.5 13.5C25.1 13.8 25.5 14.4 25.5 15.1V18C25.5 18.7 25.2 19.3 24.5 19.6L22 21.1C21.4 21.4 20.7 21.4 20.1 21.1L17.6 19.6C17 19.3 16.6 18.7 16.6 18V16.2L14.5 17.5V19.3C14.5 20 14.8 20.6 15.5 20.9L20 23.3C20.6 23.6 21.3 23.6 21.9 23.3L26.4 20.9C27 20.6 27.4 20 27.4 19.3V14.5C27.4 13.8 27.1 13.2 26.4 12.9L22 10.5Z" fill="#8247E5"/>
  </svg>
);

const SolidityLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <path d="M20 4L16 11L20 18L24 11L20 4Z" fill="#7F8C8D" fillOpacity="0.45"/>
    <path d="M12 4L8 11L12 18L16 11L12 4Z" fill="#7F8C8D"/>
    <path d="M20 14L16 21L20 28L24 21L20 14Z" fill="#7F8C8D"/>
    <path d="M12 14L8 21L12 28L16 21L12 14Z" fill="#7F8C8D" fillOpacity="0.45"/>
  </svg>
);

const PlaywrightLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <circle cx="16" cy="16" r="14" fill="#2EAD33"/>
    <path d="M11 12L16 8L21 12V20L16 24L11 20V12Z" fill="white"/>
    <path d="M16 11V21" stroke="#2EAD33" strokeWidth="2"/>
    <path d="M13 14L16 11L19 14" stroke="#2EAD33" strokeWidth="2" fill="none"/>
  </svg>
);

const StripeLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="6" fill="#635BFF"/>
    <path d="M16.5 12.5C16.5 11.7 17.1 11.3 18.2 11.3C19.7 11.3 21.6 11.8 23.1 12.6V8.3C21.5 7.7 19.9 7.5 18.2 7.5C14.3 7.5 11.5 9.5 11.5 12.9C11.5 18.2 19 17.4 19 19.6C19 20.5 18.3 20.9 17.1 20.9C15.4 20.9 13.3 20.2 11.6 19.2V23.6C13.4 24.4 15.2 24.7 17.1 24.7C21.1 24.7 24.1 22.8 24.1 19.3C24 13.7 16.5 14.7 16.5 12.5Z" fill="white"/>
  </svg>
);

const PixLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="6" fill="#32BCAD"/>
    <path d="M16 8L10 14L16 20L22 14L16 8Z" fill="white"/>
    <path d="M10 14L8 16L10 18L12 16L10 14Z" fill="white"/>
    <path d="M22 14L20 16L22 18L24 16L22 14Z" fill="white"/>
    <path d="M16 20L14 22L16 24L18 22L16 20Z" fill="white"/>
  </svg>
);

const MercadoPagoLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="6" fill="#00B1EA"/>
    <path d="M16 8C11.6 8 8 11.6 8 16C8 20.4 11.6 24 16 24C20.4 24 24 20.4 24 16C24 11.6 20.4 8 16 8ZM16 21.5C13 21.5 10.5 19 10.5 16C10.5 13 13 10.5 16 10.5C19 10.5 21.5 13 21.5 16C21.5 19 19 21.5 16 21.5Z" fill="white"/>
    <path d="M18 14L15 17L13 15" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
  </svg>
);

// ============================================================================
// MAIN APP COMPONENT
// ============================================================================

function App() {
  const [currentLang, setCurrentLang] = useState('en');
  const [showCodeModal, setShowCodeModal] = useState(false);
  
  // PAYMENT MODAL STATE - PROMPT 2
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState(null); // 'card', 'pix', 'crypto'
  const [paymentStep, setPaymentStep] = useState('method'); // 'method', 'form', 'processing', 'success', 'error'
  const [formData, setFormData] = useState({
    contractUrl: '',
    email: '',
    wallet: ''
  });
  const [pixData, setPixData] = useState(null);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  useEffect(() => {
    const lang = detectLanguage();
    setCurrentLang(lang);
  }, []);
  
  const t = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
  
  const changeLang = (lang) => {
    setCurrentLang(lang);
    localStorage.setItem('dmsentinel_lang', lang);
  };

  // PAYMENT HANDLERS - PROMPT 2
  const openPaymentModal = (plan) => {
    setSelectedPlan(plan);
    setShowPaymentModal(true);
    setPaymentStep('method');
    setPaymentMethod(null);
    setErrorMessage('');
  };

  const closePaymentModal = () => {
    setShowPaymentModal(false);
    setSelectedPlan(null);
    setPaymentMethod(null);
    setPaymentStep('method');
    setFormData({ contractUrl: '', email: '', wallet: '' });
    setPixData(null);
    setErrorMessage('');
  };

  const selectPaymentMethod = (method) => {
    setPaymentMethod(method);
    setPaymentStep('form');
  };

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const sendWebhook = async (paymentData) => {
    try {
      await fetch(WEBHOOK_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_wallet: formData.wallet || paymentData.wallet_address || null,
          plan_selected: selectedPlan.name.toLowerCase(),
          contract_url: formData.contractUrl,
          payment_method: paymentData.payment_method,
          amount_usd: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
          transaction_id: paymentData.transaction_hash || paymentData.charge_id || paymentData.payment_id,
          client_email: formData.email,
          timestamp: new Date().toISOString(),
          metadata: {
            language: currentLang,
            browser: navigator.userAgent,
            referrer: document.referrer
          }
        })
      });
    } catch (error) {
      console.error('Webhook error:', error);
    }
  };

  const handleStripePayment = async () => {
    try {
      setPaymentStep('processing');
      const stripe = await loadStripe();
      
      // Simulate backend call (replace with real API)
      const response = await fetch(`${WEBHOOK_URL}/create-checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: selectedPlan.name,
          amount: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
          contract_url: formData.contractUrl,
          email: formData.email,
          wallet: formData.wallet,
          success_url: window.location.origin + '/payment-success',
          cancel_url: window.location.origin + '/payment-cancel'
        })
      });
      
      const session = await response.json();
      await stripe.redirectToCheckout({ sessionId: session.id });
      
    } catch (error) {
      console.error('Stripe error:', error);
      setErrorMessage(error.message);
      setPaymentStep('error');
    }
  };

  const handlePixPayment = async () => {
    try {
      setPaymentStep('processing');
      
      // Call backend to create Mercado Pago payment
      const response = await fetch(`${WEBHOOK_URL}/create-pix-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plan: selectedPlan.name,
          amount: parseFloat(selectedPlan.price.replace(/[^0-9.]/g, '')),
          contract_url: formData.contractUrl,
          email: formData.email,
          payer: { email: formData.email }
        })
      });
      
      const payment = await response.json();
      
      setPixData({
        qr_code: payment.point_of_interaction.transaction_data.qr_code,
        qr_code_base64: payment.point_of_interaction.transaction_data.qr_code_base64,
        payment_id: payment.id
      });
      
      setPaymentStep('pix');
      
      // Poll for payment status
      const pollInterval = setInterval(async () => {
        const statusResponse = await fetch(`${WEBHOOK_URL}/check-payment/${payment.id}`);
        const statusData = await statusResponse.json();
        
        if (statusData.status === 'approved') {
          clearInterval(pollInterval);
          await sendWebhook({
            payment_method: 'mercadopago',
            payment_id: payment.id
          });
          setPaymentStep('success');
        }
      }, 3000);
      
    } catch (error) {
      console.error('Pix error:', error);
      setErrorMessage(error.message);
      setPaymentStep('error');
    }
  };

  const handleCryptoPayment = async () => {
    try {
      setPaymentStep('processing');
      
      if (!window.ethereum) {
        throw new Error('Please install MetaMask');
      }
      
      // Dynamic import of ethers
      const { ethers } = await import('ethers');
      
      const provider = new ethers.BrowserProvider(window.ethereum);
      await provider.send('eth_requestAccounts', []);
      const signer = await provider.getSigner();
      const walletAddress = await signer.getAddress();
      
      setWalletConnected(true);
      setWalletAddress(walletAddress);
      
      const network = await provider.getNetwork();
      const chainId = network.chainId;
      
      // USDC contract addresses
      const USDC_CONTRACT = {
        1: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // Ethereum
        137: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174' // Polygon
      };
      
      const DM_SENTINEL_WALLET = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'; // Replace with real wallet
      
      const usdcAddress = USDC_CONTRACT[Number(chainId)];
      if (!usdcAddress) {
        throw new Error('Please switch to Ethereum or Polygon network');
      }
      
      const usdcAbi = ['function transfer(address to, uint256 amount) returns (bool)'];
      const usdcContract = new ethers.Contract(usdcAddress, usdcAbi, signer);
      
      const amount = parseFloat(selectedPlan.price.replace(/[^0-9.]/g, ''));
      const amountInWei = ethers.parseUnits(amount.toString(), 6); // USDC has 6 decimals
      
      const tx = await usdcContract.transfer(DM_SENTINEL_WALLET, amountInWei);
      const receipt = await tx.wait();
      
      await sendWebhook({
        payment_method: 'web3',
        transaction_hash: receipt.hash,
        wallet_address: walletAddress,
        network: chainId === 1n ? 'ethereum' : 'polygon'
      });
      
      setPaymentStep('success');
      
    } catch (error) {
      console.error('Crypto error:', error);
      setErrorMessage(error.message);
      setPaymentStep('error');
    }
  };

  const executePayment = () => {
    if (!formData.contractUrl || !formData.email) {
      setErrorMessage('Please fill all required fields');
      return;
    }

    if (paymentMethod === 'card') {
      handleStripePayment();
    } else if (paymentMethod === 'pix') {
      handlePixPayment();
    } else if (paymentMethod === 'crypto') {
      handleCryptoPayment();
    }
  };

  return (
    <div className="app">
      {/* Language Selector */}
      <div className="lang-selector">
        {Object.entries(TRANSLATIONS).map(([code, trans]) => (
          <button
            key={code}
            onClick={() => changeLang(code)}
            className={currentLang === code ? 'active' : ''}
          >
            {trans.name}
          </button>
        ))}
      </div>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1 className="gradient-title">{t.hero.title}</h1>
          <p className="hero-subtitle">{t.hero.subtitle}</p>
          <div className="hero-cta">
            <button className="cta-primary">{t.hero.cta}</button>
            <span className="hero-price">{t.hero.price}</span>
          </div>
        </div>
        
        {/* Animated background */}
        <div className="hero-bg">
          <div className="grid-overlay"></div>
        </div>
      </section>

      {/* Vulnerability Demo Section */}
      <section className="vulnerability-section">
        <div className="container">
          <h2 className="gradient-title">{t.vulnerability.title}</h2>
          <p className="section-subtitle">{t.vulnerability.subtitle}</p>
          
          <div className="terminal-box" onClick={() => setShowCodeModal(true)}>
            <div className="terminal-header">
              <span className="terminal-dot red"></span>
              <span className="terminal-dot yellow"></span>
              <span className="terminal-dot green"></span>
              <span className="terminal-title">contract.sol</span>
            </div>
            <div className="terminal-body">
              <pre className="code-block">
                <code>
{`pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        
        `}<span className="code-highlight-error">{`// ⚠️ ${t.vulnerability.issue}`}</span>{`
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        
        balances[msg.sender] -= amount;  // Too late!
    }
}`}
                </code>
              </pre>
            </div>
            <div className="terminal-footer">
              <span className="severity-badge critical">{t.vulnerability.severity}</span>
              <span className="vulnerability-desc">{t.vulnerability.description}</span>
            </div>
          </div>
          
          <div className="vulnerability-explanation">
            <div className="vuln-icon">⚠️</div>
            <p>{t.vulnerability.line}</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="gradient-title">{t.features.title}</h2>
          <div className="features-grid">
            {t.features.items.map((feature, idx) => (
              <div key={idx} className="feature-card">
                <div className="feature-icon">
                  {idx === 0 && '🤖'}
                  {idx === 1 && '🎭'}
                  {idx === 2 && '📊'}
                  {idx === 3 && '📈'}
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section">
        <div className="container">
          <h2 className="gradient-title">{t.pricing.title}</h2>
          <div className="pricing-grid">
            {/* Basic */}
            <div className="pricing-card">
              <h3>{t.pricing.basic.name}</h3>
              <div className="price">{t.pricing.basic.price}</div>
              <ul className="features-list">
                {t.pricing.basic.features.map((f, i) => (
                  <li key={i}>✓ {f}</li>
                ))}
              </ul>
              <button 
                className="cta-secondary" 
                onClick={() => openPaymentModal({
                  name: 'Basic',
                  price: t.pricing.basic.price,
                  features: t.pricing.basic.features
                })}
              >
                {t.pricing.basic.cta}
              </button>
            </div>
            
            {/* Pro */}
            <div className="pricing-card featured">
              {t.pricing.pro.badge && (
                <div className="pricing-badge">{t.pricing.pro.badge}</div>
              )}
              <h3>{t.pricing.pro.name}</h3>
              <div className="price">{t.pricing.pro.price}</div>
              <ul className="features-list">
                {t.pricing.pro.features.map((f, i) => (
                  <li key={i}>✓ {f}</li>
                ))}
              </ul>
              <button 
                className="cta-primary" 
                onClick={() => openPaymentModal({
                  name: 'Pro',
                  price: t.pricing.pro.price,
                  features: t.pricing.pro.features
                })}
              >
                {t.pricing.pro.cta}
              </button>
            </div>
            
            {/* Enterprise */}
            <div className="pricing-card">
              <h3>{t.pricing.enterprise.name}</h3>
              <div className="price">{t.pricing.enterprise.price}</div>
              <ul className="features-list">
                {t.pricing.enterprise.features.map((f, i) => (
                  <li key={i}>✓ {f}</li>
                ))}
              </ul>
              <button 
                className="cta-secondary" 
                onClick={() => openPaymentModal({
                  name: 'Enterprise',
                  price: t.pricing.enterprise.price,
                  features: t.pricing.enterprise.features
                })}
              >
                {t.pricing.enterprise.cta}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="integrations-section">
        <div className="container">
          <h2 className="gradient-title">{t.integrations.title}</h2>
          <p className="section-subtitle">{t.integrations.subtitle}</p>
          
          <div className="logos-grid">
            <div className="logo-item" title="Ethereum">
              <EthereumLogo />
              <span>Ethereum</span>
            </div>
            <div className="logo-item" title="Polygon">
              <PolygonLogo />
              <span>Polygon</span>
            </div>
            <div className="logo-item" title="Solidity">
              <SolidityLogo />
              <span>Solidity</span>
            </div>
            <div className="logo-item" title="Playwright">
              <PlaywrightLogo />
              <span>Playwright</span>
            </div>
            <div className="logo-item" title="Stripe">
              <StripeLogo />
              <span>Stripe</span>
            </div>
            <div className="logo-item" title="Pix">
              <PixLogo />
              <span>Pix</span>
            </div>
            <div className="logo-item" title="Mercado Pago">
              <MercadoPagoLogo />
              <span>Mercado Pago</span>
            </div>
          </div>
        </div>
      </section>

      {/* CASE STUDIES SECTION - PROMPT 3 */}
      <section className="case-studies-section">
        <div className="container">
          <h2 className="gradient-title">{t.case_studies.title}</h2>
          <p className="section-subtitle">{t.case_studies.subtitle}</p>
          
          <div className="case-studies-grid">
            {t.case_studies.cases.map((caseStudy, index) => (
              <div key={caseStudy.id} className={`case-study-card case-${caseStudy.id}`}>
                {/* Icon and Title */}
                <div className="case-header">
                  <div className="case-icon">{caseStudy.icon}</div>
                  <div className="case-title-area">
                    <h3 className="case-title">{caseStudy.title}</h3>
                    <p className="case-date">{caseStudy.date}</p>
                  </div>
                </div>
                
                {/* Impact Badge */}
                <div className="impact-badge">{caseStudy.impact}</div>
                
                {/* Problem Section */}
                <div className="case-section">
                  <h4 className="section-title problem-title">
                    <span className="title-icon">⚠️</span> {caseStudy.problem_title}
                  </h4>
                  <p className="section-description">{caseStudy.problem_desc}</p>
                  <div className="technical-note">
                    <span className="tech-label">💻</span>
                    <p>{caseStudy.technical}</p>
                  </div>
                  
                  {/* Stats */}
                  <ul className="case-stats">
                    {caseStudy.stats.map((stat, i) => (
                      <li key={i}>
                        <span className="stat-bullet">►</span> {stat}
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Solution Section */}
                <div className="case-section solution-section">
                  <h4 className="section-title solution-title">
                    <span className="title-icon">🛡️</span> {caseStudy.solution_title}
                  </h4>
                  <p className="section-description">{caseStudy.solution_desc}</p>
                  
                  {/* Solution Features */}
                  <ul className="solution-features">
                    {caseStudy.solution_features.map((feature, i) => (
                      <li key={i}>{feature}</li>
                    ))}
                  </ul>
                </div>
                
                {/* CTA Button */}
                <button className="case-cta-button" onClick={() => openPaymentModal({
                  name: 'Pro',
                  price: t.pricing.pro.price,
                  features: t.pricing.pro.features
                })}>
                  {caseStudy.cta} →
                </button>
              </div>
            ))}
          </div>
          
          {/* Final CTA within Case Studies */}
          <div className="case-studies-final-cta">
            <h3 className="final-cta-title">{t.case_studies.final_cta.title}</h3>
            <p className="final-cta-subtitle">{t.case_studies.final_cta.subtitle}</p>
            <button className="cta-primary large" onClick={() => openPaymentModal({
              name: 'Pro',
              price: t.pricing.pro.price,
              features: t.pricing.pro.features
            })}>
              {t.case_studies.final_cta.button}
            </button>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="cta-final-section">
        <div className="container">
          <h2 className="gradient-title">{t.cta_final.title}</h2>
          <p className="section-subtitle">{t.cta_final.subtitle}</p>
          <button className="cta-primary large">{t.cta_final.button}</button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>{t.footer.company}</p>
          <p>{t.footer.contact}</p>
        </div>
      </footer>

      {/* Code Modal */}
      {showCodeModal && (
        <div className="modal-overlay" onClick={() => setShowCodeModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowCodeModal(false)}>×</button>
            <h3>{t.vulnerability.title}</h3>
            <div className="terminal-box large">
              <div className="terminal-header">
                <span className="terminal-dot red"></span>
                <span className="terminal-dot yellow"></span>
                <span className="terminal-dot green"></span>
                <span className="terminal-title">contract.sol - Full Analysis</span>
              </div>
              <div className="terminal-body">
                <pre className="code-block">
                  <code>
{`pragma solidity ^0.8.0;

contract VulnerableBank {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        `}<span className="code-highlight-error">{`// CRITICAL: Reentrancy vulnerability!`}</span>{`
        `}<span className="code-highlight-error">{`// External call before state update`}</span>{`
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        `}<span className="code-highlight-error">{`// State update happens AFTER external call`}</span>{`
        balances[msg.sender] -= amount;  // ⚠️ TOO LATE!
    }
    
    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}

`}<span className="code-highlight-success">{`// ✓ FIXED VERSION:`}</span>{`
contract SecureBank {
    mapping(address => uint256) public balances;
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        
        `}<span className="code-highlight-success">{`// Update state FIRST (Checks-Effects-Interactions)`}</span>{`
        balances[msg.sender] -= amount;
        
        `}<span className="code-highlight-success">{`// Then make external call`}</span>{`
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}`}
                  </code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* PAYMENT MODAL - PROMPT 2 */}
      {showPaymentModal && (
        <div className="modal-overlay" onClick={closePaymentModal}>
          <div className="payment-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closePaymentModal}>✕</button>
            
            <h2 className="gradient-title">{t.payment.modal_title}</h2>
            <p className="modal-subtitle">{t.payment.modal_subtitle}</p>
            
            {selectedPlan && (
              <div className="plan-summary">
                <span className="plan-name">{t.payment.plan_selected}: <strong>{selectedPlan.name}</strong></span>
                <span className="plan-price">{t.payment.amount}: <strong>{selectedPlan.price}</strong></span>
              </div>
            )}
            
            {/* Step 1: Method Selection */}
            {paymentStep === 'method' && (
              <div className="payment-methods">
                <div className="payment-method-card" onClick={() => selectPaymentMethod('card')}>
                  <div className="method-icon">💳</div>
                  <h3>{t.payment.methods.card}</h3>
                  <p>{t.payment.methods.card_desc}</p>
                </div>
                <div className="payment-method-card" onClick={() => selectPaymentMethod('pix')}>
                  <div className="method-icon">📱</div>
                  <h3>{t.payment.methods.pix}</h3>
                  <p>{t.payment.methods.pix_desc}</p>
                </div>
                <div className="payment-method-card" onClick={() => selectPaymentMethod('crypto')}>
                  <div className="method-icon">🔐</div>
                  <h3>{t.payment.methods.crypto}</h3>
                  <p>{t.payment.methods.crypto_desc}</p>
                </div>
              </div>
            )}
            
            {/* Step 2: Form Input */}
            {paymentStep === 'form' && (
              <div className="payment-form">
                <div className="form-group">
                  <label>{t.payment.form.contract_url} *</label>
                  <input
                    type="text"
                    placeholder={t.payment.form.contract_placeholder}
                    value={formData.contractUrl}
                    onChange={(e) => handleFormChange('contractUrl', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>{t.payment.form.email} *</label>
                  <input
                    type="email"
                    placeholder={t.payment.form.email_placeholder}
                    value={formData.email}
                    onChange={(e) => handleFormChange('email', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>{t.payment.form.wallet}</label>
                  <input
                    type="text"
                    placeholder={t.payment.form.wallet_placeholder}
                    value={formData.wallet}
                    onChange={(e) => handleFormChange('wallet', e.target.value)}
                  />
                </div>
                
                {errorMessage && (
                  <div className="error-message">{errorMessage}</div>
                )}
                
                <div className="form-actions">
                  <button className="btn-secondary" onClick={() => setPaymentStep('method')}>
                    {t.payment.form.cancel}
                  </button>
                  <button className="btn-primary" onClick={executePayment}>
                    {t.payment.form.pay_button}
                  </button>
                </div>
              </div>
            )}
            
            {/* Step 3: Processing */}
            {paymentStep === 'processing' && (
              <div className="payment-processing">
                <div className="spinner"></div>
                <p>{t.payment.form.processing}</p>
              </div>
            )}
            
            {/* Step 4: Pix QR Code */}
            {paymentStep === 'pix' && pixData && (
              <div className="payment-pix">
                <h3>{t.payment.pix.title}</h3>
                <p>{t.payment.pix.instructions}</p>
                <div className="qr-code">
                  <img src={`data:image/png;base64,${pixData.qr_code_base64}`} alt="Pix QR Code" />
                </div>
                <button className="btn-secondary" onClick={() => {
                  navigator.clipboard.writeText(pixData.qr_code);
                  alert('Código copiado!');
                }}>
                  {t.payment.pix.copy_code}
                </button>
                <p className="waiting-text">{t.payment.pix.waiting}</p>
              </div>
            )}
            
            {/* Step 5: Success */}
            {paymentStep === 'success' && (
              <div className="payment-success">
                <div className="success-icon">✓</div>
                <h3>{t.payment.success.title}</h3>
                <p>{t.payment.success.message}</p>
                <p className="email-sent">{t.payment.success.email_sent}</p>
                <button className="btn-primary" onClick={closePaymentModal}>OK</button>
              </div>
            )}
            
            {/* Step 6: Error */}
            {paymentStep === 'error' && (
              <div className="payment-error">
                <div className="error-icon">✕</div>
                <h3>{t.payment.error.title}</h3>
                <p>{t.payment.error.message}</p>
                {errorMessage && <p className="error-details">{errorMessage}</p>}
                <div className="form-actions">
                  <button className="btn-secondary" onClick={closePaymentModal}>
                    {t.payment.form.cancel}
                  </button>
                  <button className="btn-primary" onClick={() => {
                    setPaymentStep('form');
                    setErrorMessage('');
                  }}>
                    {t.payment.error.try_again}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
