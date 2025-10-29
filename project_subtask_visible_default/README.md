# Project Subtask Visible by Default

## 📋 Descripción

Módulo para Odoo 18 que modifica el comportamiento predeterminado de las subtareas en el módulo de Proyectos, haciendo que sean visibles automáticamente al crearlas.

## 🎯 Problema que Resuelve

En Odoo 18, cuando se crean subtareas, estas aparecen ocultas por defecto y es necesario hacer clic en el icono de visibilidad para mostrarlas. Este módulo cambia ese comportamiento para que todas las subtareas nuevas sean visibles automáticamente.

## ✨ Características

- ✅ Subtareas visibles por defecto al crearlas
- ✅ Compatible con Odoo 18 Community y Enterprise
- ✅ No requiere configuración adicional
- ✅ Respeta todas las funcionalidades existentes del módulo de Proyectos
- ✅ Ligero y sin impacto en el rendimiento
- ✅ Código limpio y bien documentado

## 🚀 Instalación

### Requisitos Previos
- Odoo 18 (Community o Enterprise)
- Módulo `project` instalado y configurado
- Acceso de administrador al sistema

### Pasos de Instalación

1. **Copiar el módulo al servidor:**
   ```bash
   # Navegar a la carpeta de addons personalizados
   cd /odoo/custom_addons/
   
   # Copiar el módulo (o clonar desde repositorio)
   cp -r project_subtask_visible_default /odoo/custom_addons/
   ```

2. **Establecer permisos correctos:**
   ```bash
   sudo chown -R odoo:odoo /odoo/custom_addons/project_subtask_visible_default
   sudo chmod -R 755 /odoo/custom_addons/project_subtask_visible_default
   ```

3. **Actualizar la lista de aplicaciones:**
   - Ir a `Aplicaciones` en Odoo
   - Hacer clic en `Actualizar lista de aplicaciones`
   - Confirmar la actualización

4. **Instalar el módulo:**
   - Buscar "Project Subtask Visible"
   - Hacer clic en `Instalar`

### Instalación por Línea de Comandos (Alternativa)
```bash
# Detener Odoo
sudo systemctl stop odoo

# Instalar el módulo
sudo -u odoo /usr/bin/odoo \
    -c /etc/odoo/odoo.conf \
    -d nombre_base_datos \
    -i project_subtask_visible_default \
    --stop-after-init

# Reiniciar Odoo
sudo systemctl start odoo
```

## 🔧 Configuración

Este módulo funciona automáticamente sin necesidad de configuración adicional. Una vez instalado:

1. Las nuevas subtareas serán visibles por defecto
2. Las subtareas existentes mantienen su estado actual
3. Los usuarios pueden seguir ocultando/mostrando subtareas manualmente si lo desean

### Configuración Opcional

Si deseas hacer visibles todas las subtareas existentes:

1. Ir a `Proyecto > Tareas`
2. Filtrar por "Es Subtarea"
3. Seleccionar todas las tareas
4. Acción > Hacer Visibles Todas las Subtareas

## 📝 Uso

### Comportamiento Automático
- Al crear una nueva subtarea desde cualquier vista, esta será visible automáticamente
- No es necesaria ninguna acción adicional del usuario

### Control Manual
- Los usuarios mantienen la capacidad de ocultar/mostrar subtareas usando el icono de visibilidad
- El módulo solo afecta el valor predeterminado, no fuerza la visibilidad permanente

## 🧪 Testing

### Pruebas Básicas

1. **Crear una subtarea desde la vista Kanban:**
   - Abrir un proyecto
   - Seleccionar una tarea
   - Crear una subtarea
   - ✅ Verificar que la subtarea es visible inmediatamente

2. **Crear una subtarea desde el formulario:**
   - Abrir una tarea en vista formulario
   - Agregar una subtarea
   - ✅ Verificar que aparece visible en la lista

3. **Toggle manual de visibilidad:**
   - Hacer clic en el icono de visibilidad
   - ✅ Verificar que sigue funcionando correctamente

## 🐛 Solución de Problemas

### El módulo no aparece en la lista
```bash
# Verificar que el módulo está en la ruta correcta
ls -la /odoo/custom_addons/project_subtask_visible_default

# Verificar permisos
sudo chown -R odoo:odoo /odoo/custom_addons/project_subtask_visible_default

# Reiniciar Odoo con modo debug
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf --dev=all
```

### Las subtareas no se muestran visibles
1. Verificar que el módulo está instalado correctamente
2. Limpiar la caché del navegador
3. Verificar en los logs: `/var/log/odoo/odoo.log`

### Conflicto con otros módulos
- Verificar compatibilidad con otros módulos de proyectos instalados
- Revisar el orden de carga de los módulos en `__manifest__.py`

## 📊 Impacto en el Sistema

- **Rendimiento:** Mínimo, solo modifica valores por defecto
- **Base de datos:** No crea nuevas tablas
- **Seguridad:** Mantiene todos los permisos existentes
- **Compatibilidad:** Total con el ecosistema Odoo 18

## 🔄 Actualización

Para actualizar el módulo:
```bash
# Método 1: Desde la interfaz
Aplicaciones > Project Subtask Visible > Actualizar

# Método 2: Por línea de comandos
sudo -u odoo /usr/bin/odoo \
    -c /etc/odoo/odoo.conf \
    -d nombre_base_datos \
    -u project_subtask_visible_default \
    --stop-after-init
```

## 🗑️ Desinstalación

1. Ir a `Aplicaciones`
2. Buscar "Project Subtask Visible"
3. Hacer clic en el menú desplegable
4. Seleccionar `Desinstalar`

**Nota:** La desinstalación restaurará el comportamiento por defecto de Odoo.

## 📚 Estructura del Módulo

```
project_subtask_visible_default/
├── __init__.py                    # Inicialización del módulo
├── __manifest__.py                 # Metadatos y dependencias
├── models/
│   ├── __init__.py                # Inicialización de modelos
│   └── project_task.py            # Extensión del modelo project.task
├── views/
│   └── project_config_settings_views.xml  # Vistas y configuración
├── static/
│   └── description/
│       └── icon.png               # Icono del módulo
└── README.md                      # Esta documentación
```

## 🤝 Soporte

Para soporte o consultas:
- Email: soporte@tuempresa.com
- Documentación: https://www.tuempresa.com/docs
- Issues: https://github.com/tuempresa/project_subtask_visible_default

## 📜 Licencia

LGPL-3.0

## 🏷️ Versiones

- **1.0.0** - Versión inicial para Odoo 18
  - Funcionalidad básica de visibilidad automática
  - Compatible con vistas Kanban y Lista
  - Integración con configuración de proyectos

## 👥 Autores

- Tu Empresa - Desarrollo inicial
- Tu Equipo de Desarrollo - Mantenimiento

---

**Última actualización:** Octubre 2025