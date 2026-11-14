# S03 Verified Ingest Record — Harper et al. (2026), "How Well Do We Know How Others See Us? A Systematic Review of Meta-Accuracy"

## 1. Provenance & Access Metadata
- **Source ID:** S03
- **Authors:** Craig Harper, Melissa Cameron, Lucy Albertella, Odkhishig Ganbold, Campbell Ince, Lars Kooijman, Maria Suetin, Benjamin Kozoolin, Murat Yücel, Kristian Rotaru
- **Publication Year:** 2026 (*Journal of Personality*, DOI: `10.1111/jopy.70075`, PMID: `42083441`, OSF Preregistration: `10.17605/OSF.IO/VMH6W`)
- **Primary Registered URL:** https://onlinelibrary.wiley.com/doi/full/10.1111/jopy.70075
- **Verified Retrieval Endpoint:** Official NCBI Entrez E-utilities XML API (`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=42083441&retmode=xml`, HTTP 200)
- **Retrieved At:** 2026-11-14T13:42:36+08:00
- **Access Scope:** `pubmed_structured_abstract_verified`（Wiley Online Library 對腳本連線回傳 Cloudflare HTTP 403；改由 NCBI PubMed 官方 API 取得完整結構化摘要 `INTRODUCTION / METHOD / RESULTS / CONCLUSION` 並完成逐句核對。依誠實證據原則，將本次驗證錨點限縮至已直接核實之 PubMed 結構化摘要，不宣稱本次腳本直接抓取出 Wiley 內文 §4.5–4.8）
- **License & Redistribution Review:** © 2026 The Author(s). *Journal of Personality* published by Wiley Periodicals LLC. 本文為開放取用（open access），授權為 CC BY（依 OpenAlex 開放取用紀錄；確切版本以 Wiley 文章頁標示為準）。本檔引用之摘要段落依 CC BY 標示出處：Harper, C., Cameron, M., Albertella, L., et al. (2026). *Journal of Personality*. https://doi.org/10.1111/jopy.70075
- **Verified Anchor:** PubMed PMID `42083441` Structured Abstract (`INTRODUCTION`, `METHOD`, `RESULTS`, `CONCLUSION`), DOI `10.1111/jopy.70075`.

## 2. Verbatim Ingested Structured Abstract (PMID: 42083441)

> **INTRODUCTION:** Meta-accuracy, the degree to which individuals accurately infer how others perceive them, is fundamental to social interactions. Yet the field draws on diverse methods across disciplines, and variation in conceptualizations and approaches has not been systematically captured. This review synthesizes the meta-accuracy literature across relational contexts, research foci, attribute domains, and measurement approaches.
>
> **METHOD:** Following PRISMA 2020 guidelines, we searched five databases (January 2025; coverage through December 31, 2024) for peer-reviewed empirical studies assessing meta-accuracy. Two reviewers independently screened 1,336 records and extracted data using a preregistered protocol (OSF: https://doi.org/10.17605/OSF.IO/VMH6W).
>
> **RESULTS:** Ninety-three studies met inclusion criteria: dyadic meta-accuracy (DMA; k = 56; 60.2%), generalized meta-accuracy (GMA; k = 17; 18.3%), and combined approaches (k = 20; 21.5%). DMA and GMA differed in interaction settings and acquaintance levels; research foci diverged across disciplines; most studies targeted personality traits; and measurement approaches varied across studies. The majority of studies were cross-sectional (k = 88; 94.6%) and most samples were tertiary students (k = 60; 64.5%).
>
> **CONCLUSION:** This review systematically maps the conceptual, methodological, and contextual diversity in meta-accuracy research. We propose three priorities: (1) standardizing terminology to distinguish DMA from GMA, (2) transparent reporting of measurement approaches, and (3) developing unified frameworks that bridge disciplinary boundaries to support integrated future research.

## 3. Claim & Wiki Mapping
- **Supported Claims:**
  - `C02`: 定義 meta-accuracy 為「個人準確推論他人如何看待自己的程度（the degree to which individuals accurately infer how others perceive them）」，以他人實際知覺為推論對象。
  - `C03`: 指出推論他人評價屬於後設知覺（metaperception），並區分特定雙人關係中的後設準確度（dyadic meta-accuracy, DMA; `k = 56`，占納入研究 60.2%）與一般化／群體後設準確度（generalized meta-accuracy, GMA; `k = 17`，占 18.3%）；百分比為研究取向分布，不是準確率。
  - `C05`: `RESULTS` 與 `CONCLUSION` 明確指出：DMA 與 GMA 在互動場域（interaction settings）與熟識程度（acquaintance levels）上有所差異，測量方式（measurement approaches）亦各異；且既有 93 篇實證研究中，94.6%（`k = 88`）為橫斷面研究（cross-sectional），64.5%（`k = 60`）樣本為大專學生（tertiary students）。因此不能將單一情境推論為普遍定律。
- **Access note:** Wiley 網頁對程式請求回傳 HTTP 403；本紀錄的核實錨點以 NCBI E-utilities 取得的 PubMed PMID `42083441` 結構化摘要（Results & Conclusion）為準，不宣稱已讀取 Wiley 內文章節。
- **Updated Wiki Pages:** `wiki/sources/S03.md`, `wiki/concepts/他人評價.md`, `wiki/concepts/後設知覺.md`, `wiki/concepts/觀點邊界.md`
