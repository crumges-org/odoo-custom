# -*- coding: utf-8 -*-
# Copyright 2024 Cybrosys Technologies Pvt. Ltd.
# Copyright 2024 Crumges
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    'name': 'Multi Agent Shop',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'website': 'https://crumges.com',
    'author': 'Crumges (Adaptación de Cybrosys Technologies Pvt. Ltd.)',
    'license': 'LGPL-3',
    'summary': 'Permite que agentes (internos y de portal) realicen compras en nombre de clientes',
    'description': '''
        Multi Agent Shop
        ================
        
        Este módulo es una adaptación mejorada del módulo "Shopping Through Agent" de 
        Cybrosys Technologies Pvt. Ltd., con mejoras significativas en seguridad, 
        permisos de usuario y soporte completo para usuarios de portal.
        
        Características Principales:
        ----------------------------
        
        * **Compras por Agentes:** Usuarios marcados como agentes pueden crear pedidos
          en nombre de clientes específicos
        
        * **Soporte Completo para Usuarios de Portal:** Los usuarios de portal pueden 
          actuar como agentes sin necesidad de ser usuarios internos. El módulo maneja 
          correctamente los permisos y restricciones de acceso
        
        * **Soporte para Usuarios Internos:** Los usuarios internos también pueden 
          actuar como agentes con todas las funcionalidades disponibles
        
        * **Gestión de Clientes Asignados:** Los agentes solo pueden comprar para
          clientes que les han sido específicamente asignados
        
        * **Interfaz Intuitiva:** Menú dedicado para seleccionar cliente antes de
          comenzar la compra
        
        * **Trazabilidad Completa:** Registro automático del agente responsable en
          cada pedido de venta
        
        * **Gestión de Direcciones:** Manejo automático de direcciones de facturación
          y envío según el cliente seleccionado
        
        * **Reportes Mejorados:** Vistas y reportes adaptados para mostrar información
          de agentes en órdenes de venta e invoices
        
        * **Validaciones de Seguridad Robustas:** Múltiples capas de validación de
          permisos para asegurar que solo agentes autorizados puedan crear pedidos
        
        Mejoras Respecto a la Versión Original:
        ----------------------------------------
        
        * ✅ Soporte completo para usuarios de portal como agentes
        * ✅ Validaciones mejoradas de permisos de acceso
        * ✅ Uso estratégico de sudo() para operaciones seguras
        * ✅ Mejor manejo de carritos en transiciones entre clientes
        * ✅ Integración mejorada con el flujo de Website Sale
        * ✅ Compatibilidad total con Odoo 18
        * ✅ Documentación completa en estilo OCA
        
        Funcionalidades Técnicas:
        -------------------------
        
        * Campo booleano `is_agent` para marcar contactos como agentes
        
        * Relación many2one `agent_id` para asignar agentes a clientes
        
        * Campo many2many `agent_ids` para múltiples agentes por cliente
        
        * Controlador web mejorado para soportar tanto usuarios internos como de portal
        
        * Flujo de compra seguro con validaciones de permisos en múltiples puntos
        
        * Soporte para módulo complementario `shopping_through_agent_ux` para 
          mejoras adicionales de UX
        
        Flujo de Uso:
        ---------
        
        1. Administrador marca un contacto como "Es Agente"
        2. Administrador asigna clientes específicos al agente
        3. Agente accede al menú "Multi Agent Shop"
        4. Selecciona un cliente de su lista de clientes asignados
        5. Sistema crea un carrito a nombre del cliente
        6. Agente completa la compra normalmente
        7. El pedido se crea automáticamente con el cliente y agente registrados
        
        Dependencias:
        ----------------
        
        * sale: Módulo base de ventas
        * website_sale: Portal de tienda web
        * base: Módulo base de Odoo
        * account: Módulo de contabilidad
        
        Dependencias Opcionales:
        -------------------------
        
        * sale_ux: Para mejoras avanzadas de experiencia de usuario
        * shopping_through_agent_ux: Módulo complementario con mejoras UX
        
        Créditos:
        ---------
        
        Módulo original: "Shopping Through Agent" por Cybrosys Technologies Pvt. Ltd.
        Adaptación, mejoras y soporte para portal: Crumges
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