# © 2025 Crumges
# License OPL-1

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CatalogWizard(models.TransientModel):
    _name = "catalog.wizard"
    _description = "Asistente de Catálogo de Productos"

    product_ids = fields.Many2many(
        "product.template",
        string="Productos",
        required=True,
    )
    config_id = fields.Many2one(
        "catalog.config",
        string="Configuración",
        required=True,
    )

    # Campos relacionados para mostrar/ocultar en la vista según el layout
    layout_mode = fields.Selection(
        related="config_id.layout_mode",
        string="Tipo de layout",
        readonly=False,
        store=False,
    )
    
    group_by = fields.Selection(
        related="config_id.group_by",
        readonly=False,
        required=True,
    )
    sort_by = fields.Selection(
        related="config_id.sort_by",
        readonly=False,
        required=True,
    )
    pricelist_id = fields.Many2one(
        related="config_id.pricelist_id",
        readonly=False,
    )
    show_pricelist_info = fields.Boolean(
        related="config_id.show_pricelist_info",
        readonly=False,
    )
    # Related para la preview del membrete en el wizard
    header_image = fields.Binary(
        related="config_id.header_image",
        string="Cabecera (preview)",
        readonly=True,
    )
    footer_image = fields.Binary(
        related="config_id.footer_image",
        string="Pie de página (preview)",
        readonly=True,
    )

    # --- Email ---
    send_email = fields.Boolean(string="Enviar por email")
    email_to = fields.Char(string="Destinatarios", help="Separá múltiples emails con comas.")
    subject = fields.Char(string="Asunto", default="Catálogo de Productos")
    body = fields.Html(
        string="Mensaje",
        default="<p>Adjunto encontrará nuestro catálogo de productos.</p>",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids", [])
        if active_ids and "product_ids" in fields_list:
            res["product_ids"] = [fields.Command.set(active_ids)]
        # Buscar la primera configuración disponible como default
        if "config_id" in fields_list:
            config = self.env["catalog.config"].search([], limit=1)
            if config:
                res["config_id"] = config.id
        return res

    def _get_report_action(self):
        if self.config_id.layout_mode == "custom":
            return self.env.ref("crumges_product_catalog.action_catalog_report_custom")
        return self.env.ref("crumges_product_catalog.action_catalog_report")

    def _build_report_data(self):
        return {
            "config_id": self.config_id.id,
            "product_ids": self.product_ids.ids,
            "group_by": self.group_by,
            "sort_by": self.sort_by,
            "pricelist_id": self.pricelist_id.id,
            "show_pricelist_info": self.show_pricelist_info,
        }

    def action_print_pdf(self):
        """Genera y descarga el catálogo en PDF."""
        self.ensure_one()
        if not self.product_ids:
            raise UserError(_("Seleccioná al menos un producto."))
        return self._get_report_action().report_action(
            self,
            data=self._build_report_data(),
        )

    def action_send_email(self):
        """Genera el PDF y lo envía por email."""
        self.ensure_one()
        if not self.product_ids:
            raise UserError(_("Seleccioná al menos un producto."))
        if not self.email_to:
            raise UserError(_("Ingresá al menos un destinatario de email."))

        report = self._get_report_action()
        pdf_content, _ = report._render_qweb_pdf(
            self.id,
            data=self._build_report_data(),
        )

        attachment = self.env["ir.attachment"].create({
            "name": "Catalogo_Productos.pdf",
            "type": "binary",
            "datas": base64.b64encode(pdf_content),
            "mimetype": "application/pdf",
        })

        mail = self.env["mail.mail"].create({
            "email_to": self.email_to,
            "subject": self.subject or _("Catálogo de Productos"),
            "body_html": self.body or "<p>Adjunto encontrará nuestro catálogo de productos.</p>",
            "attachment_ids": [fields.Command.link(attachment.id)],
        })
        mail.send()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Email enviado"),
                "message": _("El catálogo fue enviado a %s") % self.email_to,
                "type": "success",
                "sticky": False,
            },
        }

    def action_print_and_send(self):
        """Genera el PDF, lo descarga y lo envía por email."""
        self.ensure_one()
        self.action_send_email()
        return self.action_print_pdf()
