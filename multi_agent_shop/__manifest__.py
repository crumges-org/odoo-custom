# -*- coding: utf-8 -*-
# Copyright 2024 Cybrosys Technologies Pvt. Ltd.
# Copyright 2024 Crumges
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Multi Agent Shop',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'website': 'https://crumges.com',
    'author': 'Crumges (Basado en Shopping Through Agent de Cybrosys Technologies)',
    'license': 'LGPL-3',
    'summary': 'Permite que agentes realicen compras en nombre de clientes con mejoras de seguridad y soporte para usuarios de portal',
    'description': '''
        Multi Agent Shop
        ================
        
        Módulo Original
        ---------------
        Este módulo es una adaptación mejorada del módulo **"Shopping Through Agent"** 
        de Cybrosys Technologies Pvt. Ltd. (https://www.cybrosys.com/)
        
        Agradecemos a Cybrosys por el concepto original y la base del módulo.
        
        Funcionalidad Original (Cybrosys)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        El módulo original permitía:
        
        * Marcar contactos como "agentes"
        * Que los agentes realicen compras en el portal web
        * Asignar un cliente a cada compra realizada por un agente
        * Registro básico del agente en la orden de venta
        
        Mejoras Implementadas por Crumges
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        **Seguridad Mejorada:**
        
        * Validaciones robustas de permisos en múltiples capas
        * Uso estratégico de sudo() solo donde es necesario
        * Aislamiento completo de datos según tipo de usuario
        * Restricciones de acceso granulares para usuarios de portal
        * Verificación de que agentes solo compren para clientes asignados
        
        **Soporte Completo para Usuarios de Portal:**
        
        * Los usuarios de portal pueden actuar como agentes sin ser usuarios internos
        * Acceso controlado a información sensible sin exposición de datos
        * Gestión segura de sesiones y carritos por usuario
        * Validaciones de permisos en cada operación crítica
        
        **Experiencia de Usuario Mejorada:**
        
        * Interfaz intuitiva dedicada (/agent/shop) para selección de cliente
        * Información clara del cliente durante todo el flujo de compra
        * Carrito persistente mientras se compra para un cliente
        * Advertencias explícitas sobre cambio de cliente
        * Diseño responsivo para dispositivos móviles
        * Mensajes informativos y recordatorios estratégicos
        
        **Gestión Avanzada de Clientes:**
        
        * Asignación clara de clientes a agentes
        * Vista filtrada de clientes disponibles por agente
        * Validación de asignación en cada compra
        * Soporte para múltiples clientes por agente
        
        **Trazabilidad y Reportes:**
        
        * Campo agent_id en órdenes de venta para trazabilidad completa
        * Información del agente visible en reportes de órdenes
        * Integración en reportes de facturas
        * Capacidad de filtrar y analizar ventas por agente
        
        **Controladores Mejorados:**
        
        * Herencia correcta de WebsiteSale para Odoo 18
        * Rutas seguras con validación de permisos
        * Manejo correcto de carritos y sesiones
        * Integración fluida con el flujo de checkout estándar
        
        Características Principales
        ===========================
        
        ✅ Compras por agentes en nombre de clientes específicos
        ✅ Soporte para usuarios internos y de portal como agentes
        ✅ Gestión de clientes asignados a cada agente
        ✅ Información del cliente visible en toda la compra
        ✅ Advertencias y recordatorios en interfaz
        ✅ Trazabilidad completa del agente responsable
        ✅ Validaciones de seguridad robustas
        ✅ Diseño responsivo para móviles
        ✅ Compatible con Odoo 18
        ✅ Código limpio y bien documentado
        
        Créditos y Atribuciones
        ========================
        
        **Módulo Original:**
        
        * "Shopping Through Agent" por Cybrosys Technologies Pvt. Ltd.
        * https://www.cybrosys.com/
        * Versión original para Odoo 15/16
        
        **Adaptación y Mejoras:**
        
        * Crumges (https://crumges.com/)
        * Adaptación a Odoo 18
        * Mejoras de seguridad y UX
        * Soporte completo para usuarios de portal
        * Documentación y mantenimiento
        
        **Licencia:**
        
        * LGPL-3.0 (compatible con OCA)
        * Respeta la licencia original del módulo de Cybrosys
    ''',
    'depends': [
        'sale',
        'website_sale',
        'base',
        'account',
    ],
    'data': [
        'data/website_menu_data.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/agent_shop_template.xml',
        'views/sale_order_cart_template.xml',
        'views/sale_order_portal_template.xml',
        'views/invoice_report_template.xml',
        'views/sale_order_report_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': [],
    },
}