====================
Multi Agent Shop
====================

.. image:: https://img.shields.io/badge/maturity-Production%2FStable-brightgreen.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable

.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|

Multi Agent Shop
================

**Una adaptación mejorada del módulo "Shopping Through Agent" de Cybrosys Technologies Pvt. Ltd.**

Este módulo permite que agentes (usuarios internos y de portal) realicen pedidos directamente en el 
sitio web, actuando en nombre de sus clientes asignados, con mejoras significativas de seguridad, UX 
y soporte para usuarios de portal.

Origen del Módulo
===================

Este módulo es una **adaptación mejorada** de:

* **Módulo Original:** `Shopping Through Agent <https://www.cybrosys.com/>`_
* **Autor Original:** Cybrosys Technologies Pvt. Ltd.
* **Versión Original:** Odoo 15/16
* **Adaptación:** Crumges (https://crumges.com/)
* **Versión Actual:** Odoo 18

Agradecemos especialmente a Cybrosys Technologies por el concepto original y la base del módulo.

¿Qué Traía el Módulo Original?
===============================

El módulo "Shopping Through Agent" de Cybrosys proporcionaba:

* Opción para marcar contactos como "agentes"
* Capacidad de que los agentes realicen compras a través del portal web
* Asignación de un cliente a cada compra
* Registro básico del agente en la orden de venta
* Interfaz simple para seleccionar cliente y acceder a la tienda

¿Qué Se Agregó en Esta Versión?
================================

Hemos realizado mejoras significativas manteniendo la esencia del módulo original:

Mejoras de Seguridad
~~~~~~~~~~~~~~~~~~~~

* Validaciones robustas de permisos en múltiples capas
* Soporte completo para usuarios de portal como agentes
* Acceso controlado a datos sin exposición de información sensible
* Verificación de que agentes solo compren para clientes asignados
* Uso estratégico de sudo() con validaciones en cada operación crítica

Mejoras de Experiencia de Usuario
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Interfaz dedicada (/agent/shop) para selección clara de cliente
* Información del cliente visible en la parte superior del carrito
* Sección destacada "Compra a nombre de: [Cliente]"
* Mensaje claro en formulario de selección de cliente
* Recordatorio en el carrito sobre cambio de cliente
* Diseño completamente responsivo para dispositivos móviles

Mejoras Técnicas
~~~~~~~~~~~~~~~~~

* Compatibilidad total con Odoo 18
* Herencia correcta de WebsiteSale
* Gestión avanzada de carritos y sesiones
* Trazabilidad mejorada del agente en órdenes e invoices
* Código limpio y bien documentado
* Integración fluida con flujo estándar de checkout

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

Instalación
===========

.. code-block:: bash

    # Descargar el módulo
    cd /path/to/addons
    git clone https://github.com/Crumges/odoo-modules.git

    # Actualizar módulos e instalar
    ./odoo-bin --addons-path=/path/to/addons -u all

    # Buscar "Multi Agent Shop" en Aplicaciones e instalar

Configuración
=============

**Marcar Contactos como Agentes:**

1. Ir a Contactos
2. Abrir un contacto
3. Ir a pestaña "Sales/Purchases"
4. Marcar "Es Agente"
5. Guardar

**Asignar Clientes a Agentes:**

1. Abrir un cliente (contacto)
2. Ir a pestaña "Sales/Purchases"
3. En campo "Agente", seleccionar el agente responsable
4. Guardar

Uso
===

**Para Agentes:**

1. Ir a menú "Multi Agent Shop"
2. Seleccionar un cliente
3. Hacer clic en "Ir a Comprar"
4. Seleccionar productos
5. Completar checkout
6. Orden creada automáticamente con información del agente

**Para Administradores:**

1. Ir a Ventas → Órdenes
2. Ver información del agente en cada orden
3. Generar reportes filtrados por agente

Campos Personalizados
=====================

**res.partner:**

* ``is_agent`` (Boolean): Indica si el contacto es un agente
* ``agent_id`` (Many2One): Agente asignado al cliente

**sale.order:**

* ``agent_id`` (Many2One): Agente que realizó la compra

**account.move:**

* ``agent_id`` (Many2One): Agente del pedido asociado

Créditos
========

**Módulo Original**

* **Nombre:** Shopping Through Agent
* **Autor:** Cybrosys Technologies Pvt. Ltd.
* **Sitio:** https://www.cybrosys.com/
* **Licencia:** LGPL-3

**Adaptación y Mejoras**

* **Adaptado por:** Crumges
* **Sitio:** https://crumges.com/
* **Versión:** Odoo 18
* **Mejoras:** Seguridad, UX, soporte portal, documentación

Licencia
========

Este módulo se distribuye bajo la licencia LGPL-3.0, compatible con la licencia 
original del módulo de Cybrosys Technologies Pvt. Ltd.

Información Adicional
====================

* **Versión:** 18.0.1.0.0
* **Compatibilidad:** Odoo 18.0
* **Dependencias:** sale, website_sale, base, account
* **Base de Datos:** PostgreSQL 12+
* **Navegadores:** Chrome, Firefox, Safari, Edge (versiones recientes)