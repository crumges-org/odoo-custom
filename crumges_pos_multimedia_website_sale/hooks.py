import logging

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """ Migra de crumges.pos.product.image a product.image """
    _logger.info("Migrando imágenes de POS a eCommerce...")
    try:
        pos_images = env['crumges.pos.product.image'].search([])
        for img in pos_images:
            env['product.image'].create({
                'name': img.name,
                'image_1920': img.image_1920,
                'video_url': img.video_url,
                'product_tmpl_id': img.product_tmpl_id.id,
            })
        _logger.info("Migración completada.")
    except Exception as e:
        _logger.warning("Error en migración: %s", e)

def uninstall_hook(env):
    """ Migra de product.image a crumges.pos.product.image """
    _logger.info("Restaurando imágenes del eCommerce al POS...")
    try:
        env.cr.execute("DELETE FROM crumges_pos_product_image")
        website_images = env['product.image'].search([])
        for img in website_images:
            env['crumges.pos.product.image'].create({
                'name': img.name,
                'image_1920': img.image_1920,
                'video_url': img.video_url,
                'product_tmpl_id': img.product_tmpl_id.id,
            })
        _logger.info("Restauración completada.")
    except Exception as e:
        _logger.warning("Error en restauración: %s", e)
