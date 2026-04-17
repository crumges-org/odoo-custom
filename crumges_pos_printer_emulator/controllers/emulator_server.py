# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response
import logging
import json
import datetime
import time

_logger = logging.getLogger(__name__)

# Cache en formato clave-valor (base de datos o memoria simple)
# Para evitar bloqueos, lo alojamos a nivel de clase de Python
last_receipt_xml = "No receipt received yet."
last_receipt_timestamp = time.time()
last_receipt_pos_name = "Odoo POS"

class PrinterEmulatorController(http.Controller):

    @http.route('/hw_proxy/hello', type='http', auth='public', cors='*', csrf=False, methods=['GET', 'OPTIONS'])
    def hw_proxy_hello(self, **kw):
        if request.httprequest.method == 'OPTIONS':
            return Response("")
        return Response('{"status": "ok"}', content_type='application/json')

    @http.route('/hw_proxy/print_xml_receipt', type='http', auth='public', cors='*', csrf=False, methods=['POST', 'OPTIONS'])
    def hw_proxy_print_xml_receipt(self, **kw):
        if request.httprequest.method == 'OPTIONS':
            return Response("")
        
        global last_receipt_xml, last_receipt_timestamp, last_receipt_pos_name
        try:
            data = request.httprequest.get_data(as_text=True)
            content = data
            
            # Tratamos de limpiar o extraer el receipt y pos_name
            pos_name = "Odoo POS"
            if 'receipt' in content or 'pos_name' in content:
                try:
                    js_data = json.loads(content)
                    if 'params' in js_data:
                        if 'receipt' in js_data['params']:
                            content = js_data['params']['receipt']
                        if 'pos_name' in js_data['params']:
                            pos_name = js_data['params']['pos_name']
                except Exception:
                    pass

            last_receipt_xml = content
            last_receipt_pos_name = pos_name
            last_receipt_timestamp = time.time()
            
            # Escribir a archivo
            with open("/tmp/crumges_printer_emulator.log", "a") as f:
                f.write(f"[{datetime.datetime.now().isoformat()}] Received Print Request from {pos_name}:\n")
                f.write(f"{last_receipt_xml}\n")
                f.write("-" * 50 + "\n")
                
            _logger.info("Emulated Printer received receipt and logged to /tmp/crumges_printer_emulator.log")
            return Response('{"jsonrpc": "2.0", "id": null, "result": {"status": "ok"}}', content_type='application/json')
        except Exception as e:
            _logger.error("Error processing receipt: %s", e)
            return Response('{"jsonrpc": "2.0", "id": null, "error": {"message": "Internal Error"}}', status=500, content_type='application/json')

    @http.route('/printer_emulator/check_update', type='http', auth='public', methods=['GET'])
    def check_update(self, **kw):
        global last_receipt_timestamp, last_receipt_pos_name, last_receipt_xml
        return Response(json.dumps({
            'timestamp': last_receipt_timestamp,
            'pos_name': last_receipt_pos_name,
            'html': last_receipt_xml
        }), content_type='application/json')

    @http.route('/printer_emulator/last_receipt', type='http', auth='public', website=True)
    def web_last_receipt(self, **kw):
        global last_receipt_xml, last_receipt_timestamp, last_receipt_pos_name
        
        html = f"""
        <html>
            <head>
                <title>🖨️ Visor de Recibos y Comandas ({last_receipt_pos_name})</title>
                <link rel="stylesheet" href="/point_of_sale/static/src/css/pos_receipts.css" />
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
                <style>
                    body {{
                        background: #e0e0e0;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 30px;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    }}
                    h2 {{
                        color: #444;
                        margin-bottom: 5px;
                        font-weight: 600;
                    }}
                    .subtitle {{
                        color: #666;
                        margin-bottom: 25px;
                        font-size: 15px;
                    }}
                    .controls-container {{
                        margin-bottom: 20px;
                    }}
                    .ticket-container {{
                        background: white;
                        color: black;
                        width: 400px;
                        padding: 15px;
                        box-shadow: 0px 6px 16px rgba(0,0,0,0.15);
                        font-size: 13px;
                        transition: all 0.3s ease;
                    }}
                    /* Clases para el modo Térmico */
                    .thermal-mode {{
                        filter: grayscale(100%) contrast(150%) brightness(0.95);
                        background: #fdfdf0 !important; /* Ligeramente amarillento tipo papel contable */
                        color: #222 !important; 
                    }}
                    .pos-receipt-title {{ font-weight: bold; font-size: 1.2em; }}
                </style>
                <script>
                    let currentTimestamp = {last_receipt_timestamp};
                    setInterval(() => {{
                        fetch('/printer_emulator/check_update')
                        .then(r => r.json())
                        .then(data => {{
                            if (data.timestamp > currentTimestamp) {{
                                currentTimestamp = data.timestamp;
                                document.getElementById('pos-name-label').innerText = data.pos_name;
                                document.getElementById('receipt-content').innerHTML = data.html;
                            }}
                        }}).catch(() => {{}});
                    }}, 1000);
                    
                    function setMode(mode) {{
                        const ticket = document.getElementById('ticket-wrapper');
                        const btnColor = document.getElementById('btn-color');
                        const btnThermal = document.getElementById('btn-thermal');
                        if (mode === 'thermal') {{
                            ticket.classList.add('thermal-mode');
                            btnThermal.classList.replace('btn-outline-secondary', 'btn-secondary');
                            btnColor.classList.replace('btn-primary', 'btn-outline-primary');
                        }} else {{
                            ticket.classList.remove('thermal-mode');
                            btnColor.classList.replace('btn-outline-primary', 'btn-primary');
                            btnThermal.classList.replace('btn-secondary', 'btn-outline-secondary');
                        }}
                    }}
                </script>
            </head>
            <body>
                <h2>🖨️ Visor de Recibos y Comandas</h2>
                <div class="subtitle">Capturado desde: <strong id="pos-name-label">{last_receipt_pos_name}</strong></div>
                
                <!-- Botonera de visualización -->
                <div class="controls-container btn-group" role="group" aria-label="Visual Mode">
                  <button type="button" id="btn-color" class="btn btn-primary" onclick="setMode('color')">🎨 Original UI</button>
                  <button type="button" id="btn-thermal" class="btn btn-outline-secondary" onclick="setMode('thermal')">🧾 Papel Térmico</button>
                </div>
                
                <div id="ticket-wrapper" class="ticket-container pos-receipt-print pos-receipt">
                    <div id="receipt-content" style="width: 100%;">
                        {last_receipt_xml}
                    </div>
                </div>
            </body>
        </html>
        """
        return request.make_response(html)
