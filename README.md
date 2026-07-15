# 🏠 ReservasPRO — Gerenciamento de Reservas

Dashboard de reservas (Airbnb/Booking) do apartamento sublocado, publicado em
GitHub Pages e atualizado automaticamente a partir do Google Sheets — mesmo
padrão do Dashboard Financeiro, BYD, Pinho Law e MGO.

## Arquitetura

```
Google Sheets (aba RESERVAS)
     │
     ▼ (gspread via Service Account, somente leitura)
fetch_data.py
     │ injeta const DATA= no HTML
     ▼
dashboard.html  ──▶  GitHub Pages (https://atlassolucoes.github.io/reservas/dashboard.html)
     ▲
GitHub Actions (08h/20h + push + manual)
```

## Configuração inicial

### 1. Compartilhar a planilha com a service account

A planilha precisa ser compartilhada como **Leitor** com:
`agp-dashboard@agp-dashboard.iam.gserviceaccount.com`
(mesma service account já usada no BYD, Pinho Law e MGO)

### 2. Estrutura esperada da aba RESERVAS

| Coluna | Formato |
|---|---|
| PLATAFORMA | texto (ex: AIRBNB, BOOKING) |
| DATA RESERVA | dd/mm/yyyy |
| HOSPEDE | texto |
| TELEFONE | texto |
| STATUS | texto (ex: Confirmada, Pendente) |
| QUANTIDADE DE PESSOAS | número |
| QUANTIDADE DE DIAS | número |
| QUARTO | texto (ex: QUARTO SOLTEIRO, QUARTO CASAL) |
| CHECK-IN | dd/mm/yyyy hh:mm:ss |
| CHECK-OUT | dd/mm/yyyy hh:mm:ss |
| VALOR RESERVA | R$ 0,00 |
| VALOR COMISSÃO | R$ 0,00 |
| VALOR A RECEBER | R$ 0,00 |
| DATA DO RECEBIMENTO | dd/mm/yyyy |
| OBSERVAÇÃO | texto |

Plataformas, status e tipos de quarto **não são fixos no código** — o
dashboard gera os filtros dinamicamente a partir do que existir na planilha.

## Atualização automática

Workflow roda **08h e 20h (Brasília)**, a cada push na `main`, e manualmente
via **Actions → Update Reservas Dashboard → Run workflow** (ou digitando
"ATUALIZE AS RESERVAS" para a Claude disparar via API).

## Planilha

ID: `1meO-CLIibr0L6osznnnYJXU8N7obiURP3-M56AwPvWs`
Link: https://docs.google.com/spreadsheets/d/1meO-CLIibr0L6osznnnYJXU8N7obiURP3-M56AwPvWs/edit
