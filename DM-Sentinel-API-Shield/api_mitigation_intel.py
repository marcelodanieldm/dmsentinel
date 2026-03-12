"""
DM Sentinel - API Mitigation Intelligence Engine
PROMPT 7: Motor de Inteligencia de Mitigación Multilingüe

Author: DM Sentinel Security Team
Role: Senior API Pentester + Product Owner
Date: 2026-03-12

Purpose:
    Multilingual remediation advice engine for OWASP API Top 10 vulnerabilities.
    Provides technical, actionable mitigation strategies in 5 languages.

Supported Languages:
    - ES: Español (Spanish)
    - EN: English
    - FR: Français (French)
    - PT: Português (Portuguese)
    - EO: Esperanto

Compliance:
    ISO 27001, SOC2 aligned recommendations
"""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


# ============================================================================
# Vulnerability Types (OWASP API Top 10)
# ============================================================================

class VulnerabilityType(Enum):
    """OWASP API Security Top 10 vulnerability categories."""
    
    # API1:2023 - Broken Object Level Authorization
    BOLA = "BOLA"
    BROKEN_OBJECT_AUTH = "BROKEN_OBJECT_AUTH"
    
    # API2:2023 - Broken Authentication
    BROKEN_AUTH = "BROKEN_AUTH"
    WEAK_AUTHENTICATION = "WEAK_AUTHENTICATION"
    
    # API3:2023 - Broken Object Property Level Authorization
    MASS_ASSIGNMENT = "MASS_ASSIGNMENT"
    EXCESSIVE_DATA_EXPOSURE = "EXCESSIVE_DATA_EXPOSURE"
    
    # API4:2023 - Unrestricted Resource Consumption
    RATE_LIMITING = "RATE_LIMITING"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    
    # API5:2023 - Broken Function Level Authorization
    BFLA = "BFLA"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    
    # API6:2023 - Unrestricted Access to Sensitive Business Flows
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    FLOW_ABUSE = "FLOW_ABUSE"
    
    # API7:2023 - Server Side Request Forgery
    SSRF = "SSRF"
    
    # API8:2023 - Security Misconfiguration
    SECURITY_MISCONFIGURATION = "SECURITY_MISCONFIGURATION"
    CORS_MISCONFIGURATION = "CORS_MISCONFIGURATION"
    
    # API9:2023 - Improper Inventory Management
    API_VERSIONING = "API_VERSIONING"
    SHADOW_API = "SHADOW_API"
    
    # API10:2023 - Unsafe Consumption of APIs
    INJECTION = "INJECTION"
    SQL_INJECTION = "SQL_INJECTION"
    NOSQL_INJECTION = "NOSQL_INJECTION"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    XSS = "XSS"


class Language(Enum):
    """Supported languages for mitigation advice."""
    SPANISH = "ES"
    ENGLISH = "EN"
    FRENCH = "FR"
    PORTUGUESE = "PT"
    ESPERANTO = "EO"


# ============================================================================
# Mitigation Advice Database (Multilingual)
# ============================================================================

MITIGATION_DATABASE: Dict[VulnerabilityType, Dict[str, Dict[str, str]]] = {
    
    # ========================================================================
    # API1:2023 - BOLA (Broken Object Level Authorization)
    # ========================================================================
    VulnerabilityType.BOLA: {
        "title": {
            "ES": "Autorización Rota a Nivel de Objeto (BOLA)",
            "EN": "Broken Object Level Authorization (BOLA)",
            "FR": "Autorisation au Niveau Objet Cassée (BOLA)",
            "PT": "Autorização Quebrada em Nível de Objeto (BOLA)",
            "EO": "Rompita Objektnivela Aŭtorizo (BOLA)"
        },
        "description": {
            "ES": "Usuarios pueden acceder a objetos de otros usuarios sin validación de propiedad.",
            "EN": "Users can access other users' objects without ownership validation.",
            "FR": "Les utilisateurs peuvent accéder aux objets d'autres utilisateurs sans validation de propriété.",
            "PT": "Usuários podem acessar objetos de outros usuários sem validação de propriedade.",
            "EO": "Uzantoj povas aliri objektojn de aliaj uzantoj sen proprietecovalidigo."
        },
        "mitigation": {
            "ES": "Implementar validación de propiedad (Ownership) en el middleware de autorización. Verificar que user_id del token coincida con el propietario del recurso solicitado. Usar políticas ABAC (Attribute-Based Access Control) para validar acceso a objetos.",
            "EN": "Implement ownership validation in authorization middleware. Verify that token user_id matches the requested resource owner. Use ABAC (Attribute-Based Access Control) policies to validate object access.",
            "FR": "Implémenter la validation de propriété dans le middleware d'autorisation. Vérifier que l'user_id du token correspond au propriétaire de la ressource demandée. Utiliser des politiques ABAC (Contrôle d'Accès Basé sur les Attributs) pour valider l'accès aux objets.",
            "PT": "Implementar validação de propriedade no middleware de autorização. Verificar que o user_id do token corresponde ao proprietário do recurso solicitado. Usar políticas ABAC (Controle de Acesso Baseado em Atributos) para validar acesso a objetos.",
            "EO": "Efektivigu proprietecovalidigon en la aŭtorizadmezilo. Kontrolu ke la token-uzantidentigilo kongruas kun la petita rimedposedanto. Uzu ABAC-politikojn (Atribut-Bazita Alirkontrolo) por validigi objektaliran."
        },
        "code_example": {
            "ES": "# Middleware de autorización\n@app.before_request\ndef validate_ownership():\n    resource_id = request.view_args.get('id')\n    user_id = get_jwt_identity()\n    resource = Resource.query.get(resource_id)\n    if resource.owner_id != user_id:\n        abort(403, 'No autorizado')",
            "EN": "# Authorization middleware\n@app.before_request\ndef validate_ownership():\n    resource_id = request.view_args.get('id')\n    user_id = get_jwt_identity()\n    resource = Resource.query.get(resource_id)\n    if resource.owner_id != user_id:\n        abort(403, 'Unauthorized')",
            "FR": "# Middleware d'autorisation\n@app.before_request\ndef validate_ownership():\n    resource_id = request.view_args.get('id')\n    user_id = get_jwt_identity()\n    resource = Resource.query.get(resource_id)\n    if resource.owner_id != user_id:\n        abort(403, 'Non autorisé')",
            "PT": "# Middleware de autorização\n@app.before_request\ndef validate_ownership():\n    resource_id = request.view_args.get('id')\n    user_id = get_jwt_identity()\n    resource = Resource.query.get(resource_id)\n    if resource.owner_id != user_id:\n        abort(403, 'Não autorizado')",
            "EO": "# Aŭtorizadmezilo\n@app.before_request\ndef validate_ownership():\n    resource_id = request.view_args.get('id')\n    user_id = get_jwt_identity()\n    resource = Resource.query.get(resource_id)\n    if resource.owner_id != user_id:\n        abort(403, 'Neaŭtorizita')"
        },
        "tags": ["authorization", "ownership", "ABAC", "ISO27001:A.9.4.1"]
    },
    
    # ========================================================================
    # API2:2023 - Broken Authentication
    # ========================================================================
    VulnerabilityType.BROKEN_AUTH: {
        "title": {
            "ES": "Autenticación Rota",
            "EN": "Broken Authentication",
            "FR": "Authentification Cassée",
            "PT": "Autenticação Quebrada",
            "EO": "Rompita Aŭtentikigo"
        },
        "description": {
            "ES": "Mecanismos de autenticación débiles o mal implementados que permiten acceso no autorizado.",
            "EN": "Weak or poorly implemented authentication mechanisms allowing unauthorized access.",
            "FR": "Mécanismes d'authentification faibles ou mal implémentés permettant un accès non autorisé.",
            "PT": "Mecanismos de autenticação fracos ou mal implementados permitindo acesso não autorizado.",
            "EO": "Malfortaj aŭ malbone efektivigitaj aŭtentikigmekanismoj permesantaj neaŭtorizitan aliron."
        },
        "mitigation": {
            "ES": "Forzar MFA (Multi-Factor Authentication) para todas las cuentas. Implementar rotación de tokens JWT con tiempos de expiración cortos (15 minutos para access tokens). Usar refresh tokens con HttpOnly cookies. Implementar rate limiting en endpoints de autenticación (5 intentos/minuto).",
            "EN": "Enforce MFA (Multi-Factor Authentication) for all accounts. Implement JWT token rotation with short expiration times (15 minutes for access tokens). Use refresh tokens with HttpOnly cookies. Implement rate limiting on authentication endpoints (5 attempts/minute).",
            "FR": "Imposer MFA (Authentification Multi-Facteurs) pour tous les comptes. Implémenter la rotation des tokens JWT avec des temps d'expiration courts (15 minutes pour les access tokens). Utiliser des refresh tokens avec cookies HttpOnly. Implémenter une limitation de débit sur les endpoints d'authentification (5 tentatives/minute).",
            "PT": "Forçar MFA (Autenticação Multi-Fator) para todas as contas. Implementar rotação de tokens JWT com tempos de expiração curtos (15 minutos para access tokens). Usar refresh tokens com cookies HttpOnly. Implementar limitação de taxa em endpoints de autenticação (5 tentativas/minuto).",
            "EO": "Devigi MFA (Multfaktora Aŭtentikigo) por ĉiuj kontoj. Efektivigu JWT-symbolrotacion kun mallongaj datiĝtempoj (15 minutoj por alirtokenoj). Uzu refreŝigajn tokenojn kun HttpOnly-kuketoj. Efektivigu rapidlimigon ĉe aŭtentikigfinoj (5 provoj/minuto)."
        },
        "code_example": {
            "ES": "# JWT con expiración corta\nfrom datetime import timedelta\n\naccess_token = create_access_token(\n    identity=user.id,\n    expires_delta=timedelta(minutes=15)\n)\n\nrefresh_token = create_refresh_token(\n    identity=user.id,\n    expires_delta=timedelta(days=30)\n)",
            "EN": "# JWT with short expiration\nfrom datetime import timedelta\n\naccess_token = create_access_token(\n    identity=user.id,\n    expires_delta=timedelta(minutes=15)\n)\n\nrefresh_token = create_refresh_token(\n    identity=user.id,\n    expires_delta=timedelta(days=30)\n)",
            "FR": "# JWT avec expiration courte\nfrom datetime import timedelta\n\naccess_token = create_access_token(\n    identity=user.id,\n    expires_delta=timedelta(minutes=15)\n)\n\nrefresh_token = create_refresh_token(\n    identity=user.id,\n    expires_delta=timedelta(days=30)\n)",
            "PT": "# JWT com expiração curta\nfrom datetime import timedelta\n\naccess_token = create_access_token(\n    identity=user.id,\n    expires_delta=timedelta(minutes=15)\n)\n\nrefresh_token = create_refresh_token(\n    identity=user.id,\n    expires_delta=timedelta(days=30)\n)",
            "EO": "# JWT kun mallonga datiĝo\nfrom datetime import timedelta\n\naccess_token = create_access_token(\n    identity=user.id,\n    expires_delta=timedelta(minutes=15)\n)\n\nrefresh_token = create_refresh_token(\n    identity=user.id,\n    expires_delta=timedelta(days=30)\n)"
        },
        "tags": ["authentication", "MFA", "JWT", "ISO27001:A.9.4.2", "SOC2:CC6.1"]
    },
    
    # ========================================================================
    # API3:2023 - Mass Assignment / Excessive Data Exposure
    # ========================================================================
    VulnerabilityType.MASS_ASSIGNMENT: {
        "title": {
            "ES": "Asignación Masiva / Exposición Excesiva de Datos",
            "EN": "Mass Assignment / Excessive Data Exposure",
            "FR": "Affectation Massive / Exposition Excessive de Données",
            "PT": "Atribuição em Massa / Exposição Excessiva de Dados",
            "EO": "Masa Asigno / Troega Datummalkaŝo"
        },
        "description": {
            "ES": "Permitir que clientes modifiquen propiedades no autorizadas o exponer datos sensibles innecesariamente.",
            "EN": "Allowing clients to modify unauthorized properties or unnecessarily exposing sensitive data.",
            "FR": "Permettre aux clients de modifier des propriétés non autorisées ou exposer inutilement des données sensibles.",
            "PT": "Permitir que clientes modifiquem propriedades não autorizadas ou expor desnecessariamente dados sensíveis.",
            "EO": "Permesi al klientoj modifi neaŭtorizitajn propraĵojn aŭ senutile malkaŝi sentemajn datumojn."
        },
        "mitigation": {
            "ES": "Definir esquemas de entrada estrictos usando DTOs (Data Transfer Objects). Implementar 'allow-lists' explícitas para campos del JSON permitidos. Usar serializers con campos whitelisted. Aplicar el principio de 'least privilege' en respuestas API: solo devolver datos necesarios.",
            "EN": "Define strict input schemas using DTOs (Data Transfer Objects). Implement explicit 'allow-lists' for permitted JSON fields. Use serializers with whitelisted fields. Apply 'least privilege' principle in API responses: return only necessary data.",
            "FR": "Définir des schémas d'entrée stricts en utilisant des DTOs (Objets de Transfert de Données). Implémenter des 'listes blanches' explicites pour les champs JSON autorisés. Utiliser des sérialiseurs avec champs en liste blanche. Appliquer le principe du 'moindre privilège' dans les réponses API: retourner uniquement les données nécessaires.",
            "PT": "Definir esquemas de entrada estritos usando DTOs (Objetos de Transferência de Dados). Implementar 'listas de permissão' explícitas para campos JSON permitidos. Usar serializadores com campos em lista de permissão. Aplicar o princípio do 'menor privilégio' em respostas API: retornar apenas dados necessários.",
            "EO": "Difinu striktan enirskedon uzante DTO-ojn (Datumtransportajn Objektojn). Efektivigu eksplicitan 'permes-listojn' por permesitaj JSON-kampoj. Uzu seriigajn kampojn kun blankaj listoj. Apliku la principon de 'malplej privilegio' en API-respondoj: redonu nur necesajn datumojn."
        },
        "code_example": {
            "ES": "# DTO con allow-list\nfrom pydantic import BaseModel\n\nclass UserUpdateDTO(BaseModel):\n    name: str\n    email: str\n    # is_admin NO está en el DTO (protegido)\n    \n@app.patch('/users/{id}')\ndef update_user(id: int, data: UserUpdateDTO):\n    user = User.query.get(id)\n    user.name = data.name\n    user.email = data.email\n    # Solo campos permitidos son actualizados",
            "EN": "# DTO with allow-list\nfrom pydantic import BaseModel\n\nclass UserUpdateDTO(BaseModel):\n    name: str\n    email: str\n    # is_admin NOT in DTO (protected)\n    \n@app.patch('/users/{id}')\ndef update_user(id: int, data: UserUpdateDTO):\n    user = User.query.get(id)\n    user.name = data.name\n    user.email = data.email\n    # Only allowed fields are updated",
            "FR": "# DTO avec liste blanche\nfrom pydantic import BaseModel\n\nclass UserUpdateDTO(BaseModel):\n    name: str\n    email: str\n    # is_admin PAS dans le DTO (protégé)\n    \n@app.patch('/users/{id}')\ndef update_user(id: int, data: UserUpdateDTO):\n    user = User.query.get(id)\n    user.name = data.name\n    user.email = data.email\n    # Seuls les champs autorisés sont mis à jour",
            "PT": "# DTO com lista de permissão\nfrom pydantic import BaseModel\n\nclass UserUpdateDTO(BaseModel):\n    name: str\n    email: str\n    # is_admin NÃO está no DTO (protegido)\n    \n@app.patch('/users/{id}')\ndef update_user(id: int, data: UserUpdateDTO):\n    user = User.query.get(id)\n    user.name = data.name\n    user.email = data.email\n    # Apenas campos permitidos são atualizados",
            "EO": "# DTO kun permes-listo\nfrom pydantic import BaseModel\n\nclass UserUpdateDTO(BaseModel):\n    name: str\n    email: str\n    # is_admin NE estas en la DTO (protektita)\n    \n@app.patch('/users/{id}')\ndef update_user(id: int, data: UserUpdateDTO):\n    user = User.query.get(id)\n    user.name = data.name\n    user.email = data.email\n    # Nur permesitaj kampoj estas ĝisdatigitaj"
        },
        "tags": ["mass-assignment", "DTO", "data-exposure", "ISO27001:A.14.1.2"]
    },
    
    # ========================================================================
    # API4:2023 - Rate Limiting / Resource Exhaustion
    # ========================================================================
    VulnerabilityType.RATE_LIMITING: {
        "title": {
            "ES": "Limitación de Tasa / Agotamiento de Recursos",
            "EN": "Rate Limiting / Resource Exhaustion",
            "FR": "Limitation de Débit / Épuisement des Ressources",
            "PT": "Limitação de Taxa / Esgotamento de Recursos",
            "EO": "Rapidlimigo / Rimedmalpleniĝo"
        },
        "description": {
            "ES": "Falta de límites en consumo de recursos permitiendo ataques DoS.",
            "EN": "Lack of resource consumption limits allowing DoS attacks.",
            "FR": "Absence de limites de consommation de ressources permettant les attaques DoS.",
            "PT": "Falta de limites de consumo de recursos permitindo ataques DoS.",
            "EO": "Manko de rimedkonsumlimoj permesantaj DoS-atakojn."
        },
        "mitigation": {
            "ES": "Implementar rate limiting multinivel: por IP (100 req/min), por usuario autenticado (1000 req/min), por endpoint crítico (10 req/min). Usar Redis para almacenar contadores distribuidos. Implementar timeout en operaciones costosas (max 30s). Aplicar paginación obligatoria en listados (max 100 items).",
            "EN": "Implement multi-level rate limiting: per IP (100 req/min), per authenticated user (1000 req/min), per critical endpoint (10 req/min). Use Redis for distributed counters. Implement timeout on expensive operations (max 30s). Apply mandatory pagination on listings (max 100 items).",
            "FR": "Implémenter une limitation de débit multi-niveaux: par IP (100 req/min), par utilisateur authentifié (1000 req/min), par endpoint critique (10 req/min). Utiliser Redis pour les compteurs distribués. Implémenter un timeout sur les opérations coûteuses (max 30s). Appliquer une pagination obligatoire sur les listes (max 100 éléments).",
            "PT": "Implementar limitação de taxa multinível: por IP (100 req/min), por usuário autenticado (1000 req/min), por endpoint crítico (10 req/min). Usar Redis para contadores distribuídos. Implementar timeout em operações custosas (max 30s). Aplicar paginação obrigatória em listagens (max 100 itens).",
            "EO": "Efektivigu multnivelan rapidlimigon: per IP (100 pet/min), per aŭtentikigita uzanto (1000 pet/min), per kritika fino (10 pet/min). Uzu Redis por distribuitaj kalkuliloj. Efektivigu tempolimiton sur multekostaj operacioj (maks 30s). Apliku devigan paĝigon sur listoj (maks 100 eroj)."
        },
        "code_example": {
            "ES": "# Rate limiting con Flask-Limiter\nfrom flask_limiter import Limiter\n\nlimiter = Limiter(\n    app,\n    key_func=get_remote_address,\n    storage_uri='redis://localhost:6379'\n)\n\n@app.route('/api/users')\n@limiter.limit('100 per minute')\ndef get_users():\n    return User.query.paginate(page=1, per_page=100)",
            "EN": "# Rate limiting with Flask-Limiter\nfrom flask_limiter import Limiter\n\nlimiter = Limiter(\n    app,\n    key_func=get_remote_address,\n    storage_uri='redis://localhost:6379'\n)\n\n@app.route('/api/users')\n@limiter.limit('100 per minute')\ndef get_users():\n    return User.query.paginate(page=1, per_page=100)",
            "FR": "# Limitation de débit avec Flask-Limiter\nfrom flask_limiter import Limiter\n\nlimiter = Limiter(\n    app,\n    key_func=get_remote_address,\n    storage_uri='redis://localhost:6379'\n)\n\n@app.route('/api/users')\n@limiter.limit('100 per minute')\ndef get_users():\n    return User.query.paginate(page=1, per_page=100)",
            "PT": "# Limitação de taxa com Flask-Limiter\nfrom flask_limiter import Limiter\n\nlimiter = Limiter(\n    app,\n    key_func=get_remote_address,\n    storage_uri='redis://localhost:6379'\n)\n\n@app.route('/api/users')\n@limiter.limit('100 per minute')\ndef get_users():\n    return User.query.paginate(page=1, per_page=100)",
            "EO": "# Rapidlimigo kun Flask-Limiter\nfrom flask_limiter import Limiter\n\nlimiter = Limiter(\n    app,\n    key_func=get_remote_address,\n    storage_uri='redis://localhost:6379'\n)\n\n@app.route('/api/users')\n@limiter.limit('100 per minute')\ndef get_users():\n    return User.query.paginate(page=1, per_page=100)"
        },
        "tags": ["rate-limiting", "DoS", "Redis", "ISO27001:A.12.1.3"]
    },
    
    # ========================================================================
    # API5:2023 - BFLA (Broken Function Level Authorization)
    # ========================================================================
    VulnerabilityType.BFLA: {
        "title": {
            "ES": "Autorización Rota a Nivel de Función (BFLA)",
            "EN": "Broken Function Level Authorization (BFLA)",
            "FR": "Autorisation au Niveau Fonction Cassée (BFLA)",
            "PT": "Autorização Quebrada em Nível de Função (BFLA)",
            "EO": "Rompita Funkcinivela Aŭtorizo (BFLA)"
        },
        "description": {
            "ES": "Usuarios con privilegios bajos pueden ejecutar funciones administrativas.",
            "EN": "Low-privilege users can execute administrative functions.",
            "FR": "Les utilisateurs à faibles privilèges peuvent exécuter des fonctions administratives.",
            "PT": "Usuários com privilégios baixos podem executar funções administrativas.",
            "EO": "Malaltprivilegiaj uzantoj povas plenumi administrajn funkciojn."
        },
        "mitigation": {
            "ES": "Implementar RBAC (Role-Based Access Control) estricto en todos los endpoints. Validar roles en cada request usando decoradores @require_role('admin'). Denegar por defecto: solo permitir acceso si rol está explícitamente autorizado. Auditar todos los accesos a funciones privilegiadas.",
            "EN": "Implement strict RBAC (Role-Based Access Control) on all endpoints. Validate roles on each request using @require_role('admin') decorators. Deny by default: only allow access if role is explicitly authorized. Audit all accesses to privileged functions.",
            "FR": "Implémenter un RBAC (Contrôle d'Accès Basé sur les Rôles) strict sur tous les endpoints. Valider les rôles à chaque requête en utilisant des décorateurs @require_role('admin'). Refuser par défaut: autoriser l'accès uniquement si le rôle est explicitement autorisé. Auditer tous les accès aux fonctions privilégiées.",
            "PT": "Implementar RBAC (Controle de Acesso Baseado em Funções) estrito em todos os endpoints. Validar funções em cada requisição usando decoradores @require_role('admin'). Negar por padrão: permitir acesso apenas se a função estiver explicitamente autorizada. Auditar todos os acessos a funções privilegiadas.",
            "EO": "Efektivigu striktan RBAC (Rolbazan Alirkontrolo) sur ĉiuj finoj. Validigi rolojn ĉe ĉiu peto uzante @require_role('admin') dekoraĵojn. Rifuzi defaŭlte: nur permesi aliron se rolo estas eksplicite aŭtorizita. Kontroli ĉiujn alirojn al privilegiitaj funkcioj."
        },
        "code_example": {
            "ES": "# Decorador RBAC\nfrom functools import wraps\n\ndef require_role(*roles):\n    def decorator(f):\n        @wraps(f)\n        def wrapper(*args, **kwargs):\n            user = get_current_user()\n            if user.role not in roles:\n                abort(403, 'Rol insuficiente')\n            return f(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@app.delete('/users/{id}')\n@require_role('admin', 'superadmin')\ndef delete_user(id):\n    User.query.get(id).delete()",
            "EN": "# RBAC decorator\nfrom functools import wraps\n\ndef require_role(*roles):\n    def decorator(f):\n        @wraps(f)\n        def wrapper(*args, **kwargs):\n            user = get_current_user()\n            if user.role not in roles:\n                abort(403, 'Insufficient role')\n            return f(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@app.delete('/users/{id}')\n@require_role('admin', 'superadmin')\ndef delete_user(id):\n    User.query.get(id).delete()",
            "FR": "# Décorateur RBAC\nfrom functools import wraps\n\ndef require_role(*roles):\n    def decorator(f):\n        @wraps(f)\n        def wrapper(*args, **kwargs):\n            user = get_current_user()\n            if user.role not in roles:\n                abort(403, 'Rôle insuffisant')\n            return f(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@app.delete('/users/{id}')\n@require_role('admin', 'superadmin')\ndef delete_user(id):\n    User.query.get(id).delete()",
            "PT": "# Decorador RBAC\nfrom functools import wraps\n\ndef require_role(*roles):\n    def decorator(f):\n        @wraps(f)\n        def wrapper(*args, **kwargs):\n            user = get_current_user()\n            if user.role not in roles:\n                abort(403, 'Função insuficiente')\n            return f(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@app.delete('/users/{id}')\n@require_role('admin', 'superadmin')\ndef delete_user(id):\n    User.query.get(id).delete()",
            "EO": "# RBAC-dekoraĵo\nfrom functools import wraps\n\ndef require_role(*roles):\n    def decorator(f):\n        @wraps(f)\n        def wrapper(*args, **kwargs):\n            user = get_current_user()\n            if user.role not in roles:\n                abort(403, 'Nesufiĉa rolo')\n            return f(*args, **kwargs)\n        return wrapper\n    return decorator\n\n@app.delete('/users/{id}')\n@require_role('admin', 'superadmin')\ndef delete_user(id):\n    User.query.get(id).delete()"
        },
        "tags": ["authorization", "RBAC", "privilege-escalation", "ISO27001:A.9.2.3"]
    },
    
    # ========================================================================
    # API6:2023 - Business Logic Abuse
    # ========================================================================
    VulnerabilityType.BUSINESS_LOGIC: {
        "title": {
            "ES": "Abuso de Lógica de Negocio",
            "EN": "Business Logic Abuse",
            "FR": "Abus de Logique Métier",
            "PT": "Abuso de Lógica de Negócio",
            "EO": "Misuso de Komerca Logiko"
        },
        "description": {
            "ES": "Explotación de flujos de negocio legítimos para propósitos maliciosos.",
            "EN": "Exploitation of legitimate business flows for malicious purposes.",
            "FR": "Exploitation de flux métier légitimes à des fins malveillantes.",
            "PT": "Exploração de fluxos de negócio legítimos para propósitos maliciosos.",
            "EO": "Ekspluato de legitimaj komercaj fluoj por malbonajn celojn."
        },
        "mitigation": {
            "ES": "Implementar validación de secuencia: verificar que acciones sigan un orden lógico (ej: checkout solo después de add-to-cart). Usar state machines para flujos complejos. Implementar CAPTCHA en acciones críticas. Agregar delays obligatorios entre acciones sensibles (ej: 2 segundos entre transferencias).",
            "EN": "Implement sequence validation: verify actions follow logical order (e.g., checkout only after add-to-cart). Use state machines for complex flows. Implement CAPTCHA on critical actions. Add mandatory delays between sensitive actions (e.g., 2 seconds between transfers).",
            "FR": "Implémenter la validation de séquence: vérifier que les actions suivent un ordre logique (ex: paiement seulement après ajout au panier). Utiliser des machines à états pour les flux complexes. Implémenter CAPTCHA sur les actions critiques. Ajouter des délais obligatoires entre actions sensibles (ex: 2 secondes entre transferts).",
            "PT": "Implementar validação de sequência: verificar que ações sigam uma ordem lógica (ex: checkout somente após add-to-cart). Usar máquinas de estado para fluxos complexos. Implementar CAPTCHA em ações críticas. Adicionar atrasos obrigatórios entre ações sensíveis (ex: 2 segundos entre transferências).",
            "EO": "Efektivigu sekvencovalidigon: kontrolu ke agoj sekvas logikan ordon (ekz: eliro nur post aldoni-al-korbeto). Uzu statmaŝinojn por kompleksaj fluoj. Efektivigu CAPTCHA sur kritikaj agoj. Aldonu devigajn prokrastojn inter sentemaj agoj (ekz: 2 sekundoj inter translokigoj)."
        },
        "code_example": {
            "ES": "# State machine para pedidos\nclass OrderStateMachine:\n    STATES = ['CART', 'CHECKOUT', 'PAYMENT', 'CONFIRMED']\n    \n    def can_transition(self, from_state, to_state):\n        allowed = {\n            'CART': ['CHECKOUT'],\n            'CHECKOUT': ['PAYMENT', 'CART'],\n            'PAYMENT': ['CONFIRMED', 'CHECKOUT'],\n            'CONFIRMED': []\n        }\n        return to_state in allowed.get(from_state, [])\n\n@app.post('/orders/{id}/checkout')\ndef checkout(id):\n    order = Order.query.get(id)\n    if not state_machine.can_transition(order.state, 'CHECKOUT'):\n        abort(400, 'Transición inválida')",
            "EN": "# State machine for orders\nclass OrderStateMachine:\n    STATES = ['CART', 'CHECKOUT', 'PAYMENT', 'CONFIRMED']\n    \n    def can_transition(self, from_state, to_state):\n        allowed = {\n            'CART': ['CHECKOUT'],\n            'CHECKOUT': ['PAYMENT', 'CART'],\n            'PAYMENT': ['CONFIRMED', 'CHECKOUT'],\n            'CONFIRMED': []\n        }\n        return to_state in allowed.get(from_state, [])\n\n@app.post('/orders/{id}/checkout')\ndef checkout(id):\n    order = Order.query.get(id)\n    if not state_machine.can_transition(order.state, 'CHECKOUT'):\n        abort(400, 'Invalid transition')",
            "FR": "# Machine à états pour commandes\nclass OrderStateMachine:\n    STATES = ['CART', 'CHECKOUT', 'PAYMENT', 'CONFIRMED']\n    \n    def can_transition(self, from_state, to_state):\n        allowed = {\n            'CART': ['CHECKOUT'],\n            'CHECKOUT': ['PAYMENT', 'CART'],\n            'PAYMENT': ['CONFIRMED', 'CHECKOUT'],\n            'CONFIRMED': []\n        }\n        return to_state in allowed.get(from_state, [])\n\n@app.post('/orders/{id}/checkout')\ndef checkout(id):\n    order = Order.query.get(id)\n    if not state_machine.can_transition(order.state, 'CHECKOUT'):\n        abort(400, 'Transition invalide')",
            "PT": "# Máquina de estados para pedidos\nclass OrderStateMachine:\n    STATES = ['CART', 'CHECKOUT', 'PAYMENT', 'CONFIRMED']\n    \n    def can_transition(self, from_state, to_state):\n        allowed = {\n            'CART': ['CHECKOUT'],\n            'CHECKOUT': ['PAYMENT', 'CART'],\n            'PAYMENT': ['CONFIRMED', 'CHECKOUT'],\n            'CONFIRMED': []\n        }\n        return to_state in allowed.get(from_state, [])\n\n@app.post('/orders/{id}/checkout')\ndef checkout(id):\n    order = Order.query.get(id)\n    if not state_machine.can_transition(order.state, 'CHECKOUT'):\n        abort(400, 'Transição inválida')",
            "EO": "# Statmaŝino por mendoj\nclass OrderStateMachine:\n    STATES = ['CART', 'CHECKOUT', 'PAYMENT', 'CONFIRMED']\n    \n    def can_transition(self, from_state, to_state):\n        allowed = {\n            'CART': ['CHECKOUT'],\n            'CHECKOUT': ['PAYMENT', 'CART'],\n            'PAYMENT': ['CONFIRMED', 'CHECKOUT'],\n            'CONFIRMED': []\n        }\n        return to_state in allowed.get(from_state, [])\n\n@app.post('/orders/{id}/checkout')\ndef checkout(id):\n    order = Order.query.get(id)\n    if not state_machine.can_transition(order.state, 'CHECKOUT'):\n        abort(400, 'Nevalida transpaso')"
        },
        "tags": ["business-logic", "state-machine", "captcha", "ISO27001:A.14.1.1"]
    },
    
    # ========================================================================
    # API7:2023 - SSRF (Server-Side Request Forgery)
    # ========================================================================
    VulnerabilityType.SSRF: {
        "title": {
            "ES": "Falsificación de Solicitud del Lado del Servidor (SSRF)",
            "EN": "Server-Side Request Forgery (SSRF)",
            "FR": "Falsification de Requête Côté Serveur (SSRF)",
            "PT": "Falsificação de Solicitação do Lado do Servidor (SSRF)",
            "EO": "Servil-Flanke Peto-Falsigo (SSRF)"
        },
        "description": {
            "ES": "Aplicación hace requests a URLs arbitrarias controladas por atacantes.",
            "EN": "Application makes requests to arbitrary URLs controlled by attackers.",
            "FR": "L'application effectue des requêtes vers des URLs arbitraires contrôlées par des attaquants.",
            "PT": "Aplicação faz requisições para URLs arbitrárias controladas por atacantes.",
            "EO": "Aplikaĵo faras petojn al arbitraj URL-oj kontrolitaj de atakantoj."
        },
        "mitigation": {
            "ES": "Implementar whitelist estricta de dominios permitidos. Validar y sanitizar todas las URLs de entrada. Bloquear IPs privadas y localhost (127.0.0.1, 192.168.x.x, 10.x.x.x). Usar biblioteca de validación de URLs. Deshabilitar redirects automáticos en HTTP clients.",
            "EN": "Implement strict whitelist of allowed domains. Validate and sanitize all input URLs. Block private IPs and localhost (127.0.0.1, 192.168.x.x, 10.x.x.x). Use URL validation library. Disable automatic redirects in HTTP clients.",
            "FR": "Implémenter une liste blanche stricte des domaines autorisés. Valider et assainir toutes les URLs d'entrée. Bloquer les IPs privées et localhost (127.0.0.1, 192.168.x.x, 10.x.x.x). Utiliser une bibliothèque de validation d'URL. Désactiver les redirections automatiques dans les clients HTTP.",
            "PT": "Implementar whitelist estrita de domínios permitidos. Validar e sanitizar todas as URLs de entrada. Bloquear IPs privados e localhost (127.0.0.1, 192.168.x.x, 10.x.x.x). Usar biblioteca de validação de URLs. Desabilitar redirecionamentos automáticos em clientes HTTP.",
            "EO": "Efektivigu striktan blankanliston de permesitaj domajnoj. Validigi kaj sanigi ĉiujn enirajn URL-ojn. Bloki privatajn IP-ojn kaj localhost (127.0.0.1, 192.168.x.x, 10.x.x.x). Uzi URL-validigan bibliotekon. Malŝalti aŭtomatajn alidirektojn en HTTP-klientoj."
        },
        "code_example": {
            "ES": "# Validación SSRF\nimport ipaddress\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    parsed = urlparse(url)\n    \n    # Validar dominio\n    if parsed.netloc not in ALLOWED_DOMAINS:\n        return False\n    \n    # Bloquear IPs privadas\n    try:\n        ip = ipaddress.ip_address(parsed.hostname)\n        if ip.is_private or ip.is_loopback:\n            return False\n    except:\n        pass\n    \n    return True\n\n@app.post('/fetch')\ndef fetch_url(url: str):\n    if not is_safe_url(url):\n        abort(400, 'URL no permitida')\n    return requests.get(url, allow_redirects=False)",
            "EN": "# SSRF validation\nimport ipaddress\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    parsed = urlparse(url)\n    \n    # Validate domain\n    if parsed.netloc not in ALLOWED_DOMAINS:\n        return False\n    \n    # Block private IPs\n    try:\n        ip = ipaddress.ip_address(parsed.hostname)\n        if ip.is_private or ip.is_loopback:\n            return False\n    except:\n        pass\n    \n    return True\n\n@app.post('/fetch')\ndef fetch_url(url: str):\n    if not is_safe_url(url):\n        abort(400, 'URL not allowed')\n    return requests.get(url, allow_redirects=False)",
            "FR": "# Validation SSRF\nimport ipaddress\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    parsed = urlparse(url)\n    \n    # Valider le domaine\n    if parsed.netloc not in ALLOWED_DOMAINS:\n        return False\n    \n    # Bloquer les IPs privées\n    try:\n        ip = ipaddress.ip_address(parsed.hostname)\n        if ip.is_private or ip.is_loopback:\n            return False\n    except:\n        pass\n    \n    return True\n\n@app.post('/fetch')\ndef fetch_url(url: str):\n    if not is_safe_url(url):\n        abort(400, 'URL non autorisée')\n    return requests.get(url, allow_redirects=False)",
            "PT": "# Validação SSRF\nimport ipaddress\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    parsed = urlparse(url)\n    \n    # Validar domínio\n    if parsed.netloc not in ALLOWED_DOMAINS:\n        return False\n    \n    # Bloquear IPs privados\n    try:\n        ip = ipaddress.ip_address(parsed.hostname)\n        if ip.is_private or ip.is_loopback:\n            return False\n    except:\n        pass\n    \n    return True\n\n@app.post('/fetch')\ndef fetch_url(url: str):\n    if not is_safe_url(url):\n        abort(400, 'URL não permitida')\n    return requests.get(url, allow_redirects=False)",
            "EO": "# SSRF-validigo\nimport ipaddress\nfrom urllib.parse import urlparse\n\nALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']\n\ndef is_safe_url(url):\n    parsed = urlparse(url)\n    \n    # Validigi domajnon\n    if parsed.netloc not in ALLOWED_DOMAINS:\n        return False\n    \n    # Bloki privatajn IP-ojn\n    try:\n        ip = ipaddress.ip_address(parsed.hostname)\n        if ip.is_private or ip.is_loopback:\n            return False\n    except:\n        pass\n    \n    return True\n\n@app.post('/fetch')\ndef fetch_url(url: str):\n    if not is_safe_url(url):\n        abort(400, 'URL ne permesita')\n    return requests.get(url, allow_redirects=False)"
        },
        "tags": ["SSRF", "URL-validation", "whitelist", "ISO27001:A.14.1.3"]
    },
    
    # ========================================================================
    # API8:2023 - Security Misconfiguration
    # ========================================================================
    VulnerabilityType.SECURITY_MISCONFIGURATION: {
        "title": {
            "ES": "Configuración de Seguridad Incorrecta",
            "EN": "Security Misconfiguration",
            "FR": "Mauvaise Configuration de Sécurité",
            "PT": "Configuração de Segurança Incorreta",
            "EO": "Malbona Sekureca Agordo"
        },
        "description": {
            "ES": "Configuraciones inseguras que exponen la aplicación a ataques.",
            "EN": "Insecure configurations exposing application to attacks.",
            "FR": "Configurations non sécurisées exposant l'application aux attaques.",
            "PT": "Configurações inseguras que expõem a aplicação a ataques.",
            "EO": "Nesekuraj agordoj malkaŝantaj aplikaĵon al atakoj."
        },
        "mitigation": {
            "ES": "Configurar CORS restrictivo: solo orígenes explícitamente permitidos. Deshabilitar stack traces en producción. Remover headers que revelen tecnología (X-Powered-By, Server). Habilitar security headers: HSTS, X-Frame-Options, CSP, X-Content-Type-Options. Usar HTTPS obligatorio con TLS 1.3+.",
            "EN": "Configure restrictive CORS: only explicitly allowed origins. Disable stack traces in production. Remove headers revealing technology (X-Powered-By, Server). Enable security headers: HSTS, X-Frame-Options, CSP, X-Content-Type-Options. Use mandatory HTTPS with TLS 1.3+.",
            "FR": "Configurer CORS restrictif: seulement origines explicitement autorisées. Désactiver les traces de pile en production. Retirer les en-têtes révélant la technologie (X-Powered-By, Server). Activer les en-têtes de sécurité: HSTS, X-Frame-Options, CSP, X-Content-Type-Options. Utiliser HTTPS obligatoire avec TLS 1.3+.",
            "PT": "Configurar CORS restritivo: apenas origens explicitamente permitidas. Desabilitar stack traces em produção. Remover headers que revelam tecnologia (X-Powered-By, Server). Habilitar security headers: HSTS, X-Frame-Options, CSP, X-Content-Type-Options. Usar HTTPS obrigatório com TLS 1.3+.",
            "EO": "Agordi restriktivan CORS: nur eksplicite permesitaj originaloj. Malŝalti stakspadojn en produktado. Forigi titolojn malkaŝantajn teknologion (X-Powered-By, Server). Ebligi sekurecajn titolojn: HSTS, X-Frame-Options, CSP, X-Content-Type-Options. Uzi devigan HTTPS kun TLS 1.3+."
        },
        "code_example": {
            "ES": "# Security headers con Flask\nfrom flask import Flask\nfrom flask_cors import CORS\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\n\n# CORS restrictivo\nCORS(app, origins=['https://app.example.com'])\n\n# Security headers\nTalisman(app,\n    force_https=True,\n    strict_transport_security=True,\n    frame_options='DENY',\n    content_security_policy={\n        'default-src': \"'self'\"\n    }\n)\n\n# Remover headers reveladores\n@app.after_request\ndef remove_headers(response):\n    response.headers.pop('Server', None)\n    response.headers.pop('X-Powered-By', None)\n    return response",
            "EN": "# Security headers with Flask\nfrom flask import Flask\nfrom flask_cors import CORS\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\n\n# Restrictive CORS\nCORS(app, origins=['https://app.example.com'])\n\n# Security headers\nTalisman(app,\n    force_https=True,\n    strict_transport_security=True,\n    frame_options='DENY',\n    content_security_policy={\n        'default-src': \"'self'\"\n    }\n)\n\n# Remove revealing headers\n@app.after_request\ndef remove_headers(response):\n    response.headers.pop('Server', None)\n    response.headers.pop('X-Powered-By', None)\n    return response",
            "FR": "# En-têtes de sécurité avec Flask\nfrom flask import Flask\nfrom flask_cors import CORS\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\n\n# CORS restrictif\nCORS(app, origins=['https://app.example.com'])\n\n# En-têtes de sécurité\nTalisman(app,\n    force_https=True,\n    strict_transport_security=True,\n    frame_options='DENY',\n    content_security_policy={\n        'default-src': \"'self'\"\n    }\n)\n\n# Retirer en-têtes révélateurs\n@app.after_request\ndef remove_headers(response):\n    response.headers.pop('Server', None)\n    response.headers.pop('X-Powered-By', None)\n    return response",
            "PT": "# Security headers com Flask\nfrom flask import Flask\nfrom flask_cors import CORS\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\n\n# CORS restritivo\nCORS(app, origins=['https://app.example.com'])\n\n# Security headers\nTalisman(app,\n    force_https=True,\n    strict_transport_security=True,\n    frame_options='DENY',\n    content_security_policy={\n        'default-src': \"'self'\"\n    }\n)\n\n# Remover headers reveladores\n@app.after_request\ndef remove_headers(response):\n    response.headers.pop('Server', None)\n    response.headers.pop('X-Powered-By', None)\n    return response",
            "EO": "# Sekurecaj titoloj kun Flask\nfrom flask import Flask\nfrom flask_cors import CORS\nfrom flask_talisman import Talisman\n\napp = Flask(__name__)\n\n# Restriktiva CORS\nCORS(app, origins=['https://app.example.com'])\n\n# Sekurecaj titoloj\nTalisman(app,\n    force_https=True,\n    strict_transport_security=True,\n    frame_options='DENY',\n    content_security_policy={\n        'default-src': \"'self'\"\n    }\n)\n\n# Forigi malkaŝajn titolojn\n@app.after_request\ndef remove_headers(response):\n    response.headers.pop('Server', None)\n    response.headers.pop('X-Powered-By', None)\n    return response"
        },
        "tags": ["misconfiguration", "CORS", "HTTPS", "security-headers", "ISO27001:A.14.1.2"]
    },
    
    # ========================================================================
    # API9:2023 - Improper Inventory Management
    # ========================================================================
    VulnerabilityType.API_VERSIONING: {
        "title": {
            "ES": "Gestión Inadecuada de Inventario de APIs",
            "EN": "Improper API Inventory Management",
            "FR": "Gestion Inadéquate de l'Inventaire d'API",
            "PT": "Gestão Inadequada de Inventário de APIs",
            "EO": "Malbona Administrado de API-Inventaro"
        },
        "description": {
            "ES": "APIs antiguas, sin documentar o shadow APIs exponen vulnerabilidades.",
            "EN": "Old, undocumented or shadow APIs expose vulnerabilities.",
            "FR": "APIs anciennes, non documentées ou shadow APIs exposent des vulnérabilités.",
            "PT": "APIs antigas, não documentadas ou shadow APIs expõem vulnerabilidades.",
            "EO": "Malnovaj, nedokumentitaj aŭ ombraj API-oj malkaŝas vundeblecojn."
        },
        "mitigation": {
            "ES": "Implementar versionado explícito en URLs (/api/v1/, /api/v2/). Deprecar versiones antiguas con avisos (Sunset header). Mantener inventario actualizado de todos los endpoints. Usar OpenAPI/Swagger para documentación automática. Implementar API gateway para centralizar control.",
            "EN": "Implement explicit versioning in URLs (/api/v1/, /api/v2/). Deprecate old versions with warnings (Sunset header). Maintain updated inventory of all endpoints. Use OpenAPI/Swagger for automatic documentation. Implement API gateway to centralize control.",
            "FR": "Implémenter un versionnage explicite dans les URLs (/api/v1/, /api/v2/). Déprécier les anciennes versions avec avertissements (en-tête Sunset). Maintenir un inventaire actualisé de tous les endpoints. Utiliser OpenAPI/Swagger pour documentation automatique. Implémenter une passerelle API pour centraliser le contrôle.",
            "PT": "Implementar versionamento explícito em URLs (/api/v1/, /api/v2/). Depreciar versões antigas com avisos (header Sunset). Manter inventário atualizado de todos os endpoints. Usar OpenAPI/Swagger para documentação automática. Implementar API gateway para centralizar controle.",
            "EO": "Efektivigu eksplicitan versiigon en URL-oj (/api/v1/, /api/v2/). Malrekomendu malnovajn versiojn kun averoj (Sunset-titolo). Tenu ĝisdatigitan inventaron de ĉiuj finoj. Uzu OpenAPI/Swagger por aŭtomatan dokumentadon. Efektivigu API-pordegon por centraligi kontrolon."
        },
        "code_example": {
            "ES": "# Versionado de API\nfrom flask import Blueprint\n\n# API v1 (deprecada)\napi_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n\n@api_v1.after_request\ndef add_deprecation_header(response):\n    response.headers['Sunset'] = 'Wed, 01 Jan 2027 00:00:00 GMT'\n    response.headers['Deprecation'] = 'true'\n    response.headers['Link'] = '</api/v2/>; rel=\"successor-version\"'\n    return response\n\n# API v2 (actual)\napi_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')\n\napp.register_blueprint(api_v1)\napp.register_blueprint(api_v2)",
            "EN": "# API versioning\nfrom flask import Blueprint\n\n# API v1 (deprecated)\napi_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n\n@api_v1.after_request\ndef add_deprecation_header(response):\n    response.headers['Sunset'] = 'Wed, 01 Jan 2027 00:00:00 GMT'\n    response.headers['Deprecation'] = 'true'\n    response.headers['Link'] = '</api/v2/>; rel=\"successor-version\"'\n    return response\n\n# API v2 (current)\napi_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')\n\napp.register_blueprint(api_v1)\napp.register_blueprint(api_v2)",
            "FR": "# Versionnage d'API\nfrom flask import Blueprint\n\n# API v1 (dépréciée)\napi_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n\n@api_v1.after_request\ndef add_deprecation_header(response):\n    response.headers['Sunset'] = 'Wed, 01 Jan 2027 00:00:00 GMT'\n    response.headers['Deprecation'] = 'true'\n    response.headers['Link'] = '</api/v2/>; rel=\"successor-version\"'\n    return response\n\n# API v2 (actuelle)\napi_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')\n\napp.register_blueprint(api_v1)\napp.register_blueprint(api_v2)",
            "PT": "# Versionamento de API\nfrom flask import Blueprint\n\n# API v1 (depreciada)\napi_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n\n@api_v1.after_request\ndef add_deprecation_header(response):\n    response.headers['Sunset'] = 'Wed, 01 Jan 2027 00:00:00 GMT'\n    response.headers['Deprecation'] = 'true'\n    response.headers['Link'] = '</api/v2/>; rel=\"successor-version\"'\n    return response\n\n# API v2 (atual)\napi_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')\n\napp.register_blueprint(api_v1)\napp.register_blueprint(api_v2)",
            "EO": "# API-versiigo\nfrom flask import Blueprint\n\n# API v1 (malrekomendita)\napi_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')\n\n@api_v1.after_request\ndef add_deprecation_header(response):\n    response.headers['Sunset'] = 'Wed, 01 Jan 2027 00:00:00 GMT'\n    response.headers['Deprecation'] = 'true'\n    response.headers['Link'] = '</api/v2/>; rel=\"successor-version\"'\n    return response\n\n# API v2 (nuna)\napi_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')\n\napp.register_blueprint(api_v1)\napp.register_blueprint(api_v2)"
        },
        "tags": ["versioning", "API-gateway", "OpenAPI", "ISO27001:A.12.1.1"]
    },
    
    # ========================================================================
    # API10:2023 - Injection Attacks
    # ========================================================================
    VulnerabilityType.INJECTION: {
        "title": {
            "ES": "Ataques de Inyección",
            "EN": "Injection Attacks",
            "FR": "Attaques par Injection",
            "PT": "Ataques de Injeção",
            "EO": "Injekt-Atakoj"
        },
        "description": {
            "ES": "Datos no validados ejecutados como comandos o consultas.",
            "EN": "Unvalidated data executed as commands or queries.",
            "FR": "Données non validées exécutées comme commandes ou requêtes.",
            "PT": "Dados não validados executados como comandos ou consultas.",
            "EO": "Nevalidigitaj datumoj plenumitaj kiel komandoj aŭ demandoj."
        },
        "mitigation": {
            "ES": "Usar SIEMPRE prepared statements/parametrized queries para SQL. Validar y sanitizar TODA entrada de usuario. Usar ORMs (SQLAlchemy, Django ORM) correctamente. Escapar caracteres especiales en NoSQL. Implementar input validation con schemas estrictos (Pydantic, Marshmallow). Principio: NUNCA concatenar strings para queries.",
            "EN": "ALWAYS use prepared statements/parametrized queries for SQL. Validate and sanitize ALL user input. Use ORMs (SQLAlchemy, Django ORM) correctly. Escape special characters in NoSQL. Implement input validation with strict schemas (Pydantic, Marshmallow). Principle: NEVER concatenate strings for queries.",
            "FR": "TOUJOURS utiliser des requêtes préparées/paramétrées pour SQL. Valider et assainir TOUTES les entrées utilisateur. Utiliser correctement les ORMs (SQLAlchemy, Django ORM). Échapper les caractères spéciaux en NoSQL. Implémenter la validation d'entrée avec schémas stricts (Pydantic, Marshmallow). Principe: JAMAIS concaténer des chaînes pour les requêtes.",
            "PT": "SEMPRE usar prepared statements/parametrized queries para SQL. Validar e sanitizar TODA entrada de usuário. Usar ORMs (SQLAlchemy, Django ORM) corretamente. Escapar caracteres especiais em NoSQL. Implementar validação de entrada com schemas estritos (Pydantic, Marshmallow). Princípio: NUNCA concatenar strings para queries.",
            "EO": "ĈIAM uzu preparitajn deklarojn/parametrigitajn demandojn por SQL. Validigi kaj sanigi ĈIUJN uzant-enirojn. Uzi ĝuste ORM-ojn (SQLAlchemy, Django ORM). Eskapi specialajn signojn en NoSQL. Efektivigu enirvalidigon kun strikta skemo (Pydantic, Marshmallow). Principo: NENIAM kunkatenigi ĉenojn por demandoj."
        },
        "code_example": {
            "ES": "# ❌ INCORRECTO (vulnerable a SQL injection)\nuser_id = request.args.get('id')\nquery = f\"SELECT * FROM users WHERE id = {user_id}\"\nresult = db.execute(query)\n\n# ✅ CORRECTO (prepared statement)\nuser_id = request.args.get('id')\nquery = \"SELECT * FROM users WHERE id = :id\"\nresult = db.execute(query, {'id': user_id})\n\n# ✅ MEJOR (ORM)\nuser_id = request.args.get('id')\nuser = User.query.filter_by(id=user_id).first()",
            "EN": "# ❌ WRONG (vulnerable to SQL injection)\nuser_id = request.args.get('id')\nquery = f\"SELECT * FROM users WHERE id = {user_id}\"\nresult = db.execute(query)\n\n# ✅ CORRECT (prepared statement)\nuser_id = request.args.get('id')\nquery = \"SELECT * FROM users WHERE id = :id\"\nresult = db.execute(query, {'id': user_id})\n\n# ✅ BETTER (ORM)\nuser_id = request.args.get('id')\nuser = User.query.filter_by(id=user_id).first()",
            "FR": "# ❌ FAUX (vulnérable à l'injection SQL)\nuser_id = request.args.get('id')\nquery = f\"SELECT * FROM users WHERE id = {user_id}\"\nresult = db.execute(query)\n\n# ✅ CORRECT (requête préparée)\nuser_id = request.args.get('id')\nquery = \"SELECT * FROM users WHERE id = :id\"\nresult = db.execute(query, {'id': user_id})\n\n# ✅ MEILLEUR (ORM)\nuser_id = request.args.get('id')\nuser = User.query.filter_by(id=user_id).first()",
            "PT": "# ❌ ERRADO (vulnerável a SQL injection)\nuser_id = request.args.get('id')\nquery = f\"SELECT * FROM users WHERE id = {user_id}\"\nresult = db.execute(query)\n\n# ✅ CORRETO (prepared statement)\nuser_id = request.args.get('id')\nquery = \"SELECT * FROM users WHERE id = :id\"\nresult = db.execute(query, {'id': user_id})\n\n# ✅ MELHOR (ORM)\nuser_id = request.args.get('id')\nuser = User.query.filter_by(id=user_id).first()",
            "EO": "# ❌ MALĜUSTA (vundebla al SQL-injekto)\nuser_id = request.args.get('id')\nquery = f\"SELECT * FROM users WHERE id = {user_id}\"\nresult = db.execute(query)\n\n# ✅ ĜUSTA (preparita deklaro)\nuser_id = request.args.get('id')\nquery = \"SELECT * FROM users WHERE id = :id\"\nresult = db.execute(query, {'id': user_id})\n\n# ✅ PLIBONE (ORM)\nuser_id = request.args.get('id')\nuser = User.query.filter_by(id=user_id).first()"
        },
        "tags": ["injection", "SQL", "prepared-statements", "ORM", "ISO27001:A.14.2.5", "SOC2:CC7.2"]
    }
}


# ============================================================================
# Mitigation Provider (Main Class)
# ============================================================================

@dataclass
class MitigationAdvice:
    """Structured mitigation advice for a vulnerability."""
    vulnerability_type: VulnerabilityType
    language: Language
    title: str
    description: str
    mitigation: str
    code_example: str
    tags: List[str]


class MitigationProvider:
    """
    Multilingual mitigation advice provider.
    
    Provides technical remediation strategies for OWASP API Top 10 vulnerabilities
    in 5 languages with intelligent fallback system.
    
    Features:
    - 10 vulnerability categories (OWASP API Security Top 10)
    - 5 languages: ES, EN, FR, PT, EO
    - Intelligent fallback: requested language → English → Spanish
    - ISO 27001 / SOC2 aligned recommendations
    - Code examples for each vulnerability
    - Compliance tags
    
    Usage:
        provider = MitigationProvider()
        advice = provider.get_advice(VulnerabilityType.BOLA, Language.SPANISH)
        print(advice.mitigation)
    """
    
    def __init__(self, database: Optional[Dict] = None):
        """
        Initialize mitigation provider.
        
        Args:
            database: Custom mitigation database (default: MITIGATION_DATABASE)
        """
        self.database = database or MITIGATION_DATABASE
        self.supported_languages = [lang.value for lang in Language]
        self.fallback_order = [Language.ENGLISH.value, Language.SPANISH.value]
        
        print(f"🛡️  Mitigation Provider initialized")
        print(f"   Vulnerabilities: {len(self.database)}")
        print(f"   Languages: {', '.join(self.supported_languages)}")
    
    def get_advice(
        self,
        vuln_type: VulnerabilityType,
        lang: Language = Language.ENGLISH
    ) -> Optional[MitigationAdvice]:
        """
        Get mitigation advice for vulnerability type in specified language.
        
        Intelligent fallback system:
        1. Try requested language
        2. Fallback to English if not available
        3. Fallback to Spanish if English not available
        4. Return None if no fallback available
        
        Args:
            vuln_type: Vulnerability type (OWASP API Top 10)
            lang: Target language (default: English)
        
        Returns:
            MitigationAdvice object or None
        """
        # Get vulnerability data
        vuln_data = self.database.get(vuln_type)
        
        if not vuln_data:
            print(f"⚠️  Vulnerability type {vuln_type.value} not found")
            return None
        
        # Try requested language
        lang_code = lang.value if isinstance(lang, Language) else lang
        
        if self._has_translation(vuln_data, lang_code):
            return self._build_advice(vuln_type, vuln_data, lang_code)
        
        # Fallback system
        print(f"⚠️  Language {lang_code} not available for {vuln_type.value}, trying fallback...")
        
        for fallback_lang in self.fallback_order:
            if self._has_translation(vuln_data, fallback_lang):
                print(f"   Using fallback language: {fallback_lang}")
                return self._build_advice(vuln_type, vuln_data, fallback_lang)
        
        print(f"❌ No translation available for {vuln_type.value}")
        return None
    
    def _has_translation(self, vuln_data: Dict, lang_code: str) -> bool:
        """Check if translation exists for language."""
        return (
            lang_code in vuln_data.get("title", {}) and
            lang_code in vuln_data.get("description", {}) and
            lang_code in vuln_data.get("mitigation", {})
        )
    
    def _build_advice(
        self,
        vuln_type: VulnerabilityType,
        vuln_data: Dict,
        lang_code: str
    ) -> MitigationAdvice:
        """Build MitigationAdvice object from data."""
        # Convert lang_code to Language enum
        lang_enum = next(
            (lang for lang in Language if lang.value == lang_code),
            Language.ENGLISH
        )
        
        return MitigationAdvice(
            vulnerability_type=vuln_type,
            language=lang_enum,
            title=vuln_data["title"].get(lang_code, ""),
            description=vuln_data["description"].get(lang_code, ""),
            mitigation=vuln_data["mitigation"].get(lang_code, ""),
            code_example=vuln_data["code_example"].get(lang_code, ""),
            tags=vuln_data.get("tags", [])
        )
    
    def get_all_vulnerabilities(self) -> List[VulnerabilityType]:
        """Get list of all supported vulnerability types."""
        return list(self.database.keys())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.supported_languages
    
    def search_by_tag(self, tag: str) -> List[VulnerabilityType]:
        """
        Search vulnerabilities by compliance tag.
        
        Args:
            tag: Tag to search (e.g., 'ISO27001:A.9.4.1', 'SOC2:CC6.1')
        
        Returns:
            List of vulnerability types matching tag
        """
        matching = []
        
        for vuln_type, vuln_data in self.database.items():
            tags = vuln_data.get("tags", [])
            if tag in tags or any(tag in t for t in tags):
                matching.append(vuln_type)
        
        return matching
    
    def export_advice(
        self,
        vuln_type: VulnerabilityType,
        lang: Language = Language.ENGLISH,
        format: str = "markdown"
    ) -> str:
        """
        Export mitigation advice in specified format.
        
        Args:
            vuln_type: Vulnerability type
            lang: Language
            format: Output format ('markdown', 'text', 'html')
        
        Returns:
            Formatted advice string
        """
        advice = self.get_advice(vuln_type, lang)
        
        if not advice:
            return ""
        
        if format == "markdown":
            return f"""# {advice.title}

## Description
{advice.description}

## Mitigation
{advice.mitigation}

## Code Example
```python
{advice.code_example}
```

## Tags
{', '.join(advice.tags)}
"""
        
        elif format == "text":
            return f"""{advice.title}

Description:
{advice.description}

Mitigation:
{advice.mitigation}

Code Example:
{advice.code_example}

Tags: {', '.join(advice.tags)}
"""
        
        elif format == "html":
            return f"""<div class="mitigation-advice">
    <h1>{advice.title}</h1>
    <h2>Description</h2>
    <p>{advice.description}</p>
    <h2>Mitigation</h2>
    <p>{advice.mitigation}</p>
    <h2>Code Example</h2>
    <pre><code class="language-python">{advice.code_example}</code></pre>
    <h2>Tags</h2>
    <p>{', '.join(advice.tags)}</p>
</div>
"""
        
        return ""


# ============================================================================
# Convenience Functions
# ============================================================================

def get_mitigation(vuln_type: str, lang: str = "EN") -> Optional[MitigationAdvice]:
    """
    Convenience function to get mitigation advice.
    
    Args:
        vuln_type: Vulnerability type string (e.g., 'BOLA', 'INJECTION')
        lang: Language code (e.g., 'ES', 'EN', 'FR', 'PT', 'EO')
    
    Returns:
        MitigationAdvice object or None
    """
    provider = MitigationProvider()
    
    try:
        vuln_enum = VulnerabilityType(vuln_type)
        lang_enum = Language(lang)
        return provider.get_advice(vuln_enum, lang_enum)
    except ValueError as e:
        print(f"❌ Invalid vulnerability type or language: {e}")
        return None


# ============================================================================
# Main Entry Point (Demo)
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🛡️  DM SENTINEL - MITIGATION INTELLIGENCE ENGINE")
    print("   PROMPT 7: Motor de Inteligencia de Mitigación Multilingüe")
    print("=" * 80 + "\n")
    
    # Initialize provider
    provider = MitigationProvider()
    
    # Demo: BOLA in Spanish
    print("📋 Example 1: BOLA in Spanish")
    print("-" * 80)
    advice = provider.get_advice(VulnerabilityType.BOLA, Language.SPANISH)
    if advice:
        print(f"Title: {advice.title}")
        print(f"Description: {advice.description[:100]}...")
        print(f"Mitigation: {advice.mitigation[:100]}...")
        print(f"Tags: {', '.join(advice.tags)}")
    
    print("\n" + "=" * 80)
    
    # Demo: Injection in Esperanto
    print("📋 Example 2: Injection in Esperanto")
    print("-" * 80)
    advice = provider.get_advice(VulnerabilityType.INJECTION, Language.ESPERANTO)
    if advice:
        print(f"Title: {advice.title}")
        print(f"Description: {advice.description[:100]}...")
    
    print("\n" + "=" * 80)
    
    # Demo: Search by compliance tag
    print("📋 Example 3: ISO27001 A.9.4.1 compliance")
    print("-" * 80)
    matching = provider.search_by_tag("ISO27001:A.9.4.1")
    print(f"Vulnerabilities matching tag: {[v.value for v in matching]}")
    
    print("\n" + "=" * 80)
    print("✅ Demo completed successfully")
    print("=" * 80 + "\n")
