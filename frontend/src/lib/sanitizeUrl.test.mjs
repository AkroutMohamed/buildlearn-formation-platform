import { test } from "node:test";
import assert from "node:assert/strict";
import { sanitizeUrl } from "./sanitizeUrl.mjs";

test("allows http and https URLs", () => {
  assert.equal(sanitizeUrl("https://www.gypsobat.com/doc.pdf"), "https://www.gypsobat.com/doc.pdf");
  assert.equal(sanitizeUrl("http://example.com/page"), "http://example.com/page");
  assert.equal(sanitizeUrl("  https://gyproc.in/tech.pdf  "), "https://gyproc.in/tech.pdf");
});

test("rejects non-http(s) schemes", () => {
  assert.equal(sanitizeUrl("javascript:alert(1)"), null);
  assert.equal(sanitizeUrl("data:text/html,<script>alert(1)</script>"), null);
  assert.equal(sanitizeUrl("vbscript:msgbox(1)"), null);
  assert.equal(sanitizeUrl("file:///etc/passwd"), null);
  assert.equal(sanitizeUrl("ftp://example.com/x"), null);
});

test("rejects malformed, empty, or non-string values", () => {
  assert.equal(sanitizeUrl("not a url"), null);
  assert.equal(sanitizeUrl(""), null);
  assert.equal(sanitizeUrl("   "), null);
  assert.equal(sanitizeUrl(null), null);
  assert.equal(sanitizeUrl(undefined), null);
  assert.equal(sanitizeUrl(42), null);
});
