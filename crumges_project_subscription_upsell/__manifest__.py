{
    'name': 'Venta adicional de Suscripción desde Tareas',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Generación de upsell en suscripciones desde tareas de proyecto.',
    'description': """
        Este módulo permite generar ventas adicionales (upsell) para una suscripción directamente desde una Tarea de Proyecto.
        
        Detalle de funcionalidades:
        --------------------------
        
        1. Gestión de Ventas Adicionales (Upsell)
           - Creación directa de cotizaciones desde la tarea.
           - Cálculo nativo de prorrateos y precios de suscripción.
           - Vinculación automática Task -> Sale Line -> Subscription.
           - Sincronización bidireccional inteligente del nombre de la tarea.

        2. Integridad del Flujo de Trabajo (Workflow Safety)
           - Exclusividad Mutua: Bloqueo de Upsell si existen Subtareas.
           - Exclusividad Mutua: Bloqueo de Subtareas si existe Upsell activo.
           - Ocultación dinámica de elementos de interfaz no permitidos.

        3. Seguridad y Accesibilidad
           - Acceso para usuarios de Proyecto (No Ventas) mediante reglas de registro (ir.rule).
           - Escalado de privilegios controlado (sudo) para la creación de órdenes.
           - Visibilidad de solo lectura para Suscripciones pertinentes.

        4. Experiencia de Usuario (UX)
           - Creación en estado "Borrador" garantizado (bypass de auto-confirmación).
           - Recarga suave de la vista (sin redirecciones molestas).
           - Botón de "Reset" para correcciones rápidas.
    """,
    'author': 'Crumges',
    'website': 'https://crumges.com',
    'depends': ['project', 'sale_management', 'sale_subscription', 'sale_project'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/project_task_views.xml',
        'views/product_template_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
