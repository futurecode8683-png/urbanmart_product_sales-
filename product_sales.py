from pathlib import Path
import pandas as pd
import numpy as np

# =====================================================
# STEP 1: LOAD URBANMART PRODUCT SALES DATASET
# =====================================================


def find_dataset_file():
    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parent
    candidate_names = [
        "urbanmart_product_sales.xlsx",
        "urbanmart_product_sales.csv",
        "urbanmart_product_sales.tsv",
        "urbanmart_product_sales.txt",
        "olist_order_items_dataset.xlsx",
        "olist_order_items_dataset.csv",
        "olist_order_items_dataset.tsv",
        "olist_order_items_dataset.txt",
    ]
    candidate_paths = [
        *[script_dir / name for name in candidate_names],
        *[workspace_root / name for name in candidate_names],
    ]
    return next((path for path in candidate_paths if path.exists()), candidate_paths[0])


def load_dataset(file_path):
    suffix = file_path.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(file_path)
        except ValueError:
            with open(file_path, "rb") as f:
                sample = f.read(4096)
            if b"\t" in sample:
                return pd.read_csv(file_path, sep="\t")
            raise

    if suffix in {".csv", ".tsv", ".txt"}:
        sep = "\t" if suffix in {".tsv", ".txt"} else None
        return pd.read_csv(file_path, sep=sep, engine="python")

    with open(file_path, "rb") as f:
        sample = f.read(4096)

    if b"\t" in sample:
        return pd.read_csv(file_path, sep="\t")
    return pd.read_csv(file_path)


data_file = find_dataset_file()

if not data_file.exists():
    raise FileNotFoundError(
        "Dataset not found. Checked the workspace root and the .vscode folder."
    )

df = load_dataset(data_file)

print("\n========== DATASET LOADED ==========")
print("File Name:", data_file.name)


# =====================================================
# STEP 2: DATASET OVERVIEW
# =====================================================

# First 5 rows
print("\nFirst 5 Rows:")
print(df.head())

# Last 5 rows
print("\nLast 5 Rows:")
print(df.tail())

# Dataset rows and columns
print("\nDataset Shape:", df.shape)

# Column names
print("\nColumn Names:")
print(df.columns.tolist())

# Data types and non-null counts
print("\nDataset Information:")
df.info()

# Statistical summary
print("\nStatistical Summary:")
print(df.describe(include="all"))


# =====================================================
# STEP 3: MISSING VALUE ANALYSIS
# =====================================================

# Missing values in each column
print("\nMissing Values:")
print(df.isnull().sum())

# Total missing values
print(
    "\nTotal Missing Values:",
    df.isnull().sum().sum()
)

# Missing value percentage
missing_percent = (
    df.isnull().sum() / len(df)
) * 100

print("\nMissing Value Percentage:")
print(missing_percent.round(2))


# =====================================================
# STEP 4: DUPLICATE ANALYSIS
# =====================================================

# Exact duplicate rows
print(
    "\nDuplicate Rows:",
    df.duplicated().sum()
)

# Duplicate product IDs
if "product_id" in df.columns:
    print(
        "Duplicate Product IDs:",
        df["product_id"].duplicated().sum()
    )


# =====================================================
# STEP 5: DATA TYPE CHECKING
# =====================================================

print("\nData Types Before Conversion:")
print(df.dtypes)

# Convert product detail columns to numeric
numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

print("\nData Types After Conversion:")
print(df.dtypes)


# =====================================================
# STEP 6: DATA QUALITY CHECKS
# =====================================================

# Negative product weights
if "product_weight_g" in df.columns:
    print(
        "\nNegative Product Weights:",
        (df["product_weight_g"] < 0).sum()
    )

# Zero product weights
if "product_weight_g" in df.columns:
    print(
        "Zero Product Weights:",
        (df["product_weight_g"] == 0).sum()
    )

# Negative dimensions
dimension_columns = [
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

for col in dimension_columns:
    if col in df.columns:
        print(
            f"Negative Values in {col}:",
            (df[col] < 0).sum()
        )


# =====================================================
# STEP 7: PRODUCT KPI ANALYSIS
# =====================================================

total_records = len(df)

if "product_id" in df.columns:
    unique_products = df["product_id"].nunique()
else:
    unique_products = np.nan

if "product_category_name" in df.columns:
    total_categories = df["product_category_name"].nunique()
else:
    total_categories = np.nan

if pd.notna(total_categories) and total_categories > 0:
    average_products_per_category = (
        unique_products / total_categories
    )
else:
    average_products_per_category = np.nan

print("\n========== PRODUCT KPI ANALYSIS ==========")

print("Total Records:", total_records)
print("Unique Products:", unique_products)
print("Total Categories:", total_categories)

print(
    "Average Products per Category:",
    round(average_products_per_category, 2)
    if pd.notna(average_products_per_category)
    else "N/A"
)


# =====================================================
# STEP 8: PRODUCT CATEGORY COMPLETENESS
# =====================================================

if "product_category_name" in df.columns:

    missing_category_count = (
        df["product_category_name"].isnull().sum()
    )

    missing_category_rate = (
        missing_category_count / len(df)
    ) * 100

    category_completeness = (
        df["product_category_name"].notna().mean()
    ) * 100

    print("\n========== CATEGORY ANALYSIS ==========")

    print(
        "Missing Category Count:",
        missing_category_count
    )

    print(
        "Missing Category Rate:",
        round(missing_category_rate, 2), "%"
    )

    print(
        "Category Completeness:",
        round(category_completeness, 2), "%"
    )


# =====================================================
# STEP 9: PRODUCT METADATA COMPLETENESS
# =====================================================

product_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

completeness_results = []

print("\n========== PRODUCT DETAIL COMPLETENESS ==========")

for col in product_columns:

    if col in df.columns:

        completeness = df[col].notna().mean() * 100

        missing_count = df[col].isnull().sum()

        print(
            f"{col} Completeness: "
            f"{completeness:.2f}%"
        )

        completeness_results.append({
            "Metric": col,
            "Completeness_Percentage": round(
                completeness, 2
            ),
            "Missing_Count": missing_count
        })

    else:
        print(f"{col}: Column not available")


completeness_df = pd.DataFrame(completeness_results)


# =====================================================
# STEP 10: CATEGORY-WISE PRODUCT ANALYSIS
# =====================================================

if "product_category_name" in df.columns:

    category_analysis = (
        df.groupby(
            "product_category_name",
            dropna=False
        )
        .agg(
            product_count=("product_id", "nunique")
            if "product_id" in df.columns
            else ("product_category_name", "size")
        )
        .reset_index()
        .sort_values(
            "product_count",
            ascending=False
        )
    )

    print("\n========== TOP 10 PRODUCT CATEGORIES ==========")
    print(category_analysis.head(10))


# =====================================================
# STEP 11: PRODUCT PRICE ANALYSIS (IF AVAILABLE)
# =====================================================

# This section runs only if a price column exists.

if "price" in df.columns:

    print("\n========== PRODUCT PRICE ANALYSIS ==========")

    print("Total Price:", round(df["price"].sum(), 2))
    print("Average Price:", round(df["price"].mean(), 2))
    print("Minimum Price:", df["price"].min())
    print("Maximum Price:", df["price"].max())

else:
    print(
        "\nPrice Analysis Skipped: "
        "Price column not available."
    )


# =====================================================
# STEP 12: CREATE KPI SUMMARY
# =====================================================

kpi_summary = pd.DataFrame({
    "KPI": [
        "Total Records",
        "Unique Products",
        "Total Categories",
        "Average Products per Category"
    ],
    "Value": [
        total_records,
        unique_products,
        total_categories,
        average_products_per_category
    ]
})

print("\n========== KPI SUMMARY ==========")
print(kpi_summary)


# =====================================================
# STEP 13: EXPORT PYTHON ANALYSIS TO EXCEL
# =====================================================

output_file = (
    data_file.parent
    / "UrbanMart_Python_Analysis.xlsx"
)

missing_report = pd.DataFrame({
    "Column": df.columns,
    "Missing_Values": df.isnull().sum().values,
    "Missing_Percentage": (
        df.isnull().mean().values * 100
    ).round(2)
})

with pd.ExcelWriter(
    output_file,
    engine="openpyxl"
) as writer:

    df.to_excel(
        writer,
        sheet_name="Product_Data",
        index=False
    )

    kpi_summary.to_excel(
        writer,
        sheet_name="KPI_Summary",
        index=False
    )

    missing_report.to_excel(
        writer,
        sheet_name="Missing_Values",
        index=False
    )

    completeness_df.to_excel(
        writer,
        sheet_name="Metadata_Completeness",
        index=False
    )

    if "product_category_name" in df.columns:
        category_analysis.to_excel(
            writer,
            sheet_name="Category_Analysis",
            index=False
        )

print("\n========== ANALYSIS COMPLETED ==========")
print("Report Saved At:", output_file)