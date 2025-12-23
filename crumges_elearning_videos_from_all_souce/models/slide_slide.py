# Copyright 2025 Crumges
# License OPL-1 or later (https://www.odoo.com/documentation/17.0/legal/licenses.html).

import base64
import hashlib
import hmac
import time
import requests
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Slide(models.Model):
    _inherit = "slide.slide"

    slide_type = fields.Selection(
        selection_add=[
            ("externalvideo", "MP4 External Video"),
            ("googledrivevideo", "Google Drive Video"),
            ("vimeovideo", "Vimeo Video"),
            ("localvideo", "Local Video"),
            ("zoom_meeting", "Zoom Meeting"),
        ],
        ondelete={
            "externalvideo": "cascade",
            "googledrivevideo": "cascade",
            "vimeovideo": "cascade",
            "localvideo": "cascade",
            "zoom_meeting": "cascade",
        },
    )
    external_url = fields.Char(help="URL for external video sources")
    
    # Zoom related fields
    zoom_meeting_id = fields.Char(string="Zoom Meeting ID")
    zoom_meeting_pwd = fields.Char(string="Zoom Meeting Password")
    
    # Visualization options
    show_drive_popout = fields.Boolean(string="Show Drive Popout", default=True, help="If unchecked, hides the external link button on Google Drive videos.")
    hide_embed_option = fields.Boolean(string="Hide Embed Option", default=False, help="If checked, the 'Embed in another website' option will be hidden in the share modal.")

    # Local video storage
    local_video_file = fields.Binary(string="Local Video File", attachment=True)
    local_video_filename = fields.Char(string="Local Video Filename")
    
    @api.onchange("local_video_file")
    def _onchange_local_video_file(self):
        if self.local_video_file and self.slide_type == "localvideo":
            # Basic validation based on filename extension as getting mime from binary
            # might be heavy efficiently on onchange without magic lib
            if self.local_video_filename:
                ext = self.local_video_filename.lower().split('.')[-1]
                if ext not in ['mp4', 'webm', 'ogg']:
                     return {
                        'warning': {
                            'title': _('Invalid File'),
                            'message': _('Please upload only mp4, ogg, or webm files.')
                        }
                    }

    @api.onchange("external_url", "slide_type")
    def _onchange_external_url_vimeo(self):
        if self.slide_type == "vimeovideo" and self.external_url:
            self._fetch_vimeo_metadata()

    def _fetch_vimeo_metadata(self):
        """Fetch metadata from Vimeo oEmbed API."""
        try:
            oembed_url = f"https://vimeo.com/api/oembed.json?url={self.external_url}"
            response = requests.get(oembed_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.name = data.get("title", self.name)
                self.description = data.get("description", self.description)
                # Duration in seconds to hours
                if "duration" in data:
                    self.completion_time = data["duration"] / 3600
                if "thumbnail_url" in data:
                    image_content = requests.get(data["thumbnail_url"], timeout=5).content
                    self.image_1920 = base64.b64encode(image_content)
        except Exception:
            # SIlent fail to not block user
            pass

    def _generate_zoom_signature(self, api_key, api_secret, meeting_number, role=0):
        """Generate a signature for Zoom Web SDK."""
        ts = int(round(time.time() * 1000)) - 30000
        msg = f"{api_key}{meeting_number}{ts}{role}"
        
        # Create signature
        message_bytes = msg.encode("utf-8")
        secret_bytes = api_secret.encode("utf-8")
        
        signature_hash = hmac.new(secret_bytes, message_bytes, hashlib.sha256).digest()
        signature_b64 = base64.b64encode(signature_hash).decode("utf-8")
        
        tmp_str = f"{api_key}.{meeting_number}.{ts}.{role}.{signature_b64}"
        final_signature = base64.b64encode(tmp_str.encode("utf-8")).decode("utf-8")
        
        return final_signature.rstrip("=")

    @api.depends("slide_type", "external_url", "zoom_meeting_id", "local_video_file", "show_drive_popout")
    def _compute_embed_code(self):
        # We override to handle new types, fallback to super for standard types
        super()._compute_embed_code()
        for record in self:
            if record.slide_type not in [
                "externalvideo", "googledrivevideo", "vimeovideo", "localvideo", "zoom_meeting"
            ]:
                continue
                
            code = ""
            if record.slide_type == "externalvideo" and record.external_url:
                code = f'<video class="w-100" controls controlsList="nodownload"><source src="{record.external_url}" type="video/mp4"/></video>'
            
            elif record.slide_type == "localvideo" and record.local_video_file:
                # Use the download URL for the field
                url = f"/web/content/slide.slide/{record.id}/local_video_file"
                code = f'<video class="w-100" controls controlsList="nodownload"><source src="{url}"/></video>'

            # Handle both custom and standard Google Drive slide types
            elif (record.slide_type == "googledrivevideo" and record.external_url) or \
                 (record.slide_type == "google_drive_video" and record.google_drive_id):
                
                # Use appropriate ID source
                file_id = record.external_url if record.slide_type == "googledrivevideo" else record.google_drive_id
                url = f"https://drive.google.com/file/d/{file_id}/preview"
                
                # We inject the overlay directly here because the Fullscreen player fetches embed_code via JS/RPC
                if not record.show_drive_popout:
                    code = f'<div class="crm-drive-wrapper position-relative w-100 h-100"><div class="drivehidecontrols"></div><iframe src="{url}" width="100%" height="100%" frameborder="0" allow="autoplay"></iframe></div>'
                else:
                    code = f'<iframe src="{url}" width="100%" height="100%" frameborder="0" allow="autoplay"></iframe>'

            elif record.slide_type == "vimeovideo" and record.external_url:
                # Basic parsing to get ID, or use oEmbed link if available
                # Logic: last part of URL usually
                vimeo_id = record.external_url.split("/")[-1]
                url = f"https://player.vimeo.com/video/{vimeo_id}"
                code = f'<iframe src="{url}" width="100%" height="100%" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>'

            elif record.slide_type == "zoom_meeting" and record.zoom_meeting_id:
                # TODO: This requires a static HTML file to handle the Web SDK logic 
                # or a controller route. For now, we will generate an iframe pointing to a controller or static resource.
                # The original module used a static html with query params.
                # We should replicate that or improve it.
                # Let's assume we will have a route or static file.
                
                # Fetch config
                param_obj = self.env["ir.config_parameter"].sudo()
                api_key = param_obj.get_param("crumges_elearning_videos.zoom_api_key")
                api_secret = param_obj.get_param("crumges_elearning_videos.zoom_api_secret")
                
                if api_key and api_secret:
                    signature = self._generate_zoom_signature(api_key, api_secret, record.zoom_meeting_id)
                    # We will need to create this 'meeting.html' in static
                    base_url = "/crumges_elearning_videos/static/description/meeting.html" 
                    # Warning: The original module had it in static/src... 
                    # let's put it in static/meeting_client/meeting.html roughly
                    
                    # NOTE: A robust implementation would use a Controller to render a QWeb template
                    # instead of a static HTML with query params, to avoid exposing logic/keys 
                    # but the keys are needed in JS frontend for logic.
                    # The signature hides the secret.
                    
                    # For simplicty and V18 standard, let's keep the structure simple or just show a placeholder
                    # if we don't implement the full JS Web SDK right now. 
                    # But the prompt asked for it. 
                    
                    # Let's construct a smart URL
                    # We will point to a specialized route we will create? Or just iframe a static resource?
                    # Static resource is easier for iframe embedding.
                    
                    # Pass the signature and info to the iframe src
                    # Note: We expose API Key, which is required by Zoom Web SDK 1.9.x+ (Client View) 
                    # checking docs... Client View uses SDK Key (formerly API Key).
                    
                    query_params = {
                        "mn": record.zoom_meeting_id,
                        "pwd": record.zoom_meeting_pwd or "",
                        "signature": signature,
                        "apiKey": api_key,
                        "name": self.env.user.name,
                        "email": self.env.user.email or "",
                    }
                    encoded_params = urls.url_encode(query_params)
                    # We need to ensure we ship this meeting.html
                    code = f'<iframe src="/crumges_elearning_videos/static/lib/zoom/meeting.html?{encoded_params}" width="100%" height="100%" frameborder="0" allow="microphone; camera; fullscreen"></iframe>'
                else:
                    code = '<div class="alert alert-warning">Zoom is not configured.</div>'

            record.embed_code = code
