# © 2025 Crumges
# License OPL-1

from odoo import api, fields, models


class CatalogConfig(models.Model):
    _name = "catalog.config"
    _description = "Configuración de Catálogo de Productos"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    columns = fields.Selection(
        [("2", "2 columnas"), ("3", "3 columnas"), ("4", "4 columnas")],
        string="Columnas por fila",
        default="4",
        required=True,
    )
    show_price = fields.Boolean(string="Mostrar precio", default=True)
    show_code = fields.Boolean(string="Mostrar código interno", default=True)
    show_description = fields.Boolean(string="Mostrar descripción de venta", default=False)
    product_image_height = fields.Integer(
        string="Altura de imagen de producto (px)",
        default=120,
        help="Altura en píxeles de la imagen de cada producto en la tarjeta.",
    )
    show_date = fields.Boolean(string="Mostrar fecha", default=False)
    date_position = fields.Selection(
        [("header", "Cabecera"), ("footer", "Pie de página")],
        string="Posición de la fecha",
        default="header",
    )

    # --- Opciones de Listado ---
    group_by = fields.Selection(
        [
            ("none", "No agrupar"),
            ("categ_id", "Categoría interna"),
            ("public_categ_ids", "Categoría de sitio web"),
            ("product_tag_ids", "Etiquetas de producto"),
        ],
        string="Agrupar por",
        default="none",
        required=True,
    )
    sort_by = fields.Selection(
        [
            ("name", "Alfabético (A-Z)"),
            ("list_price", "Precio (Menor a Mayor)"),
            ("list_price_desc", "Precio (Mayor a Menor)"),
        ],
        string="Ordenar por",
        default="name",
        required=True,
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Lista de Precios",
        help="Opcional. Si se selecciona, los precios se recalcularán usando esta tarifa.",
    )
    show_pricelist_info = fields.Boolean(
        string="Mostrar detalles de tarifa",
        help="Si está activo, mostrará la cantidad mínima y las fechas de validez de la regla aplicada.",
        default=False,
    )

    # --- Switch de layout ---
    layout_mode = fields.Selection(
        [("odoo", "Diseño estándar de Odoo"), ("custom", "Membrete personalizado")],
        string="Tipo de layout",
        default="odoo",
        required=True,
    )

    # --- Imágenes de membrete (solo para layout custom) ---
    header_image = fields.Binary(
        string="Imagen de cabecera",
        attachment=True,
        help=(
            "Imagen que aparecerá como cabecera en cada página del catálogo.\n"
            "Tamaño recomendado: 1438 × 300 px (relación aprox. 4.8:1) a 192 dpi.\n"
            "Ancho útil del lienzo A4: ~190 mm ≈ 719 px a 96 dpi.\n"
            "Si la imagen es más ancha, se escala automáticamente al 100% del ancho."
        ),
    )
    header_image_filename = fields.Char(string="Nombre archivo cabecera")
    footer_image = fields.Binary(
        string="Imagen de pie de página",
        attachment=True,
        help="Opcional. Se muestra al final de cada página bajo el contenido.",
    )
    footer_image_filename = fields.Char(string="Nombre archivo pie")

    @api.constrains("product_image_height")
    def _check_product_image_height(self):
        for rec in self:
            if rec.product_image_height < 60 or rec.product_image_height > 400:
                raise models.ValidationError(
                    "La altura de imagen de producto debe estar entre 60 y 400 px."
                )
