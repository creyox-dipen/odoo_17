/** @odoo-module **/

import { parseHTML } from "@web_editor/js/editor/odoo-editor/src/OdooEditor";
import { _t } from "@web/core/l10n/translation";
import { DrawioDialog } from "./drawio_dialog";
import { Wysiwyg } from '@web_editor/js/wysiwyg/wysiwyg';
import { patch } from "@web/core/utils/patch";

/**
 * DrawioPlugin
 *
 * HOW IT WORKS (Odoo 17):
 *  1. Patches Wysiwyg prototype to:
 *     - Inject DrawioPlugin class into editor options plugins.
 *     - Add '/drawio' command to the powerbox.
 *  2. In start(), adds a click listener to the editable zone to catch diagram clicks.
 *  3. Inserts the diagram as a PNG <img>.
 *  4. Stores Draw.io XML in data-drawio-xml on the wrapper <div>.
 *  5. Re-opens Draw.io dialog when the diagram is clicked.
 */
export class DrawioPlugin {
    constructor(options = {}) {
        this.editor = options.editor;
    }

    start() {
        this.editable = this.editor.editable;
        this.editor.addDomListener(this.editable, "click", this.onEditorClick.bind(this));
    }

    openDrawio(existingElement = null) {
        const wysiwyg = window.$(this.editor.editable).data('wysiwyg');
        if (!wysiwyg) {
            console.error("Wysiwyg instance not found on editable element");
            return;
        }

        // Read the stored XML from the data attribute (raw, not encoded)
        const existingXml = existingElement
            ? (existingElement.getAttribute("data-drawio-xml") || "")
            : "";

        wysiwyg.env.services.dialog.add(DrawioDialog, {
            xml: existingXml,
            onSave: (data) => {
                if (existingElement) {
                    this.updateDiagram(existingElement, data.xml, data.png);
                } else {
                    this.insertDiagram(data.xml, data.png);
                }
            },
            onClose: () => {
                this.editor.editable.focus();
            },
        });
    }

    insertDiagram(xml, pngDataUrl) {
        const newNode = parseHTML(this.editor.document, this.buildDiagramHtml(xml, pngDataUrl)).firstElementChild;
        if (newNode) {
            this.editor.execCommand('insert', newNode);
        }
    }

    updateDiagram(element, xml, pngDataUrl) {
        const newNode = parseHTML(this.editor.document, this.buildDiagramHtml(xml, pngDataUrl)).firstElementChild;
        if (newNode) {
            element.replaceWith(newNode);
            this.editor.historyStep();
        }
    }

    /**
     * Builds the diagram HTML.
     */
    buildDiagramHtml(xml, pngDataUrl) {
        return `
            <div class="o_drawio_diagram"
                 data-drawio-xml="${this.escapeAttr(xml)}"
                 contenteditable="false">
                <img class="o_b64_image_to_save"
                     src="${pngDataUrl}"
                     alt="Draw.io Diagram"
                     style="max-width:100%; display:block;" />
            </div>
        `.trim();
    }

    onEditorClick(ev) {
        const diagram = ev.target.closest(".o_drawio_diagram");
        if (diagram) {
            ev.preventDefault();
            ev.stopPropagation();
            this.openDrawio(diagram);
        }
    }

    // Escapes XML so it can be safely placed inside an HTML attribute value
    escapeAttr(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }
}

// Patch Wysiwyg to register DrawioPlugin and Powerbox command
patch(Wysiwyg.prototype, {
    _getEditorOptions() {
        const options = super._getEditorOptions(...arguments);
        options.editorPlugins = options.editorPlugins || [];
        options.editorPlugins.push(DrawioPlugin);
        return options;
    },
    _getPowerboxOptions() {
        const result = super._getPowerboxOptions(...arguments);
        result.commands.push({
            category: _t('Widgets'),
            name: _t('Draw.io Diagram'),
            description: _t('Insert a Draw.io diagram'),
            fontawesome: 'fa-pencil-square-o',
            callback: () => {
                const drawioPlugin = this.odooEditor._plugins.find(p => p instanceof DrawioPlugin);
                if (drawioPlugin) {
                    drawioPlugin.openDrawio();
                }
            },
        });
        return result;
    }
});
