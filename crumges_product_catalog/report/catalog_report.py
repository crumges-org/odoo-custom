# © 2025 Crumges
# License OPL-1

from types import SimpleNamespace

from odoo import api, fields, models

_COL_WIDTHS = {
    "2": "49.5%",
    "3": "33%",
    "4": "24.5%",
}

_DEFAULT_CONFIG = SimpleNamespace(
    layout_mode="odoo",
    columns="4",
    show_price=True,
    show_code=True,
    show_description=False,
    header_image=False,
    footer_image=False,
    product_image_height=120,
)


class CatalogReport(models.AbstractModel):
    _name = "report.crumges_product_catalog.catalog_report"
    _description = "Reporte: Catálogo de Productos"

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        config_id = data.get("config_id")
        product_ids = data.get("product_ids") or docids or []
        group_by = data.get("group_by", "none")
        sort_by = data.get("sort_by", "name")

        if config_id:
            config = self.env["catalog.config"].browse(config_id)
        else:
            config = self.env["catalog.config"].search([], limit=1)

        if not config:
            config = _DEFAULT_CONFIG

        products = self.env["product.template"].browse(product_ids)
        columns = getattr(config, "columns", "4")

        # --- Lista de Precios ---
        pricelist_id = data.get("pricelist_id")
        show_pricelist_info = data.get("show_pricelist_info")
        pricelist = False
        pricelist_info = {}

        if pricelist_id:
            pricelist = self.env["product.pricelist"].browse(pricelist_id)
            products = products.with_context(pricelist=pricelist.id)

            if show_pricelist_info:
                for p in products:
                    # En lugar de consultar el precio para cantidad=1, buscamos explícitamente
                    # si hay reglas de tarifa configuradas para este producto en la lista.
                    # Esto permite detectar descuentos por volumen (cantidad > 1).
                    domain = [
                        ('pricelist_id', '=', pricelist.id),
                        '|', ('product_tmpl_id', '=', p.id),
                             ('product_id', 'in', p.product_variant_ids.ids)
                    ]
                    rules = self.env['product.pricelist.item'].search(domain, order="min_quantity desc", limit=1)
                    
                    if rules:
                        rule = rules[0]
                        if rule.min_quantity > 1 or rule.date_start or rule.date_end:
                            pricelist_info[p.id] = {
                                'min_quantity': int(rule.min_quantity),
                                'date_start': rule.date_start,
                                'date_end': rule.date_end,
                            }

        # --- Precios Computados ---
        computed_prices = {}
        for p in products:
            price = p.list_price
            if pricelist:
                try:
                    if hasattr(pricelist, '_get_product_price'):
                        # Odoo 17+
                        price = pricelist._get_product_price(p, 1.0, False)
                    else:
                        # Odoo < 17
                        price = pricelist.price_get(p.id, 1.0)[pricelist.id]
                except Exception:
                    price = p.list_price
            computed_prices[p.id] = price

        # --- Ordenamiento ---
        if sort_by == "name":
            products = products.sorted(key=lambda p: p.name or "")
        elif sort_by == "list_price":
            products = products.sorted(key=lambda p: computed_prices[p.id])
        elif sort_by == "list_price_desc":
            products = products.sorted(key=lambda p: computed_prices[p.id], reverse=True)

        # --- Agrupamiento ---
        grouped_docs = {}
        is_grouped = False

        if group_by == "categ_id":
            is_grouped = True
            for p in products:
                cat_name = p.categ_id.name if p.categ_id else "Sin Categoría"
                grouped_docs.setdefault(cat_name, []).append(p)
        elif group_by == "public_categ_ids":
            is_grouped = True
            for p in products:
                if p.public_categ_ids:
                    for cat in p.public_categ_ids:
                        grouped_docs.setdefault(cat.name, []).append(p)
                else:
                    grouped_docs.setdefault("Sin Categoría Web", []).append(p)
        elif group_by == "product_tag_ids":
            is_grouped = True
            for p in products:
                if p.product_tag_ids:
                    for tag in p.product_tag_ids:
                        grouped_docs.setdefault(tag.name, []).append(p)
                else:
                    grouped_docs.setdefault("Sin Etiquetas", []).append(p)
        else:
            grouped_docs["Todos los Productos"] = list(products)

        return {
            "docs": products,
            "config": config,
            "col_width": _COL_WIDTHS.get(columns, "23%"),
            "cols": int(columns),
            "grouped_docs": grouped_docs,
            "is_grouped": is_grouped,
            "report_date": fields.Date.today(),
            "pricelist": pricelist,
            "pricelist_info": pricelist_info,
            "computed_prices": computed_prices,
        }
