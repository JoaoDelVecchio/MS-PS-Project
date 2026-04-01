# Diagrama de Classes

```mermaid
classDiagram
    %% Relações e Heranças
    Order <|-- LimitOrder
    Order <|-- PeggedOrder
    OrderDoubleLinkedList o-- Order : contém nós
    LimitOrderBook *-- OrderDoubleLinkedList : gerencia filas
    LimitOrderBook *-- Order : mapeia IDs
    MatchingEngine --> LimitOrderBook : altera estado
    CommandParser --> MatchingEngine : envia comandos
    BookPrinter --> LimitOrderBook : lê estado

    %% Definição das Classes
    class Order {
        -String _order_id
        -int _seq_id
        -String _side
        +float price
        +int qty
        +Order prev
        +Order next
        +String order_id
        +int seq_id
        +String side
        +reduce_qty(amount)
    }

    class LimitOrder {
    }

    class PeggedOrder {
        +String peg_type
    }

    class OrderDoubleLinkedList {
        +Order head
        +Order tail
        +insert_sorted(order)
        +append(order)
        +remove(order)
    }

    class LimitOrderBook {
        -dict _orders_map
        -dict _bids_dict
        -dict _asks_dict
        -list _bids_prices
        -list _asks_prices
        -dict _pegged_bids
        -dict _pegged_asks
        -int _time_counter
        -_insert_into_price_list(order)
        +add_limit_order(...)
        +add_pegged_order(...)
        +remove_order(order_id)
        +update_pegged_orders(...)
        +get_order(order_id)
        +get_best_bid()
        +get_best_ask()
        +get_best_limit_bid_price()
        +get_best_limit_ask_price()
        +get_best_resting_bid()
        +get_best_resting_ask()
        +get_all_positions()
    }

    class MatchingEngine {
        +LimitOrderBook lob
        +process_limit_order(...)
        +process_market_order(...)
        +process_pegged_order(...)
        +process_cancel_order(...)
        +process_modify_order(...)
    }

    class CommandParser {
        +MatchingEngine engine
        +process(command)
        -_parse_print_book()
        -_parse_limit()
        -_parse_market()
        -_parse_peg()
        -_parse_cancel()
        -_parse_modify()
    }

    class BookPrinter {
        +print_book(lob)
    }
    