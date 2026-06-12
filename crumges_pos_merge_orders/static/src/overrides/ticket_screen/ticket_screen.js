/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useState } from "@odoo/owl";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // Extendemos el estado para rastrear los pedidos seleccionados para fusión
        this.state = useState({
            ...this.state,
            selectedMergeUuids: new Set(),
        });
    },

    toggleMergeSelection(order) {
        if (order.finalized) {
            return;
        }
        
        const currentOrder = this.getSelectedOrder();
        if (currentOrder && order.uuid === currentOrder.uuid) {
            return; // No se puede fusionar consigo mismo
        }

        if (this.state.selectedMergeUuids.has(order.uuid)) {
            this.state.selectedMergeUuids.delete(order.uuid);
        } else {
            this.state.selectedMergeUuids.add(order.uuid);
        }
    },

    // Limpiamos la selección si cambiamos de pedido activo
    _setOrder(order) {
        if (this.state.selectedMergeUuids) {
            this.state.selectedMergeUuids.clear();
        }
        super._setOrder(order);
    },

    get selectedMergeOrders() {
        if (!this.state.selectedMergeUuids || this.state.selectedMergeUuids.size === 0) return [];
        return this.pos.models["pos.order"].filter((o) => this.state.selectedMergeUuids.has(o.uuid));
    },

    get selectedMergeTotal() {
        return this.selectedMergeOrders.reduce((total, order) => total + order.get_total_with_tax(), 0);
    },

    onClickClearSelection() {
        // Deselecciona el pedido cargado en el panel derecho
        this.setSelectedOrder(null);
        // Deselecciona todos los checkboxes
        this.state.selectedMergeUuids.clear();
    },

    async onClickConfirmMerge() {
        if (this.state.selectedMergeUuids.size === 0) {
            return;
        }

        const eligibleOrders = this.pos.models["pos.order"].filter(
            (o) => this.state.selectedMergeUuids.has(o.uuid) && !o.finalized
        );

        if (eligibleOrders.length === 0) return;

        let targetOrder = this.getSelectedOrder();

        // Si no hay pedido seleccionado en el panel derecho, 
        // usamos el primer pedido seleccionado en la lista de checkboxes como el destino principal.
        if (!targetOrder || !this.state.selectedMergeUuids.has(targetOrder.uuid)) {
            if (!targetOrder) {
                if (eligibleOrders.length < 2) {
                    this.env.services.dialog.add(AlertDialog, {
                        title: _t("Selección insuficiente"),
                        body: _t("Por favor, seleccione al menos dos pedidos para fusionar, o seleccione un pedido destino principal en el panel derecho."),
                    });
                    return;
                }
                targetOrder = eligibleOrders.shift();
            }
        } else {
            // Removemos el targetOrder de la lista de orígenes para no fusionarlo consigo mismo
            const targetIndex = eligibleOrders.findIndex(o => o.uuid === targetOrder.uuid);
            if (targetIndex !== -1) {
                eligibleOrders.splice(targetIndex, 1);
            }
        }

        if (eligibleOrders.length === 0) return;

        // Detectar si hay múltiples clientes distintos
        const partnerMap = new Map();
        const addPartner = (partner) => {
            if (partner) {
                partnerMap.set(partner.id, partner);
            } else {
                partnerMap.set("none", null);
            }
        };

        addPartner(targetOrder.get_partner());
        for (const order of eligibleOrders) {
            addPartner(order.get_partner());
        }

        // Si hay más de un cliente diferente, preguntar al usuario con qué cliente se queda
        if (partnerMap.size > 1) {
            const partnerOptions = [];
            for (const [key, partner] of partnerMap.entries()) {
                // Evitamos añadir duplicados si de casualidad hay
                partnerOptions.push({
                    id: key,
                    item: partner,
                    label: partner ? partner.name : _t("Consumidor Final"),
                    isSelected: false,
                });
            }

            const selectedPartner = await makeAwaitable(this.env.services.dialog, SelectionPopup, {
                title: _t("Múltiples clientes. ¿A quién asignar el pedido?"),
                list: partnerOptions,
            });

            // Si devuelve undefined, el usuario canceló el popup de selección
            if (selectedPartner === undefined) {
                return;
            }

            // Asignar el cliente seleccionado a la orden destino
            targetOrder.set_partner(selectedPartner);
        }

        // Lógica de validación de tarifas basada en la configuración
        const mergeBehavior = this.pos.config.merge_pricelist_behavior || "keep";
        
        const currentPricelistId = targetOrder.pricelist?.id;
        const differentPricelists = eligibleOrders.some((order) => order.pricelist?.id !== currentPricelistId);

        if (differentPricelists) {
            if (mergeBehavior === "block") {
                this.env.services.dialog.add(AlertDialog, {
                    title: _t("Error de Tarifas"),
                    body: _t("No se pueden fusionar pedidos con listas de precios diferentes. La configuración actual bloquea esta acción."),
                });
                return;
            } else if (mergeBehavior === "ask") {
                // Collect unique pricelists
                const pricelistMap = new Map();
                if (targetOrder.pricelist) pricelistMap.set(targetOrder.pricelist.id, targetOrder.pricelist);
                for (const order of eligibleOrders) {
                    if (order.pricelist) pricelistMap.set(order.pricelist.id, order.pricelist);
                }

                const pricelistOptions = [];
                for (const [key, pricelist] of pricelistMap.entries()) {
                    pricelistOptions.push({
                        id: key,
                        item: pricelist,
                        label: pricelist.name,
                    });
                }

                const selectedPricelist = await makeAwaitable(this.env.services.dialog, SelectionPopup, {
                    title: _t("Tarifas diferentes. ¿Cuál aplicar?"),
                    list: pricelistOptions,
                });

                if (selectedPricelist === undefined) {
                    return; // Cancelled
                }

                // Asignar tarifa elegida
                targetOrder.set_pricelist(selectedPricelist);
                // Nota: Odoo se encargará de recalcular si `targetOrder.set_pricelist` dispara el recálculo
                // Si no lo dispara automáticamente en Odoo 18, set_pricelist ya lo hace nativamente.
            }
        }

        // Ejecutar fusión CLONANDO las líneas en lugar de moverlas para evitar fallos de sincronización con el backend
        for (const order of eligibleOrders) {
            const orderlines = [...order.get_orderlines()];
            for (const line of orderlines) {
                this.pos.models["pos.order.line"].create({
                    order_id: targetOrder,
                    product_id: line.product_id,
                    qty: line.qty,
                    price_unit: line.price_unit,
                    discount: line.discount,
                    price_type: line.price_type,
                    price_manually_set: (differentPricelists && mergeBehavior === "keep") ? true : line.price_manually_set,
                    customer_note: line.customer_note,
                    note: line.note,
                    tax_ids: line.tax_ids ? line.tax_ids.map((tax) => ["link", tax]) : [],
                    pack_lot_ids: line.pack_lot_ids ? line.pack_lot_ids.map((pl) => ["create", { lot_name: pl.lot_name }]) : [],
                    attribute_value_ids: line.attribute_value_ids ? line.attribute_value_ids.map((attr) => ["link", attr]) : [],
                });
            }
            
            const paymentlines = [...order.payment_ids];
            for (const payment of paymentlines) {
                this.pos.models["pos.payment"].create({
                    pos_order_id: targetOrder,
                    payment_method_id: payment.payment_method_id,
                    amount: payment.amount,
                    payment_status: payment.payment_status,
                    ticket: payment.ticket,
                    card_type: payment.card_type,
                    transaction_id: payment.transaction_id,
                });
            }

            // Añadir nota para identificar la orden fusionada
            if (!targetOrder.general_note) {
                targetOrder.update({ general_note: `Fusión: [${targetOrder.tracking_number}]` });
            }
            const mergeNote = `[+ ${order.tracking_number}]`;
            targetOrder.update({
                general_note: `${targetOrder.general_note} ${mergeNote}`
            });

            this.pos.removeOrder(order);
        }

        // Limpiar selección y forzar renderizado
        this.state.selectedMergeUuids.clear();
        this.pos.set_order(targetOrder);
    }
});
