import argparse
import yaml
from pathlib import Path

from database.db_utils import get_engine
from models import RecommenderSystem


def load_config(config_path):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file {config_path} not found.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def cmd_build_models(config_path):
    config = load_config(config_path)
    engine = get_engine(config["database"]["uri"])
    recsys = RecommenderSystem(engine=engine, config=config)
    recsys.load_data().build_models()
    print("Models built successfully.")


def cmd_recommend(config_path, customer_id, top_n):
    config = load_config(config_path)
    engine = get_engine(config["database"]["uri"])
    recsys = RecommenderSystem(engine=engine, config=config)
    recsys.load_data().build_models()
    df = recsys.recommend_products(customer_id, top_n=top_n)
    print(df.to_string(index=False))


def cmd_export(config_path, outpath, top_n):
    config = load_config(config_path)
    engine = get_engine(config["database"]["uri"])
    recsys = RecommenderSystem(engine=engine, config=config)
    recsys.load_data().build_models()
    recsys.export_all(outpath=outpath, top_n=top_n)
    print(f"Report exported to {outpath}")


def main():
    parser = argparse.ArgumentParser(description="E-commerce Recommendation System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build-models command
    p_build = subparsers.add_parser("build-models", help="Build recommendation models")
    p_build.add_argument("--config", default="config_example.yaml", help="Path to config YAML")

    # recommend command
    p_recommend = subparsers.add_parser("recommend", help="Recommend products for a customer")
    p_recommend.add_argument("customer_id", type=int, help="Customer ID")
    p_recommend.add_argument("--config", default="config_example.yaml", help="Path to config YAML")
    p_recommend.add_argument("--top-n", type=int, default=10, help="Number of recommendations")

    # export command
    p_export = subparsers.add_parser("export", help="Export Excel reports for all customers")
    p_export.add_argument("--config", default="config_example.yaml", help="Path to config YAML")
    p_export.add_argument("--outpath", default="data/sample_reports.xlsx", help="Output Excel file path")
    p_export.add_argument("--top-n", type=int, default=10, help="Number of recommendations per customer")

    args = parser.parse_args()

    if args.command == "build-models":
        cmd_build_models(args.config)
    elif args.command == "recommend":
        cmd_recommend(args.config, args.customer_id, args.top_n)
    elif args.command == "export":
        cmd_export(args.config, args.outpath, args.top_n)


if __name__ == "__main__":
    main()
