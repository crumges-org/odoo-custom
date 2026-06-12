======================
Límite de Usuarios Odoo
======================

Este módulo proporciona la funcionalidad de restringir la cantidad máxima de usuarios internos activos que se pueden crear en Odoo.
Permite establecer un límite en los Ajustes Generales para gestionar fácilmente las licencias ocupadas y disponibles, previniendo que administradores secundarios superen la cuota sin autorización.

Características principales
==========================

* Establecer un límite global de usuarios internos desde **Ajustes > Usuarios**.
* Validación automática al crear o habilitar un usuario (`share=False`, `active=True`).
* Visualización en tiempo real de **Licencias Ocupadas** y **Licencias Disponibles**.
* Permiso dedicado: Solo los usuarios con el grupo *"Permitir editar límite de usuarios"* pueden modificar esta cantidad. Para el resto de administradores, el campo es de solo lectura.
* Un límite de `0` significa "Sin límite".

Autor
=====

* Crumges

Contacto y Soporte
==================

Para más información, visita: `crumges.com <https://crumges.com>`_
