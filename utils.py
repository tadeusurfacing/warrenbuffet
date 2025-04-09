import pandas as pd

def formatar_valores(row):
    row = row.copy()

    row["Preço Médio"] = f"R$ {row['Preço Médio']:.2f}"

    row["Preço Atual"] = (
        f"R$ {row['Preço Atual']:.2f}" if pd.notna(row["Preço Atual"]) else "-"
    )

    preco_teto_valor = pd.to_numeric(row.get("Preço Teto"), errors="coerce")
    row["Preço Teto"] = (
        f"R$ {preco_teto_valor:.2f}" if pd.notna(preco_teto_valor) else "-"
    )

    row["Total Investido"] = f"R$ {row['Total Investido']:.2f}"
    row["Valor Atual"] = f"R$ {row['Valor Atual']:.2f}"

    dividendos = pd.to_numeric(row.get("Dividendos"), errors="coerce")
    row["Dividendos"] = (
        f"R$ {dividendos:.2f}" if pd.notna(dividendos) else "R$ 0.00"
    )

    row["Rentabilidade"] = f"{row['Rentabilidade']:.2f}%"

    div_acao = pd.to_numeric(row.get("Dividendos/Ação"), errors="coerce")
    row["Dividendos/Ação"] = (
        f"R$ {div_acao:.2f}" if pd.notna(div_acao) else "R$ 0.00"
    )

    pt_bazin = pd.to_numeric(row.get("PT Bazin"), errors="coerce")
    row["PT Bazin"] = f"R$ {pt_bazin:.2f}" if pd.notna(pt_bazin) else "-"

    return row
