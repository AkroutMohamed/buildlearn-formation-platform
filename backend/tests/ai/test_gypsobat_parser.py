from app.ai.scraping.registry import get_scraper
from app.ai.scraping.sources.gypsobat import (
    PRODUCT_ALIASES,
    _extract_product_from_api,
    _filename_tokens,
    _infer_document_type,
    _infer_manufacturer,
    _match_documents,
    _normalize_name,
    _parse_doc_table,
    _slug_from_url,
)


def test_normalize_name_basic():
    assert _normalize_name("BA13 Hydro") == "ba13 hydro"
    assert _normalize_name("BA13 hydrofuge") == "ba13 hydrofuge"
    assert _normalize_name("FIRELINE 13 FRA") == "fireline 13 fra"
    assert _normalize_name("Lika Pap90") == "lika pap90"


def test_normalize_name_accents_and_punctuation():
    assert _normalize_name("Prégybel WAB") == "pregybel wab"
    assert _normalize_name("BA13-standard") == "ba13 standard"
    assert _normalize_name("HYDRO_13_FRA.pdf") == "hydro 13 fra pdf"


def test_slug_from_url():
    assert _slug_from_url("https://www.gypsobat.com/produit/ba13-hydro/") == "ba13-hydro"
    assert _slug_from_url("https://www.gypsobat.com/produit/ba13-feu-2/") == "ba13-feu-2"
    assert _slug_from_url("") == ""


def test_filename_tokens():
    assert _filename_tokens("https://www.gypsobat.com/wp-content/uploads/fichie_technique/HYDRO%2013%20FRA.pdf") == {
        "hydro",
        "13",
        "fra",
    }
    assert _filename_tokens("") == set()


def test_gypsobat_scraper_registry():
    scraper = get_scraper("gypsobat")
    assert scraper.source == "gypsobat"
    assert hasattr(scraper, "discover_products")
    assert hasattr(scraper, "scrape_product")
    assert hasattr(scraper, "discover_documents")


def test_extract_product_from_api_minimal():
    product_data = {
        "id": 123,
        "title": {"rendered": "BA13 Hydro"},
        "content": {"rendered": "<p>Plaque hydrofuge</p>"},
        "excerpt": {"rendered": "<p>BA13 Hydro pour milieux humides</p>"},
        "link": "https://www.gypsobat.com/produit/ba13-hydro/",
        "product_cat": [1, 2],
    }
    product = _extract_product_from_api(product_data)
    assert product.product_id == "123"
    assert product.name == "BA13 Hydro"
    assert product.manufacturer == "Gypsobat"
    assert product.language == "fr"
    assert product.source_url == "https://www.gypsobat.com/produit/ba13-hydro/"
    assert "ba13 hydro pour milieux humides" in product.description.lower()


def test_extract_product_from_api_missing_fields():
    product_data = {
        "id": 456,
        "title": {"rendered": ""},
        "content": {"rendered": ""},
        "excerpt": {"rendered": ""},
        "link": "",
        "product_cat": [],
    }
    product = _extract_product_from_api(product_data)
    assert product.product_id == "456"
    assert product.name == "Unknown"
    assert product.description is None
    assert product.category is None
    assert product.source_url is None


def test_parse_doc_table_extracts_rows():
    html = """<!DOCTYPE html>
<html>
<body>
<article>
<table>
<tbody>
<tr>
<td><strong>Produit</strong></td>
<td><strong>Désignation</strong></td>
<td><strong>Fournisseur</strong></td>
<td><strong>Télécharger</strong></td>
</tr>
<tr>
<td><img src="photo.jpg" alt="BA13 hydrofuge"></td>
<td>BA13 hydrofuge</td>
<td>GYPROC</td>
<td><a href="https://www.gypsobat.com/wp-content/uploads/fichie_technique/HYDRO%2013%20FRA.pdf" target="_blank">Télécharger fiche technique BA13 hydrofuge</a></td>
</tr>
<tr>
<td><img src="photo2.jpg" alt="BA13 feu"></td>
<td>BA13 feu</td>
<td>GYPROC</td>
<td><a href="https://www.gypsobat.com/wp-content/uploads/fichie_technique/FIRELINE%2013%20FRA.pdf" target="_blank">Télécharger fiche technique BA13 feu</a></td>
</tr>
</tbody>
</table>
</article>
</body>
</html>
"""
    docs = _parse_doc_table("https://www.gypsobat.com/dossiers-techniques/dossier-technique-gyproc/", "technical_dossier", html=html)
    assert len(docs) == 2
    assert docs[0]["product_name"] == "BA13 hydrofuge"
    assert docs[0]["document_url"].endswith(".pdf")
    assert docs[0]["mime_type"] == "application/pdf"
    assert docs[0]["document_type"] == "technical_sheet"
    assert docs[0]["supplier"] == "GYPROC"
    assert docs[0]["source_url"] == "https://www.gypsobat.com/dossiers-techniques/dossier-technique-gyproc/"
    assert docs[1]["product_name"] == "BA13 feu"


def test_parse_doc_table_extracts_multiple_links_per_row():
    html = """<!DOCTYPE html>
<html>
<body>
<article>
<table>
<tbody>
<tr>
<td><strong>Produit</strong></td>
<td><strong>Désignation</strong></td>
<td><strong>Fournisseur</strong></td>
<td><strong>Télécharger</strong></td>
</tr>
<tr>
<td><img src="photo.jpg" alt="BA13 feu"></td>
<td>BA13 feu</td>
<td>GYPROC</td>
<td>
<a href="https://www.gypsobat.com/wp-content/uploads/fichie_technique/FIRELINE%2013%20FRA.pdf" target="_blank">Télécharger fiche technique BA13 feu</a>
<p><a href="https://www.gypsobat.com/wp-content/uploads/fichie_technique/Brandwerende%20systemen%20FR.pdf" target="_blank">Brochure BA13 feu</a></p>
</td>
</tr>
</tbody>
</table>
</article>
</body>
</html>
"""
    docs = _parse_doc_table("https://www.gypsobat.com/dossiers-techniques/dossier-technique-gyproc/", "technical_dossier", html=html)
    assert len(docs) == 2
    assert docs[0]["product_name"] == "BA13 feu"
    assert docs[0]["document_type"] == "technical_sheet"
    assert docs[1]["product_name"] == "BA13 feu"
    assert docs[1]["document_type"] == "brochure"


def test_parse_doc_table_three_columns():
    html = """<!DOCTYPE html>
<html>
<body>
<article>
<table>
<tbody>
<tr>
<td><strong>Désignation</strong></td>
<td><strong>Fournisseur</strong></td>
<td><strong>Télécharger</strong></td>
</tr>
<tr>
<td>Guide de pose SINIAT</td>
<td>SINIAT</td>
<td><a href="https://www.gypsobat.com/wp-content/uploads/fichie_technique/Carnet%20de%20pose%202017-2018.pdf" target="_blank">Télécharger</a></td>
</tr>
</tbody>
</table>
</article>
</body>
</html>
"""
    docs = _parse_doc_table("https://www.gypsobat.com/dossiers-techniques/dossier-technique-siniat/", "technical_dossier", html=html)
    assert len(docs) == 1
    assert docs[0]["product_name"] == "Guide de pose SINIAT"
    assert docs[0]["supplier"] == "SINIAT"
    assert docs[0]["document_type"] == "technical_dossier"


def test_parse_doc_table_fallback_pdf_links():
    html = """<!DOCTYPE html>
<html>
<body>
<article>
<p>Consultez nos documents :</p>
<a href="https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf">fiche technique Lika PAP2</a>
<a href="https://www.gypsobat.com/wp-content/uploads/2024/11/LIKA-FINA.pdf">LIKA-FINA</a>
</article>
</body>
</html>
"""
    docs = _parse_doc_table("https://www.gypsobat.com/fiche-technique-systemes-humides/", "technical_sheet", html=html)
    assert len(docs) == 2
    assert docs[0]["product_name"] == "fiche technique Lika PAP2"
    assert docs[0]["document_url"].endswith(".pdf")
    assert docs[1]["document_url"].endswith("LIKA-FINA.pdf")


def test_infer_document_type():
    assert _infer_document_type("Télécharger fiche technique BA13 feu", "other") == "technical_sheet"
    assert _infer_document_type("Brochure BA13 standard", "other") == "brochure"
    assert _infer_document_type("Présentation Glasroc X", "other") == "presentation"
    assert _infer_document_type("Guide de pose SINIAT", "other") == "installation_guide"
    assert _infer_document_type("Télécharger", "technical_sheet") == "technical_sheet"


def test_match_documents_alias_high_confidence():
    product = type("Product", (), {"name": "BA13 Hydro", "source_url": "https://www.gypsobat.com/produit/ba13-hydro/"})()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://example.com/hydro.pdf"},
        {"product_name": "BA13 feu", "document_url": "https://example.com/feu.pdf"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["product_name"] == "BA13 hydrofuge"
    assert matched[0]["match_confidence"] == "high"


def test_match_documents_slug_medium_confidence():
    product = type("Product", (), {"name": "BA13 Hydro", "source_url": "https://www.gypsobat.com/produit/ba13-hydro/"})()
    docs = [
        {"product_name": "BA13 Hydro Spec", "document_url": "https://example.com/ba13-hydro-technique.pdf"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["match_confidence"] == "medium"


def test_match_documents_filename_medium_confidence():
    product = type("Product", (), {"name": "BA13 Standard", "source_url": "https://www.gypsobat.com/produit/ba13-standard-2/"})()
    docs = [
        {"product_name": "Some doc", "document_url": "https://www.gypsobat.com/wp-content/uploads/fichie_technique/BA13_standard_test.pdf"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["match_confidence"] == "medium"


def test_match_documents_no_false_positives():
    product = type("Product", (), {"name": "BA6 Flex", "source_url": "https://www.gypsobat.com/produit/ba6-flex/"})()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://example.com/hydro.pdf"},
        {"product_name": "BA13 feu", "document_url": "https://example.com/feu.pdf"},
        {"product_name": "Lika PAP2", "document_url": "https://example.com/pap2.pdf"},
    ]
    matched = _match_documents(product, docs)
    assert matched == []


def test_match_documents_no_fallback_on_empty_match():
    product = type("Product", (), {"name": "LIKA PAP 90", "source_url": "https://www.gypsobat.com/produit/lika-pap-90/"})()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://example.com/hydro.pdf"},
        {"product_name": "BA13 feu", "document_url": "https://example.com/feu.pdf"},
    ]
    matched = _match_documents(product, docs)
    assert matched == []


def test_match_documents_rejects_conflicting_brand_supplier():
    product = type("Product", (), {
        "name": "Habito Forte",
        "source_url": "https://www.gypsobat.com/produit/habito-forte/",
        "manufacturer": "GYPROC",
    })()
    docs = [
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/gyproc-habito.pdf", "supplier": "GYPROC"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/tacer-habito.pdf", "supplier": "TACER"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/siniat-habito.pdf", "supplier": "SINIAT"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/gypsobat-habito.pdf", "supplier": "Gypsobat"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/no-supplier.pdf", "supplier": ""},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 3
    assert {m["document_url"] for m in matched} == {
        "https://example.com/gyproc-habito.pdf",
        "https://example.com/gypsobat-habito.pdf",
        "https://example.com/no-supplier.pdf",
    }
    assert all(m["match_confidence"] == "medium" for m in matched)


def test_match_documents_rejects_lika_pap2_for_gypsobat_ba13_hydro():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "Gypsobat",
    })()
    docs = [
        {"product_name": "Lika PAP2", "document_url": "https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf", "supplier": "LIKA"},
        {"product_name": "Lika PAP2", "document_url": "https://www.gypsobat.com/produit/ba13-hydro/fiche_technique_pap2.pdf", "supplier": "LIKA"},
        {"product_name": "BA13 Hydro", "document_url": "https://www.gypsobat.com/wp-content/uploads/fichie_technique/HYDRO%2013%20FRA.pdf", "supplier": "Gypsobat"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["document_url"].endswith("HYDRO%2013%20FRA.pdf")
    assert matched[0]["match_confidence"] == "high"


def test_match_documents_slug_not_matched_via_url():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "Gypsobat",
    })()
    docs = [
        {"product_name": "Lika PAP2", "document_url": "https://www.gypsobat.com/produit/ba13-hydro/fiche_technique_pap2.pdf", "supplier": "LIKA"},
        {"product_name": "Lika PAP2", "document_url": "https://www.gypsobat.com/wp-content/uploads/ba13-hydro/lika-pap2.pdf", "supplier": "LIKA"},
    ]
    matched = _match_documents(product, docs)
    assert matched == []


def test_match_documents_legitimate_gypsobat_document_still_accepted():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "Gypsobat",
    })()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://www.gypsobat.com/wp-content/uploads/fichie_technique/HYDRO%2013%20FRA.pdf", "supplier": "Gypsobat"},
        {"product_name": "BA13 Hydro Spec", "document_url": "https://www.gypsobat.com/produit/ba13-hydro/technique.pdf", "supplier": "Gypsobat"},
        {"product_name": "Some doc", "document_url": "https://www.gypsobat.com/wp-content/uploads/fichie_technique/BA13_hydro_test.pdf", "supplier": "Gypsobat"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 3
    assert matched[0]["match_confidence"] == "high"
    assert matched[1]["match_confidence"] == "medium"
    assert matched[2]["match_confidence"] == "medium"


def test_discover_documents_never_returns_all_on_no_match():
    scraper = get_scraper("gypsobat")
    product = type("Product", (), {"name": "Unknown Product XYZ", "source_url": "https://www.gypsobat.com/produit/unknown-xyz/", "manufacturer": "Gypsobat"})()
    docs = scraper.discover_documents(product)
    assert docs == []


def test_infer_manufacturer_from_slug():
    assert _infer_manufacturer("Gyproc DuraGyp 13 Activ'Air", "gyproc-duragyp-13-activair") == "GYPROC"
    assert _infer_manufacturer("Siniat Pregybel WAB", "siniat-pregybel-wab") == "SINIAT"
    assert _infer_manufacturer("LIKA PAP 90", "lika-pap-90") == "LIKA"
    assert _infer_manufacturer("BA13 Hydro", "ba13-hydro") == "Gypsobat"
    assert _infer_manufacturer("Unknown Product", "unknown-product") == "Gypsobat"
    assert _infer_manufacturer("", "") == "Gypsobat"


def test_match_documents_high_confidence_ignores_supplier():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "Gypsobat",
    })()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://example.com/siniat-ba13-hydro.pdf", "supplier": "SINIAT"},
        {"product_name": "BA13 hydrofuge", "document_url": "https://example.com/gyproc-ba13-hydro.pdf", "supplier": "GYPROC"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 2
    assert matched[0]["match_confidence"] == "high"
    assert matched[1]["match_confidence"] == "high"


def test_match_documents_alias_high_confidence_ignores_supplier():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "Gypsobat",
    })()
    docs = [
        {"product_name": "BA13 Hydrofuge", "document_url": "https://example.com/siniat-ba13-hydro.pdf", "supplier": "SINIAT"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["match_confidence"] == "high"


def test_match_documents_medium_confidence_rejects_conflicting_supplier():
    product = type("Product", (), {
        "name": "Habito Forte",
        "source_url": "https://www.gypsobat.com/produit/habito-forte/",
        "manufacturer": "GYPROC",
    })()
    docs = [
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/tacer-habito.pdf", "supplier": "TACER"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/siniat-habito.pdf", "supplier": "SINIAT"},
    ]
    matched = _match_documents(product, docs)
    assert matched == []


def test_match_documents_medium_confidence_accepts_matching_supplier():
    product = type("Product", (), {
        "name": "Habito Forte",
        "source_url": "https://www.gypsobat.com/produit/habito-forte/",
        "manufacturer": "GYPROC",
    })()
    docs = [
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/gyproc-habito.pdf", "supplier": "GYPROC"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/gypsobat-habito.pdf", "supplier": "Gypsobat"},
        {"product_name": "Habito Forte Spec", "document_url": "https://example.com/no-supplier.pdf", "supplier": ""},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 3
    assert all(m["match_confidence"] == "medium" for m in matched)


def test_match_documents_gyproc_ba13_hydro_with_gyproc_supplier():
    product = type("Product", (), {
        "name": "BA13 Hydro",
        "source_url": "https://www.gypsobat.com/produit/ba13-hydro/",
        "manufacturer": "GYPROC",
    })()
    docs = [
        {"product_name": "BA13 hydrofuge", "document_url": "https://www.gypsobat.com/wp-content/uploads/fichie_technique/HYDRO%2013%20FRA.pdf", "supplier": "GYPROC"},
    ]
    matched = _match_documents(product, docs)
    assert len(matched) == 1
    assert matched[0]["match_confidence"] == "high"
