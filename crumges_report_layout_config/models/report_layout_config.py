from odoo import models, fields, api, _

class ReportLayoutConfig(models.Model):
    _name = 'report.layout.config'
    _description = 'Report Layout Configuration'
    _inherit = ['image.mixin']

    name = fields.Char(string='Layout Name', required=True)
    active = fields.Boolean(default=True)

    # --- Layout Style ---
    layout_style = fields.Selection([
        ('standard', 'Standard'),
        ('modern', 'Modern'),
        ('compact', 'Compact'),
        ('minimal', 'Minimal')
    ], string='Layout Style', default='standard', required=True)

    # --- Branding ---
    use_company_logo = fields.Boolean(string='Use Company Logo', default=True, help='If checked, the current company logo will be used.')
    # --- Colors ---
    use_company_colors = fields.Boolean(string='Use Company Colors', default=False, help='If checked, uses the primary and secondary colors set on the company (if available).')
    primary_color = fields.Char(string='Primary Color', default='#000000', help='Main color for headers, titles, etc.')
    secondary_color = fields.Char(string='Secondary Color', default='#888888', help='Accent color for borders, secondary text.')
    text_color = fields.Char(string='Text Color', default='#212529', help='Main body text color.')

    logo_position = fields.Selection([
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
        ('none', 'Hidden')
    ], string='Logo Position', default='left')

    # --- Typography ---
    font_family = fields.Selection([
        ('Lato', 'Lato'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Montserrat', 'Montserrat'),
        ('Oswald', 'Oswald'),
        ('Raleway', 'Raleway'),
    ], string='Font Family', default='Lato')
    
    font_size = fields.Integer(string='Base Font Size (pt)', default=10)

    # --- Content ---
    layout_mode = fields.Selection([
        ('structured', 'Standard'),
        ('html', 'Custom HTML')
    ], string='Layout Mode', default='structured', required=True, help="Choose between a structured header/footer based on fields (Standard) or full custom HTML control (Custom HTML).")

    # -- Address --
    address_source = fields.Selection([
        ('company', 'Use Company Address'),
        ('custom', 'Custom Address'),
        ('none', 'None')
    ], string='Address Source', default='company')
    custom_address = fields.Html(string='Custom Address')

    # -- Motto --
    motto_source = fields.Selection([
        ('company', 'Use Company Motto'),
        ('custom', 'Custom Motto'),
        ('none', 'None')
    ], string='Motto Source', default='company', help="Company Motto is set in Company Settings.")
    custom_motto = fields.Char(string='Custom Motto')
    motto_position = fields.Selection([
        ('header', 'Header'),
        ('footer', 'Footer')
    ], string='Motto Position', default='header')

    # -- Footer --
    footer_source = fields.Selection([
        ('company', 'Use Company Footer'),
        ('custom', 'Custom Footer'),
        ('none', 'None')
    ], string='Footer Source', default='company')
    # Note: reusing footer_content for custom footer to avoid migration issues if possible, or just add new field. 
    # Existing footer_content was for Custom HTML mode. Let's keep using `footer_content` as the custom content field for both logic if that simplifies?
    # Actually, let's allow `footer_content` to be the field for "Custom HTML mode" AND "Custom Footer" in structured mode.
    # But wait, header_content is for Custom HTML header.
    # Let's align:
    # Custom HTML Mode -> uses header_content, footer_content.
    # Structured Mode -> uses granular fields.
    # So `custom_footer` is better for structured mode to separate concerns.
    custom_footer = fields.Html(string='Custom Footer Text')

    # Custom HTML Fields (Advanced)
    header_content = fields.Html(string='Custom Header Content', help='Custom HTML for the header (Visible in Custom HTML mode).')
    footer_content = fields.Html(string='Custom Footer Content', help='Custom HTML for the footer (Visible in Custom HTML mode).')
    
    show_header = fields.Boolean(string='Show Header', default=True)
    show_footer = fields.Boolean(string='Show Footer', default=True)

    # --- Advanced ---
    css_custom = fields.Text(string='Custom CSS', help='Add custom CSS to override specific styles.')
    
    # --- Preview ---
    preview_html = fields.Html(compute='_compute_preview_html', string='Preview')

    @api.depends('primary_color', 'secondary_color', 'text_color', 'font_family', 'layout_style',
                 'layout_mode', 'address_source', 'custom_address', 
                 'motto_source', 'custom_motto', 'motto_position',
                 'footer_source', 'custom_footer', 'use_company_colors',
                 'logo_position', 'show_header', 'show_footer',
                 'header_content', 'footer_content')
    def _compute_preview_html(self):
        for record in self:
            # Color logic
            p_color = record.primary_color
            s_color = record.secondary_color
            if record.use_company_colors:
                 company = self.env.company
                 p_color = company.primary_color or p_color
                 s_color = company.secondary_color or s_color
            
            style = f"""
                font-family: {record.font_family}, sans-serif;
                color: {record.text_color};
                --primary: {p_color};
                --secondary: {s_color};
            """

            # Layout Style Logic for Preview
            header_style = f"border-bottom: 2px solid {p_color}; margin-bottom: 10px;"
            footer_style = f"border-top: 1px solid {s_color}; padding: 10px; margin-top: 20px;"
            header_inner_style = ""
            
            if record.layout_style == 'modern':
                header_style = f"background-color: {p_color}; color: white; padding: 10px; margin-bottom: 10px;"
                footer_style = f"border-top: 5px solid {p_color}; padding: 10px; margin-top: 20px;"
                header_inner_style = "color: white;"
            elif record.layout_style == 'compact':
                header_style = "border-bottom: 1px dotted #ccc; margin-bottom: 10px;"

            header_html = ""
            if record.show_header:
                if record.layout_mode == 'html':
                    header_html = record.header_content or "Custom HTML Header"
                else:
                    # Structured Header Preview
                    parts = []
                    if record.logo_position != 'none':
                         parts.append("(Logo)")
                    
                    if record.address_source == 'company':
                        parts.append(f"<b>{self.env.company.name}</b><br/>{self.env.company.street or 'Address'}")
                    elif record.address_source == 'custom':
                        parts.append("(Custom Address)")

                    if record.motto_source != 'none' and record.motto_position == 'header':
                         motto_val = self.env.company.report_header if record.motto_source == 'company' else record.custom_motto
                         if motto_val:
                            parts.append(f"<i>{motto_val}</i>")
                            
                    header_html = " | ".join(parts) or "Structured Header"

            header = f'<div style="{header_style}">{header_html}</div>'

            footer_html = ""
            if record.show_footer:
                if record.layout_mode == 'html':
                     footer_html = record.footer_content or "Custom HTML Footer"
                else:
                    parts = []
                    if record.motto_source != 'none' and record.motto_position == 'footer':
                         motto_val = self.env.company.report_header if record.motto_source == 'company' else record.custom_motto
                         if motto_val:
                            parts.append(f"<i>{motto_val}</i>")
                    
                    if record.footer_source == 'company':
                        parts.append(self.env.company.report_footer or "Company Footer")
                    elif record.footer_source == 'custom':
                        parts.append("(Custom Footer)")
                    
                    footer_html = " | ".join(parts) or "Structured Footer"

            footer = f'<div style="{footer_style}">{footer_html}</div>'

            record.preview_html = f"""
                <div style="{style} border: 1px solid #ccc; padding: 20px; max-width: 800px; margin: 0 auto; min-height: 500px; display: flex; flex-direction: column;">
                    {header}
                    <div style="flex: 1; padding: 20px 0;">
                        <h1 style="color: var(--primary);">Document Title</h1>
                        <p>This is a preview of the <strong>{record.layout_style}</strong> layout.</p>
                        <p style="color: var(--secondary);">Secondary text example.</p>
                        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                    </div>
                    {footer}
                </div>
            """

    def get_css_variables(self):
        """Returns a string of CSS variables based on the configuration."""
        self.ensure_one()
        
        p_color = self.primary_color
        s_color = self.secondary_color
        
        if self.use_company_colors:
             company = self.env.company
             # Ensure we have values, otherwise fallback to configured
             p_color = company.primary_color or p_color
             s_color = company.secondary_color or s_color

        return f"""
            :root {{
                --report-primary: {p_color};
                --report-secondary: {s_color};
                --report-text: {self.text_color};
                --report-font-family: '{self.font_family}', sans-serif;
                --report-font-size: {self.font_size}pt;
            }}
        """ + (self.css_custom or "")

    def action_compute_colors_from_logo(self):
        """Extracts dominant colors from the logo (or company logo) and updates primary/secondary colors."""
        self.ensure_one()
        image_data = None
        if self.use_company_logo:
             image_data = self.env.company.logo
        else:
             image_data = self.image_1920
             
        if not image_data:
            return
        
        try:
            from PIL import Image
            import io
            import base64
            
            # Decode image
            image_bytes = base64.b64decode(image_data)
            img = Image.open(io.BytesIO(image_bytes))
            
            # Resize for speed and to reduce noise
            img = img.resize((150, 150))
            
            # Get dominant colors using palette
            # We want 3 colors to hopefully get a primary and secondary distinct from white/black
            result = img.convert('P', palette=Image.ADAPTIVE, colors=5)
            result.putalpha(0)
            colors = result.getcolors(150*150)
            
            # Sort by count (most frequent first)
            if colors:
                ordered_colors = sorted(colors, key=lambda x: x[0], reverse=True)
                
                # Helper to convert RGB to Hex
                def rgb_to_hex(rgb):
                    return '#%02x%02x%02x' % rgb[:3]
                
                # Filter out near-white and near-black if possible, unless they are the only ones
                valid_colors = []
                for count, rgb in ordered_colors:
                    # Simple check to avoid pure white/black background dominance if possible
                    # Luminance check could be better but let's stick to simple hex
                    hex_col = rgb_to_hex(self.env['ir.qweb.field.image']._get_palette_data(rgb) if hasattr(self.env['ir.qweb.field.image'], '_get_palette_data') else rgb) # fallback
                    # Just use raw RGB
                    hex_col = rgb_to_hex(rgb)
                    valid_colors.append(hex_col)

                if len(valid_colors) > 0:
                    self.primary_color = valid_colors[0]
                if len(valid_colors) > 1:
                    # Try to find a secondary that allows contrast or just the next dominant
                    self.secondary_color = valid_colors[1]
                    
        except Exception as e:
            # Fallback or log error
            return
            
    # Helper to get the actual logo to use (config or company)
    def _get_active_logo(self):
        self.ensure_one()
        return self.image_1920 or self.env.company.logo
