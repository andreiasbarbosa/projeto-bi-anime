<div align="center">

# 🎌 Dashboard de Análise de Dados sobre o Universo dos Animes

**Projeto acadêmico de BI/Análise de Dados** — do dado bruto ao dashboard interativo

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![GitHub Projects](https://img.shields.io/badge/GitHub%20Projects-181717?style=for-the-badge&logo=github&logoColor=white)

</div>

---

## 🎯 Sobre o projeto

Este projeto usa dados públicos do universo dos **animes** para construir do zero, um fluxo completo de BI: extração de dados → limpeza (ETL) → banco de dados relacional → dashboard interativo.

O dashboard é dividido em **4 páginas**, cada uma respondendo diferentes perguntas, como: gêneros mais populares, estúdios mais produtivos e relação entre popularidade e qualidade — sempre com gráficos e tabelas pensados para contar uma história com os dados, e não paenas exibir números soltos.

O projeto conta com **4 etapas incrementais**, cada uma acrescentando uma nova página/funcionalidade ao dashboard.

---

## 📚 Fonte dos dados

Dataset público **[Anime Recommendation Database 2020](https://www.kaggle.com/hernan4444/anime-recommendation-database-2020)**, disponível no Kaggle.

---

## 🗂️ O que você vai encontrar por aqui

```
.
├── 📁 database/          → Modelo do banco de dados (schema.sql) e os dados já tratados
├── 📁 etl/                → Scripts Python que extraem, limpam e carregam os dados
├── 📁 dashboard/          → Arquivo do Power BI (.pbix)
├── 📁 docs/               → Prints e materiais de apoio
└── 📄 README.md           → Este arquivo
```

- **`database/`** — contém a definição das tabelas e os arquivos de dados já limpos e prontos para consulta.
- **`etl/`** — os scripts que transformam os dados brutos do Kaggle nas tabelas finais do banco.
- **`dashboard/`** — o dashboard em si, construído no Power BI.

> O banco de dados usado é um **PostgreSQL hospedado no Supabase**.

---

## 🗓️ Linha do tempo do projeto

| Etapa | Data | O que entrega |
|---|:---:|---|
| ✅ Estrutura inicial | — | Repositório, board de acompanhamento e definição da arquitetura |
| ✅ Dados e banco | — | Dataset tratado e carregado no banco de dados |
| 🔵 **Entrega 1** | **14/09/2026** | Banco funcionando + Página 1: **Panorama Geral** |
| ⚪ Entrega 2 | 13/10/2026 | Página 2: **Gêneros ao longo do tempo** |
| ⚪ Entrega 3 | 08/11/2026 | Página 3: **Estúdios — quantidade x qualidade** |
| ⚪ Entrega 4 | 22/11/2026 | Página 4: **Popularidade vs Qualidade** (fechamento) |

✅ concluído · 🔵 em andamento · ⚪ próximo

---

## 📊 O dashboard

Construído no **Power BI**, com cada página explorando um ângulo diferente dos animes. O link de acesso (via "Publicar na Web") será adicionado aqui assim que o dashboard estiver publicado.
