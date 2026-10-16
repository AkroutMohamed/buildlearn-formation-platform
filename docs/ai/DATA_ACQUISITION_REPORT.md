# BuildLearn AI — Data Acquisition Report

**Generated:** 2026-09-27T14:54:09.118979+00:00
**Pipeline version:** 6.5.0

---

## Summary

| Brand | Products | With Docs | Without Docs | Documents | Accessible | Broken | Duplicates | OCR Required | Indexed Chunks |
|-------|----------|-----------|--------------|-----------|------------|--------|------------|--------------|----------------|
| gypsobat | 1 | 1 | 0 | 2 | 2 | 0 | 0 | 0 | 0 |

## Document Classification Breakdown

| Classification | Count |
|---------------|-------|
| accessible | 1 |
| broken | 0 |
| invalid | 0 |
| duplicate | 0 |
| image_only | 0 |
| text_extractable | 0 |

## Products Without Usable Technical Documents

| Brand | Product | Product URL | Problem | Search Performed | External Candidate | Confidence | Action |
|-------|---------|-------------|---------|------------------|---------------------|------------|--------|
| gypsobat | Test Product | https://gypsobat.fr/p1/ | extractable_text (external_candidate_found) | No | None | N/A | Verify external document matches product before... |

### Successfully Processed Products

No documents have been successfully processed yet.

### Products with Broken Official Documents

No broken official documents found.

### Products with No Documents Found

All products have at least one document candidate.

### Products with External Official Documents

No external official documents found.

### Products with Distributor Documents

No distributor documents found.

### Documents Requiring OCR

No documents required OCR.

### Duplicate Documents

No duplicate documents found.

### External Sources Used

No external sources were used.

---

## Known Limitations

1. EMTOP product pages typically do not include direct PDF technical document downloads on the product page itself.
   Technical documents for EMTOP products are only available in the general catalogue or via external search.
2. SOFAP product pages include PDF download links, but the WordPress REST API content field may be empty.
3. External search results are classified by domain trust level. LOW-confidence candidates are not indexed automatically.
4. OCR processing depends on local tesseract installation. Image-only PDFs without OCR will remain unprocessed.
5. Re-running the pipeline will not create duplicate vectors due to deterministic chunk IDs and SHA-256 deduplication.
6. Documents discovered from Gypsobat documentation pages that reference SOFAP, SIPS, GYPROC, SINIAT, or TACER products
   are attributed to their actual supplier, not to Gypsobat.
