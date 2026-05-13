import argparse
import os
from dotenv import load_dotenv
from src.database import Database
from src.manager import Manager

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="SG Mobile Price Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add Brand Command
    brand_parser = subparsers.add_parser("add-brand", help="Add a new brand")
    brand_parser.add_argument("name", type=str, help="Brand name")

    # Add Family Command
    family_parser = subparsers.add_parser("add-family", help="Add a new product family")
    family_parser.add_argument("brand_id", type=str, help="Brand UUID")
    family_parser.add_argument("name", type=str, help="Family name")
    family_parser.add_argument("slug", type=str, help="Family slug (URL friendly)")

    args = parser.parse_args()

    # Initialize DB and Manager
    db = Database()
    manager = Manager(db)

    if args.command == "add-brand":
        result = manager.add_brand(args.name)
        print(result)
    elif args.command == "add-family":
        result = manager.add_family(args.brand_id, args.name, args.slug)
        print(result)
    else:
        parser.print_help()

    db.close()

if __name__ == "__main__":
    main()
