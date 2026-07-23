from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


BASE_DIR = Path(r"C:\Users\yamun\AppData\Local\Temp\tradeiq_docx_extract")
OUTPUT_DOCX = Path(r"C:\Users\yamun\1_Projects\SalesTrading\TradeIQ_Technical_Document_Yamuna_Revised.docx")


REPLACEMENTS = [
    "TECHNICAL ARCHITECTURE",
    "& SYSTEM DOCUMENTATION",
    "Table of Contents",
    "1. Platform Overview",
    "SalesTrading is a paper-trading platform for students that simulates investing without using real money.",
    "It helps users register, explore stocks, place BUY/SELL trades, track holdings, submit a thesis, and see scores.",
    "1.1 Core Purpose & Audience",
    "The platform is meant for learners who want a safe way to practice trading and understand how portfolio decisions affect results.",
    "1.2 Deployment Topology",
    "The system has three parts: a Vercel-hosted frontend, a Flask API backend, and a managed MySQL-compatible database such as TiDB Cloud.",
    "1.3 Core Feature Matrix",
    "The main features are authentication, market lookup, simulated trading, portfolio tracking, thesis scoring, and leaderboard display.",
    "2. System Architecture",
    "SalesTrading uses a simple three-layer design: user interface, application logic, and data storage.",
    "2.1 High-Level Architecture Diagram",
    "The frontend sends HTTPS requests to the backend, and the backend reads or writes the database and fetches market data from Yahoo Finance.",
    "Figure 1 -- SalesTrading High-Level Architecture Diagram",
    "2.2 Trade Execution Flow",
    "When a user buys or sells, the backend checks cash and holdings, records the trade, updates the portfolio, and returns the new state.",
    "The diagram shows the full path from button click to database update and refreshed portfolio values.",
    "Figure 2 -- Trade Execution Flow Diagram",
    "2.3 Scoring & Leaderboard Flow",
    "Scores combine portfolio performance, thesis quality, execution quality, and risk metrics.",
    "The backend computes and stores score snapshots so the leaderboard can be shown quickly to users.",
    "Figure 3 -- Scoring & Leaderboard Flow",
    "2.4 Frontend Architecture (Expo / React Native Web)",
    "The frontend is an Expo application that runs on web through React Native Web and is hosted on Vercel.",
    "It keeps the JWT token on the client and attaches it to protected API calls.",
    "2.5 Backend Architecture (Flask + Python)",
    "The backend is a Flask REST API organized into modules for auth, market data, portfolio logic, analytics, and scoring.",
    "It runs with Gunicorn in production and gets configuration from environment variables.",
    "3. Database Architecture",
    "The database is a relational MySQL-compatible store that keeps all persistent user, trade, scoring, and report data.",
    "3.1 Entity Relationship Diagram",
    "The tables are connected mainly through user_id and related score or trade references.",
    "Figure 4 -- Database Entity Relationship Diagram",
    "3.2 Table Reference",
    "users stores account details, login identity, and profile fields.",
    "portfolio_setup stores starting capital and each user's portfolio configuration.",
    "trade_log stores every BUY and SELL action for history and auditing.",
    "holdings stores the current stock positions for each user.",
    "investment_thesis stores the user's written reason for a trade.",
    "thesis_scores stores the system's evaluation of the thesis.",
    "risk_metrics stores volatility and other risk calculations.",
    "weekly_scores stores score snapshots by week.",
    "leaderboard stores the ranked results shown on screen.",
    "reports stores generated report references or downloadable output.",
    "4. API Reference",
    "The backend exposes REST endpoints for login, stock lookup, trading, portfolio views, and analytics.",
    "4.1 Authentication Flow",
    "Users register with email and password, then receive a JWT access token after login.",
    "Figure 5 -- Authentication & JWT Token Flow",
    "4.2 Route Map",
    "/auth handles register and login.",
    "/market handles stock search, price lookup, history, benchmark data, and indices.",
    "/portfolio handles trade execution, holdings, summary, and trade history.",
    "/analytics handles scores, leaderboard, and recalculation jobs.",
    "/health is used for uptime and deployment checks.",
    "4.3 Flask Project Structure",
    "app/auth contains the registration and login routes and supporting logic.",
    "app/market contains market-data fetchers and search endpoints.",
    "app/portfolio contains trade execution and portfolio summary logic.",
    "app/analytics contains leaderboard and scoring endpoints.",
    "app/scoring contains helper functions used by the scoring engine.",
    "5. Security, Deployment, and Scale",
    "Security is based on JWT auth, environment-based secrets, database SSL/TLS, and careful control of browser access.",
    "Passwords should be hashed safely, protected routes should validate JWT, and secrets should never be committed to source control.",
    "In production, CORS should be restricted, rate limiting should be enabled, and the app should use secure environment variables for config.",
    "The recommended cloud setup is Vercel for frontend, Render or AWS for backend, and TiDB Cloud or managed MySQL for the database.",
    "SalesTrading is ready for demos and early users today, and the next roadmap items are caching, background jobs, monitoring, backups, stronger password hashing, and autoscaling for growth.",
]


def set_paragraph_text(paragraph: ET.Element, text: str, ns: dict[str, str]) -> None:
    runs = paragraph.findall("w:r", ns)
    if not runs:
        return

    first_text_node = None
    for run in runs:
        for text_node in run.findall("w:t", ns):
            if first_text_node is None:
                first_text_node = text_node
                first_text_node.text = text
                if text and (text[0].isspace() or text[-1].isspace()):
                    first_text_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            else:
                text_node.text = ""
                text_node.attrib.pop("{http://www.w3.org/XML/1998/namespace}space", None)


def rewrite_docx(base_dir: Path, output_docx: Path) -> None:
    document_xml = base_dir / "word" / "document.xml"
    tree = ET.parse(document_xml)
    root = tree.getroot()
    ns = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    }

    text_paragraphs = []
    for paragraph in root.findall(".//w:body/w:p", ns):
        if "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip():
            text_paragraphs.append(paragraph)

    if len(text_paragraphs) != len(REPLACEMENTS):
        raise RuntimeError(
            f"Paragraph count mismatch: found {len(text_paragraphs)} text paragraphs, "
            f"but have {len(REPLACEMENTS)} replacements."
        )

    for paragraph, replacement in zip(text_paragraphs, REPLACEMENTS):
        set_paragraph_text(paragraph, replacement, ns)

    tree.write(document_xml, encoding="utf-8", xml_declaration=True)

    if output_docx.exists():
        output_docx.unlink()

    with zipfile.ZipFile(output_docx, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in base_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(base_dir))


if __name__ == "__main__":
    rewrite_docx(BASE_DIR, OUTPUT_DOCX)
    print(f"Wrote {OUTPUT_DOCX}")
