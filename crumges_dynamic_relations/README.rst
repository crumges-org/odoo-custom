====================
Relaciones Dinámicas
====================

Este módulo proporciona un motor genérico para crear relaciones navegables (bidireccionales) entre cualquier tipo de documento en Odoo sin necesidad de desarrollo adicional por cada par de modelos. A través de la configuración en la interfaz de usuario, inyecta automáticamente *Smart Buttons* en las vistas de formulario correspondientes.

**Tabla de Contenidos**

.. contents::
   :local:

Configuración
=============

Para crear y gestionar las relaciones dinámicas entre modelos:

1. Asegúrate de tener habilitado el modo desarrollador.
2. Ve a **Ajustes > Técnico > Relaciones Dinámicas > Tipos de Relaciones**.
3. Haz clic en "Nuevo" para crear una nueva configuración.
4. Define:
   * **Nombre de la Relación**: Un nombre descriptivo para identificarla (ej. "CRM a Proyectos").
   * **Modelo A**: Selecciona el primer modelo (ej. `crm.lead`).
   * **Modelo B**: Selecciona el segundo modelo (ej. `project.project`).
   * **Mostrar en Modelo A/B**: Puedes hacer que la relación sea visible de un solo lado (ej. ver compras en proyectos pero no proyectos en compras).
   * **Icono**: Haz clic en el selector visual para elegir un icono FontAwesome para el Smart Button (cada lado tiene su propio icono).
   * **Etiquetas**: Define el texto que verá el usuario en el botón dependiendo desde qué modelo lo esté viendo (ej. Lado A verá "Proyectos", Lado B verá "Oportunidad").

Uso
===

**Caso de Uso Típico**

Una empresa de servicios necesita vincular tickets de Helpdesk (`helpdesk.ticket`) con los Pedidos de Venta (`sale.order`) que originaron el reclamo, o bien proyectos de implementación (`project.project`) directamente a las oportunidades ganadas de CRM (`crm.lead`), sin depender de un nodo central (como un Partner) ni requerir programación de campos Many2many cruzados.

**Forma de Uso**

1. **Navegación**: Una vez configurado el Tipo de Relación por el administrador, el usuario final ingresa a un documento de origen (por ejemplo, una Oportunidad de CRM). En la parte superior de la vista (en la caja de botones o `oe_button_box`), verá un nuevo Smart Button con el icono configurado y la etiqueta "Proyectos".
2. **Visualización de Documentos**: Al hacer clic en el botón, el sistema abrirá la vista de lista del Modelo Destino (Proyectos) filtrada únicamente para mostrar los registros vinculados.
3. **Vinculación (Crear relación)**: 
   * Dentro de Odoo, al encontrarse en un documento activo, el usuario puede acceder al menú de **Acción** (la rueda de engranaje superior) y seleccionar **"Vincular Documento Dinámico"**.
   * Se abrirá un asistente (Wizard) que permitirá seleccionar la relación y buscar el documento destino para crear un nuevo enlace bidireccional de forma instantánea.

Detalles Técnicos
=================

Este módulo logra la flexibilidad inyectando nodos XML al vuelo interceptando el método de carga de vistas de Odoo (`_get_view` o `fields_view_get` dependiendo de la versión).
Los vínculos físicos no se guardan como columnas en las tablas nativas de cada modelo, sino que se persiste en una tabla intermedia optimizada (`crumges.relation.link`), manteniendo la base de datos limpia de "basura estructural" y garantizando que las relaciones sean automáticamente bidireccionales.

Bugs Conocidos / Roadmap
========================

* **Fase 2**: Integrar un Dashboard de vista 360° para visualizar un mapa jerárquico de las relaciones de un Partner o un Caso base.
* Debido a que no utiliza campos calculados (compute fields) tradicionales de Python para el recuento, los Smart Buttons inyectados se renderizan sin el número de recuento por defecto, priorizando el rendimiento en la carga masiva de formularios.

Créditos
========

Autores
-------

* Crumges

Mantenedores
------------

Este módulo es mantenido por Crumges.

Para soporte y nuevas funcionalidades, visite `Crumges <https://crumges.com>`_.
