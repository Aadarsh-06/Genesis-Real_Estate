<<<<<<< HEAD
<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">

<img src="genesis-frontend/public/logo.png" width="400px" alt="EstateEngine - Intelligent Property Analysis"/>

# EstateEngine - Real Estate Investment Advisor

<em></em>

<!-- BADGES -->
<!-- local repository, no metadata badges. -->

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
<img src="https://img.shields.io/badge/npm-CB3837.svg?style=default&logo=npm&logoColor=white" alt="npm">
<img src="https://img.shields.io/badge/Autoprefixer-DD3735.svg?style=default&logo=Autoprefixer&logoColor=white" alt="Autoprefixer">
<img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=default&logo=SQLAlchemy&logoColor=white" alt="SQLAlchemy">
<img src="https://img.shields.io/badge/PostCSS-DD3A0A.svg?style=default&logo=PostCSS&logoColor=white" alt="PostCSS">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=default&logo=JavaScript&logoColor=black" alt="JavaScript">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=default&logo=FastAPI&logoColor=white" alt="FastAPI">
<br>
<img src="https://img.shields.io/badge/React-61DAFB.svg?style=default&logo=React&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Vite-646CFF.svg?style=default&logo=Vite&logoColor=white" alt="Vite">
<img src="https://img.shields.io/badge/OpenAI-412991.svg?style=default&logo=OpenAI&logoColor=white" alt="OpenAI">
<img src="https://img.shields.io/badge/Axios-5A29E4.svg?style=default&logo=Axios&logoColor=white" alt="Axios">
<img src="https://img.shields.io/badge/CSS-663399.svg?style=default&logo=CSS&logoColor=white" alt="CSS">
<img src="https://img.shields.io/badge/Chart.js-FF6384.svg?style=default&logo=chartdotjs&logoColor=white" alt="Chart.js">

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Website Flow](#website-flow)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

**EstateEngine** is an AI-powered real estate investment advisor that helps users make informed decisions about whether to **buy or rent** properties in India. The platform leverages RAG (Retrieval-Augmented Generation) technology with OpenAI to analyze property data from multiple cities and provide personalized financial recommendations.

The system analyzes real estate data from **Mumbai** and **Bangalore**, calculating metrics like EMI, ROI, wealth projections, and break-even years to deliver data-driven buy vs. rent recommendations.

---

## Features

- 🤖 **AI-Powered Property Search** - Natural language queries to find properties
- 📊 **Buy vs Rent Analysis** - Financial comparison with wealth projections
- 💡 **"Why?" Explanations** - Understand the reasoning behind each recommendation
- 🔄 **"What Would Flip?" Analysis** - See what changes would reverse the decision
- 📈 **Market Insights Dashboard** - Visual analytics for market trends
- 🎯 **Smart Filters** - Filter by city, BHK, price range, and localities
- ⚡ **Real-time RAG** - ChromaDB vector search with TF-IDF embeddings

---

## Website Flow


flowchart TD
    A[🏠 User Opens EstateEngine] --> B{Select Tab}
    
    B -->|AI Advisor| C[💬 Chat Interface]
    B -->|Market Insights| D[📊 Market Snapshot Dashboard]
    B -->|About| E[ℹ️ About Page]
    
    C --> F[User Enters Query]
    F --> G{Query Type?}
    
    G -->|Greeting/Chitchat| H[Direct Response]
    G -->|Broad Query| I[Show Filter Chips]
    G -->|Specific Query| J[RAG Retrieval]
    
    I --> K[User Selects Filters]
    K --> J
    
    J --> L[ChromaDB Vector Search]
    L --> M[TF-IDF Embeddings]
    M --> N[Retrieve Matching Properties]
    N --> O[OpenAI Generates Response]
    O --> P[Display Property Cards]
    
    P --> Q{User Action?}
    Q -->|"Why?"| R[/explain API]
    Q -->|"What Would Flip?"| S[/flip API]
    Q -->|Show More| T[Pagination - Next Results]
    
    R --> U[AI Explains Buy/Rent Decision]
    S --> V[AI Shows Decision Flip Factors]
    T --> N
    
    D --> W[Fetch Market Filters]
    W --> X[Apply BHK/Price/Area Filters]
    X --> Y[Display Charts]
    Y --> Z[Buy vs Rent Distribution]
    Y --> AA[Median Price/sqft]
    Y --> AB[Break-even Years]
```

### User Journey

1. **Landing** → User arrives at the AI Advisor chat interface
2. **Query** → User types a natural language question (e.g., "Show me 3BHK in Mumbai")
3. **Intent Classification** → Backend classifies query intent (greeting, property search, comparison, etc.)
4. **Retrieval** → ChromaDB searches for matching properties using TF-IDF embeddings
5. **Response** → AI generates a contextual response with property cards
6. **Deep Dive** → User can click "Why?" for detailed financial reasoning or "What Would Flip?" for sensitivity analysis
7. **Market Insights** → Switch to dashboard for aggregate market analytics

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Main chat endpoint - handles queries and returns property recommendations |
| `/explain` | POST | Returns detailed explanation for why a property is recommended to buy/rent |
| `/flip` | POST | Analyzes what factors would flip the buy/rent decision |
| `/market_snapshot` | GET | Returns market analytics with optional filters |
| `/market_filters` | GET | Returns available filter options for the market dashboard |

---

## Project Structure

```sh
└── Genesis-Real_Estate/
    ├── calaculate_financial_terms
    │   ├── banks.csv
    │   ├── generate_final_buy_rent_csv.py
    │   ├── merged_real_estate_data_RAG_final.csv
    │   ├── modules
    │   └── output
    ├── data
    │   ├── blrsuratpune-MB-analysis.csv
    │   ├── blrsuratpune-MB.csv
    │   ├── housing_pune_analysis.csv
    │   ├── merged_real_estate_data.csv
    │   ├── merged_real_estate_data_FINAL_CLEAN.csv
    │   ├── MumDelHyd_99acres_data.csv
    │   ├── MumDelHyd_99acres_full_investment_analysis_final.csv
    │   ├── MumDelHyd_housing.com_data.csv
    │   ├── MumDelHyd_housing_full_investment_analysis_final.csv
    │   ├── MumDelHyd_magicbricks_data.csv
    │   └── MumDelHyd_magicbricks_data_analysis.csv
    ├── genesis-frontend
    │   ├── index.html
    │   ├── package-lock.json
    │   ├── package.json
    │   ├── postcss.config.cjs
    │   ├── public
    │   ├── README.md
    │   ├── src
    │   ├── tailwind.config.cjs
    │   └── vite.config.js
    ├── package-lock.json
    ├── rag_app
    │   ├── __init__.py
    │   ├── check_db.py
    │   ├── config.py
    │   ├── db.py
    │   ├── embeddings.py
    │   ├── ingest.py
    │   ├── intent.py
    │   ├── main.py
    │   ├── rag.py
    │   ├── requirements.txt
    │   ├── test_query.py
    │   ├── test_rag.py
    │   └── tfidf_embedding.py
    └── README.md
```

### Project Index

<details open>
	<summary><b><code>C:\USERS\JUVAN\GENESIS-REAL_ESTATE/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/package-lock.json'>package-lock.json</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- calaculate_financial_terms Submodule -->
	<details>
		<summary><b>calaculate_financial_terms</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ calaculate_financial_terms</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\generate_final_buy_rent_csv.py'>generate_final_buy_rent_csv.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
			<!-- modules Submodule -->
			<details>
				<summary><b>modules</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ calaculate_financial_terms.modules</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\buy.py'>buy.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\comapre.py'>comapre.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\compare.py'>compare.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\loan.py'>loan.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\plots.py'>plots.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\rent.py'>rent.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/calaculate_financial_terms\modules\tax.py'>tax.py</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- genesis-frontend Submodule -->
	<details>
		<summary><b>genesis-frontend</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ genesis-frontend</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\index.html'>index.html</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\package-lock.json'>package-lock.json</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\package.json'>package.json</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\postcss.config.cjs'>postcss.config.cjs</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\tailwind.config.cjs'>tailwind.config.cjs</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\vite.config.js'>vite.config.js</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
			<!-- src Submodule -->
			<details>
				<summary><b>src</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ genesis-frontend.src</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\src\App.jsx'>App.jsx</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\src\index.css'>index.css</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\src\main.jsx'>main.jsx</a></b></td>
							<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
						</tr>
					</table>
					<!-- components Submodule -->
					<details>
						<summary><b>components</b></summary>
						<blockquote>
							<div class='directory-path' style='padding: 8px 0; color: #666;'>
								<code><b>⦿ genesis-frontend.src.components</b></code>
							<table style='width: 100%; border-collapse: collapse;'>
							<thead>
								<tr style='background-color: #f8f9fa;'>
									<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
									<th style='text-align: left; padding: 8px;'>Summary</th>
								</tr>
							</thead>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\src\components\About.jsx'>About.jsx</a></b></td>
									<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
								</tr>
								<tr style='border-bottom: 1px solid #eee;'>
									<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/genesis-frontend\src\components\MarketSnapshot.jsx'>MarketSnapshot.jsx</a></b></td>
									<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
								</tr>
							</table>
						</blockquote>
					</details>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- rag_app Submodule -->
	<details>
		<summary><b>rag_app</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ rag_app</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\check_db.py'>check_db.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\config.py'>config.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\db.py'>db.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\embeddings.py'>embeddings.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\ingest.py'>ingest.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\intent.py'>intent.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\main.py'>main.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\rag.py'>rag.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\test_query.py'>test_query.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\test_rag.py'>test_rag.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='C:\Users\juvan\Genesis-Real_Estate/blob/master/rag_app\tfidf_embedding.py'>tfidf_embedding.py</a></b></td>
					<td style='padding: 8px;'>Code>❯ REPLACE-ME</code></td>
				</tr>
			</table>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Npm, Pip

### Installation

Build Genesis-Real_Estate from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone ../Genesis-Real_Estate
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd Genesis-Real_Estate
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![npm][npm-shield]][npm-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [npm-shield]: None -->
	<!-- [npm-link]: None -->

	**Using [npm](None):**

	```sh
	❯ echo 'INSERT-INSTALL-COMMAND-HERE'
	```
<!-- SHIELDS BADGE CURRENTLY DISABLED -->
	<!-- [![pip][pip-shield]][pip-link] -->
	<!-- REFERENCE LINKS -->
	<!-- [pip-shield]: https://img.shields.io/badge/Pip-3776AB.svg?style={badge_style}&logo=pypi&logoColor=white -->
	<!-- [pip-link]: https://pypi.org/project/pip/ -->

	**Using [pip](https://pypi.org/project/pip/):**

	```sh
	❯ pip install -r rag_app\requirements.txt
	```

### Usage

Run the project with:

**Using [npm](None):**
```sh
echo 'INSERT-RUN-COMMAND-HERE'
```
**Using [pip](https://pypi.org/project/pip/):**
```sh
python {entrypoint}
```

### Testing

Genesis-real_estate uses the {__test_framework__} test framework. Run the test suite with:

**Using [npm](None):**
```sh
echo 'INSERT-TEST-COMMAND-HERE'
```
**Using [pip](https://pypi.org/project/pip/):**
```sh
pytest
```

---

## Contributing

- **💬 [Join the Discussions](https://LOCAL/juvan/Genesis-Real_Estate/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://LOCAL/juvan/Genesis-Real_Estate/issues)**: Submit bugs found or log feature requests for the `Genesis-Real_Estate` project.
- **💡 [Submit Pull Requests](https://LOCAL/juvan/Genesis-Real_Estate/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your LOCAL account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone C:\Users\juvan\Genesis-Real_Estate
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to LOCAL**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://LOCAL{/juvan/Genesis-Real_Estate/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=juvan/Genesis-Real_Estate">
   </a>
</p>
</details>

---

## License

Genesis-real_estate is protected under the [LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## Acknowledgments

- Credit `contributors`, `inspiration`, `references`, etc.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---
