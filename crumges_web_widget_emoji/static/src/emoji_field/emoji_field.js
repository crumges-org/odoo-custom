/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useEmojiPicker } from "@web/core/emoji_picker/emoji_picker";
import { Component, useRef } from "@odoo/owl";

export class EmojiField extends Component {
    static template = "crumges_web_widget_emoji.EmojiField";
    static props = {
        ...standardFieldProps,
        placeholder: { type: String, optional: true },
    };

    setup() {
        this.buttonRef = useRef("emoji-button");
        this.emojiPicker = useEmojiPicker(this.buttonRef, {
            onSelect: (emoji) => {
                this.props.record.update({ [this.props.name]: emoji });
            },
        });
    }

    get formattedValue() {
        return this.props.record.data[this.props.name] || "";
    }
}

registry.category("fields").add("emoji", {
    component: EmojiField,
    supportedTypes: ["char"],
    extractProps: ({ attrs }) => ({
        placeholder: attrs.placeholder,
    }),
});
