import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Se ejecuta al INSTALAR el módulo puente.
    Copia los registros de venta cruzada que el usuario tenía configurados en el POS
    hacia las tablas nativas de eCommerce (website_sale), asegurando que no se pierdan.
    """
    _logger.info("Iniciando migración de datos de venta cruzada: POS -> eCommerce...")
    try:
        # Migrar Alternativas (product.template)
        env.cr.execute("""
            INSERT INTO product_alternative_rel (src_id, dest_id)
            SELECT src_id, dest_id FROM crumges_pos_product_alternative_rel
            ON CONFLICT DO NOTHING;
        """)
        
        # Migrar Accesorios (product.product)
        env.cr.execute("""
            INSERT INTO product_accessory_rel (src_id, dest_id)
            SELECT src_id, dest_id FROM crumges_pos_product_accessory_rel
            ON CONFLICT DO NOTHING;
        """)
        
        _logger.info("Migración POS -> eCommerce completada exitosamente.")
    except Exception as e:
        _logger.warning("Excepción durante la migración POS -> eCommerce (posiblemente la tabla ya no exista): %s", e)


def uninstall_hook(env):
    """
    Se ejecuta al DESINSTALAR el módulo puente.
    Como el módulo puente hace que el eCommerce sea la "fuente de la verdad",
    al desinstalarlo queremos que el POS conserve todos los cambios recientes.
    Por lo tanto, vaciamos las tablas internas del POS y las sobrescribimos con
    la información actual del eCommerce.
    """
    _logger.info("Desinstalando módulo puente. Restaurando datos: eCommerce -> POS...")
    try:
        # 1. Limpiar las tablas del POS
        env.cr.execute("DELETE FROM crumges_pos_product_alternative_rel;")
        env.cr.execute("DELETE FROM crumges_pos_product_accessory_rel;")

        # 2. Copiar todo desde eCommerce hacia el POS
        env.cr.execute("""
            INSERT INTO crumges_pos_product_alternative_rel (src_id, dest_id)
            SELECT src_id, dest_id FROM product_alternative_rel
            ON CONFLICT DO NOTHING;
        """)
        
        env.cr.execute("""
            INSERT INTO crumges_pos_product_accessory_rel (src_id, dest_id)
            SELECT src_id, dest_id FROM product_accessory_rel
            ON CONFLICT DO NOTHING;
        """)
        
        _logger.info("Restauración eCommerce -> POS completada exitosamente.")
    except Exception as e:
        _logger.warning("Excepción durante la restauración eCommerce -> POS: %s", e)
