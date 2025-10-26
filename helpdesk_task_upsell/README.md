# Helpdesk Ventas Adicionales en Suscripciones

## Información General

**Autor:** Crumges  
**Website:** [https://crumges.com](https://crumges.com)  
**Colaboradores:** 
- Crumges
- Alain Alvarez Caignet  
**Versión:** 18.0.1.0.0  
**Licencia:** LGPL-3  

## Propósito del Módulo

Este módulo extiende las funcionalidades de Helpdesk y Field Service Management (FSM) en Odoo 18, permitiendo agregar **ventas adicionales directamente a suscripciones activas** de clientes mediante la creación de tareas de servicio facturables desde tickets de soporte. 

El módulo está diseñado para empresas que gestionan contratos de suscripción y necesitan agregar servicios puntuales o trabajos específicos que no están incluidos en el contrato base, manteniendo todo vinculado para una facturación y trazabilidad completa.

### Casos de Uso Principales

- **Empresas con contratos de mantenimiento** que realizan trabajos adicionales no incluidos en el contrato base
- **Proveedores de servicios con suscripciones** que necesitan facturar servicios puntuales adicionales
- **Gestión de flotas o equipos** donde se requiere documentar trabajos específicos por unidad (vehículo, equipo, etc.)
- **Servicios técnicos especializados** que manejan diferentes categorías de servicios adicionales

## Funcionalidades Principales

### 1. Categorías de Ventas Adicionales Flexibles
El módulo permite crear y gestionar diferentes categorías de servicios adicionales, no limitándose a tipos predefinidos:
- **Instalación:** Con información específica del equipo o vehículo
- **Desinstalación:** Con detalles del componente a retirar
- **Reparación:** Con descripción del problema y solución
- **Categorías personalizadas:** Según las necesidades del negocio

### 2. Información Adicional por Categoría
Cada categoría de venta adicional puede incluir información específica que se propaga automáticamente:
- **Descripción detallada del trabajo:** Información específica del servicio
- **Identificación del activo:** Por ejemplo, número de vehículo, equipo, ubicación
- **Cantidad/Horas:** Tiempo estimado o unidades del servicio
- Esta información se agrega tanto a la tarea FSM como a la línea de la orden de suscripción

### 3. Integración Completa con Suscripciones
- Añade servicios directamente a suscripciones activas del cliente
- Crea líneas de orden de venta automáticamente en la suscripción
- Mantiene la facturación recurrente con los adicionales incluidos
- Vincula todo el historial de servicios adicionales con el contrato

### 4. Flujo desde Ticket hasta Facturación
- **Ticket de Soporte → Tarea FSM → Línea de Suscripción → Facturación**
- Trazabilidad completa del proceso
- Documentación automática en cada etapa

### 5. Gestión de Productos de Servicio
- Productos configurables para cada categoría de servicio
- Facturación por tiempo trabajado (timesheet)
- Vinculación automática con proyectos FSM

## Requisitos y Dependencias

### Módulos Requeridos:
- `helpdesk_fsm` - Integración entre Helpdesk y Field Service
- `product` - Gestión de productos
- `sale_project` - Integración entre ventas y proyectos
- `sale_timesheet` - Facturación por tiempo trabajado
- `sale_subscription` - Gestión de suscripciones

## Instalación

1. **Clonar o descargar el módulo:**
   ```bash
   cd /path/to/odoo/addons
   git clone [repository_url] helpdesk_task_upsell
   ```

2. **Actualizar la lista de módulos:**
   - Activar modo desarrollador en Odoo
   - Ir a Aplicaciones → Actualizar lista de aplicaciones

3. **Instalar el módulo:**
   - Buscar "Helpdesk Ventas Adicionales"
   - Click en Instalar

## Configuración

### Configuración Inicial

1. **Categorías de Servicio:**
   El módulo incluye productos de ejemplo para:
   - Reparación
   - Instalación  
   - Desinstalación
   
   Puedes crear productos adicionales según tus categorías de servicio.

2. **Proyecto FSM:**
   Los productos se vinculan con el proyecto FSM para gestión de tareas de campo.

### Configuración de Categorías Personalizadas

1. **Crear nuevo producto de servicio:**
   - Ir a Productos → Crear
   - Tipo: Servicio
   - Política de servicio: Facturar por tiempo trabajado
   - Seguimiento: Crear tarea en proyecto existente
   - Asignar proyecto FSM

2. **Configurar campos booleanos:**
   - Marcar el tipo correspondiente (is_reparation, is_installation, etc.)
   - El sistema valida que no se marquen múltiples tipos

## Flujo de Trabajo

### 1. Recepción del Ticket
1. Cliente con suscripción activa crea ticket de soporte
2. Agente identifica necesidad de servicio adicional no incluido en contrato

### 2. Creación de Venta Adicional
1. Desde el ticket, abrir wizard "Crear tarea FSM"
2. Activar opción "Para Venta Adicional" (for_upsell)
3. Completar información:
   - **Suscripción del cliente:** Se filtra automáticamente por cliente
   - **Categoría de servicio:** Instalación, Reparación, etc.
   - **Descripción del trabajo:** Información específica
   - **Información adicional:** Ej: "Vehículo ABC-123, instalación de GPS"
   - **Cantidad:** Horas estimadas o unidades

### 3. Generación Automática
El sistema crea automáticamente:
- **Tarea FSM** con toda la información detallada
- **Línea en la suscripción** con:
  - Producto de servicio correspondiente
  - Descripción: "[Categoría]: [Información adicional]"
  - Ejemplo: "Instalación: Vehículo ABC-123, instalación de GPS"
  - Cantidad especificada
- **Vinculación completa** entre ticket, tarea y suscripción

### 4. Ejecución y Facturación
- Técnico ejecuta la tarea en campo
- Registra horas reales trabajadas
- Sistema incluye el servicio adicional en la próxima factura de suscripción

## Ejemplo Práctico

**Escenario:** Cliente tiene suscripción de mantenimiento de flota

1. **Ticket:** "Necesito instalar GPS en vehículo nuevo"
2. **Categoría seleccionada:** Instalación
3. **Información adicional:** "Vehículo Toyota Hilux patente ABC-123, GPS modelo X"
4. **Sistema genera:**
   - Tarea: "Instalación: Vehículo Toyota Hilux patente ABC-123, GPS modelo X"
   - Línea en suscripción con la misma descripción
   - Asignación de 2 horas estimadas

## Modelos y Campos

### Helpdesk Ticket (`helpdesk.ticket`)
**Campos añadidos:**
- `for_upsell` (Boolean): Indica si incluye venta adicional
- `upsell_type` (Selection): Categoría del servicio adicional
- `subsription_id` (Many2one): Suscripción vinculada

### Product Template (`product.template`)
**Campos añadidos:**
- `is_reparation` (Boolean): Categoría reparación
- `is_installation` (Boolean): Categoría instalación
- `is_uninstallation` (Boolean): Categoría desinstalación

**Validaciones:**
- Sistema impide marcar múltiples categorías en un mismo producto

### Wizard Create FSM Task (`helpdesk.create.fsm.task`)
**Campos añadidos:**
- `for_upsell` (Boolean): Activar modo venta adicional
- `subsription_id` (Many2one): Suscripción del cliente
- `upsell_type` (Selection): Categoría del servicio
- `task_description` (Text): Información adicional específica
- `qty` (Integer): Cantidad/horas del servicio

**Lógica de Negocio:**
- Concatena categoría + descripción para nombre de tarea y línea de venta
- Propaga información a todos los documentos relacionados
- Mantiene trazabilidad completa

## Vistas y Interfaz

### Vista de Ticket
- Pestaña "Venta Adicional" (Upsell) en formulario de ticket
- Visible cuando ticket tiene venta adicional asociada
- Muestra categoría de servicio y suscripción vinculada

### Wizard de Creación de Tarea
- Campos adicionales cuando se activa venta adicional
- Validación de campos requeridos
- Filtro inteligente de suscripciones activas por cliente
- Campo de texto para información adicional específica

## Beneficios del Módulo

### Para el Negocio
- **Control de servicios adicionales:** Gestión clara de trabajos fuera del contrato base
- **Facturación integrada:** Todo incluido en la factura de suscripción
- **Trazabilidad completa:** Historial detallado por cliente y activo
- **Flexibilidad:** Categorías personalizables según el negocio

### Para Operaciones
- **Información detallada:** Cada tarea incluye toda la información necesaria
- **Proceso estandarizado:** Flujo consistente para ventas adicionales
- **Documentación automática:** Reduce errores manuales
- **Gestión por activo:** Permite seguimiento por vehículo, equipo, etc.

### Para Clientes
- **Transparencia total:** Ve claramente qué servicios adicionales se realizaron
- **Facturación unificada:** Todo en una sola factura de suscripción
- **Historial completo:** Registro de todos los trabajos por activo
- **Servicio ágil:** Respuesta rápida a necesidades puntuales

## Soporte y Mantenimiento

Para soporte, consultas o reportar problemas:
- **Email:** contacto@crumges.com
- **Website:** https://crumges.com
- **Issues:** [Repositorio del proyecto]

## Roadmap y Mejoras Futuras

- [ ] Categorías dinámicas de servicios configurables desde interfaz
- [ ] Plantillas de información adicional por categoría
- [ ] Reportes de servicios adicionales por suscripción
- [ ] Dashboard de ventas adicionales por período
- [ ] Integración con app móvil FSM para captura de información en campo
- [ ] Aprobaciones automáticas según monto del servicio adicional
- [ ] Histórico de servicios por activo/vehículo
- [ ] Notificaciones automáticas al cliente de servicios agregados

## Changelog

### Versión 18.0.1.0.0
- Release inicial para Odoo 18
- Gestión de ventas adicionales en suscripciones
- Categorías de servicio flexibles
- Información adicional propagable a tareas y ventas
- Integración completa con helpdesk_fsm
- Vinculación con suscripciones activas

---

**© 2024 Crumges** - Todos los derechos reservados