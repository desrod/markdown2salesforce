// ==UserScript==
// @name         md2sfweb - Convert pasted Markdown into Salesforce format
// @namespace    md2sfweb
// @description  Web'ify md2sf: Convert raw Markdown to Salesforce-friendly HTML
// @version      2026.03.17.11
// @author       setuid@gmail.com
// @updateURL    https://raw.githubusercontent.com/desrod/markdown2salesforce/refs/heads/main/md2sfweb.user.js
// @downloadURL  https://raw.githubusercontent.com/desrod/markdown2salesforce/refs/heads/main/md2sfweb.user.js
// @match        https://*.lightning.force.com/*
// @match        https://*.my.salesforce.com/*
// @match        https://*.salesforce-sites.com/*
// @run-at       document-start
// @inject-into  content
// @allFrames    true
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js
// @require      https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js
// ==/UserScript==

(() => {
    "use strict";

    const md = (typeof markdownit !== "undefined") ?
        markdownit({
            html: false,
            linkify: true,
            breaks: true
        }) :
        null;

    const purify = (typeof DOMPurify !== "undefined") ? DOMPurify : null;

    // Belts and braces, if the remote @require can't be loaded for any reason
    if (!md || !purify) {
        console.error("md2sfweb: markdown-it or DOMPurify failed to load");
        return;
    }

    const seen_docs = new WeakSet();
    const seen_editors = new WeakSet();

    function sanitize_rendered_markdown(raw) {
        return purify.sanitize(md.render(raw), {
            ALLOWED_URI_REGEXP: /^(?:(?:https?):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
        });
    }

    function replace_selection_with_html_in_doc(doc, html) {
        doc.execCommand("insertHTML", false, html);
        return true;
    }

    function on_paste(ev, owning_doc) {
        const text = ev.clipboardData?.getData("text/plain") || "";
        if (!text.trim()) return;

        const html = sanitize_rendered_markdown(text);

        // Hook the paste function and convert straight away
        ev.preventDefault();
        ev.stopPropagation();
        ev.stopImmediatePropagation?.();

        replace_selection_with_html_in_doc(owning_doc, html);
    }

    function attach_paste_handler_to_doc(doc) {
        if (!doc || seen_docs.has(doc)) return;
        seen_docs.add(doc);

        doc.addEventListener("paste", (ev) => on_paste(ev, doc), true);
    }

    function try_attach_tiny_mce_frame(iframe) {
        if (!iframe || seen_editors.has(iframe)) return;

        let doc;
        doc = iframe.contentDocument;

        if (!doc) return;

        const is_tiny_mce_like =
            /tox-edit-area|mce-content-body|tinymce/i.test(
                `${iframe.className || ""} ${iframe.id || ""} ${iframe.name || ""}`
            ) ||
            !!doc.querySelector("body.mce-content-body, body[data-id], .mce-content-body");

        if (!is_tiny_mce_like) return;

        seen_editors.add(iframe);

        const attach_now = () => {
            const inner_doc = iframe.contentDocument;
            if (!inner_doc) return;
            attach_paste_handler_to_doc(inner_doc);
        };

        if (doc.readyState === "complete" || doc.readyState === "interactive") {
            attach_now();
        } else {
            iframe.addEventListener("load", attach_now, {
                once: false
            });
            doc.addEventListener("DOMContentLoaded", attach_now, {
                once: true
            });
        }
    }

    function scan_for_editors(root_doc = document) {
        attach_paste_handler_to_doc(root_doc);

        const iframes = root_doc.querySelectorAll("iframe");
        for (const iframe of iframes) {
            try_attach_tiny_mce_frame(iframe);
        }
    }

    function install_observer(root_doc = document) {
        const observer = new MutationObserver(() => {
            scan_for_editors(root_doc);
        });

        observer.observe(root_doc.documentElement || root_doc, {
            childList: true,
            subtree: true
        });
    }

    function install() {
        scan_for_editors(document);
        install_observer(document);

        window.addEventListener("load", () => scan_for_editors(document), {
            once: false
        });
        document.addEventListener("focusin", () => scan_for_editors(document), true);
    }

    install();
})();