# Copyright 2025 Crumges
# License OPL-1 or later (https://www.odoo.com/documentation/17.0/legal/licenses.html).

{
    "name": "eLearning Videos Extended - Zoom, Drive, Vimeo & Local",
    "summary": "Todo su contenido en un solo lugar: Zoom, Drive, Vimeo y archivos locales.",
    "description": """
eLearning Videos Extended
=========================

Todo su contenido en un solo lugar: Zoom, Drive, Vimeo y archivos locales.

Rompa las barreras de contenido en Odoo eLearning. Este módulo extiende las capacidades nativas para soportar fuentes de video esenciales en el mundo corporativo y educativo.

Características Principales
---------------------------
*   **Zoom Integration:** Incruste reuniones y webinars de Zoom directamente como lecciones.
*   **Google Drive:** Reproduzca videos de Drive ocultando el botón "pop-out" para mantener al alumno en su sitio.
*   **Videos Locales:** Suba archivos MP4 o WebM directamente a su servidor Odoo.
*   **Vimeo Enhanced:** Mejor integración con Vimeo para cursos profesionales.
""",
    "description": """
eLearning Videos Extended (Zoom, Drive, Vimeo, Local)
=====================================================

Rompa las barreras de contenido en Odoo eLearning.
Este módulo extiende las capacidades nativas para soportar fuentes de video esenciales en el mundo corporativo y educativo.

Características Principales
---------------------------
*   **Zoom**: Integre reuniones de Zoom directamente como diapositivas (requiere configuración de API).
*   **Google Drive**: Soporte nativo para videos de Drive con opción de ocultar el botón "pop-out" para mayor control.
*   **Vimeo**: Integración fluida con metadatos automáticos.
*   **Videos Locales**: Suba archivos MP4/WebM directamente a Odoo si prefiere no usar plataformas externas.

Perfecto para instituciones educativas, formación corporativa y academias online.
    """,
    "version": "18.0.1.0.1",
    "category": "Website/eLearning",
    "website": "https://crumges.com",
    "author": "Crumges",
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "depends": [
        "website_slides",
    ],
    "data": [
        "views/slide_slide_views.xml",
        "views/res_config_settings_views.xml",
        "views/website_slides_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "crumges_elearning_videos/static/src/css/style.scss",
        ],
    },
    "images": ["static/description/banner.png"],
    "maintainers": ["Crumges"],
}
