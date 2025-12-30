{
    "name": "CRM: Forzar Leads desde Bot",
    "summary": "Mantenga limpio su flujo de oportunidades. Deje que los bots conversen en la etapa de Leads.",
    "description": """
CRM: Force Leads from Bot
=========================

Mantenga limpio su flujo de oportunidades. Deje que los bots conversen en la etapa de Leads.

Este módulo asegura que todas las conversaciones iniciadas por bots o livechats entren al sistema como "Leads" (Iniciativas), evitando saturar el pipeline de Oportunidades con consultas de soporte o spam.

Características:
----------------
- Detecta origen "bot" en fuentes y etiquetas.
- Fuerza tipo Leads para Livechats.
- Mantiene la higiene del CRM automáticamente.
""",
    "version": "18.0.1.0.0",
    "category": "CRM",
    "license": "LGPL-3",
    "author": "Crumges",
    "website": "https://crumges.com",
    "maintainers": ["Crumges"],
    "repository": "https://github.com/crumges-org/odoo-custom",
    "depends": ["crm"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "development_status": "Beta",
    "description": """
CRM: Forzar Leads desde Bot
===========================

Este módulo asegura que todos los registros `crm.lead` creados desde bots conversacionales
(Odoo Livechat, scripts automatizados, etc.) se creen con `type = 'lead'`, incluso si el sistema
por defecto los marcaría como `opportunity`.

Características:
----------------
- Detecta si el lead fue creado desde:
  - Fuente (utm.source) que contenga "bot"
  - Etiquetas (crm.tag) que incluyan "bot"
  - Canal de livechat (channel_id)
- Fuerza automáticamente `type = 'lead'` si corresponde.
- Compatible con modo Leads/Oportunidades activado.
- No requiere configuración adicional.
- Desinstalable sin dejar rastro (no modifica datos existentes).
    """
}
