import re
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOSSARY_PATH = os.path.join(BASE_DIR, 'glossaire_formation_vibe_coding.md')
OUTPUT_PATH = os.path.join(BASE_DIR, 'glossaire_interactive.html')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
SCRATCH_EXPORT_DIR = os.path.join(BASE_DIR, 'scratch', 'glossaire-vibecoding-export')
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# --- 1. CHARGEMENT DU GLOSSAIRE ---
with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

table_lines = [l.strip() for l in lines if l.strip().startswith('|')]
glossary_rows = []
glossary_categories_set = set()
alphabet_set = set()

for line in table_lines[2:]:
    parts = [p.strip() for p in line.split('|')[1:-1]]
    if len(parts) >= 5:
        word_raw, statut, category, definition, ref = parts[0], parts[1], parts[2], parts[3], parts[4]
        word = re.sub(r'\*\*(.*?)\*\*', r'\1', word_raw)
        cat_clean = category.replace('`', '').strip()
        
        mod_match = re.search(r'(M[1-4])', ref)
        mod_code = mod_match.group(1) if mod_match else "Autre"
        
        glossary_categories_set.add(cat_clean)
        
        first_char = word.strip().lstrip('.').lstrip('(')[0].upper()
        if first_char.isalpha():
            alphabet_set.add(first_char)
        
        glossary_rows.append({
            'id': len(glossary_rows) + 1,
            'word': word,
            'statut': statut.replace('`', ''),
            'category': cat_clean,
            'definition': definition,
            'ref': ref,
            'module': mod_code
        })

glossary_categories_list = sorted(list(glossary_categories_set))
alphabet_list = sorted(list(alphabet_set))

# --- 2. BIBLIOTHÈQUE DE PROMPTS VIBE CODING ---
prompts_data = [
    {
        "id": "vercel-ai-studio-arch",
        "title": "Adaptation architecture Vercel & Google AI Studio",
        "description": "Migration vers une architecture serverless compatible Vercel sans casser le fonctionnement dans Google AI Studio.",
        "prompt": "Adapte l'architecture du projet pour un déploiement Vercel sans casser le comportement actuel dans Google AI studio. Créé les fonctions serverless dans /api et les fichiers nécéssaires.",
        "tags": ["Déploiement", "Vercel", "Serverless", "Google AI Studio"]
    },
    {
        "id": "prompt-zero-cadrage",
        "title": "Prompt Zéro : Cadrage initial et architecture",
        "description": "Cadrer le projet avec l'agent avant d'écrire la moindre ligne de code.",
        "prompt": "Agis en tant qu'architecte logiciel et formateur Vibe Coding. Nous allons initialiser un nouveau projet web. Ne génère aucun code pour l'instant. Pose 3 questions ciblées pour valider le périmètre fonctionnel, les outils retenus et la structure des données avant de rédiger le plan d'action.",
        "tags": ["Exemple", "Cadrage", "Méthode"]
    },
    {
        "id": "decoupage-modulaire-clean",
        "title": "Refactoring modulaire d'un composant monolithique",
        "description": "Découper un composant trop volumineux en briques indépendantes.",
        "prompt": "Ce composant dépasse 300 lignes et cumule trop de responsabilités. Analyse sa structure et découpe-le en sous-composants réutilisables dans un sous-dossier dédié, sans modifier aucune fonctionnalité visuelle ni logique métier. Présente d'abord le plan de découpe.",
        "tags": ["Exemple", "Refactoring", "Clean Code", "Frontend"]
    },
    {
        "id": "analyse-resolution-bug",
        "title": "Diagnostic d'erreur console et correction ciblée",
        "description": "Identifier la cause racine d'un bug sans casser les fonctionnalités existantes.",
        "prompt": "Voici le message d'erreur console exact et le contexte du problème : [COLLER L'ERREUR ICI]. Analyse la chaîne d'exécution, explique la cause racine en une phrase simple, puis propose la correction minimale nécessaire sans introduire de régression.",
        "tags": ["Exemple", "Débogage", "Maintenance"]
    },
    {
        "id": "isolation-secrets-env",
        "title": "Migration et isolation des secrets dans .env.local",
        "description": "Sécuriser les clés API et paramètres sensibles hors du code source public.",
        "prompt": "Audit le code pour repérer toutes les clés d'API, secrets ou URLs sensibles codés en dur. Déplace-les dans un fichier .env.local, crée un gabarit .env.example avec des valeurs fictives documentées, et adapte le code pour consommer ces variables de façon sécurisée.",
        "tags": ["Exemple", "Sécurité", "Architecture"]
    },
    {
        "id": "composant-ui-accessible",
        "title": "Composant UI accessible, responsive et mobile-first",
        "description": "Créer un composant autonome avec gestion clavier, ARIA et responsive.",
        "prompt": "Crée un composant d'interface [NOM DU COMPOSANT] en respectant une approche mobile-first stricte. Il doit s'adapter à toutes les largeurs d'écran, respecter les standards d'accessibilité (contraste, focus visible, balises sémantiques) et être entièrement autonome.",
        "tags": ["Exemple", "UI / UX", "Frontend", "Accessibilité"]
    },
    {
        "id": "mock-api-front-first",
        "title": "Mise en place d'un service mock de données",
        "description": "Simuler une API avec latence réseau pour développer l'interface en avance.",
        "prompt": "Nous développons l'interface avant le serveur. Crée un service de données fictives (mock) réaliste avec un délai simulé de 300ms pour imiter une requête réseau réelle. Gère les états de chargement, de succès et un cas d'erreur simulé pour tester la robustesse de l'affichage.",
        "tags": ["Exemple", "Mock", "Architecture", "Frontend"]
    },
    {
        "id": "optimisation-performance-web",
        "title": "Audit et optimisation de la vitesse d'affichage",
        "description": "Fluidifier l'application et supprimer les ralentissements sur mobile.",
        "prompt": "Analyse les performances de cette page web. Repère les goulots d'étranglement (chargements superflus, recalculs de style, taille des assets) et applique les optimisations prioritaires pour rendre l'interface instantanée, même avec un réseau mobile bridé.",
        "tags": ["Exemple", "Performance", "Frontend", "Mobile"]
    },
    {
        "id": "securisation-formulaire-xss",
        "title": "Validation stricte et assainissement d'un formulaire",
        "description": "Empêcher les injections de code et valider les saisies utilisateurs.",
        "prompt": "Audit et renforce la sécurité de ce formulaire. Mets en place une validation stricte côté client (formats attendus, longueur maximale) et assainis les données avant tout affichage ou envoi pour prévenir les attaques de type injection XSS.",
        "tags": ["Exemple", "Sécurité", "Frontend"]
    },
    {
        "id": "export-donnees-client",
        "title": "Fonctionnalité d'export de données (CSV / JSON)",
        "description": "Générer et télécharger un fichier de données directement depuis le navigateur.",
        "prompt": "Ajoute une action permettant à l'utilisateur d'exporter la liste des éléments actuellement filtrés dans un fichier CSV ou JSON téléchargeable en un clic, exécuté directement côté navigateur sans dépendance lourde.",
        "tags": ["Exemple", "Fonctionnalité", "Data"]
    },
    {
        "id": "theme-sombre-persistant",
        "title": "Interrupteur Mode Sombre / Clair avec localStorage",
        "description": "Gestion fluide de thème avec détection système et persistance.",
        "prompt": "Implémente un interrupteur de thème clair / sombre basé sur les variables CSS de la charte. L'état doit être mémorisé dans le localStorage et respecter par défaut la préférence système (prefers-color-scheme) au premier chargement de la page.",
        "tags": ["Exemple", "UI / UX", "Frontend"]
    }
]

prompt_tags_set = set()
for p in prompts_data:
    for t in p["tags"]:
        prompt_tags_set.add(t)

prompt_tags_list = sorted(list(prompt_tags_set))

terms_json = json.dumps(glossary_rows, ensure_ascii=False)
prompts_json = json.dumps(prompts_data, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
  <title>Le Glossaire & Bibliothèque de Prompts Vibe Coding</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cousine:wght@400;700&family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --color-brand-purple: #6634D9;
      --color-brand-fig: #18093B;
      --color-brand-sunny: #FFFF77;
      --color-brand-pink: #FFB2B2;
      --color-pink-20: #FCF1F0;
      --color-bg-light: #F8FAFC;
      --color-card-bg: #FFFFFF;
      --color-border: #E2E8F0;
      --color-border-dark: #CBD5E1;
      --color-text-dark: #18093B;
      --color-text-muted: #64748B;
      --font-main: 'Basic Sans Alt', 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
      --font-code: 'Cousine', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    body {{
      font-family: var(--font-main);
      background-color: var(--color-bg-light);
      color: var(--color-text-dark);
      line-height: 1.5;
      padding: 0;
      margin: 0;
    }}

    .app-viewport {{
      width: 100%;
      max-width: 960px;
      margin: 0 auto;
      padding: 1rem 1rem 3rem 1rem;
    }}

    @media (min-width: 640px) {{
      .app-viewport {{
        padding: 2rem 1.5rem 4rem 1.5rem;
      }}
    }}

    /* Header */
    header {{
      background: var(--color-brand-fig);
      color: #FFFFFF;
      padding: 1.5rem 1.25rem;
      border: 3px solid var(--color-brand-fig);
      box-shadow: 4px 4px 0px var(--color-brand-purple);
      margin-bottom: 1rem;
    }}

    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.5rem;
    }}

    .brand-badge {{
      background: var(--color-brand-sunny);
      color: var(--color-brand-fig);
      font-weight: 900;
      font-size: 0.75rem;
      padding: 0.25rem 0.6rem;
      border: 1px solid var(--color-brand-fig);
      text-transform: uppercase;
    }}

    h1 {{
      font-size: clamp(1.4rem, 4.5vw, 2.1rem);
      font-weight: 900;
      line-height: 1.15;
      text-transform: uppercase;
      letter-spacing: -0.02em;
    }}

    .header-desc {{
      margin-top: 0.4rem;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--color-brand-sunny);
    }}

    /* Navigation Tabs */
    .tab-nav {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1.25rem;
      border-bottom: 3px solid var(--color-brand-fig);
      padding-bottom: 0.5rem;
      overflow-x: auto;
    }}

    .tab-btn {{
      background: #FFFFFF;
      color: var(--color-brand-fig);
      border: 2px solid var(--color-brand-fig);
      padding: 0.65rem 1.1rem;
      font-family: var(--font-main);
      font-weight: 800;
      font-size: 0.92rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      transition: all 0.15s ease;
      white-space: nowrap;
      box-shadow: 2px 2px 0px var(--color-brand-fig);
    }}

    .tab-btn:hover {{
      background: var(--color-pink-20);
    }}

    .tab-btn.active {{
      background: var(--color-brand-purple);
      color: #FFFFFF;
      border-color: var(--color-brand-fig);
      box-shadow: 3px 3px 0px var(--color-brand-fig);
    }}

    .tab-badge {{
      background: var(--color-brand-fig);
      color: var(--color-brand-sunny);
      padding: 0.1rem 0.4rem;
      font-size: 0.75rem;
      font-weight: 900;
    }}

    .tab-btn.active .tab-badge {{
      background: var(--color-brand-sunny);
      color: var(--color-brand-fig);
    }}

    /* Shared Search & Filter Boxes */
    .search-filter-section {{
      background: #FFFFFF;
      border: 2px solid var(--color-brand-fig);
      box-shadow: 4px 4px 0px var(--color-brand-fig);
      padding: 1.25rem;
      margin-bottom: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .search-box {{
      position: relative;
      width: 100%;
    }}

    .search-input {{
      width: 100%;
      padding: 0.85rem 1rem 0.85rem 2.75rem;
      font-family: var(--font-main);
      font-size: 1rem;
      font-weight: 600;
      color: var(--color-brand-fig);
      background: #FFFFFF;
      border: 2px solid var(--color-brand-fig);
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--color-brand-purple);
      box-shadow: 0 0 0 3px rgba(102, 52, 217, 0.2);
    }}

    .search-icon {{
      position: absolute;
      left: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.1rem;
      color: var(--color-brand-fig);
      pointer-events: none;
    }}

    .clear-btn {{
      position: absolute;
      right: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      background: #E2E8F0;
      border: none;
      color: #475569;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      cursor: pointer;
      font-weight: bold;
      display: none;
      align-items: center;
      justify-content: center;
      font-size: 0.8rem;
    }}

    .toggle-filters-btn {{
      background: #F1F5F9;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-brand-fig);
      padding: 0.6rem 1rem;
      font-family: var(--font-main);
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      transition: background 0.15s ease;
    }}

    .toggle-filters-btn:hover {{
      background: #E2E8F0;
    }}

    .toggle-icon {{
      font-size: 0.75rem;
      transition: transform 0.2s ease;
    }}

    .toggle-icon.open {{
      transform: rotate(180deg);
    }}

    .filters-panel {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      padding-top: 0.5rem;
      border-top: 1px dashed var(--color-border);
    }}

    .filters-panel.collapsed {{
      display: none;
    }}

    .filter-group {{
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }}

    .filter-label {{
      font-size: 0.8rem;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--color-brand-fig);
      letter-spacing: 0.03em;
    }}

    .pills-row {{
      display: flex;
      gap: 0.4rem;
      overflow-x: auto;
      padding-bottom: 0.4rem;
      scrollbar-width: thin;
      -webkit-overflow-scrolling: touch;
    }}

    .pills-row::-webkit-scrollbar {{
      height: 4px;
    }}
    .pills-row::-webkit-scrollbar-thumb {{
      background: var(--color-brand-purple);
    }}

    .pill-btn {{
      background: #F1F5F9;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-brand-fig);
      padding: 0.3rem 0.75rem;
      font-family: var(--font-main);
      font-size: 0.82rem;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
      flex-shrink: 0;
    }}

    .pill-btn:hover {{
      background: #E2E8F0;
    }}

    .pill-btn.active {{
      background: var(--color-brand-fig);
      color: var(--color-brand-sunny);
    }}

    .pill-btn.tag-exemple {{
      border-color: #be123c;
    }}
    .pill-btn.tag-exemple.active {{
      background: #be123c;
      color: #FFFFFF;
    }}

    .alpha-bar {{
      display: flex;
      gap: 0.3rem;
      overflow-x: auto;
      padding-bottom: 0.3rem;
    }}

    .alpha-btn {{
      min-width: 32px;
      height: 32px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: #F1F5F9;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-brand-fig);
      font-family: var(--font-main);
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      flex-shrink: 0;
    }}

    .alpha-btn.active {{
      background: var(--color-brand-purple);
      color: #FFFFFF;
      border-color: var(--color-brand-fig);
    }}

    .results-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding: 0 0.25rem;
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--color-text-muted);
    }}

    .counter-tag {{
      background: var(--color-brand-purple);
      color: #FFFFFF;
      padding: 0.15rem 0.55rem;
      font-weight: 800;
    }}

    /* Tab Content Wrappers */
    .tab-view {{
      display: none;
    }}
    .tab-view.active {{
      display: block;
    }}

    /* Cards - Glossaire */
    .cards-container {{
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
    }}

    .card-item {{
      background: var(--color-card-bg);
      border: 1px solid var(--color-border);
      border-left: 4px solid var(--color-brand-purple);
      padding: 1.1rem 1.25rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}

    .card-item:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.08);
      border-color: var(--color-brand-fig);
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .term-title {{
      font-size: 1.2rem;
      font-weight: 800;
      color: var(--color-brand-fig);
      letter-spacing: -0.01em;
      word-break: break-word;
    }}

    .type-badge {{
      background: var(--color-brand-fig);
      color: var(--color-brand-sunny);
      font-weight: 800;
      font-size: 0.72rem;
      padding: 0.2rem 0.6rem;
      border: 1px solid var(--color-brand-fig);
      text-transform: uppercase;
      white-space: nowrap;
    }}

    .term-def {{
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--color-brand-fig);
      line-height: 1.5;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-top: 0.25rem;
      padding-top: 0.5rem;
      border-top: 1px dashed var(--color-border);
      font-size: 0.8rem;
      font-weight: 700;
      flex-wrap: wrap;
    }}

    .ref-code {{
      background: var(--color-brand-purple);
      color: #FFFFFF;
      padding: 0.15rem 0.5rem;
      font-size: 0.75rem;
      font-weight: 900;
    }}

    .ref-title {{
      color: var(--color-text-muted);
      font-weight: 600;
    }}

    /* Cards - Prompts Library (Bordures subtiles & fond gris très clair) */
    .prompt-card {{
      background: var(--color-card-bg);
      border: 1px solid var(--color-border);
      border-left: 4px solid var(--color-brand-purple);
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      padding: 1.2rem 1.35rem;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }}

    .prompt-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.08);
      border-color: var(--color-brand-fig);
    }}

    .prompt-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .prompt-title {{
      font-size: 1.18rem;
      font-weight: 800;
      color: var(--color-brand-fig);
      letter-spacing: -0.01em;
      line-height: 1.3;
    }}

    .prompt-desc {{
      font-size: 0.92rem;
      color: var(--color-text-muted);
      font-weight: 500;
      line-height: 1.45;
    }}

    .prompt-tags {{
      display: flex;
      gap: 0.35rem;
      flex-wrap: wrap;
    }}

    .prompt-tag-badge {{
      background: #F1F5F9;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-border-dark);
      font-size: 0.72rem;
      font-weight: 800;
      padding: 0.15rem 0.5rem;
      text-transform: uppercase;
      cursor: pointer;
      transition: background 0.15s ease, border-color 0.15s ease;
    }}

    .prompt-tag-badge:hover {{
      background: #E2E8F0;
      border-color: var(--color-brand-fig);
    }}

    .prompt-tag-badge.badge-example {{
      background: #ffe4e6;
      color: #be123c;
      border-color: #fda4af;
    }}

    /* Zone de texte du prompt : FOND GRIS TRÈS CLAIR (pas rose) & Police Cousine */
    .prompt-box-wrapper {{
      position: relative;
    }}

    .prompt-text-block {{
      font-family: var(--font-code);
      font-size: 0.93rem;
      line-height: 1.55;
      background: #F8FAFC; /* Gris très clair neutre */
      border: 1px solid var(--color-border);
      color: #18093B;
      padding: 0.95rem 1.1rem;
      white-space: pre-wrap;
      word-break: break-word;
      user-select: text;
    }}

    .prompt-actions {{
      display: flex;
      gap: 0.6rem;
      flex-wrap: wrap;
      align-items: center;
    }}

    .btn-copy-prompt {{
      background: var(--color-brand-fig);
      color: var(--color-brand-sunny);
      border: 1px solid var(--color-brand-fig);
      padding: 0.5rem 0.95rem;
      font-family: var(--font-main);
      font-size: 0.82rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      text-transform: uppercase;
      transition: all 0.15s ease;
    }}

    .btn-copy-prompt:hover {{
      background: #251052;
      transform: translateY(-1px);
    }}

    .btn-copy-prompt.copied {{
      background: #15803d;
      color: #FFFFFF;
      border-color: #15803d;
    }}

    .btn-share-prompt {{
      background: #FFFFFF;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-border-dark);
      padding: 0.5rem 0.85rem;
      font-family: var(--font-main);
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      text-transform: uppercase;
      transition: background 0.15s ease, border-color 0.15s ease;
    }}

    .btn-share-prompt:hover {{
      background: #F1F5F9;
      border-color: var(--color-brand-fig);
    }}

    .btn-share-prompt.copied {{
      background: #dcfce7;
      color: #166534;
      border-color: #86efac;
    }}

    /* Navigation Mode Isolé : Simple bouton de retour (plus de bandeau jaune) */
    .isolated-nav {{
      display: none;
      margin-bottom: 1rem;
    }}

    .isolated-nav.active {{
      display: flex;
      align-items: center;
    }}

    .btn-back-all {{
      background: #FFFFFF;
      color: var(--color-brand-fig);
      border: 1px solid var(--color-border-dark);
      padding: 0.55rem 1rem;
      font-family: var(--font-main);
      font-size: 0.85rem;
      font-weight: 800;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: background 0.15s ease, border-color 0.15s ease;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .btn-back-all:hover {{
      background: #F1F5F9;
      border-color: var(--color-brand-fig);
    }}

    /* Surlignage de recherche */
    mark {{
      background: var(--color-brand-sunny);
      color: var(--color-brand-fig);
      padding: 0;
      margin: 0;
      font-weight: inherit;
      font-style: inherit;
    }}

    .empty-state {{
      background: #FFFFFF;
      border: 2px dashed var(--color-border);
      padding: 3rem 1.5rem;
      text-align: center;
      display: none;
    }}

    .empty-title {{
      font-size: 1.2rem;
      font-weight: 800;
      color: var(--color-brand-fig);
      margin-bottom: 0.5rem;
    }}

    .empty-desc {{
      font-size: 0.9rem;
      color: var(--color-text-muted);
      margin-bottom: 1rem;
    }}

    .reset-btn {{
      background: var(--color-brand-purple);
      color: var(--color-brand-sunny);
      border: 2px solid var(--color-brand-fig);
      padding: 0.6rem 1.2rem;
      font-family: var(--font-main);
      font-weight: 800;
      font-size: 0.85rem;
      cursor: pointer;
      text-transform: uppercase;
    }}

    /* Toast notification */
    .toast-msg {{
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      background: var(--color-brand-fig);
      color: var(--color-brand-sunny);
      border: 2px solid var(--color-brand-sunny);
      padding: 0.75rem 1.25rem;
      font-weight: 800;
      font-size: 0.88rem;
      box-shadow: 4px 4px 0px var(--color-brand-purple);
      z-index: 1000;
      transform: translateY(150%);
      transition: transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      pointer-events: none;
    }}

    .toast-msg.show {{
      transform: translateY(0);
    }}
  </style>
</head>
<body>

  <div class="app-viewport">
    
    <!-- En-tête -->
    <header>
      <div class="header-top">
        <span class="brand-badge">Formation Vibe Coding</span>
        <span style="font-weight: 800; font-size: 0.85rem;">Espace Apprenant • v2.2</span>
      </div>
      <h1 id="mainTitle">Le Glossaire Vibe Coding</h1>
      <div class="header-desc" id="mainSubtitle">57 notions clés et boîte à outils pour le Vibe Coding</div>
    </header>

    <!-- Navigation entre Onglets -->
    <nav class="tab-nav">
      <button class="tab-btn active" id="tabBtnGlossary" data-target="glossaryView">
        <span>📖 Glossaire</span>
        <span class="tab-badge">{len(glossary_rows)}</span>
      </button>
      <button class="tab-btn" id="tabBtnPrompts" data-target="promptsView">
        <span>⚡ Bibliothèque de Prompts</span>
        <span class="tab-badge">{len(prompts_data)}</span>
      </button>
    </nav>

    <!-- Navigation retour Mode Isolé (Simple bouton, plus de carte jaune) -->
    <div class="isolated-nav" id="isolatedNav">
      <button class="btn-back-all" id="btnBackAll">← Retour à tous les prompts ({len(prompts_data)})</button>
    </div>

    <!-- ============================================== -->
    <!-- ONGLET 1 : GLOSSAIRE                           -->
    <!-- ============================================== -->
    <div class="tab-view active" id="glossaryView">
      
      <div class="search-filter-section">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="glossarySearchInput" class="search-input" placeholder="Rechercher par 1ère lettre (ex: B) ou mot-clé..." autocomplete="off">
          <button id="glossaryClearBtn" class="clear-btn" title="Effacer">✕</button>
        </div>

        <button id="toggleGlossaryFiltersBtn" class="toggle-filters-btn" aria-expanded="false">
          <span>🎛️ Index A-Z & Filtres Avancés</span>
          <span id="toggleGlossaryIcon" class="toggle-icon">▼</span>
        </button>

        <div id="glossaryFiltersPanel" class="filters-panel collapsed">
          <div class="filter-group">
            <div class="filter-label">Index Alphabétique :</div>
            <div class="alpha-bar" id="alphaBar">
              <button class="alpha-btn active" data-letter="ALL">TOUS</button>
"""

for letter in alphabet_list:
    html_content += f'              <button class="alpha-btn" data-letter="{letter}">{letter}</button>\n'

html_content += f"""            </div>
          </div>

          <div class="filter-group">
            <div class="filter-label">Filtrer par Module :</div>
            <div class="pills-row" id="modulePills">
              <button class="pill-btn active" data-module="ALL">Tous les modules</button>
              <button class="pill-btn" data-module="M1">Module 1 (Bases)</button>
              <button class="pill-btn" data-module="M2">Module 2 (Web)</button>
              <button class="pill-btn" data-module="M3">Module 3 (Mobile)</button>
              <button class="pill-btn" data-module="M4">Module 4 (Agents)</button>
            </div>
          </div>

          <div class="filter-group">
            <div class="filter-label">Filtrer par Thématique :</div>
            <div class="pills-row" id="categoryPills">
              <button class="pill-btn active" data-cat="ALL">Toutes les thématiques</button>
"""

for cat in glossary_categories_list:
    html_content += f'              <button class="pill-btn" data-cat="{cat}">{cat}</button>\n'

html_content += f"""            </div>
          </div>
        </div>
      </div>

      <div class="results-bar">
        <span>Résultats du glossaire :</span>
        <span class="counter-tag" id="glossaryCounterTag">{len(glossary_rows)} termes</span>
      </div>

      <div class="cards-container" id="glossaryCardsContainer"></div>

      <div class="empty-state" id="glossaryEmptyState">
        <div class="empty-title">Aucun terme ne correspond à la recherche</div>
        <div class="empty-desc">Essayez avec d'autres mots-clés ou réinitialisez les filtres.</div>
        <button class="reset-btn" id="glossaryResetBtn">Réinitialiser les filtres</button>
      </div>

    </div>

    <!-- ============================================== -->
    <!-- ONGLET 2 : BIBLIOTHÈQUE DE PROMPTS             -->
    <!-- ============================================== -->
    <div class="tab-view" id="promptsView">
      
      <div class="search-filter-section" id="promptsFilterSection">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="promptsSearchInput" class="search-input" placeholder="Rechercher dans les prompts (mot-clé, Vercel, refactoring...)" autocomplete="off">
          <button id="promptsClearBtn" class="clear-btn" title="Effacer">✕</button>
        </div>

        <div class="filter-group">
          <div class="filter-label">Filtrer par Tag / Sujet :</div>
          <div class="pills-row" id="promptTagPills">
            <button class="pill-btn active" data-tag="ALL">Tous ({len(prompts_data)})</button>
"""

for tag in prompt_tags_list:
    is_ex = 'tag-exemple' if tag == 'Exemple' else ''
    html_content += f'            <button class="pill-btn {is_ex}" data-tag="{tag}">{tag}</button>\n'

html_content += f"""          </div>
        </div>
      </div>

      <div class="results-bar">
        <span>Prompts disponibles :</span>
        <span class="counter-tag" id="promptsCounterTag">{len(prompts_data)} prompts</span>
      </div>

      <div class="cards-container" id="promptsCardsContainer"></div>

      <div class="empty-state" id="promptsEmptyState">
        <div class="empty-title">Aucun prompt ne correspond à vos critères</div>
        <div class="empty-desc">Modifiez votre recherche ou réinitialisez les filtres.</div>
        <button class="reset-btn" id="promptsResetBtn">Afficher tous les prompts</button>
      </div>

    </div>

  </div>

  <div class="toast-msg" id="toastMsg">Notification</div>

  <script>
    const GLOSSARY_DATA = {terms_json};
    const PROMPTS_DATA = {prompts_json};

    // État global
    let currentTab = 'glossary';
    let isolatedPromptId = null;

    // État Glossaire
    let activeModule = 'ALL';
    let activeCategory = 'ALL';
    let activeLetter = 'ALL';
    let glossaryQuery = '';

    // État Prompts
    let activePromptTag = 'ALL';
    let promptsQuery = '';

    // Éléments Onglets
    const tabBtnGlossary = document.getElementById('tabBtnGlossary');
    const tabBtnPrompts = document.getElementById('tabBtnPrompts');
    const glossaryView = document.getElementById('glossaryView');
    const promptsView = document.getElementById('promptsView');
    const mainTitle = document.getElementById('mainTitle');
    const mainSubtitle = document.getElementById('mainSubtitle');
    const isolatedNav = document.getElementById('isolatedNav');
    const btnBackAll = document.getElementById('btnBackAll');
    const toastMsg = document.getElementById('toastMsg');

    // Éléments Glossaire
    const glossarySearchInput = document.getElementById('glossarySearchInput');
    const glossaryClearBtn = document.getElementById('glossaryClearBtn');
    const glossaryCardsContainer = document.getElementById('glossaryCardsContainer');
    const glossaryCounterTag = document.getElementById('glossaryCounterTag');
    const glossaryEmptyState = document.getElementById('glossaryEmptyState');
    const glossaryResetBtn = document.getElementById('glossaryResetBtn');
    const toggleGlossaryFiltersBtn = document.getElementById('toggleGlossaryFiltersBtn');
    const glossaryFiltersPanel = document.getElementById('glossaryFiltersPanel');
    const toggleGlossaryIcon = document.getElementById('toggleGlossaryIcon');

    // Éléments Prompts
    const promptsSearchInput = document.getElementById('promptsSearchInput');
    const promptsClearBtn = document.getElementById('promptsClearBtn');
    const promptsFilterSection = document.getElementById('promptsFilterSection');
    const promptsCardsContainer = document.getElementById('promptsCardsContainer');
    const promptsCounterTag = document.getElementById('promptsCounterTag');
    const promptsEmptyState = document.getElementById('promptsEmptyState');
    const promptsResetBtn = document.getElementById('promptsResetBtn');
    const promptTagPills = document.getElementById('promptTagPills');

    // --- GESTION DES NOTIFICATIONS TOAST ---
    function showToast(text) {{
      toastMsg.textContent = text;
      toastMsg.classList.add('show');
      setTimeout(() => {{
        toastMsg.classList.remove('show');
      }}, 2200);
    }}

    // --- NAVIGATION ONGLETS ---
    function switchTab(tabName, updateUrl = true) {{
      currentTab = tabName;
      if (tabName === 'prompts') {{
        tabBtnGlossary.classList.remove('active');
        tabBtnPrompts.classList.add('active');
        glossaryView.classList.remove('active');
        promptsView.classList.add('active');
        mainTitle.textContent = "Bibliothèque de Prompts";
        mainSubtitle.textContent = "Prompts Vibe Coding prêts à copier pour vos sessions de code";
      }} else {{
        tabBtnPrompts.classList.remove('active');
        tabBtnGlossary.classList.add('active');
        promptsView.classList.remove('active');
        glossaryView.classList.add('active');
        mainTitle.textContent = "Le Glossaire Vibe Coding";
        mainSubtitle.textContent = "57 notions clés et définitions pour le Vibe Coding";
        isolatedPromptId = null;
        isolatedNav.classList.remove('active');
        promptsFilterSection.style.display = 'flex';
      }}

      if (updateUrl && !isolatedPromptId) {{
        const url = new URL(window.location);
        url.searchParams.set('tab', tabName);
        url.searchParams.delete('prompt');
        history.replaceState(null, '', url.toString());
      }}
    }}

    tabBtnGlossary.addEventListener('click', () => switchTab('glossary'));
    tabBtnPrompts.addEventListener('click', () => switchTab('prompts'));

    // --- RENDU GLOSSAIRE ---
    function matchWordStart(fullText, query) {{
      if (!query) return true;
      const q = escapeRegExp(query.trim().toLowerCase());
      const regex = new RegExp(`(?:^|[^a-zA-Z0-9à-ÿÀ-Ÿ])${{q}}`, 'i');
      return regex.test(fullText);
    }}

    function renderGlossary() {{
      const query = glossaryQuery.trim().toLowerCase();
      
      const filtered = GLOSSARY_DATA.filter(item => {{
        const matchMod = (activeModule === 'ALL' || item.module === activeModule);
        const matchCat = (activeCategory === 'ALL' || item.category === activeCategory);
        
        let matchAlpha = true;
        if (activeLetter !== 'ALL') {{
          const cleanWord = item.word.replace(/^[^a-zA-Z0-9]+/, '');
          matchAlpha = cleanWord.toUpperCase().startsWith(activeLetter);
        }}

        const textToSearch = item.word + ' ' + item.category + ' ' + item.definition + ' ' + item.ref;
        const matchSearch = matchWordStart(textToSearch, query);

        return matchMod && matchCat && matchAlpha && matchSearch;
      }});

      glossaryCounterTag.textContent = `${{filtered.length}} terme${{filtered.length > 1 ? 's' : ''}}`;

      if (filtered.length === 0) {{
        glossaryCardsContainer.style.display = 'none';
        glossaryEmptyState.style.display = 'block';
        return;
      }}

      glossaryCardsContainer.style.display = 'flex';
      glossaryEmptyState.style.display = 'none';

      glossaryCardsContainer.innerHTML = filtered.map(item => {{
        let wordHtml = escapeHtml(item.word);
        let defHtml = escapeHtml(item.definition);

        if (query !== '') {{
          const qEscaped = escapeRegExp(query);
          const regex = new RegExp(`(^|[^a-zA-Z0-9à-ÿÀ-Ÿ])(${{qEscaped}})`, 'gi');
          wordHtml = wordHtml.replace(regex, '$1<mark>$2</mark>');
          defHtml = defHtml.replace(regex, '$1<mark>$2</mark>');
        }}

        const refParts = item.ref.split('—');
        const code = refParts[0] ? refParts[0].trim() : item.ref;
        const title = refParts[1] ? refParts[1].trim() : '';

        return `
          <div class="card-item">
            <div class="card-header">
              <div class="term-title">${{wordHtml}}</div>
              <span class="type-badge">${{escapeHtml(item.category)}}</span>
            </div>
            <div class="term-def">${{defHtml}}</div>
            <div class="card-footer">
              <span class="ref-code">${{escapeHtml(code)}}</span>
              ${{title ? `<span class="ref-title">${{escapeHtml(title)}}</span>` : ''}}
            </div>
          </div>
        `;
      }}).join('');
    }}

    // --- RENDU BIBLIOTHÈQUE DE PROMPTS ---
    function renderPrompts() {{
      const query = promptsQuery.trim().toLowerCase();

      // Cas Vue Isolée par URL
      if (isolatedPromptId) {{
        const singlePrompt = PROMPTS_DATA.find(p => p.id === isolatedPromptId);
        if (singlePrompt) {{
          promptsFilterSection.style.display = 'none';
          isolatedNav.classList.add('active');
          promptsCounterTag.textContent = '1 prompt isolé';
          promptsCardsContainer.style.display = 'flex';
          promptsEmptyState.style.display = 'none';

          promptsCardsContainer.innerHTML = renderSinglePromptCard(singlePrompt, true);
          return;
        }}
      }}

      promptsFilterSection.style.display = 'flex';
      isolatedNav.classList.remove('active');

      const filtered = PROMPTS_DATA.filter(item => {{
        const matchTag = (activePromptTag === 'ALL' || item.tags.includes(activePromptTag));
        
        const fullText = (item.title + ' ' + item.description + ' ' + item.prompt + ' ' + item.tags.join(' ')).toLowerCase();
        const matchSearch = (query === '' || fullText.includes(query));

        return matchTag && matchSearch;
      }});

      promptsCounterTag.textContent = `${{filtered.length}} prompt${{filtered.length > 1 ? 's' : ''}}`;

      if (filtered.length === 0) {{
        promptsCardsContainer.style.display = 'none';
        promptsEmptyState.style.display = 'block';
        return;
      }}

      promptsCardsContainer.style.display = 'flex';
      promptsEmptyState.style.display = 'none';

      promptsCardsContainer.innerHTML = filtered.map(item => renderSinglePromptCard(item, false, query)).join('');
    }}

    function renderSinglePromptCard(item, isIsolated = false, query = '') {{
      let titleHtml = escapeHtml(item.title);
      let descHtml = escapeHtml(item.description);
      let promptHtml = escapeHtml(item.prompt);

      if (query !== '') {{
        const qEscaped = escapeRegExp(query);
        const regex = new RegExp(`(${{qEscaped}})`, 'gi');
        titleHtml = titleHtml.replace(regex, '<mark>$1</mark>');
        descHtml = descHtml.replace(regex, '<mark>$1</mark>');
        promptHtml = promptHtml.replace(regex, '<mark>$1</mark>');
      }}

      const tagsHtml = item.tags.map(t => {{
        const isEx = (t === 'Exemple');
        return `<span class="prompt-tag-badge ${{isEx ? 'badge-example' : ''}}" data-tag="${{escapeHtml(t)}}">${{escapeHtml(t)}}</span>`;
      }}).join('');

      return `
        <div class="prompt-card" id="prompt-${{item.id}}">
          <div class="prompt-header">
            <div class="prompt-title">${{titleHtml}}</div>
            <div class="prompt-tags">${{tagsHtml}}</div>
          </div>
          <div class="prompt-desc">${{descHtml}}</div>
          <div class="prompt-box-wrapper">
            <pre class="prompt-text-block" id="text-${{item.id}}"><code>${{promptHtml}}</code></pre>
          </div>
          <div class="prompt-actions">
            <button class="btn-copy-prompt" onclick="copyPromptText('${{item.id}}', this)">
              <span>📋 Copier le prompt</span>
            </button>
            <button class="btn-share-prompt" onclick="sharePrompt('${{item.id}}', this)">
              <span>🔗 Partager ce prompt</span>
            </button>
          </div>
        </div>
      `;
    }}

    // --- ACTIONS PROMPT : COPIER ET PARTAGER ---
    function copyPromptText(promptId, btn) {{
      const item = PROMPTS_DATA.find(p => p.id === promptId);
      if (!item) return;

      navigator.clipboard.writeText(item.prompt).then(() => {{
        btn.classList.add('copied');
        btn.innerHTML = '<span>✅ Copié dans le presse-papier !</span>';
        showToast('Prompt copié avec succès !');
        setTimeout(() => {{
          btn.classList.remove('copied');
          btn.innerHTML = '<span>📋 Copier le prompt</span>';
        }}, 2500);
      }}).catch(() => {{
        showToast('Erreur lors de la copie');
      }});
    }}

    function sharePrompt(promptId, btn) {{
      const shareUrl = `${{window.location.origin}}${{window.location.pathname}}?prompt=${{encodeURIComponent(promptId)}}`;
      navigator.clipboard.writeText(shareUrl).then(() => {{
        btn.classList.add('copied');
        btn.innerHTML = '<span>🔗 Lien copié !</span>';
        showToast('Lien isolé copié dans le presse-papier !');
        setTimeout(() => {{
          btn.classList.remove('copied');
          btn.innerHTML = '<span>🔗 Partager ce prompt</span>';
        }}, 2500);
      }}).catch(() => {{
        showToast('Erreur lors de la copie du lien');
      }});
    }}

    btnBackAll.addEventListener('click', () => {{
      isolatedPromptId = null;
      const url = new URL(window.location);
      url.searchParams.delete('prompt');
      url.searchParams.set('tab', 'prompts');
      history.replaceState(null, '', url.toString());
      renderPrompts();
    }});

    // Clic sur un tag de carte pour filtrer
    promptsCardsContainer.addEventListener('click', (e) => {{
      const tagBadge = e.target.closest('.prompt-tag-badge');
      if (!tagBadge) return;
      const tag = tagBadge.getAttribute('data-tag');
      if (!tag) return;
      
      activePromptTag = tag;
      document.querySelectorAll('#promptTagPills .pill-btn').forEach(b => {{
        b.classList.toggle('active', b.getAttribute('data-tag') === tag);
      }});
      renderPrompts();
    }});

    // Filtres tags Prompts
    promptTagPills.addEventListener('click', (e) => {{
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      document.querySelectorAll('#promptTagPills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activePromptTag = btn.getAttribute('data-tag');
      renderPrompts();
    }});

    // Recherche Prompts
    promptsSearchInput.addEventListener('input', (e) => {{
      promptsQuery = e.target.value;
      promptsClearBtn.style.display = promptsQuery ? 'flex' : 'none';
      renderPrompts();
    }});

    promptsClearBtn.addEventListener('click', () => {{
      promptsSearchInput.value = '';
      promptsQuery = '';
      promptsClearBtn.style.display = 'none';
      promptsSearchInput.focus();
      renderPrompts();
    }});

    promptsResetBtn.addEventListener('click', () => {{
      promptsQuery = '';
      promptsSearchInput.value = '';
      promptsClearBtn.style.display = 'none';
      activePromptTag = 'ALL';
      isolatedPromptId = null;
      document.querySelectorAll('#promptTagPills .pill-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('#promptTagPills .pill-btn[data-tag="ALL"]').classList.add('active');
      
      const url = new URL(window.location);
      url.searchParams.delete('prompt');
      url.searchParams.set('tab', 'prompts');
      history.replaceState(null, '', url.toString());
      
      renderPrompts();
    }});

    // --- RECHERCHE ET FILTRES GLOSSAIRE ---
    toggleGlossaryFiltersBtn.addEventListener('click', () => {{
      const isCollapsed = glossaryFiltersPanel.classList.contains('collapsed');
      if (isCollapsed) {{
        glossaryFiltersPanel.classList.remove('collapsed');
        toggleGlossaryIcon.classList.add('open');
        toggleGlossaryFiltersBtn.setAttribute('aria-expanded', 'true');
      }} else {{
        glossaryFiltersPanel.classList.add('collapsed');
        toggleGlossaryIcon.classList.remove('open');
        toggleGlossaryFiltersBtn.setAttribute('aria-expanded', 'false');
      }}
    }});

    glossarySearchInput.addEventListener('input', (e) => {{
      glossaryQuery = e.target.value;
      glossaryClearBtn.style.display = glossaryQuery ? 'flex' : 'none';
      renderGlossary();
    }});

    glossaryClearBtn.addEventListener('click', () => {{
      glossarySearchInput.value = '';
      glossaryQuery = '';
      glossaryClearBtn.style.display = 'none';
      glossarySearchInput.focus();
      renderGlossary();
    }});

    document.getElementById('alphaBar').addEventListener('click', (e) => {{
      const btn = e.target.closest('.alpha-btn');
      if (!btn) return;
      document.querySelectorAll('.alpha-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeLetter = btn.getAttribute('data-letter');
      renderGlossary();
    }});

    document.getElementById('modulePills').addEventListener('click', (e) => {{
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      document.querySelectorAll('#modulePills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeModule = btn.getAttribute('data-module');
      renderGlossary();
    }});

    document.getElementById('categoryPills').addEventListener('click', (e) => {{
      const btn = e.target.closest('.pill-btn');
      if (!btn) return;
      document.querySelectorAll('#categoryPills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-cat');
      renderGlossary();
    }});

    glossaryResetBtn.addEventListener('click', () => {{
      glossaryQuery = '';
      glossarySearchInput.value = '';
      glossaryClearBtn.style.display = 'none';
      activeModule = 'ALL';
      activeCategory = 'ALL';
      activeLetter = 'ALL';
      
      document.querySelectorAll('#glossaryView .pill-btn, #glossaryView .alpha-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('#modulePills .pill-btn[data-module="ALL"]').classList.add('active');
      document.querySelector('#categoryPills .pill-btn[data-cat="ALL"]').classList.add('active');
      document.querySelector('#alphaBar .alpha-btn[data-letter="ALL"]').classList.add('active');
      
      renderGlossary();
    }});

    // Utilitaires
    function escapeRegExp(string) {{
      return string.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    }}

    function escapeHtml(str) {{
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }}

    // --- INITIALISATION AU CHARGEMENT (Gestion de l'URL) ---
    function init() {{
      const params = new URLSearchParams(window.location.search);
      const promptParam = params.get('prompt');
      const tabParam = params.get('tab');

      if (promptParam) {{
        isolatedPromptId = promptParam;
        switchTab('prompts', false);
      }} else if (tabParam === 'prompts') {{
        switchTab('prompts', false);
      }} else {{
        switchTab('glossary', false);
      }}

      renderGlossary();
      renderPrompts();
    }}

    init();
  </script>

</body>
</html>
"""

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)

with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)

# Copier également vers le dossier d'export git et le dossier scripts
if os.path.exists(SCRATCH_EXPORT_DIR):
    with open(os.path.join(SCRATCH_EXPORT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    with open(os.path.join(SCRATCH_EXPORT_DIR, 'glossaire_interactive.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

if os.path.exists(SCRIPTS_DIR):
    with open(os.path.join(SCRIPTS_DIR, 'build_interactive_web_glossary.py'), 'w', encoding='utf-8') as f:
        f.write(html_content)

print("Application interactive mise à jour avec succès (bordures subtiles, fond gris très clair, bouton retour isolé direct).")
