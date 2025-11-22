import argparse
import sys

stock_prices = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOGL": 140,
    "AMZN": 130,
    "MSFT": 330
}

def format_summary(portfolio):
    lines = []
    total = 0
    for s, q in portfolio.items():
        value = q * stock_prices.get(s, 0)
        total += value
        lines.append(f"{s} x {q} = ${value}")
    return lines, total


def save_report(path, portfolio, total):
    with open(path, "w", encoding="utf-8") as f:
        f.write("Stock Portfolio Report\n")
        f.write("-------------------------\n")
        for s, q in portfolio.items():
            value = q * stock_prices.get(s, 0)
            f.write(f"{s} x {q} = ${value}\n")
        f.write("-------------------------\n")
        f.write(f"Total Investment = ${total}\n")


def parse_stocks_arg(s):
    """Parse a string like 'AAPL:2,TSLA:1' into a portfolio dict."""
    p = {}
    if not s:
        return p
    for part in s.split(','):
        if not part.strip():
            continue
        if ':' in part:
            sym, qty = part.split(':', 1)
        elif '=' in part:
            sym, qty = part.split('=', 1)
        else:
            # If only symbol provided, assume qty 1
            sym, qty = part, '1'
        sym = sym.strip().upper()
        try:
            qty = int(qty.strip())
        except Exception:
            qty = 0
        if qty > 0:
            p[sym] = p.get(sym, 0) + qty
    return p


def run_interactive():
    print("📊 Stock Portfolio Tracker")
    print("Type 'done' when you finish.\n")
    portfolio = {}
    while True:
        try:
            stock = input("Enter stock symbol: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nInput terminated")
            break

        if stock == "DONE":
            break

        if stock not in stock_prices:
            print("Stock not available, try again.")
            continue

        try:
            qty = int(input("Enter quantity: "))
            portfolio[stock] = portfolio.get(stock, 0) + qty
        except ValueError:
            print("Enter a valid number.")
            continue

    lines, total = format_summary(portfolio)
    print("\n--- Portfolio Summary ---")
    for l in lines:
        print(l)
    print("-------------------------")
    print(f"Total Investment = ${total}")
    print("-------------------------\n")

    save = input("Save result to a file? (yes/no): ").lower()
    if save == "yes":
        save_report("portfolio_report.txt", portfolio, total)
        print("Saved as portfolio_report.txt")


def main():
    parser = argparse.ArgumentParser(description="Stock portfolio tracker. Defaults to interactive mode.")
    parser.add_argument('--demo', action='store_true', help='Run a demo portfolio and exit')
    parser.add_argument('--stocks', type=str, help="Comma-separated SYMBOL:QTY pairs, e.g. AAPL:2,TSLA:1")
    parser.add_argument('--input-file', type=str, help='Path to file with alternating lines SYMBOL then QTY (or JSON)')
    parser.add_argument('--auto-save', action='store_true', help='Automatically save report to portfolio_report.txt')
    args = parser.parse_args()

    # If no special flags, run interactive mode
    if not (args.demo or args.stocks or args.input_file):
        run_interactive()
        return

    portfolio = {}

    if args.demo:
        portfolio = {"AAPL": 2, "TSLA": 1}

    if args.stocks:
        parsed = parse_stocks_arg(args.stocks)
        # merge
        for k, v in parsed.items():
            portfolio[k] = portfolio.get(k, 0) + v

    if args.input_file:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                parts = [line.strip() for line in f if line.strip()]
            # If file is a simple list of SYMBOL and QTY on alternating lines
            i = 0
            while i < len(parts):
                sym = parts[i].upper()
                qty = 1
                if i + 1 < len(parts):
                    try:
                        qty = int(parts[i+1])
                        i += 2
                    except ValueError:
                        # Next line not an int: treat current line as symbol only
                        i += 1
                else:
                    i += 1
                if qty > 0:
                    portfolio[sym] = portfolio.get(sym, 0) + qty
        except FileNotFoundError:
            print(f"Input file not found: {args.input_file}", file=sys.stderr)
            sys.exit(2)

    # Validate symbols and drop unknown ones with a warning
    cleaned = {}
    for s, q in portfolio.items():
        if s not in stock_prices:
            print(f"Warning: unknown stock symbol '{s}' ignored", file=sys.stderr)
            continue
        cleaned[s] = q

    portfolio = cleaned

    lines, total = format_summary(portfolio)
    print("--- Portfolio Summary ---")
    for l in lines:
        print(l)
    print("-------------------------")
    print(f"Total Investment = ${total}")
    print("-------------------------")

    if args.auto_save:
        save_report("portfolio_report.txt", portfolio, total)
        print("Saved as portfolio_report.txt")


if __name__ == '__main__':
    main()
