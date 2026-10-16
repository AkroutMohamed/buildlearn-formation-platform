/**
 * Source URLs in the chat UI come from scraped external documents and are stored
 * verbatim in the Qdrant payload (product_name, supplier, document_url, source_url,
 * domain, confidence, evidence, ...). Because they originate outside our trust
 * boundary, they must never be rendered as a raw anchor href. A `javascript:`,
 * `data:`, or other non-http(s) URI would be an XSS / open-redirect vector.
 *
 * This helper allows only `http:` and `https:` schemes. Anything else (including
 * malformed values) is rejected and returns `null` so the UI can skip the link.
 */

/** @param {unknown} value */
export function sanitizeUrl(value) {
  if (!value || typeof value !== "string") {
    return null;
  }
  const candidate = value.trim();
  if (!candidate) {
    return null;
  }
  try {
    const parsed = new URL(candidate);
    if (parsed.protocol === "http:" || parsed.protocol === "https:") {
      return parsed.href;
    }
    return null;
  } catch {
    return null;
  }
}
