import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState, useRef, onMounted } from "@odoo/owl";

export class WeightAmountPopup extends Component {
    static components = { Dialog };
    static template = "crumges_pos_weighable_weight_or_amount.WeightAmountPopup";
    static props = {
        product: Object,
        price: Number,
        priceFormatted: String,
        currencySymbol: String,
        title: { type: String, optional: true },
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.state = useState({
            weight: "",
            amount: "",
            mode: "amount",
        });
        this.amountInputRef = useRef("amountInput");
        onMounted(() => {
            if (this.amountInputRef.el) {
                this.amountInputRef.el.focus();
            }
        });
    }

    onWeightInput(ev) {
        this.state.mode = "weight";
        const weight = parseFloat(ev.target.value);
        if (!isNaN(weight)) {
            this.state.amount = (weight * this.props.price).toFixed(2);
        } else {
            this.state.amount = "";
        }
    }

    onAmountInput(ev) {
        this.state.mode = "amount";
        const amount = parseFloat(ev.target.value);
        if (!isNaN(amount) && this.props.price > 0) {
            this.state.weight = (amount / this.props.price).toFixed(3);
        } else {
            this.state.weight = "";
        }
    }

    confirm() {
        const weight = parseFloat(this.state.weight);
        if (isNaN(weight) || weight <= 0) {
            return;
        }
        const payload = { weight };
        if (this.state.mode === "amount") {
            const amount = parseFloat(this.state.amount);
            if (!isNaN(amount) && amount > 0) {
                payload.targetAmount = amount;
            }
        }
        this.props.getPayload(payload);
        this.props.close();
    }
}
