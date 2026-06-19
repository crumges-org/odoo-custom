/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";

export class MultimediaViewer extends Component {
    static template = "crumges_pos_multimedia.MultimediaViewer";
    
    setup() {
        this.pos = usePos();
        this.state = useState({
            activeMedia: null,
            zoom: 1,
            isExpanded: false,
            panX: 0,
            panY: 0,
            isDragging: false,
        });
        
        this.dragStartX = 0;
        this.dragStartY = 0;
        
        this.mediaItems = this._getMediaItems();
        if (this.mediaItems.length > 0) {
            this.state.activeMedia = this.mediaItems[0];
        }
    }

    get hasMedia() {
        return this.mediaItems.length > 1; // Solo mostrar si hay mas de 1 imagen (la principal y extras)
    }

    onMouseDown(ev) {
        if (this.state.activeMedia.type !== 'image' || this.state.zoom <= 1) return;
        this.state.isDragging = true;
        this.dragStartX = ev.clientX - this.state.panX;
        this.dragStartY = ev.clientY - this.state.panY;
        ev.preventDefault(); // Evita el "ghost drag" nativo del navegador para imagenes
    }

    onMouseMove(ev) {
        if (!this.state.isDragging) return;
        this.state.panX = ev.clientX - this.dragStartX;
        this.state.panY = ev.clientY - this.dragStartY;
    }

    onMouseUp() {
        this.state.isDragging = false;
    }

    onMouseLeave() {
        this.state.isDragging = false;
    }

    toggleFullscreen() {
        const viewerElem = document.querySelector('.main-viewer');
        if (!viewerElem) return;
        
        if (!document.fullscreenElement) {
            if (viewerElem.requestFullscreen) {
                viewerElem.requestFullscreen();
            } else if (viewerElem.webkitRequestFullscreen) {
                viewerElem.webkitRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        }
    }

    zoomIn() {
        this.state.zoom += 0.25;
    }

    zoomOut() {
        this.state.zoom = Math.max(0.25, this.state.zoom - 0.25);
        if (this.state.zoom <= 1) {
            this.state.panX = 0;
            this.state.panY = 0;
        }
    }

    zoomReset() {
        this.state.zoom = 1;
        this.state.panX = 0;
        this.state.panY = 0;
    }

    setActiveMedia(media) {
        this.state.activeMedia = media;
        this.zoomReset();
        this.state.isExpanded = true;
    }

    _getEmbedUrl(url) {
        if (!url) return '';
        // Convert YouTube
        const ytMatch = url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})/);
        if (ytMatch && ytMatch[1]) {
            return `https://www.youtube.com/embed/${ytMatch[1]}?autoplay=1&rel=0`;
        }
        // Convert Vimeo
        const vimeoMatch = url.match(/vimeo\.com\/(?:video\/)?([0-9]+)/);
        if (vimeoMatch && vimeoMatch[1]) {
            return `https://player.vimeo.com/video/${vimeoMatch[1]}?autoplay=1`;
        }
        return url;
    }

    _getMediaItems() {
        const product = this.props.product;
        const items = [];
        
        // 1. Imagen principal
        items.push({
            id: 'main',
            type: 'image',
            url: `/web/image?model=product.product&field=image_1920&id=${product.id}`,
            thumbUrl: `/web/image?model=product.product&field=image_1920&id=${product.id}`
        });

        // 2. Imágenes adicionales
        let ids = product.crumges_pos_image_ids || [];
        let isWebsite = false;
        
        if (product.product_template_image_ids && product.product_template_image_ids.length > 0) {
            ids = product.product_template_image_ids;
            isWebsite = true;
        }

        const modelName = isWebsite ? 'product.image' : 'crumges.pos.product.image';
        const storeDict = isWebsite ? this.pos.product_image_by_id : this.pos.crumges_pos_product_image_by_id;

        ids.forEach(id => {
            const record = storeDict ? storeDict[id] : null;
            let type = 'image';
            let video_url = '';
            
            if (record && record.video_url) {
                type = 'video';
                video_url = this._getEmbedUrl(record.video_url);
            }

            items.push({
                id: id,
                type: type,
                video_url: video_url,
                url: `/web/image?model=${modelName}&field=image_1920&id=${id}`,
                thumbUrl: `/web/image?model=${modelName}&field=image_1920&id=${id}` // Usamos la grande como thumb porque Odoo a veces no genera image_128 a tiempo
            });
        });

        return items;
    }
}

// Inyectar el componente en el popup
patch(ProductInfoPopup, {
    components: { ...ProductInfoPopup.components, MultimediaViewer },
});
