#!/usr/bin/env python3
"""Command-line interface for Binance Futures Trading Bot."""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from bot import (
    setup_logging,
    get_futures_client,
    place_order,
    get_recent_orders,
    validate_order_params,
)
from bot.client import check_api_status
app = typer.Typer(
    name="trading-bot",
    help="🚀 Binance Futures Trading Bot (Testnet)",
    add_completion=False,
)
console = Console()
@app.command()
def order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair (e.g., BTCUSDT)"),
    side: str = typer.Option(..., "--side", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="Order type: MARKET, LIMIT, or STOP_LIMIT"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (required for LIMIT/STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", help="Stop price (required for STOP_LIMIT)"),
):
    """
    Place a futures order on Binance Testnet.
    """
    setup_logging()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🚀 Binance Futures Trading Bot[/bold cyan]\n"
        "[dim]Testnet Mode[/dim]",
        border_style="cyan",
    ))
    console.print()
    
    is_valid, error_msg = validate_order_params(
        symbol, side, order_type, quantity, price, stop_price
    )
    
    if not is_valid:
        console.print(f"[red]❌ Validation Error:[/red] {error_msg}")
        raise typer.Exit(1)
    
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Field", style="dim")
    summary_table.add_column("Value", style="bold")
    
    summary_table.add_row("Symbol", symbol.upper())
    summary_table.add_row("Side", f"[green]{side.upper()}[/green]" if side.upper() == "BUY" else f"[red]{side.upper()}[/red]")
    summary_table.add_row("Type", order_type.upper())
    summary_table.add_row("Quantity", str(quantity))
    if price:
        summary_table.add_row("Price", str(price))
    if stop_price:
        summary_table.add_row("Stop Price", str(stop_price))
    
    console.print(Panel(summary_table, title="📋 Order Summary", border_style="blue"))
    console.print()
    
    with console.status("[bold green]Connecting to Binance Testnet...[/bold green]"):
        client = get_futures_client()
    
    if not client:
        console.print("[red]❌ Failed to initialize Binance client. Check your API credentials.[/red]")
        raise typer.Exit(1)
    
    with console.status("[bold green]Placing order...[/bold green]"):
        result = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    
    console.print()
    
    if result.get("success"):
        console.print("[green]✅ Order placed successfully![/green]")
        console.print()
        
        result_table = Table(show_header=False, box=None, padding=(0, 2))
        result_table.add_column("Field", style="cyan")
        result_table.add_column("Value", style="bold white")
        
        result_table.add_row("Order ID", str(result.get("order_id", "N/A")))
        result_table.add_row("Status", result.get("status", "N/A"))
        result_table.add_row("Executed Qty", result.get("executed_qty", "N/A"))
        result_table.add_row("Avg Price", result.get("avg_price", "N/A"))
        
        console.print(Panel(result_table, title="📊 Order Result", border_style="green"))
    else:
        console.print(f"[red]❌ Order failed:[/red] {result.get('error', 'Unknown error')}")
        raise typer.Exit(1)
@app.command()
def status():
    """
    Check API connection status and account balance.
    """
    setup_logging()
    
    console.print()
    console.print("[bold cyan]🔍 Checking API Status...[/bold cyan]")
    console.print()
    
    with console.status("[bold green]Connecting...[/bold green]"):
        client = get_futures_client()
    
    if not client:
        console.print("[red]❌ Failed to connect. Check your API credentials.[/red]")
        raise typer.Exit(1)
    
    status_info = check_api_status(client)
    
    if status_info.get("connected"):
        console.print("[green]✅ Connected to Binance Futures Testnet[/green]")
        console.print()
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="dim")
        table.add_column("Value", style="bold")
        
        table.add_row("Available Balance", f"${status_info.get('available_balance', 0):,.2f} USDT")
        table.add_row("Total Balance", f"${status_info.get('total_balance', 0):,.2f} USDT")
        
        console.print(Panel(table, title="💰 Account Info", border_style="green"))
    else:
        console.print(f"[red]❌ Connection failed:[/red] {status_info.get('error', 'Unknown error')}")
        raise typer.Exit(1)
@app.command()
def history(
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s", help="Filter by symbol"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of orders to show"),
):
    """
    View recent order history.
    """
    setup_logging()
    
    console.print()
    console.print("[bold cyan]📜 Fetching Order History...[/bold cyan]")
    console.print()
    
    with console.status("[bold green]Loading...[/bold green]"):
        client = get_futures_client()
    
    if not client:
        console.print("[red]❌ Failed to connect. Check your API credentials.[/red]")
        raise typer.Exit(1)
    
    orders = get_recent_orders(client, symbol, limit)
    
    if not orders:
        console.print("[yellow]No orders found.[/yellow]")
        return
    
    table = Table(title="Recent Orders", show_lines=True)
    table.add_column("Order ID", style="cyan", no_wrap=True)
    table.add_column("Symbol", style="bold")
    table.add_column("Side")
    table.add_column("Type")
    table.add_column("Qty")
    table.add_column("Status")
    
    for order in orders:
        side_color = "green" if order["side"] == "BUY" else "red"
        table.add_row(
            str(order["order_id"]),
            order["symbol"],
            f"[{side_color}]{order['side']}[/{side_color}]",
            order["type"],
            order["quantity"],
            order["status"],
        )
    
    console.print(table)
if __name__ == "__main__":
    app()

