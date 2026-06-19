# -*- coding: utf-8 -*-
import requests
from odoo import models, fields, api

class ProductImage(models.Model):
    _inherit = 'product.image'

    image_filename = fields.Char("Nombre del Archivo")

    @api.onchange('image_1920')
    def _onchange_image_1920(self):
        # Como el widget 'image' no envía el nombre del archivo, aplicamos el Plan B (Secuencial)
        if self.image_1920 and not self.name:
            if self.product_tmpl_id:
                count = self.search_count([('product_tmpl_id', '=', self.product_tmpl_id.id)])
                self.name = f"{self.product_tmpl_id.name} - Imagen {count + 1}"
            else:
                self.name = "Imagen Multimedia"

    @api.onchange('video_url')
    def _onchange_video_url(self):
        import urllib.parse
        if self.video_url and not self.name:
            try:
                encoded_url = urllib.parse.quote(self.video_url, safe='')
                response = requests.get(f"https://www.youtube.com/oembed?url={encoded_url}&format=json", timeout=2)
                if response.status_code == 200:
                    self.name = response.json().get('title', 'Video YouTube')
                    return
            except:
                pass
            
            try:
                encoded_url = urllib.parse.quote(self.video_url, safe='')
                response = requests.get(f"https://vimeo.com/api/oembed.json?url={encoded_url}", timeout=2)
                if response.status_code == 200:
                    self.name = response.json().get('title', 'Video Vimeo')
                    return
            except:
                pass

            # Fallback secuencial
            if self.product_tmpl_id:
                count = self.search_count([('product_tmpl_id', '=', self.product_tmpl_id.id)])
                self.name = f"{self.product_tmpl_id.name} - Video {count + 1}"
            else:
                self.name = "Video Multimedia"
