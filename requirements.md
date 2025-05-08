cat requirements.md
# Requirements: ESG & Impact Pre-Investment Analyzer

## 1. Aperçu du Projet

### 1.1 Description
L'ESG & Impact Pre-Investment Analyzer est une application destinée aux équipes d'investissement pour générer automatiquement des rapports ESG (Environnement, Social, Gouvernance), Impact et Climat en phase pré-investissement. L'application utilise des modèles de langage avancés (LLM) pour analyser une description d'entreprise et produire un rapport structuré conforme aux référentiels standards du secteur. 

Le projet est conçu pour un développement solo efficace avec Cursor et une mise en production rapide, avec une architecture permettant des améliorations incrémentales après le déploiement initial.

### 1.2 Objectifs Principaux
- Automatiser la génération de rapports ESG/Impact/Climat pour les non-experts
- Standardiser l'analyse ESG/Impact selon des référentiels reconnus
- Réduire le temps de préparation des analyses préliminaires
- Garantir une couverture complète des dimensions ESG et Impact
- Faciliter la prise de décision d'investissement grâce à des rapports structurés
- Assurer l'alignement des analyses avec la stratégie du fonds

### 1.3 Utilisateurs Cibles
- Équipes d'investissement non spécialisées en ESG
- Analystes ESG/Impact
- Directeurs d'investissement
- Comités d'investissement
- Gestionnaires de fonds

## 2. Fonctionnalités Requises

### 2.1 Saisie des Données (Input)
- **Informations Basiques de l'Entreprise**:
  - Nom de l'entreprise
  - Pays d'opération principale
  - Secteur d'activité (liste prédéfinie avec option "Autre")
  - Description libre de l'activité (business model, clients, marché, etc.)
  - Taille approximative (CA, effectifs) - optionnel

- **Paramètres d'Analyse**:
  - Sélection des référentiels à appliquer (multiple choix)
  - Exclusion optionnelle de certains standards
  - Niveau de détail du rapport (standard/approfondi)

### 2.2 Traitement et Analyse
- Analyse du texte descriptif pour extraction des aspects ESG pertinents
- Application automatique des référentiels sélectionnés
- Identification des risques ESG par pilier (E, S, G)
- Analyse climatique (vulnérabilités, résilience, empreinte carbone estimée)
- Analyse d'impact (opportunités, cibles, KPI potentiels)
- Évaluation de l'alignement avec la stratégie du fonds

### 2.3 Génération du Rapport (Output)
- **Format du Rapport**:
  - Document structuré en sections thématiques
  - Version Markdown pour affichage web
  - Export au format DOCX, PDF ou PPT simplifié

- **Contenu Requis**:
  - Synthèse exécutive (1 page max)
  - Analyse des risques ESG détaillée par pilier E, S, G
  - Analyse climat complète
  - Analyse d'impact
  - Évaluation de l'alignement avec la stratégie du fonds (score ESG standardisé)
  - Tableau de recommandations priorisées par impact et difficulté de mise en œuvre
  - Clauses ESG suggérées pour pacte d'actionnaires
  - Extraction automatique de 3-5 KPIs pertinents à suivre pour l'entreprise
  - Questionnaire de due diligence ciblé basé sur l'analyse initiale
  - Référentiels utilisés et méthodologie d'analyse
  - Visualisations simples (matrice de risques, radar ESG) générées automatiquement

### 2.4 Personnalisation
- Intégration des référentiels au choix:
  - IFC Performance Standards
  - 2X Challenge Criteria
  - Principes directeurs de l'OCDE pour les PME
  - Normes internes du fonds
- Possibilité d'ajout futur de référentiels supplémentaires
- Paramétrage des pondérations par thématique ESG
- Adaptation du rapport au secteur d'activité
- Mode prévisualisation rapide pour générer une synthèse en 1 page avant le rapport complet
- Affichage par onglets pour une navigation claire entre sections E, S, G et Impact

## 3. Architecture Technique

### 3.1 Vue d'Ensemble
L'architecture sera modulaire, extensible et basée sur un workflow de traitement en pipeline:

[Frontend] → [Gestionnaire d'Entrées] → [Assembleur de Prompts] → [Service LLM] → [Post-Traitement] → [Formatage] → [Frontend]

### 3.2 Composants Principaux

#### 3.2.1 Frontend (Interface Utilisateur)
- **Technologie**: Streamlit
- **Fonctionnalités**:
  - Formulaire de saisie des informations d'entreprise
  - Sélecteurs de standards ESG à activer
  - Paramètres de personnalisation du rapport
  - Bouton de génération de rapport
  - Affichage du rapport généré avec navigation par onglets (E, S, G, Impact, Synthèse)
  - Export aux formats DOCX, PDF et PPT simplifié
  - Historique des rapports générés (local)
  - Barre de progression visuelle pendant la génération
  - Sauvegarde automatique des drafts et des paramètres utilisateur
  - Système simple de feedback utilisateur (boutons "utile"/"pas utile" avec commentaire optionnel)

#### 3.2.2 Backend
- **Processeur d'Entrées**:
  - Validation et nettoyage des données
  - Enrichissement contextuel basé sur le secteur
  - Extraction des informations clés pour le prompt

- **Gestionnaire de Prompts**:
  - Chargement dynamique des templates de prompts
  - Intégration des référentiels sélectionnés
  - Assemblage des sous-prompts thématiques
  - Système de contexte partagé entre les prompts

- **Service LLM**:
  - Interface unifiée pour multiple providers LLM
  - Gestion des clés API et authentification
  - Optimisation des requêtes et gestion de tokens
  - Mécanisme de fallback automatique entre modèles LLM en cas d'erreur
  - Modes d'utilisation économique/standard/premium selon budget tokens
  - Cache des réponses pour économiser les appels API
  - Prompt guard-rails pour éviter les hallucinations sur aspects critiques
  - Format de sortie intermédiaire structuré (JSON/YAML) pour faciliter le post-traitement
  - Gestion d'erreurs robuste avec logging complet

- **Post-Traitement**:
  - Extraction structurée des sections du rapport
  - Validation de la conformité aux référentiels
  - Standardisation des recommandations
  - Génération d'un score d'alignement avec la stratégie

- **Formatage**:
  - Conversion en markdown structuré
  - Génération de documents DOCX/PDF
  - Templates personnalisables

### 3.3 Structure du Projet

esg-impact-analyzer/
├── app.py                     # Point d'entrée principal
├── config/
│   ├── config.yaml            # Configuration globale
│   ├── llm_config.yaml        # Configuration des modèles LLM
│   ├── sectors.yaml           # Configuration spécifique par secteur
│   └── modes.yaml             # Configuration des modes (économique/standard/premium)
├── inputs/
│   ├── validators.py          # Validation des entrées utilisateur
│   ├── processors.py          # Traitement des descriptions
│   ├── enrichers.py           # Enrichissement contextuel
│   └── extractors.py          # Extraction de données structurées
├── prompts/
│   ├── master_prompt.py       # Assembleur de prompts
│   ├── templates/
│   │   ├── 00_synthese_exec.txt
│   │   ├── 01_esg.txt
│   │   ├── 02_climat.txt
│   │   ├── 03_impact.txt
│   │   ├── 04_alignement_strategie.txt
│   │   └── 05_recommandations.txt
│   ├── context.py             # Gestionnaire de contexte partagé
│   ├── sector_prompts/        # Prompts spécifiques par secteur
│   │   ├── agribusiness.py
│   │   ├── manufacturing.py
│   │   ├── services.py
│   │   └── healthcare.py
│   └── examples/              # Exemples pour guider le format
│       ├── synthese_examples.py
│       ├── esg_examples.py
│       └── recommendations_examples.py
├── standards/
│   ├── loader.py              # Chargeur de référentiels
│   ├── indexer.py             # Indexation sémantique des critères
│   ├── selector.py            # Sélection intelligente des critères pertinents
│   ├── ifc/                   # Documents IFC Performance Standards
│   │   ├── IFC-standards.md   # Document complet
│   │   └── IFC-criteria.yaml  # Critères structurés
│   ├── 2x/                    # Documents 2X Challenge
│   │   ├── 2X-criteria.md     # Document complet
│   │   └── 2X-criteria.yaml   # Critères structurés
│   └── internal/              # Normes internes fonds
│       ├── IPAE3-esg-impact.md   # Document de politique
│       └── IPAE3-esg-impact.yaml # Critères structurés
├── engine/
│   ├── llm_service.py         # Interface LLM unifiée
│   ├── providers/             # Adaptateurs pour différents LLM
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── groq.py
│   │   └── openrouter.py
│   ├── cache.py               # Système de cache
│   ├── response_parser.py     # Parseur de réponses
│   ├── token_optimizer.py     # Optimisation de l'utilisation des tokens
│   └── fallback_manager.py    # Gestion des fallbacks entre modèles
├── formatters/
│   ├── markdown.py            # Formatage Markdown
│   ├── docx.py                # Export DOCX
│   ├── pdf.py                 # Export PDF
│   ├── ppt.py                 # Export PPT simplifié
│   └── templates/             # Templates de documents
│       ├── docx_template.docx
│       └── ppt_template.pptx
├── visualization/
│   ├── radar_chart.py         # Graphique radar ESG
│   ├── risk_matrix.py         # Matrice de risques
│   ├── impact_charts.py       # Visualisations d'impact
│   └── kpi_dashboard.py       # Tableaux de bord KPI
├── utils/
│   ├── logger.py              # Système de logging
│   ├── metrics.py             # Collecte de métriques
│   ├── semantic_search.py     # Recherche sémantique
│   └── draft_manager.py       # Gestion des brouillons
├── api/
│   ├── routes.py              # Définition des routes API
│   └── schemas.py             # Schémas de données API
├── ui/
│   ├── components/            # Composants UI réutilisables
│   │   ├── progress_bar.py
│   │   ├── tabbed_display.py
│   │   └── feedback_buttons.py
│   ├── pages/                 # Pages Streamlit
│   │   ├── home.py
│   │   ├── report.py
│   │   ├── history.py
│   │   └── settings.py
│   └── styles.py              # Styles UI
└── tests/                     # Tests unitaires et d'intégration
├── test_prompts.py
├── test_standards.py
├── test_llm.py
└── test_formatters.py

### 3.4 Flux de Données
1. L'utilisateur saisit les informations d'entreprise et les paramètres d'analyse
2. Le processeur d'entrées valide et prépare les données
3. Le gestionnaire de prompts assemble le prompt maître avec les sous-prompts thématiques
4. Le service LLM envoie la requête au provider sélectionné
5. Le post-traitement structure et valide la réponse
6. Le formateur génère le rapport dans le format souhaité
7. L'interface affiche le rapport et permet l'export

## 4. Dépendances Techniques

### 4.1 Environnement d'Exécution
- Python 3.9+
- Environnement virtuel (virtualenv ou conda)
- Compatibilité multi-plateforme (Windows, MacOS, Linux)

### 4.2 Librairies Principales
- **Frontend**:
  - Streamlit >= 1.18.0
  - Streamlit-extras (pour composants UI avancés)
  - Streamlit-aggrid (pour tableaux interactifs)
  - st-annotated-text (pour visualisation des critères ESG identifiés)
  - streamlit-tabs (pour navigation par onglets E, S, G, Impact)

- **Traitement des Prompts**:
  - Jinja2 (pour templates de prompts)
  - PyYAML (pour configuration et parsing des référentiels)
  - json/yaml (pour formats structurés intermédiaires)
  - tiktoken (pour comptage et optimisation des tokens)

- **Interface LLM**:
  - openai >= 1.1.0 (compatible avec assistants et JSON mode)
  - anthropic >= 0.7.0 (support de Claude 3)
  - litellm >= 1.0.0 (pour interface unifiée et fallback)
  - groq (pour modèles rapides et économiques)
  - instructor (pour améliorer la structuration des sorties)

- **NLP et Traitement Sémantique**:
  - spacy (pour analyse sémantique des descriptions)
  - sentence-transformers (pour embeddings et recherche sémantique)
  - keybert (pour extraction de mots-clés)
  - langchain >= 0.1.0 (pour chaînes de traitement)
  - langchain_community (pour outils complémentaires)

- **Formatage**:
  - python-docx >= 0.8.11
  - markdown2 >= 2.4.8
  - reportlab >= 4.0.4 (pour PDF)
  - python-pptx >= 0.6.21 (pour présentations simplifiées)
  - camelot-py (pour extraction de données tabulaires des PDFs)

- **Visualisation**:
  - matplotlib >= 3.7.2 (pour graphiques basiques)
  - seaborn >= 0.12.2 (pour visualisations statistiques)
  - plotly >= 5.15.0 (pour graphiques interactifs)
  - radar (pour graphiques radar ESG)

- **Utilitaires**:
  - pydantic >= 2.4.0 (pour validation des modèles de données)
  - python-dotenv >= 1.0.0 (pour gestion des variables d'environnement)
  - tenacity >= 8.2.2 (pour retry et gestion robuste des erreurs)
  - fastapi (pour API backend si nécessaire)
  - pytest (pour tests unitaires)
  - loguru (pour logging avancé)
  - rich (pour affichage console amélioré lors du développement)

### 4.3 Services Externes
- API LLM (via un des fournisseurs suivants):
  - OpenAI (GPT-4o)
  - Anthropic (Claude)
  - DeepSeek
  - Groq
  - OpenRouter (comme agrégateur)

### 4.4 Référentiels Locaux
- **Formats Requis**:
  - Documents PDF structurés
  - Fichiers Markdown annotés
  - Fichiers YAML de configuration

- **Standards à Inclure**:
  - IFC Performance Standards (versions complètes)
  - 2X Challenge Criteria (documentation complète)
  - Principes directeurs OCDE pour les PME
  - Modèles de normes internes du fonds

## 5. Conception Modulaire et Scalabilité

### 5.1 Principes de Conception
- **Modularité**: Chaque composant doit être indépendant et remplaçable
- **Extensibilité**: Faciliter l'ajout de nouveaux référentiels et fonctionnalités
- **Observabilité**: Logging détaillé pour suivre le processus de génération
- **Testabilité**: Composants isolés pour tests unitaires faciles
- **Configuration**: Externalisation des paramètres pour ajustement sans code

### 5.2 Stratégies de Scaling
- **Scaling Horizontal**:
  - Architecture sans état pour permettre la distribution
  - Cache partagé pour réduire les appels API redondants
  - Séparation claire entre UI et traitement

- **Scaling Vertical**:
  - Optimisation des prompts pour réduire la taille des requêtes
  - Parallélisation des analyses par section
  - Mise en cache intelligente des résultats intermédiaires

### 5.3 Adaptabilité
- **Ajout de Nouveaux Référentiels**:
  - Interface standardisée pour l'intégration de référentiels
  - Structure de dossier dédiée pour chaque référentiel
  - Métadonnées pour la compatibilité sectorielle

- **Évolution des Modèles LLM**:
  - Abstraction du service LLM pour faciliter les changements
  - Configuration paramétrable des modèles sans modification du code
  - Tests automatisés pour valider les changements de modèles

## 6. Gestion des Standards et Référentiels

### 6.1 Organisation des Référentiels
Tous les référentiels sont disponibles localement dans le dépôt GitHub et sont déjà organisés selon la structure suivante:

- **Structure de Dossier Actuelle**:

standards/
├── 2x/
│   ├── 2X-criteria.md        # Document complet des critères 2X Challenge
│   └── 2X-criteria.yaml      # Métadonnées structurées des critères 2X
├── ifc/
│   ├── IFC-standards.md      # Document complet des 8 standards IFC
│   └── IFC-criteria.yaml     # Métadonnées structurées des critères IFC
└── internal/
├── IPAE3-esg-impact.md   # Politique ESG et Impact du fonds IPAE3
└── IPAE3-esg-impact.yaml # Métadonnées structurées de la politique IPAE3

- **Format des Fichiers**:
- Documents Markdown (`.md`) pour le contenu textuel complet de chaque référentiel
- Métadonnées YAML (`.yaml`) pour les informations structurées incluant:
  - ID unique de chaque critère/exigence
  - Titre du critère
  - Pilier concerné (Environnement, Social, Gouvernance)
  - Section du document source
  - Mots-clés associés
  - Niveau de priorité (critique, élevée, moyenne)
  - Note explicative résumant le critère

### 6.2 Exploitation Intelligente des Référentiels

#### Indexation et Structuration
- Utilisation d'un système d'indexation par ID unique pour chaque critère des référentiels (ex: `IFC-PS1-007`, `2X-Leadership-01`, `IPAE3-ESG-017`)
- Métadonnées enrichies permettant de filtrer les critères par:
- Pilier ESG (Environnement, Social, Gouvernance)
- Niveau de priorité (critique, élevée, moyenne)
- Mots-clés thématiques
- Secteur d'activité (ajouté lors de l'analyse contextuelle)

#### Chargement et Traitement
- Chargement dynamique des référentiels selon la sélection de l'utilisateur
- Extraction intelligente des sections pertinentes selon:
- Le secteur d'activité de l'entreprise analysée
- Les mots-clés identifiés dans la description de l'entreprise
- La pertinence par rapport aux enjeux ESG prioritaires
- Système de scoring pour identifier les critères les plus pertinents:
1. Critères de priorité "critique" correspondant au secteur → score élevé
2. Critères avec correspondance de mots-clés dans la description → score moyen
3. Critères de base applicables à tous les secteurs → score standard
- Cache des références fréquemment utilisées pour optimiser les temps de chargement

#### Transformation en Éléments de Prompts
- Conversion automatique des critères sélectionnés en sections structurées pour les prompts LLM
- Contextualisation des critères génériques en fonction du secteur et de la taille de l'entreprise
- Génération dynamique d'exemples concrets adaptés au secteur pour chaque critère retenu
- Formulation de questions spécifiques basées sur les critères pour guider l'analyse du LLM

### 6.3 Mise à Jour des Référentiels
- Versionnement sémantique des fichiers de référentiels (v1.0.0, v1.1.0, etc.)
- Journal des modifications (changelog) pour documenter les évolutions des standards
- Tests automatisés pour valider la structure et l'intégrité des fichiers après modification
- Procédure de mise à jour documentée:
1. Copie de sauvegarde des fichiers actuels
2. Modification des fichiers Markdown et YAML correspondants
3. Exécution des tests d'intégrité et de cohérence
4. Mise à jour du numéro de version et du changelog
5. Validation et déploiement

### 6.4 Extensibilité pour Référentiels Additionnels
Le système est conçu pour faciliter l'ajout ultérieur de nouveaux référentiels:
- OCDE PME
- Principes de la finance responsable
- Objectifs de développement durable (ODD/SDGs)
- Taxonomie européenne
- Standards sectoriels spécifiques

Chaque nouveau référentiel suivra le même modèle avec un fichier Markdown pour le contenu complet et un fichier YAML pour les métadonnées structurées.

## 7. Structure des Prompts

### 7.1 Architecture des Prompts
- **Prompt Maître**: 
- Instructions générales et contexte global
- Rôle spécifique assigné au LLM (expert ESG & Impact spécialisé dans l'analyse pré-investissement)
- Format de sortie attendu avec structure précise
- Contexte sur la stratégie d'investissement IPAE3

- **Sous-Prompts Thématiques**:
- `00_synthese_exec.txt`: Instructions pour la synthèse exécutive (1 page max)
- `01_esg.txt`: Directives pour l'analyse ESG par pilier (E, S, G) avec critères prioritaires des référentiels sélectionnés
- `02_climat.txt`: Analyse spécifique climat avec focus sur adaptation, mitigation et découplage croissance/émissions
- `03_impact.txt`: Analyse d'impact et KPIs avec alignement SDGs et évaluation de la contribution aux objectifs IPAE3
- `04_alignement_strategie.txt`: Évaluation de l'alignement avec la stratégie du fonds et critères 2X Challenge
- `05_recommandations.txt`: Génération de recommandations priorisées par impact/faisabilité, incluant suggestions pour pacte d'actionnaires et DD

- **Contexte Partagé**:
- Description de l'entreprise avec informations clés structurées (pays, secteur, taille, activité)
- Secteur et spécificités avec benchmarks sectoriels pertinents
- Stratégie d'impact du fonds IPAE3 extraite du référentiel interne
- Référentiels sélectionnés avec critères prioritaires extraits dynamiquement des fichiers YAML
- Définition des livrables attendus et format standardisé

### 7.2 Techniques de Prompt Engineering
- **Instructions claires et structurées par étape**:
- Décomposition du raisonnement en phases séquentielles
- Objectifs spécifiques pour chaque section du rapport
- Consignes précises sur le niveau de détail attendu

- **Contextualisation intelligente**:
- Injection des critères ESG les plus pertinents extraits des référentiels (IFC, 2X, IPAE3)
- Adaptation des exigences au secteur et à la taille de l'entreprise analysée
- Fourniture de benchmarks sectoriels spécifiques quand disponibles

- **Structuration avancée du prompt**:
- Structure multi-niveaux avec instructions générales suivies d'instructions spécifiques
- Séparation claire entre le contexte, les instructions et les exemples
- Balisage XML pour identifier les différentes sections (<context>, <instructions>, <examples>)

- **Mécanismes anti-hallucination**:
- Demande explicite de raisonnement étape par étape (chain of thought)
- Instruction de s'en tenir aux faits fournis et d'indiquer clairement les zones d'incertitude
- Guard-rails intégrés signalant les domaines à risque d'hallucination

- **Prompting dynamique**:
- Bibliothèque de prompts précalibrés par secteur (industrie, services, agro, santé, etc.)
- Ajustement automatique des instructions selon le niveau de détail des informations fournies
- Adaptation aux différents modes d'utilisation (économique/standard/premium)

- **Output structuré et contrôlé**:
- Format de sortie clairement défini avec des sections standardisées
- Structure JSON/YAML intermédiaire pour les éléments nécessitant un post-traitement (scores, KPIs)
- Templates d'exemples illustrant le format attendu pour chaque section

- **Techniques d'élicitation d'expertise**:
- Questions spécifiques pour guider l'analyse critique des points ESG sensibles
- Demande d'analyse de pertinence des critères pour l'entreprise spécifique
- Sollicitation d'identification proactive des risques non mentionnés dans l'input

### 7.3 Optimisation des Prompts
- Calibrage pour équilibrer concision et précision
- Test des variations pour maximiser la qualité
- Mécanisme de feedback pour amélioration continue
- Adaptation sectorielle des prompts

## 8. Extensions Futures et Cas d'Usage

### 8.1 Extensions Planifiées
- **Base de Données des Rapports**:
- Stockage et indexation des rapports générés
- Recherche par critères (secteur, pays, risques)
- Comparaison entre entreprises similaires

- **Suivi des Recommandations**:
- Tracking des actions de due diligence
- Suivi post-investissement
- Mesure de l'efficacité des recommandations

- **Intégration External Data**:
- Connecteurs pour bases de données sectorielles
- Intégration de données climatiques par région
- Benchmarks sectoriels automatisés

- **Multi-Langue**:
- Support pour rapports en plusieurs langues
- Adaptation des référentiels locaux

### 8.2 Cas d'Usage
- **Screening Pré-Due Diligence**:
- Analyse rapide pour identification des risques majeurs
- Préparation des axes d'investigation DD

- **Notes Internes Pré-Comité**:
- Préparation standardisée des dossiers d'investissement
- Support à la décision avec analyse objective

- **Identification des Axes d'Assistance Technique**:
- Repérage des besoins en AT basé sur l'analyse
- Priorisation des interventions selon impact

- **Génération de Clauses ESG/Impact**:
- Propositions de clauses pour pactes d'actionnaires
- Adaptation aux spécificités de l'entreprise

- **Communication avec Bailleurs**:
- Rapports standardisés pour FISEA, DGGF, etc.
- Alignement avec les critères des bailleurs

### 8.3 Intégration avec d'Autres Systèmes
- **Outils de Reporting Impact**:
- Passerelle vers les systèmes de reporting
- Transposition des KPIs identifiés

- **CRM et Outils de Gestion de Portefeuille**:
- Intégration avec systèmes de suivi des investissements
- Export automatisé des données clés

- **Systèmes de Workflow**:
- Intégration dans les processus d'investissement
- Notifications automatiques pour actions ESG

## 9. Exigences Non-Fonctionnelles

### 9.1 Performance
- Temps de génération de rapport < 2 minutes
- Taille maximale de prompt optimisée pour les contraintes LLM
- Utilisation efficiente des tokens pour réduire les coûts

### 9.2 Sécurité
- Gestion sécurisée des clés API
- Pas de stockage permanent des données sensibles
- Conformité RGPD pour les données utilisateurs

### 9.3 Fiabilité
- Mécanismes de retry en cas d'échec API
- Sauvegarde automatique des drafts
- Validation des outputs générés

### 9.4 Utilisabilité
- Interface intuitive sans formation requise
- Feedback visuel pendant la génération
- Aide contextuelle pour chaque section

### 9.5 Maintenabilité
- Documentation complète du code
- Conventions de nommage cohérentes
- Tests automatisés pour les composants critiques

## 10. Contraintes et Limitations

### 10.1 Contraintes Techniques
- Utilisation exclusive des fichiers standards locaux
- Pas d'appel à des APIs externes autres que les LLM
- Exécution possible en environnement local

### 10.2 Limitations Connues
- Analyse limitée aux informations fournies par l'utilisateur
- Pas de vérification factuelle des données entreprise
- Qualité dépendante de la précision de la description

### 10.3 Considérations Éthiques
- Transparence sur la génération automatisée
- Assistance à la décision, non substitution
- Évitement des biais sectoriels ou géographiques

## 11. Critères d'Acceptation

### 11.1 Fonctionnels
- Génération de rapports complets pour tous les secteurs ciblés
- Application correcte des référentiels sélectionnés
- Recommandations pertinentes et actionnables

### 11.2 Techniques
- Architecture modulaire fonctionnelle
- Performances conformes aux attentes
- Documentation complète et à jour

### 11.3 Utilisateur
- Interface intuitive et responsive
- Clarté des rapports générés
- Utilité confirmée par les équipes d'investissement

## 12. Plan de Développement

### 12.1 Phases Recommandées
1. **Phase 1**: Structure de base et architecture (1-2 semaines)
  - Mise en place du squelette applicatif
  - Implémentation du service LLM basique
  - Premier prompt fonctionnel

2. **Phase 2**: Intégration des référentiels et développement des prompts (1-2 semaines)
  - Structuration des référentiels avec métadonnées
  - Développement des prompts sectoriels de base
  - Système d'extraction intelligent des sections pertinentes

3. **Phase 3**: Développement frontend et UI enrichie (1 semaine)
  - Interface Streamlit avec navigation par onglets
  - Système de sauvegarde automatique
  - Barre de progression et feedback

4. **Phase 4**: Composants à valeur ajoutée (1-2 semaines)
  - Score ESG standardisé
  - Tableau de recommandations priorisées
  - Visualisations simples
  - Exports avancés

5. **Phase 5**: Tests, optimisation et déploiement (1 semaine)
  - Tests utilisateurs
  - Optimisation des performances
  - Documentation et déploiement

### 12.2 Approche de Développement
- Développement itératif avec MVP fonctionnel dès la phase 1-2
- Priorité aux fonctionnalités à forte valeur ajoutée
- Tests continus des prompts et de la qualité des rapports
- Configuration externalisée pour ajustements sans code
- Utilisation efficace de Cursor pour accélérer le développement
- Documentation inline et points de refactoring planifiés

