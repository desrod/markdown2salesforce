// ==UserScript==
// @name         md2sfweb - Convert pasted Markdown into Salesforce format
// @namespace    md2sfweb
// @description  Web'ify md2sf: Convert raw Markdown to Salesforce-friendly HTML
// @version      2025.11.01.04
// @author       setuid@gmail.com
// @updateURL    https://github.com/desrod/markdown2salesforce/raw/master/md2sfweb.js
// @downloadURL  https://github.com/desrod/markdown2salesforce/raw/master/md2sfweb.js
// @match        https://*.lightning.force.com/*
// @match        https://*.my.salesforce.com/*
// @match        https://*.salesforce-sites.com/*
// @run-at       document-start
// @inject-into  content
// @grant        none
// @require      https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js
// @require      https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js
// ==/UserScript==

(() => {
    "use strict";

    // Make sure this never runs in the top-most Lightning shell
    if (window === window.top) return;

    try {
        const frame_el = window.frameElement;
        if (!frame_el) return; // no frame element—bail
        const rect = frame_el.getBoundingClientRect();
        if (!rect.width || !rect.height || rect.width < 300 || rect.height < 200) return;
    } catch {
        return;
    }

    const get_markdown_it = () =>
        (typeof markdownit !== "undefined" ? markdownit :
            (typeof window !== "undefined" ? window.markdownit : undefined));

    const get_dom_purify = () =>
        (typeof DOMPurify !== "undefined" ? DOMPurify :
            (typeof window !== "undefined" ? window.DOMPurify : undefined));

    const md = get_markdown_it() ? get_markdown_it()({
        html: false,
        linkify: true,
        breaks: true
    }) : null;

    const purify = get_dom_purify() || null;

    if (!md || !purify) {
        const retry = () => {
            if (get_markdown_it() && get_dom_purify()) {
                try {
                    location.reload();
                } catch {
                    /* drop out of the loop */ }
            }
        };
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => setTimeout(retry, 400), {
                once: true
            });
        } else {
            setTimeout(retry, 400);
        }
        return;
    }

    function is_visible(node) {
        if (!node) return false;
        const cs = node.ownerDocument.defaultView.getComputedStyle(node);
        if (cs.visibility === "hidden" || cs.display === "none" || Number(cs.opacity) === 0) return false;
        const r = node.getBoundingClientRect();
        const w = (window.innerWidth || 0),
            h = (window.innerHeight || 0);
        return r.width > 2 && r.height > 2 && r.bottom > 0 && r.right > 0 && r.top < h && r.left < w;
    }

    function find_editable_in_frame() {
        const ae = document.activeElement;
        if (ae && (ae.tagName === "TEXTAREA" || ae.isContentEditable) && is_visible(ae)) return ae;

        const candidate_selectors = [
            '[contenteditable="true"]',
            '.ql-editor[contenteditable="true"]',
            'textarea'
        ];

        for (const sel of candidate_selectors) {
            const list = document.querySelectorAll(sel);
            for (const el of list) {
                if (is_visible(el)) return el;
            }
        }
        return null;
    }

    function get_plain_text(el) {
        if (!el) return "";
        if (el.tagName === "TEXTAREA") return el.value;
        return el.innerText || "";
    }

    function set_html(el, html) {
        if (!el) return;
        if (el.tagName === "TEXTAREA") {
            el.value = html;
            return;
        }
        el.innerHTML = html;
    }

    function convert_markdown_in_frame() {
        const target = find_editable_in_frame();
        if (!target) return false;

        const raw = get_plain_text(target).trim();
        if (!raw) return false;

        const html = purify.sanitize(md.render(raw), {
            // Avert your eyes, this is pretty toothy
            ALLOWED_URI_REGEXP: /^(?:(?:https?):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i
        });

        set_html(target, html);
        return true;
    }

    let host_el = null;

    function mount_once() {
        const target = find_editable_in_frame();

        if (!target) {
            if (host_el?.isConnected) host_el.remove();
            host_el = null;
            return;
        }

        if (host_el) return;

        host_el = document.createElement("div");
        host_el.style.cssText = [
            "all:initial",
            "position:fixed",
            "right:10px",
            "bottom:10px",
            "z-index:200",
            "pointer-events:none"
        ].join(";");

        const shadow = host_el.attachShadow({
            mode: "open"
        });

        // Style the button
        const style_el = document.createElement("style");
        style_el.textContent = `
      :host { all: initial; }
      button {
        all: initial; pointer-events: auto; cursor: pointer;
        font: 12px/1.2 system-ui, Ubuntu, sans-serif;
        padding: 8px 12px; border-radius: 6px; border: 1px solid #0a5;
        background: #2ee593; color: #102; box-shadow: 0 1px 4px rgba(0,0,0,.25);
      }
      button:active { transform: translateY(1px); }
    `;

        const btn_el = document.createElement("button");
        btn_el.textContent = "Convert Markdown";
        btn_el.addEventListener("click", (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            convert_markdown_in_frame();
        }, {
            capture: true
        });

        shadow.append(style_el, btn_el);
        document.documentElement.appendChild(host_el);
    }

    document.addEventListener("focusin", mount_once, true);
    document.addEventListener("blur", mount_once, true);
    new MutationObserver(() => mount_once()).observe(document, {
        childList: true,
        subtree: true
    });

    if (document.readyState === "complete" || document.readyState === "interactive") {
        setTimeout(mount_once, 0);
    } else {
        addEventListener("DOMContentLoaded", () => setTimeout(mount_once, 0), {
            once: true
        });
    }
})();
