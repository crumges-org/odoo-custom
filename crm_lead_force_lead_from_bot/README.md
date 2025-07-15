# CRM Lead Force Lead From Bot

Este módulo de Odoo permite forzar que todos los registros del modelo `crm.lead` creados desde bots conversacionales (como el `crm.script`, chat en vivo o integraciones automáticas) se guarden con el tipo `'lead'`, incluso si el sistema los crearía por defecto como `'opportunity'`.

Está especialmente diseñado para asegurar una correcta clasificación inicial de contactos cuando se utiliza Odoo como canal de entrada automatizado.

## Características

- Detecta automáticamente el origen desde:
  - `utm.source` (ejemplo: "Bot Conversacional")
  - `crm.tag` (etiquetas que contengan "bot")
  - `channel_id` (Livechat)
- Fuerza `type = 'lead'` automáticamente durante la creación.
- No requiere configuración adicional.
- Compatible con el modo de gestión de Leads/Oportunidades.
- Modular y no invasivo: se puede desinstalar sin dejar rastros.
- Soporta múltiples leads (`create_multi`).

## Instalación

Este módulo debe ser instalado como cualquier otro módulo estándar de Odoo.

1. Copiar la carpeta `crm_lead_force_lead_from_bot` dentro de tu carpeta de addons personalizados.
2. Reiniciar el servidor de Odoo.
3. Activar el modo desarrollador.
4. Ir a **Aplicaciones** y actualizar la lista.
5. Buscar "CRM: Forzar Leads desde Bot" e instalar.

## Uso

Una vez instalado, el módulo funciona automáticamente. Todos los leads creados desde el bot o desde un canal de chat con alguno de los siguientes indicadores serán guardados como tipo `'lead'`:

- Fuente (`utm.source.name`) que contenga la palabra `"bot"` (sin importar mayúsculas).
- Etiqueta (`crm.tag.name`) que contenga la palabra `"bot"`.
- Campo `channel_id` presente (Livechat).

No se requiere ninguna acción manual adicional.

## Créditos

### Autor

- Crumges

### Desarrollador

- Mario Núñez

### Colaboradores

- [💬 ChatGPT (OpenAI)](https://openai.com/chatgpt) – asistencia técnica, depuración y redacción automatizada

## Licencia

Este módulo está licenciado bajo los términos de la **Licencia Pública General Reducida GNU v3 (LGPL-3)**. Para más información, consultar el archivo LICENSE o visitar:

https://www.gnu.org/licenses/lgpl-3.0.html

---
