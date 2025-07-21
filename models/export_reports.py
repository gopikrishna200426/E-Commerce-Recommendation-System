import pandas as pd


def export_excel(customers_df, products_df, transactions_df, recommendations_dict, outpath):
    """Write multi-sheet Excel workbook.

    recommendations_dict: {customer_id: DataFrame(columns=[rank,product_id,...])}
    """
    with pd.ExcelWriter(outpath, engine="openpyxl") as writer:
        customers_df.to_excel(writer, sheet_name="customers", index=False)
        products_df.to_excel(writer, sheet_name="products", index=False)
        transactions_df.to_excel(writer, sheet_name="transactions", index=False)
        for cid, df in recommendations_dict.items():
            sheet = f"recs_{cid}"
            if len(sheet) > 31:
                sheet = f"c{cid}"
            df.to_excel(writer, sheet_name=sheet, index=False)
    return outpath
